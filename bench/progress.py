"""Completed (non-error) samples per (model, arm) across core logs, deduped by (task, epoch)."""

from collections import defaultdict

from inspect_ai.log import list_eval_logs, read_eval_log, read_eval_log_samples

EXPECTED = {"A": 231, "B": 231, "C": 231, "D": 135}
EXCLUDE = {"google/gemini-3.1-pro-preview"}  # rerouted via OpenRouter (CHANGELOG)

done = defaultdict(set)
for d in ("logs/main", "logs/main-d", "logs/main-gpro", "logs/main-d-gpro", "logs/main-bc", "logs/main-d2"):
    for info in list_eval_logs(d):
        h = read_eval_log(info.name, header_only=True)
        if h.eval.model in EXCLUDE:
            continue
        for s in read_eval_log_samples(info.name, all_samples_required=False):
            if not s.error:
                done[(h.eval.model, h.eval.task_args.get("arm"))].add((s.id, s.epoch))
tot = exp = 0
for (m, a), v in sorted(done.items()):
    print(f"{m.split('/')[-1]:28s} {a}  {len(v):4d}/{EXPECTED[a]}")
    tot += len(v); exp += EXPECTED[a]
print(f"TOTAL {tot}/{9 * (231 * 3 + 135)}")
