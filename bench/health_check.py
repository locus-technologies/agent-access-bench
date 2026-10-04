"""Mid-run health check on whatever has finished so far. Read-only."""

import glob
import json
from collections import Counter, defaultdict

from inspect_ai.log import list_eval_logs, read_eval_log_samples

from bench.summarize import LOCUS_TOOLS


def core(log_dir: str) -> None:
    stats = defaultdict(Counter)
    for info in list_eval_logs(log_dir):
        try:
            for s in read_eval_log_samples(info.name, all_samples_required=False):
                hdr = s.metadata.get("arm", "?")
                key = (hdr,)
                score = next(iter(s.scores.values())) if s.scores else None
                calls = [tc.function for m in s.messages if m.role == "assistant" for tc in (m.tool_calls or [])]
                st = stats[key]
                st["n"] += 1
                st["pass"] += int(bool(score and score.value == 1))
                st["grader_error"] += int(bool(score and "grader_error" in (score.explanation or "")))
                st["limit"] += int(bool(s.limit))
                st["error"] += int(bool(s.error))
                st["locus_used"] += int(any(c in LOCUS_TOOLS for c in calls))
        except Exception as e:
            print("unreadable", info.name[-60:], repr(e)[:100])
    for (arm,), st in sorted(stats.items()):
        n = st["n"] or 1
        print(f"{log_dir:10s} arm {arm}: n={st['n']:4d} pass={st['pass']/n:5.0%} grader_err={st['grader_error']} "
              f"limit_hits={st['limit']} errors={st['error']} runs_using_locus={st['locus_used']}")


def harness() -> None:
    stats = defaultdict(Counter)
    for f in glob.glob("results/raw/harness/full-*.jsonl"):
        for line in open(f):
            r = json.loads(line)
            st = stats[(r["harness"], r["arm"])]
            st["n"] += 1
            st["pass"] += int(r.get("score") == 1)
            st["exit_nonzero"] += int(r.get("exit_code") not in (0, None))
            st["locus_used"] += int((r.get("locus_calls") or 0) > 0)
            st["usd"] += float(r.get("locus_usd") or 0)
    for (h, a), st in sorted(stats.items()):
        n = st["n"] or 1
        print(f"harness {h:14s} {a:11s} n={st['n']:3d} pass={st['pass']/n:5.0%} exit_nonzero={st['exit_nonzero']} "
              f"runs_using_locus={st['locus_used']} locus_usd={st['usd']:.2f}")


if __name__ == "__main__":
    for d in ("logs/main", "logs/main-d", "logs/spend"):
        core(d)
    harness()
