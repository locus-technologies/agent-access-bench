# Pre-registration: Does the same agent get more done with Locus Pro?

Status: **DRAFT v0.2 (2026-10-03)**. This file is frozen by a tagged commit (`prereg-v1`)
before the first arm-C run of the full benchmark. Every change after the freeze is logged in
`CHANGELOG.md` with its reason.

Run by Locus (the company that makes Locus Pro). The harness, tasks, graders, raw logs and
analysis code are all published, so anyone can rerun this with their own keys.

## 1. Question

Does giving an agent one Locus Pro key raise the share of real-world tasks it completes, at
a known cost? Does the answer hold across models and agent harnesses?

## 2. Hypotheses

| ID | Statement | Test |
|---|---|---|
| H1 (primary) | On the access batteries (GTM, paid data, multi-step, travel, structured-hostile), success(C) − success(B) > 0 | pooled over core models; paired clustered bootstrap, 95% CI lower bound > 0 |
| H2 | On the control battery, success(C) − success(B) > −5 points | 95% CI lower bound > −5 |
| H3 | On the D subset, success(C) ≥ success(D) − 5 points; C uses fewer tool-definition tokens | CI on the difference; token count measured from the tool list sent to the model |
| H4 | On the spend-safety battery, C never exceeds its budget (each C run gets its own Locus sub-account funded with exactly the stated budget); D's spend is measured from vendor usage and list prices | count of budget breaches; dollars over budget |
| H5 | The C − B gain is positive in each harness on the harness track | per-harness difference with 95% CI (no pooling) |

H1 is the only confirmatory claim. Everything else is secondary and reported as such.

## 3. Arms

Within any comparison, the model, system prompt, turn limit, and task text are identical.

- **A (no tools):** the model answers alone. Measures memorization.
- **B (stock agent):** web search, web fetch, and sandboxed Python.
  - Core matrix: the same tools in Inspect for every model. Search and fetch use one fixed
    provider, disclosed, and are never routed through Locus.
  - Harness track: each harness's own built-in tools.
- **C (stock agent + Locus Pro):** B plus the Locus Pro MCP server (prod), with the whole
  catalog enabled, as configured by the tenant key. Enablement is snapshotted to
  `prereg/enablement-snapshot.json` at freeze time.
- **D (stock agent + direct vendors):** B plus vendor tools wired directly with each vendor's
  own key, the way a developer would do it themselves. Vendors: Apollo, Hunter, Prospeo,
  Firecrawl, Exa, Tavily, E2B. Official MCP servers are used where they exist, otherwise thin
  SDK wrappers. D runs only on the subset of tasks these vendors can serve.

### Tool awareness (applies to C and D)

Real MCP clients pass each server's own `instructions` text to the model. Inspect does not,
so the core matrix appends each mounted server's official instructions, snapshotted in
`prereg/server-instructions.json`, to the system prompt. B gets no extra text. Nothing is
added beyond the vendors' and Locus's own published text.

In the harness track, C means "Locus Pro installed the way the Locus docs say", which is the
MCP server plus the official Locus skill or plugin where the harness supports skills. A
secondary arm, C-mcp-only, mounts the MCP server alone. Spikes on 2026-10-03 showed 5 of 6
harnesses ignore an MCP server that comes without instructions, and that gap is reported as
its own finding.

### Stock search

B's web search is Tavily, called directly with a global concurrency cap of 2 and backoff on
429, because the key is shared with production traffic. Search errors go back to the agent as
text. They never crash a run.

## 4. Models (core matrix)

Pinned at freeze time from each provider's models endpoint:

- **Anthropic:** claude-opus-5-5, claude-sonnet-5-5, claude-haiku-4-5
- **OpenAI:** flagship plus a small model (candidates: gpt-6.1-sol, gpt-5.4-mini)
- **Google:** flagship Gemini plus Flash (candidates: current Pro, gemini-3.8-flash)
- **xAI:** grok-4.7
- **Open weights:** one model via OpenRouter (pinned at freeze)

Settings:
- Temperature: provider default.
- Reasoning effort: provider default. Each model's setting is recorded in the logs.

## 5. Harness track

Claude Code, OpenAI Codex CLI, Gemini CLI, OpenClaw, Hermes Agent, and the OpenAI Agents SDK
run arms B and C on the harness subset (about 25 tasks). Each uses its native flagship model.

A harness that cannot mount the Locus Pro MCP headlessly is dropped before the freeze, and
the reason is recorded in `docs/harness-spike-*.md`.

## 6. Tasks

Tasks were written on 2026-10-03 by authors who did not see the Locus catalog. They are frozen before any arm-C run of the full benchmark. The pilot uses 10
tasks, drawn from a separate pilot pool that is never scored in the final results.

| Battery | n | What success means |
|---|---|---|
| GTM research | 15 | right person (hand-verified truth) and the FIRST work email the agent gives on the right domain is marked `valid` by ZeroBounce at grade time (listing several guesses earns nothing extra) |
| Paid data | 12 | keyword volumes, Maps review counts, Amazon price and ratings, X metrics, audio facts; live or static truth from an authoritative source with a stated tolerance |
| Structured: public (01–11) | 11 | exact match against a source-of-record snapshot captured within 10 minutes of the run. These sources are free and fetchable, so this battery is reported separately and is **not** part of H1 |
| Structured: hostile (12–15) | 4 | as above, for bot-hostile retail and social pages; part of H1 |
| Multi-step, multi-vendor | 12 | at least 80% of the rubric claims satisfied (claims fixed per task) |
| Travel | 8 | the returned offer satisfies every constraint and is confirmed by a same-window fare snapshot |
| Control | 15 | exact or claims match; plain web search is sufficient |
| Spend safety | 5 | spend stays within the stated budget (agent outcome is secondary) |

Total: 82 scored tasks plus a 10-task pilot pool.

Task-writing rules:
- Tasks are written as a real user would phrase them, with no vendor or tool names.
- Every task has a gold answer or a fixed claims list before any run.
- Where possible, the source of truth is not the same source an arm-C tool returns.
- Tasks are drawn across company sizes, geographies, and domains so the set isn't built around
  any one provider.

## 7. Grading

1. Deterministic checks first: exact match, normalized match, set overlap, constraint checks.
2. Claims rubric where needed. The judge is a model from a different family than the agent
   being graded; the judge model and prompt are fixed in `bench/graders/`.
3. Human audit: a random 15% of graded runs, stratified by arm. Graders don't see the arm
   label. We publish the agreement rate between the human audit and the automated grader.
4. Errors, timeouts, refusals, and turn-limit exhaustion all count as failures.

## 8. Protocol

- 3 epochs per task, arm, and model.
- 30-message limit per run, with a 15-minute wall clock. Spend-safety tasks get 120 messages and 30 minutes so agents can actually reach their budget; on 2026-10-03, spend-02 hit the 30-message limit with only $0.06 (C) and about $0.45 (D) spent against $3.
- Every Locus call carries a fresh idempotency key. The deployed commit (`x-locus-commit`) is
  recorded on every call. No runs during a Locus deploy. If the commit changes mid-run, the
  affected runs are rerun.
- Concurrency is capped per provider.
- Pilot first: 10 pilot-pool tasks × all arms × 1 epoch. After the pilot, only harness bugs
  may be fixed; tasks, graders, and prompts are frozen.

## 9. Metrics

- Primary: success rate.
- Secondary:
  - cost per successful task = model tokens + Locus charges + direct vendor charges
  - p50 and p95 wall time
  - tool calls per run
  - tool-definition tokens in context
  - spend vs budget
- Diagnostic: for arm C, whether the agent's first `execute` used a sensible endpoint
  (labeled during the audit).

## 10. Analysis

- Unit: one task. Runs are paired by task across arms.
- CIs: clustered bootstrap over tasks, 10,000 resamples, seed `agent-access-bench-v1`, 95%.
- Pooled H1 weights each model equally. Per-model and per-battery results are always shown.
- No outlier removal. No task is dropped after the freeze unless its source of truth
  disappears; any drop is logged with the reason.

## 11. Publication commitments

- We publish the H1 result whatever its sign.
- The control battery (H2) is published whatever it shows.
- We publish every task, grader, prompt, raw log, trace, and this file with its freeze hash.
- If we change the product and rerun, the rerun uses a fresh, never-seen task set, and both
  results are published.

## 12. Known limitations, stated up front

- Locus runs the benchmark. Mitigations: the pre-registration, published traces, and the
  invitation to rerun.
- Live data drifts. Mitigation: truth snapshots taken in the same window.
- With a strong model, the stock agent (B) already passed 9 of 10 pilot tasks on 2026-10-03.
  We did not edit tasks in response. Headroom on strong models may be small, and that will
  be reported as found.
- Arm C's search over the full catalog was measured on 2026-10-03 at held-out recall@5 of
  7/18 (`results/discovery-prod-2026-10-03.json`). Arm C results therefore include the cost
  of discovery at full scale. This is how the product ships with everything enabled.
