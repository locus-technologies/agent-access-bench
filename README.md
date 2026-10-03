# agent-access-bench

Does the same agent get more done with one Locus Pro key? This is a pre-registered,
multi-model, multi-harness benchmark. Locus runs it, and everything needed to rerun it is
in this repo.

Status: in development. See `prereg/PREREGISTRATION.md`.

## Layout

- `prereg/`: the pre-registration, the discovery eval set, and the enablement snapshot
- `bench/`: arms, tasks, graders, harness adapters, analysis
- `tasks/`: task definitions (JSONL)
- `docs/`: spike notes, the changelog, the audit protocol
- `results/`: summarized results (raw logs are published separately)
