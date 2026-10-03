"""Per-run summary from Inspect logs: score, tool usage, Locus spend, grader errors."""

import glob
import json
import sys
from collections import defaultdict

from inspect_ai.log import read_eval_log

LOCUS_TOOLS = {"search_apis", "describe_api", "execute", "estimate_cost", "get_balance", "get_call_result",
               "list_tool_groups", "get_locus_guide", "pin_endpoint", "request_tool_access",
               "web_research", "web_extract", "router_web_search", "gtm_enrich", "travel_flights", "commerce_search"}


def usd_charged(msg) -> float:
    text = msg.content[0].text if isinstance(msg.content, list) and msg.content else str(msg.content)
    try:
        return float(json.loads(text).get("usd_charged") or 0)
    except Exception:
        return 0.0


def rows(log_dir: str):
    for path in sorted(glob.glob(f"{log_dir}/*.eval")):
        log = read_eval_log(path)
        if log.status != "success" or not log.samples:
            print("SKIP", path, log.status, (log.error.message[:200] if log.error else ""))
            continue
        arm = log.eval.task_args.get("arm")
        for s in log.samples:
            score = next(iter(s.scores.values()))
            calls = [tc.function for m in s.messages if m.role == "assistant" for tc in (m.tool_calls or [])]
            spend = sum(usd_charged(m) for m in s.messages if m.role == "tool" and m.function in LOCUS_TOOLS)
            yield {
                "model": log.eval.model, "arm": arm, "task": s.id, "epoch": s.epoch, "score": score.value,
                "grader_error": "grader_error" in (score.explanation or ""),
                "explanation": (score.explanation or "")[:160],
                "calls": calls, "locus_calls": sum(c in LOCUS_TOOLS for c in calls), "locus_usd": spend,
                "limit": s.limit.type if s.limit else None, "error": (s.error.message[:120] if s.error else None),
                "tokens": sum(u.total_tokens for u in s.model_usage.values()),
            }


if __name__ == "__main__":
    data = list(rows(sys.argv[1]))
    agg = defaultdict(list)
    for r in data:
        agg[(r["model"], r["arm"])].append(r)
    print(f"{'model':30s} arm  n  pass  locus_calls  locus_$  grader_err  limits  errors")
    for (m, a), rs in sorted(agg.items()):
        print(f"{m:30s} {a:3s} {len(rs):2d}  {sum(r['score'] for r in rs):4.0f}  {sum(r['locus_calls'] for r in rs):11d}  {sum(r['locus_usd'] for r in rs):7.3f}  {sum(r['grader_error'] for r in rs):10d}  {sum(bool(r['limit']) for r in rs):6d}  {sum(bool(r['error']) for r in rs):6d}")
    if "-v" in sys.argv:
        for r in sorted(data, key=lambda r: (r["task"], r["model"], r["arm"])):
            print(f"{r['task']:10s} {r['model'][-18:]:18s} {r['arm']} {r['score']:.0f} lc={r['locus_calls']:2d} ${r['locus_usd']:.3f} {r['limit'] or ''} {r['error'] or ''} | {r['explanation'][:110]}")
    json.dump(data, open(sys.argv[1].rstrip('/') + "-summary.json", "w"), default=str, indent=1)
