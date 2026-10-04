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

## 2026-10-04 ~08:10Z: Gemini CLI baseline contaminated; rerun
- Gemini CLI loads `.env` files from the working directory's parent directories. The harness
  work directories were inside the repo, so Gemini CLI loaded the repo `.env`, including the
  Locus Pro execution key, the Locus admin key and the benchmark Tavily key, into its shell
  environment. In arm B, 13 of 68 Gemini CLI traces reach Locus (paywithlocus.com), and 9
  contain an `env` dump. Arm B for Gemini CLI is therefore invalid.
- No stock-arm trace from the other five harnesses mentions Locus. The core matrix is
  unaffected: its tools run in Docker without the host environment.
- Fix: every harness home and work directory now lives under
  `/tmp/agent-access-bench-harness-home`, outside the repo. A check run shows Gemini CLI sees
  only GEMINI_API_KEY. The 68 contaminated rows are in
  `results/raw/harness/superseded/gemini-cli-B-contaminated.jsonl`. Gemini CLI arm B is rerun
  in full.
- The exposed keys went into Gemini model context and are being rotated.
