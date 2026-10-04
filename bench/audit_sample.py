"""Draw the blind human-audit sample and build the review items (no arm, model or harness shown).

    uv run python -m bench.audit_sample --out results/spot-check
Writes items.json (what the review page shows) and key.json (item -> run identity, kept private).
"""

import argparse
import ast
import csv
import glob
import hashlib
import json
import random
import re
from pathlib import Path

from inspect_ai.log import read_eval_log_samples

from bench.task_schema import Task

SEED = int(hashlib.sha256(b"agent-access-bench-audit-v1").hexdigest()[:16], 16)
EMAIL = re.compile(r"([A-Za-z0-9._%+'-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
TYPE_WEIGHT = {"claims": 3.0, "person_email": 3.0, "flight": 3.0, "set": 1.5, "number": 1.0, "exact": 1.0, "spend": 0.0}
MAX_ANSWER = 6000


def mask(text: str) -> str:
    return EMAIL.sub(lambda m: "•••@" + m.group(2), text or "")


def load_tasks() -> dict[str, Task]:
    out = {}
    for f in glob.glob("tasks/*.jsonl"):
        for line in open(f):
            if line.strip():
                t = Task.model_validate_json(line)
                out[t.id] = t
    return out


def reference(task: Task, detail: dict) -> str:
    g = task.grader
    if g.type == "exact":
        return "Accepted answers: " + " | ".join(g.gold)
    if g.type == "number":
        gold = detail.get("gold", g.gold)
        src = f"captured live from {g.capture} when graded" if g.capture else "fixed answer key"
        return f"Expected value: {gold} (tolerance ±{detail.get('tol', 0)}), {src}."
    if g.type == "set":
        gold = detail.get("gold", g.gold)
        return f"Required items: {', '.join(map(str, gold or []))}. Needs at least {int(g.min_recall * 100)}% of them."
    if g.type == "person_email":
        return (f"Right person: {' / '.join(g.person_names)}. Work email must be on: {', '.join(g.email_domains)}. "
                "Only the first address on those domains counts; ZeroBounce must rate it valid.")
    if g.type == "claims":
        return f"Passes if at least {int(g.pass_share * 100)}% of these hold:\n" + "\n".join(f"{i + 1}. {c}" for i, c in enumerate(g.claims))
    if g.type == "flight":
        parts = [f"{'/'.join(g.origin)} to {'/'.join(g.destination)} on {g.date}"]
        if g.nonstop:
            parts.append("nonstop")
        if g.max_price_usd:
            parts.append(f"at most ${g.max_price_usd:.0f}")
        return "Constraints: " + ", ".join(parts) + f". Price must be within {int(g.cheapest_within * 100)}% of the cheapest valid fare any setup found."
    return ""


def detail_text(task: Task, detail: dict, flight_row: dict | None) -> str:
    g = task.grader
    if g.type == "claims" and "verdicts" in detail:
        return "\n".join(f"{i + 1}. {'yes' if v else 'no'}" for i, v in enumerate(detail["verdicts"])) + f"\nShare: {detail.get('share', 0):.0%}"
    if g.type == "person_email":
        return (f"Person matched: {detail.get('person') or 'none'}\nFirst email domain: {detail.get('email_domain') or 'none'}\n"
                f"ZeroBounce status: {detail.get('email_status') or 'n/a'}")
    if g.type == "flight" and flight_row:
        return (f"Constraint checks: {detail.get('verdicts')}\nStated price: {flight_row.get('flight_price_usd') or 'not found'} USD\n"
                f"Cheapest valid fare found by any setup: {flight_row.get('flight_min_usd') or 'n/a'} USD\n{flight_row.get('flight_note') or ''}")
    return json.dumps(detail, default=str)[:1500]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results/full")
    ap.add_argument("--out", default="results/spot-check")
    ap.add_argument("--core", type=int, default=220)
    ap.add_argument("--harness", type=int, default=30)
    a = ap.parse_args()
    rng = random.Random(SEED)
    tasks = load_tasks()
    rows = [r for r in csv.DictReader(open(Path(a.results) / "runs.csv")) if r["battery"] not in ("spend", "pilot")]
    for r in rows:
        r["_w"] = TYPE_WEIGHT.get(r["grader_type"], 1.0)
    arms = sorted({r["arm"] for r in rows})
    per_arm = {arm: a.core // len(arms) for arm in arms}
    picked = []
    for arm in arms:
        pool = [r for r in rows if r["arm"] == arm and r["_w"] > 0]
        chosen = set()
        while len(chosen) < min(per_arm[arm], len(pool)):
            r = rng.choices(pool, weights=[x["_w"] for x in pool])[0]
            chosen.add((r["log_dir"] if "log_dir" in r else "", r["log"], r["task"], r["epoch"]))
        picked += [r for r in pool if (r.get("log_dir", ""), r["log"], r["task"], r["epoch"]) in chosen]
    # locate each picked run's sample in its log
    need = {}
    for r in picked:
        need.setdefault(r["log"], []).append(r)
    log_paths = {Path(p).name: p for p in glob.glob("logs/**/*.eval", recursive=True)}
    items, key = [], []
    for log_name, rs in need.items():
        want = {(r["task"], int(r["epoch"])): r for r in rs}
        for s in read_eval_log_samples(log_paths[log_name], all_samples_required=False):
            r = want.get((s.id, s.epoch))
            if not r or not s.scores:
                continue
            sc = next(iter(s.scores.values()))
            try:
                det = json.loads(sc.explanation or "{}")
            except ValueError:
                det = {}
            t = tasks[s.id]
            items.append({"battery": r["battery"], "kind": t.grader.type, "task_id": t.id, "prompt": t.prompt,
                          "answer": mask((s.output.completion or "")[:MAX_ANSWER]), "reference": reference(t, det),
                          "grader_pass": r["success"] == "1", "grader_detail": detail_text(t, det, r)})
            key.append({"model": r["model"], "arm": r["arm"], "log": log_name, "task": s.id, "epoch": s.epoch,
                        "weight": r["_w"], "source": "core"})
    # harness track
    hrows = [json.loads(l) for f in glob.glob("results/raw/harness/full-*.jsonl") for l in open(f)]
    hrows = [h for h in hrows if (h.get("task") or h.get("task_id")) in tasks and tasks[h.get("task") or h.get("task_id")].grader.type != "spend"]
    for h in rng.sample(hrows, min(a.harness, len(hrows))):
        tid = h.get("task") or h.get("task_id")
        t = tasks[tid]
        det = h.get("grader_detail") or {}
        if isinstance(det, str):
            try:
                det = ast.literal_eval(det)
            except (ValueError, SyntaxError):
                det = {}
        items.append({"battery": t.battery, "kind": t.grader.type, "task_id": tid, "prompt": t.prompt,
                      "answer": mask((h.get("answer") or h.get("final_answer") or "")[:MAX_ANSWER]), "reference": reference(t, det),
                      "grader_pass": str(h.get("score")) == "1", "grader_detail": detail_text(t, det, None)})
        key.append({"harness": h["harness"], "arm": h["arm"], "task": tid, "epoch": h.get("epoch"), "source": "harness"})
    order = list(range(len(items)))
    rng.shuffle(order)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    final_items, final_key = [], []
    for n, i in enumerate(order, 1):
        iid = f"i{n:03d}"
        final_items.append({"id": iid, "n": n, **items[i]})
        final_key.append({"id": iid, **key[i]})
    json.dump(final_items, open(out / "items.json", "w"), indent=1)
    json.dump(final_key, open(out / "key.json", "w"), indent=1)
    leak = sum(bool(EMAIL.search(x["answer"].replace("•••@", ""))) for x in final_items)
    print(f"items {len(final_items)} | by arm (core) {dict((arm, sum(1 for k in final_key if k.get('arm') == arm and k['source'] == 'core')) for arm in arms)} | "
          f"harness {sum(1 for k in final_key if k['source'] == 'harness')} | unmasked emails {leak}")


if __name__ == "__main__":
    main()
