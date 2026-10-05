"""Post-hoc regrade of specific tasks whose rubric was found faulty after the run.

    uv run python -m bench.regrade --runs results/full/runs.csv --out results/regrade/overrides.jsonl
    GRADE_OVERRIDES=results/regrade/overrides.jsonl uv run python -m bench.analyze <log dirs> --out results/full-corrected

Every correction is applied identically to every arm and model, and is logged in docs/CHANGELOG.md.
The pre-registered results (results/full) stay the headline. Output rows carry no answers or
email addresses: only the new verdict and the email domain/status.
"""

import argparse
import asyncio
import csv
import glob
import json
from pathlib import Path

from bench.secrets import load_secrets

load_secrets()

from inspect_ai.log import read_eval_log_samples  # noqa: E402

from bench import graders  # noqa: E402
from bench.audit_sample import load_tasks  # noqa: E402

# task id -> what changes. Keep each entry tied to a CHANGELOG entry.
CORRECTIONS = {
    # Mews moved from mewssystems.com to mews.com; the old domain still receives mail. Same
    # deliverability rule (ZeroBounce "valid") applies, checked at regrade time.
    "gtm-05": {"extra_email_domains": ["mewssystems.com"]},
    # Claim 2 cites "the 2026-10-03 snapshot in notes", but the judge was never shown the notes,
    # so claims 2-3 could not be checked. The judge now sees the task notes.
    "multistep-06": {"judge_sees_notes": True},
}


async def regrade_one(task, fix: dict, answer: str, model: str, sem: asyncio.Semaphore) -> tuple[bool, dict]:
    async with sem:
        g = task.grader
        if "extra_email_domains" in fix:
            g = g.model_copy(update={"email_domains": [*g.email_domains, *fix["extra_email_domains"]]})
            return await graders.grade(task.model_copy(update={"grader": g}), answer, model)
        if fix.get("judge_sees_notes"):
            verdicts = await graders.judge_claims(answer, g.claims, model, reference=task.notes)
            share = sum(verdicts) / len(verdicts)
            return share >= g.pass_share, {"verdicts": verdicts, "share": share}
        raise ValueError(f"unknown correction {fix}")


async def main_async(runs_csv: str, out: str, concurrency: int) -> None:
    tasks = load_tasks()
    rows = [r for r in csv.DictReader(open(runs_csv)) if r["task"] in CORRECTIONS]
    paths = {Path(p).name: p for p in glob.glob("logs/**/*.eval", recursive=True)}
    wanted: dict[str, set] = {}
    for r in rows:
        wanted.setdefault(r["log"], set()).add((r["task"], int(r["epoch"])))
    by_key = {(r["log"], r["task"], int(r["epoch"])): r for r in rows}

    sem = asyncio.Semaphore(concurrency)
    jobs = []
    for log, keys in wanted.items():
        for s in read_eval_log_samples(paths[log], all_samples_required=False):
            if (s.id, s.epoch) in keys:
                r = by_key[(log, s.id, s.epoch)]
                answer = s.output.completion if s.output else ""
                jobs.append((r, regrade_one(tasks[s.id], CORRECTIONS[s.id], answer, r["model"], sem)))
    results = await asyncio.gather(*(j for _, j in jobs))

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        for (r, _), (ok, detail) in zip(jobs, results):
            f.write(json.dumps({"log": r["log"], "task": r["task"], "epoch": int(r["epoch"]), "model": r["model"],
                                "arm": r["arm"], "success_before": int(r["success_raw"]), "success": int(ok),
                                "detail": detail}) + "\n")
    print(f"wrote {out} ({len(jobs)} runs; {len(rows)} expected)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--runs", default="results/full/runs.csv")
    p.add_argument("--out", default="results/regrade/overrides.jsonl")
    p.add_argument("--concurrency", type=int, default=8)
    a = p.parse_args()
    asyncio.run(main_async(a.runs, a.out, a.concurrency))


if __name__ == "__main__":
    main()
