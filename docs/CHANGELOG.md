# Changelog (post-freeze)

## 2026-10-04 ~02:40Z: harness fix, core and arm D resumed
- Problem: live truth captures (blocking HTTP) ran inside the async scorer and froze every
  concurrent sample in the process (median 100–180 s per no-tools sample, paid-data about
  900 s). In arm D, 112 of 208 samples errored with MCP HTTP ConnectError/ConnectTimeout,
  consistent with the frozen event loop starving the Apollo and Hunter MCP streams.
- Fix: captures run in a worker thread and are shared for up to 10 minutes per
  (capture, args), the pre-registered snapshot window. Search tool network errors now return
  text to the agent instead of raising.
- Grading logic is unchanged. Completed samples are kept; errored and unfinished samples are
  rerun via eval_retry. No task, prompt, grader rule or arm changed.

## 2026-10-04 ~02:50Z: Gemini CLI stream rescheduled
- Gemini CLI runs its internal housekeeping (history compression, routing, loop checks) on
  `gemini-3-flash-preview`, which hit its daily API quota ("You have exhausted your daily
  quota on this model") on the shared Google key. That is a provider quota, not agent
  behaviour. The benchmark model itself (gemini-3.1-pro-preview) was unaffected in direct
  calls.
- The gemini-cli+openclaw stream was stopped. Its partial results are in
  `results/raw/harness/superseded/` and are excluded. OpenClaw restarted alone. Gemini CLI
  reruns all three arms from scratch after the quota resets (00:00 PT = 07:00Z), so its arms
  stay paired in time.

## 2026-10-04 ~03:00Z: Gemini 3.1 Pro rerouted (supersedes the 02:50Z entry's diagnosis)
- Real cause, from a `gemini --debug` run: Google enforces
  `generate_requests_per_model_per_day, limit: 250, model: gemini-3.1-pro` on our API key
  tier. The preview-flash helper theory in the 02:50Z entry was wrong. 250 requests a day
  cannot support the core matrix or the harness track.
- Core matrix: Gemini 3.1 Pro runs through OpenRouter as
  `openrouter/google/gemini-3.1-pro-preview`. It is the same model, served by Google, at the
  same list price ($2/$12 per 1M tokens). Logs: `logs/main-gpro`, `logs/main-d-gpro`.
  Samples sent through the direct `google/gemini-3.1-pro-preview` route in `logs/main` and
  `logs/main-d` are excluded from analysis.
- Harness track: Gemini CLI can only call Google's API, so it runs on `gemini-3.8-flash` (GA)
  instead of 3.1 Pro. This is a deviation from "each harness uses its native flagship model"
  and is reported as such. Its helper-alias override (gemini-3-flash-base -> gemini-3.8-flash)
  stays.
- No task, prompt, grader rule or arm changed.

## 2026-10-04 ~03:20Z: missing arms launched
- `eval_retry` resumes only tasks that already had a log. When the core and D processes were
  stopped at about 02:40Z, only arm A (9 models) and arm D (3 Anthropic models) had started,
  so arms B and C (8 models) and arm D (5 models) were never queued by the resume.
- Launched them: `logs/main-bc` (B and C, 8 models) and `logs/main-d2` (D, 5 models). Same
  code, tasks and settings. Gemini 3.1 Pro runs every arm in `logs/main-gpro` and
  `logs/main-d-gpro`.

## 2026-10-04 ~03:50Z: arm A finished for 4 models; analysis log policy
- `eval_retry` processed the interrupted logs one at a time and stalled on the excluded
  direct-Google Gemini Pro log, which kept hitting its quota. Arm A for claude-opus-5-5,
  grok-4.7, gpt-6-luna and deepseek-v4-pro was rerun fresh in `logs/main-a2`.
- Analysis policy, fixed now and before any results are read: use only logs with status
  `success`; one sample per (model, arm, task, epoch); exclude
  `google/gemini-3.1-pro-preview` (rerouted). Interrupted partial logs (status
  `started`/`error`) are kept for audit but not scored.

## 2026-10-04 ~05:30Z: rule for infrastructure errors (written before their reruns)
- Samples that errored for infrastructure reasons are rerun once at the end of the run, in
  `logs/rerun`, and the rerun replaces the errored sample for that (model, arm, task, epoch).
  The reasons: Docker daemon or config errors, MCP `ConnectError` / `Connection closed`,
  provider `ModelGenerateError`, and `CancelledError` from the interruption.
- If the rerun also errors, the sample counts as a failure. Agent timeouts and message-limit
  hits are never rerun; they are failures as pre-registered.
- At the time of writing, 28 such samples exist across arms B, C and D, out of about 6,800.

## 2026-10-04 ~06:25Z: spend stream
- The sequential spend loop reached `google/gemini-3.1-pro-preview` (direct route, capped at
  250 requests a day) and stalled for about an hour. It was stopped. Spend runs for Gemini 3.1
  Pro use `openrouter/google/gemini-3.1-pro-preview`, as in the core matrix. The remaining
  models (gemini-3.8-flash, grok-4.7, deepseek-v4-pro) run in parallel processes. Spend runs
  from the direct route are excluded with the same policy as the core.
- 06:35Z addendum: `AioRpcError`, the gRPC error from xAI's client, is a provider error of the
  same kind as `ModelGenerateError` and was added to the infrastructure list before any
  rerun ran. Rerun plan: `results/rerun-plan.json` (42 samples).

## 2026-10-04 ~07:00Z: human audit size (deviation, recorded before any review)
- The pre-registration says to audit "a random 15% of graded runs". 15% of the ~7,700 scored
  core runs is ~1,150 items, more than a few hours of human review.
- Instead we audit a fixed sample of 250 items: 220 from the core matrix and 30 from the
  harness track. The sample is stratified by arm, and grader types are weighted toward those
  judged by an LLM or a verifier (claims, person_email, flight) because deterministic exact and
  number matches rarely disagree. The agreement rate is reported both as sampled and
  reweighted to the full population of runs. Sample seed: sha256("agent-access-bench-audit-v1").
- If the reviewer chooses, the full 15% can still be audited later with the same page.

## 2026-10-04 ~06:55Z: OpenClaw stream stopped
- The OpenClaw harness process wrote no output for about 1 h 45 min after its 206th of 207
  runs. Its per-run timeout did not fire, so the process was stopped by hand. The one missing
  run (paiddata-06, arm C, epoch 1) is excluded; task-level means use the remaining epochs.

## 2026-10-04 ~08:10Z: Gemini CLI baseline contaminated; excluded from the harness track
- Gemini CLI runs on the host with shell access. In arm B (no paid data), some of its runs
  picked up the benchmark's Locus Pro configuration from the host (first from a parent-folder
  `.env` it loads automatically, then, after the work directories were moved under /tmp, by
  locating the repo through the process list) and called Locus Pro. 13 of 68 arm-B traces in
  the first run and 6 of 69 in the rerun reached Locus Pro, so its baseline is not a no-data
  baseline.
- No arm-B trace from the other five harnesses reaches Locus Pro. The core matrix is
  unaffected: its tools run in Docker without the host environment.
- Gemini CLI is excluded from the harness-track results and charts; its rows are kept in
  `results/raw/harness/superseded/`. A valid rerun needs the harness in a container with no
  host filesystem. The harness track reports five harnesses.

## 2026-10-04 ~09:30Z: chart fix (presentation only)
- Chart 01 drew arm D next to the other arms, but D ran only on the tasks its vendors can serve,
  so its rates were computed over a different task set. That made the direct-vendor setup look
  better than it is. D is removed from chart 01. Chart 07 compares B, C and D on the same 34
  data tasks: C 76%, D 75%, B 54%. No numbers or analysis changed.

## 2026-10-05: flight "cheapest fare" rule (deviation, found after seeing results)
- Section 6 of the pre-registration says a flight answer passes when "the returned offer
  satisfies every constraint and is confirmed by a same-window fare snapshot". The snapshot check
  was never built. As implemented, any run that passed the constraint checks could set the
  task's cheapest fare, including approximate or stale quotes. Two cases surfaced in review:
  - travel-07: a web-search run's "around SGD 126 (≈ $93–99)" for "late October" set the bar,
    failing every Locus run ($129).
  - travel-02: a web-search run's $125 from a cached Trip.com page set the bar; live Locus fares
    were $139–145.
- Corrected rule (`FLIGHT_MIN_RULE=specific`, applied mechanically and identically to all arms):
  a run can set the cheapest fare only if its answer names a flight number and states the price
  without a hedge ("around", "about", "approx", "≈", "~", "roughly", "from", "starting at",
  "cached"). This fixes travel-07. It cannot detect travel-02's stale quote, which names a
  flight and an exact price, so that case stands.
- Both results are reported. The pre-registered rule (`results/full`) stays the headline:
  H1 +25.0 [+16.1, +33.8]; flights B 10%, C 43%. Corrected (`results/full-flightfix`):
  H1 +26.0 [+16.9, +34.8]; flights B 10%, C 50%. Constraint checks alone: B 13%, C 72%.
- Because the correction was found after seeing results and favours Locus, it does not change the
  headline.

## 2026-10-05: grading corrections for two tasks (deviation, found after seeing results)
Found while reviewing the tasks where arm C scored below arm B. Applied by `bench/regrade.py`,
identically to every arm and model, and analysed with `GRADE_OVERRIDES` into
`results/full-corrected`. The pre-registered results stay the headline.
- gtm-05 (Mews CEO + work email). The grader accepted only `mews.com`. Mews used
  `mewssystems.com` before its rebrand and that domain still receives mail. All five failing
  arm-C runs named the right CEO and gave a `mewssystems.com` address from a contact database.
  Correction: accept `mewssystems.com` under the same rule (ZeroBounce "valid"). Statuses are
  checked at regrade time (2026-10-05), not run time; all six such addresses returned "valid".
  One arm-B run that had failed only because its grader call errored now passes on regrade.
  Result: B 93% -> 96%, C 81% -> 100%, D 89% unchanged, A 4% unchanged.
- multistep-06 (PostHog roles + who runs it). Claim 2 says a role passes if it is on the careers
  page "or in the 2026-10-03 snapshot in notes", but the judge was never given the notes, and
  it may not use outside knowledge. Claims 2 and 3 (role and location match the listing) were
  therefore unverifiable, and the verdicts turned on how confidently an answer cited the
  careers page. Correction: the judge now sees the task notes (`judge_claims(reference=...)`).
  Result: B 74% -> 52%, C 37% -> 48%, D 48% -> 33%, A 0%. No other task's rubric cites the notes.
- Flight price extraction (corrected rule only): the "first currency amount" rule read the user's
  budget cap as the fare in answers that restate it first ("under your $350 budget"), in every
  arm. Under `FLIGHT_MIN_RULE=specific` an amount preceded by budget/cap/limit/under/max/spend
  is skipped. The pre-registered rule is unchanged.
- `results/full-corrected` = all of the above plus the flight rule above (`FLIGHT_MIN_RULE=specific`)
  and supersedes `results/full-flightfix`. H1 +27.1 [+18.4, +35.8] (pre-registered: +25.0
  [+16.1, +33.8]). Data tasks B 42.8%, C 69.9%. Flights B 11%, C 51%. Multistep B 63%, C 67%.
  H2 and H3 unchanged.
- Reviewed and left as scored: multistep-04, multistep-11, control-06, gtm-08 (genuine agent
  errors); structured-06, structured-08, paiddata-06 (Locus `web_research` returned stale or
  wrong data; real arm-C failures); spend-02 (5 arm-C runs crashed on connection errors to the
  Locus MCP server or web search; counted as failures under the infra-error rule because no
  rerun exists); travel-02 (a cached $125 fare with a flight number still sets the bar, as noted
  above); multistep-09 (about half of arm C's failures look like judge errors on the
  unverifiable "sells CLM per its own site" claim; flagged for the human spot-check rather
  than re-scored, because the fix would mean rewriting the rubric).
- Spend battery: 6 of 135 arm-C runs (and 3 of 135 arm-D runs) have no ledger or trace spend
  record. They are excluded from the spend chart rather than plotted as $0.
