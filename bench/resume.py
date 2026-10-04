"""Resume interrupted runs: completed samples are kept, the rest (including errored) rerun.

    uv run python -m bench.resume logs/main --max-tasks 9 --max-samples 4
"""

import argparse

from bench.secrets import load_secrets

load_secrets()

from inspect_ai import eval_retry  # noqa: E402
from inspect_ai.log import list_eval_logs, read_eval_log  # noqa: E402

import bench.eval  # noqa: E402,F401  (registers the task)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("log_dir")
    p.add_argument("--max-tasks", type=int, default=9)
    p.add_argument("--max-samples", type=int, default=4)
    a = p.parse_args()
    logs = [i for i in list_eval_logs(a.log_dir) if read_eval_log(i.name, header_only=True).status != "success"]
    print(f"resuming {len(logs)} logs from {a.log_dir}")
    eval_retry(logs, log_dir=a.log_dir, max_tasks=a.max_tasks, max_samples=a.max_samples,
               fail_on_error=False, display="plain")


if __name__ == "__main__":
    main()
