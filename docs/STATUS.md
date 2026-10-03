# Status

## Done (2026-10-03)
- [x] Repo, secrets loader, Inspect harness, end-to-end Locus MCP spike on prod
- [x] Tool-search re-measure on prod at full enablement (held-out recall@5 7/18)
- [x] 82 scored tasks + 10 pilot, written blind to the catalog; graders and live truth captures
- [x] Arm D (official vendor MCPs) and tool-definition token counts (B 760 / C 6,914 / D 79,645)
- [x] Six harness adapters (Claude Code, Codex, Gemini CLI, OpenClaw, Hermes, Agents SDK)
- [x] Server-instructions snapshot; throttled stock search; single-process runner
- [x] Clean pilot: 4 arms x 2 models x 10 tasks, no errors
- [x] Pre-registration v0.2

## Open
- [ ] Decision (Cole): turn on the prod router feature flags before the run, or benchmark prod as-is
- [ ] Harness-track runner: tasks -> run_harness -> grade; install the official Locus skill per harness
- [ ] Spend runner: one funded end-user sub-account per C run (hard cap)
- [ ] Analysis: clustered bootstrap CIs, cost per success (token prices + Locus + vendor), flight cross-arm cheapest check
- [ ] Freeze (`prereg-v1` tag), then full run
- [ ] Human audit (15%), charts, article, clips, Bookface post
