# agent-access-bench

Do AI agents finish more real work when they can reach paid data? Nine models from five labs ran
82 tasks, three times each, in four setups:

| Arm | Tools |
|---|---|
| A | none (what the model already knows) |
| B | web search (Tavily), page fetch, Python |
| C | B + one Locus Pro key over MCP (paid APIs through one balance) |
| D | B + seven vendors wired directly (Apollo, Hunter, Prospeo, Firecrawl, Exa, Tavily, E2B) |

The method was frozen before the main run (`prereg/PREREGISTRATION.md`, tag `prereg-v1`). Every
change after the freeze is in `docs/CHANGELOG.md`, and both the pre-registered and corrected
results are kept.

**Conflict of interest:** Locus makes Locus Pro (arm C) and ran this benchmark.

## Results

- `results/full/`: pre-registered analysis (`tables.md` to read, `summary.json`, `runs.csv`)
- `results/full-corrected/`: the same runs with the post-hoc grading corrections in the changelog

Headline (H1, data tasks, arm C minus arm B): +25.0 points [+16.1, +33.8], 95% clustered
bootstrap, 10,000 resamples.

## Layout

- `prereg/`: pre-registration, model list, prices, FX, the catalog snapshot at freeze
- `tasks/`: task definitions (JSONL), with the truth source and date for each answer
- `bench/`: arms, eval, graders, harness adapters, analysis, charts
- `harnesses/`: harness-track adapters (Claude Code, Codex, Hermes, OpenClaw, OpenAI Agents SDK)
- `scripts/`: the shell scripts that launched the full run
- `docs/`: changelog, task notes, spend protocol, harness notes

## Reproduce the analysis without any keys

```bash
uv sync
gh release download traces-v1 -p 'traces-v1.tar.gz' && tar xzf traces-v1.tar.gz   # creates logs/ and results/raw/
uv run python -m bench.analyze logs/main logs/main-a2 logs/main-bc logs/main-gpro logs/main-d logs/main-d2 logs/main-d-gpro logs/rerun logs/spend --out results/check
```

## Run it

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and Docker (the Python tool runs in a sandbox).

```bash
uv sync
cp .env.example .env    # fill in the keys for the arms and models you want
```

One task, one model, one arm:

```bash
uv run python -m bench.run --arm B --batteries gtm --model anthropic/claude-haiku-4-5 --epochs 1 --task-ids gtm-05 --log-dir logs/try
```

The full run is `scripts/full_run.sh` (about 7,700 graded runs; budget model and data spend
accordingly). Analysis and charts:

```bash
uv run python -m bench.analyze logs/main logs/main-a2 logs/main-bc logs/main-gpro logs/main-d logs/main-d2 logs/main-d-gpro logs/rerun logs/spend --out results/full
uv run python -m bench.charts results/full --out charts
```

Corrected results (post-hoc, see the changelog):

```bash
uv run python -m bench.regrade --runs results/full/runs.csv --out results/regrade/overrides.jsonl
FLIGHT_MIN_RULE=specific GRADE_OVERRIDES=results/regrade/overrides.jsonl uv run python -m bench.analyze <same log dirs> --out results/full-corrected
```

Tests (`BENCH_OFFLINE=1` skips the ones that call live truth sources):

```bash
BENCH_OFFLINE=1 uv run pytest bench
```

## Notes

- Live answers change. Each answer is graded against truth captured within ten minutes of the
  run that used it, so a rerun weeks later will not reproduce our exact numbers.
- Claims-rubric tasks are judged by a model from a different family than the agent
  (`bench/graders.py`).
- Raw traces (every eval log, the harness-track traces and the spend ledger) are attached to the
  `traces-v1` GitHub release as one archive. They were produced by `scripts/scrub_traces.py`,
  which removes credentials and replaces the local part of every email address with a salted hash. `bench.analyze` on the bundle reproduces `results/full` exactly. Unpack it in the
  repo root, and the analysis commands above run on it unchanged.
