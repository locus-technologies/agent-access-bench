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
