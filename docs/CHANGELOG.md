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
