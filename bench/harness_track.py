"""Harness track runner (pre-registration §3 "Tool awareness", §5).

Runs every harness-track task through real agent CLIs/SDKs in three arms, grades each answer
with bench.graders.grade, and writes one JSON line per run.

    uv run python -m bench.harness_track --harnesses claude-code,codex --arms B,C,C-mcp-only \
        --epochs 3 --batteries gtm,paiddata
    uv run python -m bench.harness_track --batteries pilot --tasks pilot-01,pilot-09 --arms B,C --epochs 1

Arms (docs/harness-track.md has the per-harness install details):
  B           the harness as shipped: built-in web tools on, no MCP servers, no Locus skill.
  C           Locus Pro installed the way the Locus docs say: the Locus Pro MCP server plus the
              official Locus skill/plugin where the harness supports skills (otherwise its
              standard instructions channel).
  C-mcp-only  the Locus Pro MCP server alone.

Task pool: tasks with harness_track=true in the requested batteries. The pilot pool is used only
when asked for (--batteries pilot), and then every pilot task is eligible (none is flagged).

Output: results/raw/harness/<run-id>.jsonl, one line per (harness, arm, task, epoch).
At most MAX_PARALLEL harness processes run at once overall: the vendor keys are shared with
production traffic. Idempotency of Locus calls is left to each harness and the Locus skill.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bench import harnesses, harnesses_extra
from bench.eval import load_tasks
from bench.graders import grade
from bench.task_schema import Task

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "results" / "raw" / "harness"

ALL_HARNESSES = ("claude-code", "codex", "gemini-cli", "openclaw", "hermes", "openai-agents")
ALL_BATTERIES = ("gtm", "paiddata", "structured", "multistep", "travel", "control", "spend")
ARM_MODES = {"B": "none", "C": "mcp+skill", "C-mcp-only": "mcp"}
MAX_PARALLEL = 2
TIMEOUT_S = 900  # pre-registration §8: 15-minute wall clock

# Provider prefix for the grader (judge family is chosen from it).
PROVIDER = {"claude-code": "anthropic", "codex": "openai", "gemini-cli": "google",
            "openclaw": "anthropic", "hermes": "anthropic", "openai-agents": "openai"}

# Locus meta-tools that never bill. Anything else on the Locus server may bill.
FREE_LOCUS_TOOLS = {
    "search_apis", "describe_api", "estimate_cost", "get_balance", "list_apis", "get_call_result",
    "cancel_cost_approval", "get_locus_guide", "list_tool_groups", "request_tool_access", "pin_endpoint",
    "workflow_definition", "workflow_validate", "workflow_runs", "search", "describe", "estimate", "get_result",
}
# usd_charged with a numeric value, at any JSON-escaping depth (schemas have an object there instead).
USD_RE = re.compile(r'usd_charged[\\"]*\s*:\s*[\\"]*(-?\d+(?:\.\d+)?)')
BALANCE_RE = re.compile(r'credits_balance[\\"]*\s*:\s*[\\"]*(-?\d+(?:\.\d+)?)')


def agent_model_id(harness: str, model: str) -> str:
    return model if "/" in model else f"{PROVIDER[harness]}/{model}"


def is_locus_call(name: str | None) -> bool:
    # claude/codex mcp__locus-pro__x, gemini mcp_locus-pro_x, openclaw locus-pro__x, hermes mcp__locus_pro__x
    return bool(name) and "locus" in name.lower() and ("__" in name or name.startswith("mcp_"))


def locus_tool(name: str) -> str:
    return re.split(r"__|_locus-pro_", name)[-1]


def trace_text(raw_trace_path: str) -> str:
    """All trace text a harness wrote for one run (a file, or a directory of files)."""
    p = Path(raw_trace_path)
    if p.is_file():
        return p.read_text(errors="replace")
    if p.is_dir():
        parts = []
        for f in sorted(p.iterdir()):
            # openclaw: transcript.json duplicates trajectory.json; result.json echoes nothing billed.
            if f.name in ("trajectory.json", "events.jsonl", "items.json") or (
                    f.suffix == ".jsonl" and f.name != "events.jsonl"):
                parts.append(f.read_text(errors="replace"))
        return "\n".join(parts)
    return ""


def locus_usd(raw_trace_path: str, locus_names: list[str]) -> float | None:
    """Sum of usd_charged in Locus tool results. Each charge is deduplicated by the balance
    printed next to it, so a result echoed twice in one trace counts once.
    0.0 when no billable Locus tool was called; None when one was but the trace shows no charge."""
    billable = [n for n in locus_names if locus_tool(n) not in FREE_LOCUS_TOOLS]
    text = trace_text(raw_trace_path)
    charges: dict[tuple, float] = {}
    for i, m in enumerate(USD_RE.finditer(text)):
        window = text[max(0, m.start() - 600):m.start()]
        bal = BALANCE_RE.findall(window)
        key = ("bal", bal[-1], m.group(1)) if bal else ("pos", i)
        charges[key] = float(m.group(1))
    if charges:
        return round(sum(charges.values()), 6)
    return 0.0 if not billable else None


def skill_loads(tool_calls: list[dict]) -> int:
    """Calls that load a Locus skill (Claude Skill, Gemini activate_skill, Hermes skill_view, or a
    read of a locus SKILL.md). Diagnostic only."""
    n = 0
    for c in tool_calls:
        name = (c.get("name") or "").lower()
        if c.get("locus") or is_locus_call(c.get("name")):
            continue
        args = json.dumps(c.get("args"), default=str).lower()
        if ("skill" in name and "locus" in args) or ("locus" in args and "skill.md" in args):
            n += 1
    return n


def run_harness(harness: str, prompt: str, arm: str, timeout_s: int) -> dict:
    mode = ARM_MODES[arm]
    if harness in harnesses.HARNESSES:
        return harnesses.run_harness(harness, prompt, mode != "none", None, timeout_s, locus_mode=mode)
    return harnesses_extra.run_harness(harness, prompt, mode != "none", None, timeout_s, locus_mode=mode)


def default_model(harness: str) -> str:
    return {**harnesses.DEFAULT_MODELS, **harnesses_extra.DEFAULT_MODELS}[harness]


def one_run(harness: str, arm: str, task: Task, epoch: int, timeout_s: int) -> dict:
    t0 = time.monotonic()
    rec: dict = {"harness": harness, "arm": arm, "locus_mode": ARM_MODES[arm], "task_id": task.id,
                 "battery": task.battery, "epoch": epoch, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    try:
        res = run_harness(harness, task.prompt, arm, timeout_s)
    except Exception as e:  # an adapter crash is a failed run, never a crashed sweep
        res = {"final_answer": "", "tool_calls": [], "raw_trace_path": None, "exit_code": 1,
               "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()[-1500:]}
    model = agent_model_id(harness, res.get("model") or default_model(harness))
    calls = res.get("tool_calls", [])
    names = [c.get("name") or "" for c in calls]
    # harnesses_extra marks Locus calls itself ("locus": bool); the Agents SDK uses bare MCP names.
    locus_names = [c.get("name") or "" for c in calls if c.get("locus") or is_locus_call(c.get("name"))]
    answer = res.get("final_answer") or ""
    try:
        ok, detail = asyncio.run(grade(task, answer, model)) if answer else (False, {"empty_answer": True})
    except Exception as e:  # grader failure is recorded as a fail, never silently passed
        ok, detail = False, {"grader_error": repr(e)[:300]}
    rec.update({
        "model": model,
        "score": 1 if ok else 0,
        "grader_detail": detail,
        "answer": answer[:4000],
        "tool_calls": names,
        "locus_calls": len(locus_names),
        "locus_tools": [locus_tool(n) for n in locus_names],
        "locus_usd": locus_usd(res["raw_trace_path"], locus_names) if res.get("raw_trace_path") else None,
        "skill_loads": skill_loads(res.get("tool_calls", [])),
        "duration_s": res.get("duration_s", round(time.monotonic() - t0, 2)),
        "exit_code": res.get("exit_code"),
        "error": res.get("error") or (res.get("usage") or {}).get("error"),
        "usage": res.get("usage"),
        "trace_path": res.get("raw_trace_path"),
    })
    return rec


def select_tasks(batteries: list[str], task_ids: list[str] | None) -> list[Task]:
    tasks: list[Task] = []
    for b in batteries:
        tasks += load_tasks([b], harness_only=(b != "pilot"))
    if task_ids:
        missing = set(task_ids) - {t.id for t in tasks}
        if missing:
            raise SystemExit(f"tasks not in the selected pool: {sorted(missing)}")
        tasks = [t for t in tasks if t.id in task_ids]
    return tasks


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harnesses", default=",".join(ALL_HARNESSES))
    ap.add_argument("--arms", default="B,C,C-mcp-only")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batteries", default=",".join(ALL_BATTERIES))
    ap.add_argument("--tasks", help="comma-separated task ids to restrict to (within the pool)")
    ap.add_argument("--timeout", type=int, default=TIMEOUT_S)
    ap.add_argument("--parallel", type=int, default=MAX_PARALLEL, help=f"max concurrent runs (cap {MAX_PARALLEL})")
    ap.add_argument("--run-id")
    a = ap.parse_args()

    hs = [h.strip() for h in a.harnesses.split(",") if h.strip()]
    hs = [harnesses.ALIASES.get(h, h) for h in hs]
    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    for h in hs:
        if h not in ALL_HARNESSES:
            raise SystemExit(f"unknown harness {h!r}; expected {ALL_HARNESSES}")
    for arm in arms:
        if arm not in ARM_MODES:
            raise SystemExit(f"unknown arm {arm!r}; expected {tuple(ARM_MODES)}")
    tasks = select_tasks([b.strip() for b in a.batteries.split(",") if b.strip()],
                         [t.strip() for t in a.tasks.split(",")] if a.tasks else None)
    jobs = [(h, arm, t, e) for e in range(1, a.epochs + 1) for t in tasks for h in hs for arm in arms]

    run_id = a.run_id or time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{run_id}.jsonl"
    print(f"run {run_id}: {len(jobs)} runs ({len(hs)} harnesses x {len(arms)} arms x {len(tasks)} tasks x "
          f"{a.epochs} epochs) -> {out_path}", flush=True)

    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=max(1, min(a.parallel, MAX_PARALLEL))) as pool, open(out_path, "a") as out:
        futs = {pool.submit(one_run, h, arm, t, e, a.timeout): (h, arm, t.id, e) for h, arm, t, e in jobs}
        for f in as_completed(futs):
            h, arm, tid, e = futs[f]
            try:
                rec = f.result()
            except Exception as ex:
                rec = {"harness": h, "arm": arm, "task_id": tid, "epoch": e, "score": 0, "error": repr(ex)[:500]}
            rec["run_id"] = run_id
            with lock:
                out.write(json.dumps(rec, default=str) + "\n")
                out.flush()
            print(f"{h:14s} {arm:10s} {tid:14s} e{e} score={rec.get('score')} locus={rec.get('locus_calls')} "
                  f"usd={rec.get('locus_usd')} {rec.get('duration_s')}s exit={rec.get('exit_code')}"
                  + (f" err={str(rec.get('error'))[:120]}" if rec.get("error") else ""), flush=True)
    summarize(out_path)


def summarize(path: Path) -> None:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    agg: dict[tuple, dict] = {}
    for r in rows:
        k = (r["harness"], r["arm"])
        s = agg.setdefault(k, {"n": 0, "passed": 0, "locus_calls": 0, "usd": 0.0})
        s["n"] += 1
        s["passed"] += r.get("score") or 0
        s["locus_calls"] += r.get("locus_calls") or 0
        s["usd"] += r.get("locus_usd") or 0.0
    print(f"\n{'harness':14s} {'arm':10s} passed  locus_calls  locus_usd")
    for (h, arm), s in sorted(agg.items()):
        print(f"{h:14s} {arm:10s} {s['passed']}/{s['n']:<5d} {s['locus_calls']:<12d} {s['usd']:.3f}")


if __name__ == "__main__":
    main()
