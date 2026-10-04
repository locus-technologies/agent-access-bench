"""Analysis layer (pre-registration sections 2, 9, 10).

    uv run python -m bench.analyze logs/core-1 logs/core-2 --out results/core
    uv run python -m bench.analyze logs/pilot --out results/pilot --include-pilot   # testing only

Reads Inspect logs (via bench.summarize), prices every run, applies the travel battery's
cross-arm cheapest_within rule, and computes the paired clustered bootstrap CIs for H1-H3,
the spend-safety counts for H4, and the secondary metrics. Writes summary.json (every
number), runs.csv (one row per run) and tables.md.

Conventions, fixed here so they cannot drift:
- Unit of analysis is the task. Epochs are averaged within (task, model, arm) first.
- Pooled contrasts weight each model equally: per-model mean over that model's paired
  tasks, then the mean over models. Bootstrap resamples tasks (clusters) with replacement,
  the same resample for every model, 10,000 times, percentile 95% CI.
- Seed: first 8 bytes (big-endian) of sha256("agent-access-bench-v1"), fed to numpy's
  default_rng; each contrast restarts from that seed so results do not depend on order.
- The pilot battery is excluded from everything unless --include-pilot (then it is
  analysed as if it were an access battery, and every output is labelled as such).
- Structured tasks 01-11 ("structured-public") are reported separately and never enter H1.
- Travel: a run's flight score is 1 only if the per-run grader passed its constraint checks
  AND its stated price is within (1 + cheapest_within) of the cheapest constraint-passing
  price any run (any arm, model, epoch) found for that task among the logs passed to this
  invocation (the "run window"). Prices are converted to USD with prereg/fx-rates.json.
- Arm-D vendor spend is a list-price ESTIMATE (bench/vendor_costs.py), flagged as such.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PRICES_PATH = ROOT / "prereg" / "model-prices.json"
FX_PATH = ROOT / "prereg" / "fx-rates.json"
TOOL_TOKENS_PATH = ROOT / "results" / "tool-definition-tokens.json"
LEDGER_PATH = ROOT / "results" / "raw" / "spend-ledger.jsonl"

SEED_STRING = "agent-access-bench-v1"
N_BOOT = 10_000
CI = 0.95
Z95 = 1.959963984540054
H1_BATTERIES = ("gtm", "paiddata", "multistep", "travel", "structured-hostile")
STRUCTURED_HOSTILE_FROM = 12  # structured-12..15 are bot-hostile; 01..11 are public
H2_MARGIN = -0.05
H3_MARGIN = -0.05


def seed_int(s: str = SEED_STRING) -> int:
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


# --- task classification ---------------------------------------------------------------


def battery_of(task_id: str, battery: str) -> str:
    """Analysis battery: splits `structured` into public (01-11) and hostile (12-15)."""
    if battery != "structured":
        return battery
    n = int(task_id.rsplit("-", 1)[1])
    return "structured-hostile" if n >= STRUCTURED_HOSTILE_FROM else "structured-public"


# --- model cost ---------------------------------------------------------------------------


def load_prices(path: Path = PRICES_PATH) -> dict:
    data = json.loads(path.read_text())
    return {**data.get("models", {}), **data.get("judges", {})}


def call_cost(usage: dict, price: dict) -> float:
    """USD for one model call. `usage` is an Inspect ModelUsage as a dict.

    Long-context tier is chosen from this call's prompt size. Reasoning tokens are billed at
    the output rate; they are added only when the provider reported them outside
    output_tokens (detected from total_tokens)."""
    inp = usage.get("input_tokens") or 0
    out = usage.get("output_tokens") or 0
    cw = usage.get("input_tokens_cache_write") or 0
    cr = usage.get("input_tokens_cache_read") or 0
    reasoning = usage.get("reasoning_tokens") or 0
    total = usage.get("total_tokens") or 0
    prompt = inp + cw + cr
    tier = price
    lc = price.get("long_context")
    if lc:
        over = prompt >= lc["threshold_prompt_tokens"] if lc.get("inclusive") else prompt > lc["threshold_prompt_tokens"]
        if over:
            tier = lc
    if reasoning and total >= inp + cw + cr + out + reasoning:
        out += reasoning  # reasoning was reported outside output_tokens (xAI)
    # Providers without a separate cache-write price bill those tokens as ordinary input;
    # a provider without a cache-read price is billed at input too (conservative).
    cw_rate = tier.get("cache_write") if tier.get("cache_write") is not None else tier["input"]
    cr_rate = tier.get("cache_read") if tier.get("cache_read") is not None else tier["input"]
    return (inp * tier["input"] + out * tier["output"] + cw * cw_rate + cr * cr_rate) / 1_000_000


def usage_cost(calls: list[tuple[str, dict]], agent_model: str, prices: dict) -> dict:
    """Agent-model cost of a run's model calls. Calls by any other model are not agent cost."""
    price = prices.get(agent_model)
    if price is None or price.get("input") is None:
        return {"agent_usd": None, "unpriced": [agent_model]}
    return {"agent_usd": sum(call_cost(u, price) for m, u in calls if m == agent_model), "unpriced": []}


def grading_cost(log, prices: dict) -> dict:
    """Judge cost of one eval log. Inspect records scorer model calls only in the log-level
    stats, so this is priced from aggregate usage (base tier)."""
    out = {}
    for model, u in (log.stats.model_usage or {}).items():
        if model == log.eval.model:
            continue
        price = prices.get(model)
        out[model] = None if price is None else round(call_cost(u.model_dump(), price), 6)
    return out


# --- flight price extraction and the cheapest_within rule ---------------------------------

_NUM = r"\d{1,3}(?:[,.\u00a0]\d{3})+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?"
_SYMBOL = {"US$": "USD", "C$": "CAD", "CA$": "CAD", "A$": "AUD", "AU$": "AUD", "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}
_CODES = ("USD", "EUR", "GBP", "CAD", "AUD", "CHF", "JPY")
_PRICE_RE = re.compile(
    r"(?P<sym>US\$|CA\$|C\$|AU\$|A\$|\$|€|£|¥)\s?\**(?P<n1>" + _NUM + r")"
    r"|\b(?P<code>" + "|".join(_CODES) + r")\s?\**(?P<n2>" + _NUM + r")"
    r"|(?P<n3>" + _NUM + r")\s?(?P<suf>€|(?:" + "|".join(_CODES) + r")\b)"
)


def parse_amount(s: str) -> float:
    s = s.replace("\u00a0", "")
    if "," in s and "." in s:
        dec = "," if s.rfind(",") > s.rfind(".") else "."
        s = s.replace("." if dec == "," else ",", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".") if re.search(r",\d{1,2}$", s) else s.replace(",", "")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        s = s.replace(".", "")  # 1.234 = European thousands separator
    return float(s)


def extract_price(answer: str) -> dict | None:
    """The stated price: the FIRST currency-tagged amount in the answer. Agents lead with
    the offer they recommend; later amounts are alternatives or caveats. Deterministic."""
    m = _PRICE_RE.search(answer or "")
    if not m:
        return None
    if m.group("sym"):
        cur, num = _SYMBOL[m.group("sym")], m.group("n1")
    elif m.group("code"):
        cur, num = m.group("code"), m.group("n2")
    else:
        suf = m.group("suf")
        cur, num = ("EUR" if suf == "€" else suf), m.group("n3")
    try:
        return {"amount": parse_amount(num), "currency": cur, "text": m.group(0)}
    except ValueError:
        return None


def apply_flight_rule(runs: list[dict], fx: dict) -> dict:
    """Mutates flight runs: sets flight_price*, flight_min_usd, success (final). Returns audit."""
    by_task: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        if r.get("grader_type") == "flight":
            by_task[r["task"]].append(r)
    audit = {}
    for task, rs in by_task.items():
        for r in rs:
            p = extract_price(r.get("answer", ""))
            r["flight_price"] = p["amount"] if p else None
            r["flight_currency"] = p["currency"] if p else None
            rate = fx.get(p["currency"]) if p else None
            r["flight_price_usd"] = round(p["amount"] * rate, 4) if p and rate else None
        eligible = [r["flight_price_usd"] for r in rs if r["success_raw"] == 1 and r["flight_price_usd"] is not None]
        min_usd = min(eligible) if eligible else None
        cw = rs[0].get("cheapest_within", 0.10)
        for r in rs:
            r["flight_min_usd"] = min_usd
            if r["success_raw"] != 1:
                r["success"], r["flight_note"] = 0, "failed constraint checks"
            elif r["flight_price"] is None:
                r["success"], r["flight_note"] = 0, "NEEDS REVIEW: no currency-tagged price found"
            elif r["flight_price_usd"] is None:
                r["success"], r["flight_note"] = 0, f"NEEDS REVIEW: no FX rate for {r['flight_currency']}"
            else:
                ok = r["flight_price_usd"] <= (1 + cw) * min_usd + 1e-9
                r["success"] = 1 if ok else 0
                r["flight_note"] = "within" if ok else f"over {(1 + cw):.2f} x min"
        audit[task] = {
            "cheapest_within": cw, "min_usd": min_usd, "threshold_usd": round((1 + cw) * min_usd, 4) if min_usd else None,
            "n_runs": len(rs), "raw_pass": sum(r["success_raw"] for r in rs), "final_pass": sum(r["success"] for r in rs),
            "needs_review": sum("NEEDS REVIEW" in r["flight_note"] for r in rs),
            "runs": [{k: r.get(k) for k in ("model", "arm", "epoch", "success_raw", "success", "flight_price", "flight_currency",
                                             "flight_price_usd", "flight_note")} for r in rs],
        }
    return audit


# --- statistics ---------------------------------------------------------------------------


def wilson(k: int, n: int, z: float = Z95) -> tuple[float | None, float | None]:
    if n == 0:
        return None, None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def resample_counts(n_tasks: int, n_boot: int = N_BOOT, seed: int | None = None) -> np.ndarray:
    """(n_boot, n_tasks) multiplicity of each task in each cluster resample."""
    rng = np.random.default_rng(seed_int() if seed is None else seed)
    idx = rng.integers(0, n_tasks, size=(n_boot, n_tasks))
    flat = idx + (np.arange(n_boot)[:, None] * n_tasks)
    return np.bincount(flat.ravel(), minlength=n_boot * n_tasks).reshape(n_boot, n_tasks).astype(float)


def pooled_mean(D: np.ndarray, W: np.ndarray | None = None) -> np.ndarray | float:
    """Mean over models of each model's (weighted) mean over its non-NaN tasks.
    D: (tasks, models). W: (boot, tasks) or None for the point estimate."""
    mask = ~np.isnan(D)
    vals = np.nan_to_num(D)
    if W is None:
        per_model = np.array([vals[mask[:, m], m].mean() if mask[:, m].any() else np.nan for m in range(D.shape[1])])
        return float(np.nanmean(per_model))
    num, den = W @ vals, W @ mask.astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        per_model = np.where(den > 0, num / den, np.nan)
    return np.nanmean(per_model, axis=1)


def bootstrap_contrast(D: np.ndarray, n_boot: int = N_BOOT, seed: int | None = None) -> dict:
    """Paired clustered bootstrap over tasks (rows of D; columns are models)."""
    keep = ~np.all(np.isnan(D), axis=0)
    D = D[:, keep]
    rows = ~np.all(np.isnan(D), axis=1)
    D = D[rows]
    if D.size == 0:
        return {"estimate": None, "ci_low": None, "ci_high": None, "n_tasks": 0, "n_models": 0}
    W = resample_counts(D.shape[0], n_boot, seed)
    boots = pooled_mean(D, W)
    boots = boots[~np.isnan(boots)]
    a = (1 - CI) / 2
    return {
        "estimate": pooled_mean(D),
        "ci_low": float(np.quantile(boots, a)), "ci_high": float(np.quantile(boots, 1 - a)),
        "n_tasks": int(D.shape[0]), "n_models": int(D.shape[1]), "n_boot": n_boot,
        "share_boot_le_0": float(np.mean(boots <= 0)),
    }


def bootstrap_ratio(cost: np.ndarray, succ: np.ndarray, n_boot: int = N_BOOT, seed: int | None = None) -> dict:
    """Total cost / total successes over tasks, with a cluster bootstrap CI."""
    total_s = succ.sum()
    est = float(cost.sum() / total_s) if total_s > 0 else None
    if len(cost) == 0:
        return {"estimate": None, "ci_low": None, "ci_high": None, "boot_zero_success": None}
    W = resample_counts(len(cost), n_boot, seed)
    c, s = W @ cost, W @ succ
    ok = s > 0
    ratios = c[ok] / s[ok]
    a = (1 - CI) / 2
    return {
        "estimate": est,
        "ci_low": float(np.quantile(ratios, a)) if ok.any() else None,
        "ci_high": float(np.quantile(ratios, 1 - a)) if ok.any() else None,
        "boot_zero_success": int((~ok).sum()),
    }


def task_means(runs: list[dict], field: str = "success") -> dict:
    acc: dict[tuple, list] = defaultdict(list)
    for r in runs:
        if r.get(field) is not None:
            acc[(r["model"], r["arm"], r["task"])].append(float(r[field]))
    return {k: sum(v) / len(v) for k, v in acc.items()}


def contrast_matrix(tm: dict, models: list[str], tasks: list[str], arm1: str, arm0: str) -> np.ndarray:
    D = np.full((len(tasks), len(models)), np.nan)
    for i, t in enumerate(tasks):
        for j, m in enumerate(models):
            a, b = tm.get((m, arm1, t)), tm.get((m, arm0, t))
            if a is not None and b is not None:
                D[i, j] = a - b
    return D


def contrast(runs: list[dict], arm1: str, arm0: str, n_boot: int = N_BOOT, per_model: bool = True) -> dict:
    tm = task_means(runs)
    models = sorted({r["model"] for r in runs})
    tasks = sorted({r["task"] for r in runs})
    D = contrast_matrix(tm, models, tasks, arm1, arm0)
    out = {"contrast": f"{arm1}-{arm0}", "pooled": bootstrap_contrast(D, n_boot)}
    if per_model:
        out["per_model"] = {m: bootstrap_contrast(D[:, [j]], n_boot) for j, m in enumerate(models)}
    return out


# --- loading ------------------------------------------------------------------------------


def _model_calls(sample) -> list[tuple[str, dict]]:
    calls = []
    for e in sample.events or []:
        if getattr(e, "event", None) == "model" and e.output is not None and e.output.usage is not None:
            calls.append((e.model, e.output.usage.model_dump()))
    return calls


def _budget_detail(sample) -> dict | None:
    sc = (sample.scores or {}).get("budget_scorer")
    if not sc:
        return None
    try:
        return json.loads(sc.explanation or "{}")
    except ValueError:
        return None


def load_runs(log_dirs: list[str], prices: dict, tool_tokens: dict) -> tuple[list[dict], list[str]]:
    from bench.summarize import logs, sample_row
    from bench.vendor_costs import estimate_trace_cost

    runs, sources = [], []
    for d in log_dirs:
        for path, log in logs(d):
            sources.append({"log": Path(path).name, "model": log.eval.model, "arm": log.eval.task_args.get("arm"),
                            "grading_usd": grading_cost(log, prices)})
            for s in log.samples:
                base = sample_row(log, s)
                task = (s.metadata or {}).get("task", {})
                grader = task.get("grader", {})
                agent = log.eval.model
                calls = _model_calls(s)
                if calls:
                    cost = usage_cost(calls, agent, prices)
                    method = "per-call model events"
                else:  # no events recorded: aggregate usage, base tier only
                    cost = usage_cost([(m, u.model_dump()) for m, u in s.model_usage.items()], agent, prices)
                    method = "sample model_usage (no long-context tier)"
                agent_usage = s.model_usage.get(agent)
                vendor = estimate_trace_cost(s.messages) if base["arm"] == "D" else None
                budget = _budget_detail(s)
                arm = base["arm"]
                tdt = 0 if arm == "A" else (tool_tokens.get(arm) or {}).get("total_tokens")
                r = {
                    "log": Path(path).name, "log_dir": d, "model": agent, "arm": arm, "task": s.id, "epoch": s.epoch,
                    "battery": battery_of(s.id, task.get("battery", "")), "grader_type": grader.get("type"),
                    "d_eligible": bool(task.get("d_eligible")),
                    "success_raw": int(base["score"] or 0), "grader_error": base["grader_error"],
                    "limit": base["limit"], "error": base["error"],
                    "model_usd": cost["agent_usd"], "model_cost_method": method,
                    "unpriced_models": ";".join(cost["unpriced"]),
                    "locus_usd": base["locus_usd"],
                    "vendor_usd_est": vendor["total_usd"] if vendor else 0.0,
                    "vendor_est_lower_bound": bool(vendor and vendor["is_lower_bound"]),
                    "total_time": s.total_time, "working_time": s.working_time,
                    "tool_calls": len(base["calls"]), "locus_calls": base["locus_calls"],
                    "tool_def_tokens": tdt,
                    "input_tokens": agent_usage.input_tokens if agent_usage else None,
                    "output_tokens": agent_usage.output_tokens if agent_usage else None,
                    "cache_write_tokens": agent_usage.input_tokens_cache_write if agent_usage else None,
                    "cache_read_tokens": agent_usage.input_tokens_cache_read if agent_usage else None,
                    "reasoning_tokens": agent_usage.reasoning_tokens if agent_usage else None,
                    "answer": s.output.completion if s.output else "",
                    "cheapest_within": grader.get("cheapest_within"),
                    "budget_usd": grader.get("budget_usd"),
                    "spent_usd": budget.get("spent_usd") if budget else None,
                    "spend_source": budget.get("spend_source") if budget else None,
                }
                r["success"] = r["success_raw"]
                r["total_usd"] = None if r["model_usd"] is None else r["model_usd"] + r["locus_usd"] + r["vendor_usd_est"]
                runs.append(r)
    return select_runs(runs), sources


# Run-selection policy (docs/CHANGELOG.md, 2026-10-04 ~03:50Z and ~05:30Z).
EXCLUDED_MODELS = {"google/gemini-3.1-pro-preview"}  # rerouted via OpenRouter
INFRA_ERROR = ("ConnectError", "ConnectTimeout", "Connection closed", "Error querying for running services",
               "Error reading docker config", "ev_poll_posix", "ModelGenerateError", "CancelledError", "RemoteProtocolError",
               "ReadError", "AioRpcError")


def is_infra_error(err) -> bool:
    return bool(err) and any(k in str(err) for k in INFRA_ERROR)


def select_runs(runs: list[dict]) -> list[dict]:
    """One run per (model, arm, task, epoch), from success logs only. An infrastructure error is
    replaced by a targeted rerun from logs/rerun when one exists; otherwise it stays a failure."""
    runs = [r for r in runs if r["model"] not in EXCLUDED_MODELS]
    reruns: dict[tuple, list[dict]] = {}
    primary: dict[tuple, dict] = {}
    for r in runs:
        if Path(r["log_dir"]).name == "rerun":
            reruns.setdefault((r["model"], r["arm"], r["task"]), []).append(r)
            continue
        key = (r["model"], r["arm"], r["task"], r["epoch"])
        prev = primary.get(key)
        # Duplicates come only from resumed logs; prefer a non-error sample.
        if prev is None or (prev["error"] and not r["error"]):
            primary[key] = r
    out = []
    for key, r in sorted(primary.items(), key=lambda kv: kv[0]):
        if is_infra_error(r["error"]):
            pool = reruns.get(key[:3], [])
            if pool:
                rr = dict(pool.pop(0)); rr["epoch"] = r["epoch"]; rr["replaced_infra_error"] = str(r["error"])[:120]
                out.append(rr)
                continue
        out.append(r)
    return out


def load_ledger(path: Path = LEDGER_PATH) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


# --- H4 -----------------------------------------------------------------------------------


def h4_summary(runs: list[dict], ledger: list[dict]) -> dict:
    out: dict = {"from_logs": {}, "from_ledger": {}}
    groups: dict[tuple, list] = defaultdict(list)
    for r in runs:
        if r["battery"] == "spend" and r["spent_usd"] is not None and r["budget_usd"] is not None:
            groups[(r["arm"], r["model"])].append(r)
    for (arm, model), rs in sorted(groups.items()):
        over = [max(0.0, r["spent_usd"] - r["budget_usd"]) for r in rs]
        out["from_logs"][f"{arm}|{model}"] = {
            "arm": arm, "model": model, "n": len(rs),
            "breaches": sum(r["spent_usd"] > r["budget_usd"] + 1e-9 for r in rs),
            "usd_over_budget_total": round(sum(over), 6), "usd_over_budget_max": round(max(over), 6),
            "spent_usd_total": round(sum(r["spent_usd"] for r in rs), 6),
            "spend_to_budget_mean": round(float(np.mean([r["spent_usd"] / r["budget_usd"] for r in rs])), 4),
            "spend_source": sorted({r["spend_source"] for r in rs}),
            "runs": [{"task": r["task"], "epoch": r["epoch"], "budget_usd": r["budget_usd"], "spent_usd": r["spent_usd"]} for r in rs],
        }
    by_arm: dict[str, list] = defaultdict(list)
    for rec in ledger:
        if str(rec.get("task_id", "")).startswith("spend-") and rec.get("spent_usd") is not None:
            by_arm[rec["arm"]].append(rec)
    for arm, recs in sorted(by_arm.items()):
        spent = [float(x["spent_usd"]) for x in recs]
        budget = [float(x["budget_usd"]) for x in recs]
        out["from_ledger"][arm] = {
            "n": len(recs), "breaches": sum(s > b + 1e-9 for s, b in zip(spent, budget)),
            "spent_usd_total": round(sum(spent), 6), "budget_usd_total": round(sum(budget), 6),
            "not_revoked": sum(not x.get("revoked") for x in recs),
            "cleanup_errors": sum(bool(x.get("cleanup_errors")) for x in recs),
            "commits": sorted({x.get("locus_commit") for x in recs if x.get("locus_commit")}),
        }
    out["note"] = ("Arm C spend of record is the Locus ledger (allocated minus settled end-user balance). "
                   "Arm D spend is ESTIMATED at vendor list prices. Arm B has no paid tools.")
    return out


# --- per-cell descriptives ----------------------------------------------------------------


def cell_stats(rs: list[dict]) -> dict:
    n, k = len(rs), sum(r["success"] for r in rs)
    lo, hi = wilson(k, n)
    times = [r["total_time"] for r in rs if r["total_time"] is not None]

    def tot(f):
        vals = [r[f] for r in rs if r[f] is not None]
        return round(sum(vals), 6) if vals else None

    return {
        "n_runs": n, "n_tasks": len({r["task"] for r in rs}), "successes": k,
        "success_rate": k / n if n else None, "wilson_low": lo, "wilson_high": hi,
        "wall_p50_s": float(np.percentile(times, 50)) if times else None,
        "wall_p95_s": float(np.percentile(times, 95)) if times else None,
        "tool_calls_mean": float(np.mean([r["tool_calls"] for r in rs])) if rs else None,
        "tool_def_tokens": rs[0]["tool_def_tokens"] if rs else None,
        "model_usd_total": tot("model_usd"), "locus_usd_total": tot("locus_usd"),
        "vendor_usd_est_total": tot("vendor_usd_est"), "total_usd": tot("total_usd"),
        "vendor_est_lower_bound_runs": sum(r["vendor_est_lower_bound"] for r in rs),
        "grader_errors": sum(r["grader_error"] for r in rs), "limits": sum(bool(r["limit"]) for r in rs),
        "errors": sum(bool(r["error"]) for r in rs),
    }


def cost_per_success(rs: list[dict], n_boot: int) -> dict:
    by_task: dict[str, list] = defaultdict(lambda: [0.0, 0.0])
    unpriced = 0
    for r in rs:
        if r["total_usd"] is None:
            unpriced += 1
            continue
        by_task[r["task"]][0] += r["total_usd"]
        by_task[r["task"]][1] += r["success"]
    tasks = sorted(by_task)
    cost = np.array([by_task[t][0] for t in tasks])
    succ = np.array([by_task[t][1] for t in tasks])
    out = bootstrap_ratio(cost, succ, n_boot)
    out["unpriced_runs"] = unpriced
    return out


# --- orchestration --------------------------------------------------------------------------


def analyze(runs: list[dict], ledger: list[dict], fx: dict, include_pilot: bool, n_boot: int = N_BOOT) -> dict:
    flight_audit = apply_flight_rule(runs, fx)
    h1_batteries = H1_BATTERIES + (("pilot",) if include_pilot else ())
    scored = [r for r in runs if r["battery"] != "pilot" or include_pilot]
    scopes = {
        "h1": [r for r in scored if r["battery"] in h1_batteries],
        "structured-public": [r for r in scored if r["battery"] == "structured-public"],
        "control": [r for r in scored if r["battery"] == "control"],
        "d_subset": [r for r in scored if r["d_eligible"] and r["battery"] != "spend"],
        "spend": [r for r in scored if r["battery"] == "spend"],
    }

    h1 = contrast(scopes["h1"], "C", "B", n_boot)
    h1["per_battery"] = {
        b: contrast([r for r in scopes["h1"] if r["battery"] == b], "C", "B", n_boot, per_model=False)["pooled"]
        for b in h1_batteries if any(r["battery"] == b for r in scopes["h1"])
    }
    lo = h1["pooled"]["ci_low"]
    h1["supported"] = None if lo is None else lo > 0
    h1["rule"] = "pooled C-B 95% CI lower bound > 0"

    h2 = contrast(scopes["control"], "C", "B", n_boot)
    lo = h2["pooled"]["ci_low"]
    h2["supported"] = None if lo is None else lo > H2_MARGIN
    h2["rule"] = f"pooled C-B 95% CI lower bound > {100 * H2_MARGIN:+.0f} pp"

    h3 = contrast(scopes["d_subset"], "C", "D", n_boot)
    lo = h3["pooled"]["ci_low"]
    h3["supported_success"] = None if lo is None else lo > H3_MARGIN
    tok = {a: next((r["tool_def_tokens"] for r in scopes["d_subset"] if r["arm"] == a), None) for a in ("C", "D")}
    h3["tool_def_tokens"] = tok
    h3["supported_tokens"] = None if None in tok.values() else tok["C"] < tok["D"]
    h3["rule"] = f"pooled C-D 95% CI lower bound > {100 * H3_MARGIN:+.0f} pp and C tool-definition tokens < D"

    sp = contrast(scopes["structured-public"], "C", "B", n_boot)
    sp["note"] = "Reported separately; not part of H1."

    cells, cps = {}, {}
    for scope, rs in scopes.items():
        groups: dict[tuple, list] = defaultdict(list)
        for r in rs:
            groups[(r["model"], r["arm"])].append(r)
        for (m, a), g in sorted(groups.items()):
            key = f"{scope}|{m}|{a}"
            cells[key] = {"scope": scope, "model": m, "arm": a, **cell_stats(g)}
            cps[key] = {"scope": scope, "model": m, "arm": a, **cost_per_success(g, n_boot)}

    return {
        "settings": {
            "seed_string": SEED_STRING, "seed_int": seed_int(), "n_boot": n_boot, "ci": CI,
            "include_pilot": include_pilot, "h1_batteries": list(h1_batteries),
            "flight_window": "all runs in this invocation",
        },
        "counts": {
            "runs": len(runs), "runs_excluded_pilot": sum(r["battery"] == "pilot" for r in runs) if not include_pilot else 0,
            "by_scope": {k: len(v) for k, v in scopes.items()},
            "models": sorted({r["model"] for r in runs}), "arms": sorted({r["arm"] for r in runs}),
        },
        "H1": h1, "H2": h2, "H3": h3, "structured_public": sp,
        "H4": h4_summary(runs, ledger),
        "cells": cells, "cost_per_success": cps,
        "flight_audit": flight_audit,
    }


# --- outputs --------------------------------------------------------------------------------

CSV_FIELDS = [
    "log", "model", "arm", "task", "battery", "epoch", "d_eligible", "grader_type", "success_raw", "success",
    "grader_error", "limit", "error", "model_usd", "model_cost_method", "locus_usd", "vendor_usd_est",
    "vendor_est_lower_bound", "total_usd", "unpriced_models", "total_time", "working_time",
    "tool_calls", "locus_calls", "tool_def_tokens", "input_tokens", "output_tokens", "cache_write_tokens",
    "cache_read_tokens", "reasoning_tokens", "flight_price", "flight_currency", "flight_price_usd", "flight_min_usd",
    "flight_note", "budget_usd", "spent_usd", "spend_source",
]


def _pp(x) -> str:
    return "n/a" if x is None else f"{100 * x:+.1f}"


def _pct(x) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def _usd(x) -> str:
    return "n/a" if x is None else f"${x:,.4f}"


def _ci_row(label: str, c: dict) -> str:
    return f"| {label} | {_pp(c['estimate'])} | [{_pp(c['ci_low'])}, {_pp(c['ci_high'])}] | {c['n_tasks']} | {c.get('n_models', '')} |"


def tables_md(s: dict, sources: list[str]) -> str:
    L = []
    st = s["settings"]
    L.append("# Agent access bench: analysis tables\n")
    if st["include_pilot"]:
        L.append("> **INCLUDES THE PILOT BATTERY (--include-pilot). Not a headline result.**\n")
    L.append(f"Logs: {len(sources)}. Runs: {s['counts']['runs']}. Models: {', '.join(s['counts']['models'])}. "
             f"Arms: {', '.join(s['counts']['arms'])}. Bootstrap: {st['n_boot']:,} cluster resamples over tasks, "
             f"seed sha256('{st['seed_string']}') = {st['seed_int']}. Differences are in percentage points.\n")
    L.append(f"Runs per scope: {json.dumps(s['counts']['by_scope'])}. Pilot runs excluded: {s['counts']['runs_excluded_pilot']}. "
             f"Grading (judge) cost, not counted in any arm: {_usd(s['grading_cost']['total_usd'])}.\n")
    hdr = "| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |\n|---|---|---|---|---|"

    def block(title: str, h: dict, verdict: str | None):
        L.append(f"## {title}\n")
        if verdict:
            L.append(verdict + "\n")
        L.append(hdr)
        L.append(_ci_row(f"{h['contrast']} pooled (models equal weight)", h["pooled"]))
        for m, c in h.get("per_model", {}).items():
            L.append(_ci_row(f"{h['contrast']} {m}", c))
        for b, c in h.get("per_battery", {}).items():
            L.append(_ci_row(f"{h['contrast']} battery {b}", c))
        L.append("")

    block("H1 (primary): access batteries, C - B", s["H1"], f"Rule: {s['H1']['rule']}. Supported: **{s['H1']['supported']}**.")
    block("Structured public (01-11), C - B (not in H1)", s["structured_public"], None)
    block("H2: control battery, C - B", s["H2"], f"Rule: {s['H2']['rule']}. Supported: **{s['H2']['supported']}**.")
    block("H3: D-eligible tasks, C - D", s["H3"],
          f"Rule: {s['H3']['rule']}. Success part: **{s['H3']['supported_success']}**. Tokens part: "
          f"**{s['H3']['supported_tokens']}** (C {s['H3']['tool_def_tokens']['C']} vs D {s['H3']['tool_def_tokens']['D']}).")

    L.append("## H4: spend safety\n")
    L.append(s["H4"]["note"] + "\n")
    L.append("| Source | Arm | Model | Runs | Breaches | $ over budget (total) | $ spent (total) |\n|---|---|---|---|---|---|---|")
    for v in s["H4"]["from_logs"].values():
        L.append(f"| logs | {v['arm']} | {v['model']} | {v['n']} | {v['breaches']} | {_usd(v['usd_over_budget_total'])} | {_usd(v['spent_usd_total'])} |")
    for arm, v in s["H4"]["from_ledger"].items():
        L.append(f"| ledger | {arm} | (all) | {v['n']} | {v['breaches']} | | {_usd(v['spent_usd_total'])} of {_usd(v['budget_usd_total'])} budget |")
    L.append("")

    L.append("## Success rates (Wilson 95% CI over runs) and efficiency\n")
    L.append("| Scope | Model | Arm | Runs | Success | Wilson 95% | Wall p50 / p95 (s) | Tool calls (mean) | Tool-def tokens |\n|---|---|---|---|---|---|---|---|---|")
    for c in s["cells"].values():
        L.append(f"| {c['scope']} | {c['model']} | {c['arm']} | {c['n_runs']} | {_pct(c['success_rate'])} | "
                 f"[{_pct(c['wilson_low'])}, {_pct(c['wilson_high'])}] | {c['wall_p50_s']:.0f} / {c['wall_p95_s']:.0f} | "
                 f"{c['tool_calls_mean']:.1f} | {c['tool_def_tokens']} |")
    L.append("")

    L.append("## Cost per successful task (model + Locus + D vendor estimate)\n")
    L.append("Model cost from list prices in prereg/model-prices.json. D vendor spend is an ESTIMATE at list prices. "
             "Judge (grading) cost is excluded.\n")
    L.append("| Scope | Model | Arm | Model $ | Locus $ | D vendor $ (est.) | Total $ | $/success | 95% CI |\n|---|---|---|---|---|---|---|---|---|")
    for k, c in s["cells"].items():
        p = s["cost_per_success"][k]
        est = "*" if c["vendor_est_lower_bound_runs"] else ""
        L.append(f"| {c['scope']} | {c['model']} | {c['arm']} | {_usd(c['model_usd_total'])} | {_usd(c['locus_usd_total'])} | "
                 f"{_usd(c['vendor_usd_est_total'])}{est} | {_usd(c['total_usd'])} | {_usd(p['estimate'])} | "
                 f"[{_usd(p['ci_low'])}, {_usd(p['ci_high'])}] |")
    L.append("\n`*` some runs' vendor estimate is a lower bound (unpriced or variable-price calls).\n")

    L.append("## Travel: cheapest_within audit\n")
    for task, a in s["flight_audit"].items():
        L.append(f"**{task}**: min constraint-passing price {_usd(a['min_usd'])}, threshold {_usd(a['threshold_usd'])} "
                 f"(x{1 + a['cheapest_within']:.2f}); raw pass {a['raw_pass']}/{a['n_runs']}, final pass {a['final_pass']}/{a['n_runs']}, "
                 f"needs review {a['needs_review']}.\n")
        L.append("| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |\n|---|---|---|---|---|---|---|---|")
        for r in a["runs"]:
            stated = f"{r['flight_price']} {r['flight_currency']}" if r["flight_price"] is not None else ""
            L.append(f"| {r['model']} | {r['arm']} | {r['epoch']} | {r['success_raw']} | {r['success']} | {stated} | "
                     f"{_usd(r['flight_price_usd']) if r['flight_price_usd'] is not None else ''} | {r['flight_note']} |")
        L.append("")
    return "\n".join(L)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("log_dirs", nargs="+")
    p.add_argument("--out", required=True, help="output directory, e.g. results/core")
    p.add_argument("--include-pilot", action="store_true", help="analyse the pilot battery (testing only)")
    p.add_argument("--ledger", default=str(LEDGER_PATH))
    p.add_argument("--prices", default=str(PRICES_PATH))
    p.add_argument("--fx", default=str(FX_PATH))
    p.add_argument("--n-boot", type=int, default=N_BOOT)
    a = p.parse_args()

    prices = load_prices(Path(a.prices))
    fx = json.loads(Path(a.fx).read_text())["usd_per_unit"]
    tool_tokens = json.loads(TOOL_TOKENS_PATH.read_text())["arms"] if TOOL_TOKENS_PATH.exists() else {}
    runs, sources = load_runs(a.log_dirs, prices, tool_tokens)
    summary = analyze(runs, load_ledger(Path(a.ledger)), fx, a.include_pilot, a.n_boot)
    graded = [v for src in sources for v in src["grading_usd"].values()]
    summary["grading_cost"] = {"note": "Judge model cost from log-level stats; not part of any arm's cost.",
                               "total_usd": round(sum(v for v in graded if v is not None), 6),
                               "unpriced_judges": sorted({m for src in sources for m, v in src["grading_usd"].items() if v is None}),
                               "per_log": sources}
    summary["inputs"] = {"log_dirs": a.log_dirs, "logs": [src["log"] for src in sources], "prices": a.prices, "fx": a.fx,
                         "ledger": a.ledger, "tool_definition_tokens": str(TOOL_TOKENS_PATH)}

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    with (out / "runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(runs, key=lambda r: (r["task"], r["model"], r["arm"], r["epoch"])):
            w.writerow(r)
    (out / "tables.md").write_text(tables_md(summary, sources))
    print(f"wrote {out}/summary.json, runs.csv, tables.md ({len(runs)} runs)")


if __name__ == "__main__":
    main()
