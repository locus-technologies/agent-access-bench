"""Entry point: load keys first, then run Inspect.

    uv run python -m bench.run --arm C --batteries pilot --model anthropic/claude-sonnet-5-5 --epochs 1
"""

import argparse

from bench.secrets import load_secrets

load_secrets()

from inspect_ai import eval as inspect_eval  # noqa: E402

from bench.eval import access_bench  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--arm", required=True)
    p.add_argument("--batteries", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--d-only", action="store_true")
    p.add_argument("--log-dir", default="logs/main")
    p.add_argument("--max-samples", type=int, default=6)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--max-tasks", type=int, default=8)
    a = p.parse_args()
    # One process for every arm and model, so the shared search gate really is global.
    tasks = [access_bench(arm=arm, batteries=a.batteries, d_only=a.d_only, epochs=a.epochs) for arm in a.arm.split(",")]
    inspect_eval(
        tasks,
        model=a.model.split(","),
        log_dir=a.log_dir,
        max_samples=a.max_samples,
        max_tasks=a.max_tasks,
        limit=a.limit,
        fail_on_error=False,
        display="plain",
    )


if __name__ == "__main__":
    main()
