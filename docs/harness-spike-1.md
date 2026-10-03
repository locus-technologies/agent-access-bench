# Harness spike 1: Claude Code, Codex CLI, Gemini CLI, with and without Locus Pro MCP

Date: 2026-10-03. Adapter: `bench/harnesses.py` (`run_harness(name, prompt, with_locus, model, timeout_s)`).

Task prompt (neutral): "Find the current CEO of Ramp (the fintech company, ramp.com) and return their name and a professional email address for them. Use your tools."

Hinted variant (wiring check only, not a benchmark arm): same prompt plus "Prefer the locus-pro MCP tools (pay-per-call API catalog) for this."

Isolation: every CLI runs with `HOME`, `XDG_*` and its own config dir under `.harness-home/<harness>/<arm>/`, in a fresh empty workdir under `.harness-home/<harness>/work/`, with a minimal env (PATH plus that harness's keys). Nothing under `~/.claude`, `~/.codex`, `~/.gemini` or `~/.config` is read or written. The Locus bearer token is passed by env var name only. No key appears in any file under `bench/`, `docs/`, `.harness-home/` or `results/raw/harness/` (checked by grep). Raw traces go to `results/raw/harness/<harness>/<arm>-<ts>.jsonl` (gitignored), with stderr next to them.

## Headline finding

All three harnesses mount the Locus Pro MCP headlessly, and all three call it successfully when steered toward it. **On the neutral prompt, none of the three chose Locus.** Each used its own built-in web search, even with Locus mounted. The likely cause is that Claude Code and Codex both defer MCP tools behind a tool-search step, so the model never sees `search_apis` and the rest unless it goes looking. Gemini CLI does list the Locus tools directly and still picked `google_web_search`. This is a real result about stock agents and should shape the benchmark design. Possible responses: a system or prompt line naming the catalog, or tasks the built-in search cannot answer.

| Harness | Arm | Locus tools called | Other tools | Duration | Answer (CEO / email) |
|---|---|---|---|---|---|
| Claude Code | baseline | n/a | ToolSearch, WebSearch x2 | 14.5 s | Glyman + Atiyeh co-CEOs / @ramp.com (from Clay, flagged unverified) |
| Claude Code | locus | none | ToolSearch, WebSearch x2 | 18.5 s | Glyman + Atiyeh / @ramp.com (Clay, unverified) |
| Claude Code | locus, hinted | search_apis x2, describe_api x2, execute x3 (brave/answers, hunter/email-finder x2) | ToolSearch | 35.1 s | Glyman + Atiyeh / @ramp.com (Hunter, score 80) |
| Codex | baseline | n/a | web_search x2 | 13.6 s | Glyman co-CEO with Atiyeh / @ramp.com (Clay) |
| Codex | locus | none | web_search x2 | 11.3 s | Glyman co-CEO / @ramp.com (Clay) |
| Codex | locus, hinted | search_apis x2, describe_api x2, execute x3 (brave/web-search x2, hunter/email-finder) | none | 34.3 s | Glyman co-CEO / @ramp.com (Hunter, score 80) |
| Gemini CLI | baseline | n/a | google_web_search x2 | 17.7 s | Glyman / @ramp.com (pattern guess) |
| Gemini CLI | locus | none | google_web_search x1 | 22.7 s | Glyman / @ramp.com (pattern guess) |
| Gemini CLI | locus, hinted | search_apis, describe_api, execute (hunter/email-finder) | google_web_search, update_topic x2 | 33.3 s | Glyman / @ramp.com (Hunter) |

Emails are redacted to the domain. In the non-Locus runs the address came from a Clay page or a naming-pattern guess. In the Locus runs it came from Hunter, which returned a different local part and noted that the domain accepts all addresses. All exit codes were 0. Claude Code cost was $0.09 to $0.13 per run (from the CLI's `total_cost_usd`). Codex and Gemini report token counts only.

## Claude Code

- Install: the global `claude` is 2.1.231 and **does not work with claude-sonnet-5-5**. WebSearch returns `API Error: 400 To turn thinking off on this model, send "thinking": {"type": "between_tools"}`, and claude-opus-5-5 is refused outright ("version 2.1.280 or newer is required"). Workaround: a local install, `npm install --prefix harnesses/node @anthropic-ai/claude-code` (2.1.288). The adapter uses `harnesses/node/node_modules/.bin/claude`.
- Invocation (env: `HOME`, `CLAUDE_CONFIG_DIR=<home>/.claude`, `ANTHROPIC_API_KEY`, `LOCUS_PRO_API_KEY` in the Locus arm only):
  ```
  claude -p "<prompt>" --output-format stream-json --verbose --model claude-sonnet-5-5 \
    --strict-mcp-config --mcp-config <home>/mcp-{locus|none}.json \
    --permission-mode dontAsk --allowedTools WebSearch,WebFetch,ToolSearch[,mcp__locus-pro] \
    --no-session-persistence
  ```
  The MCP config is `{"type":"http","url":$LOCUS_PRO_MCP_URL,"headers":{"Authorization":"Bearer ${LOCUS_PRO_API_KEY}"}}`, and Claude expands the variable from the env. The baseline arm gets `{"mcpServers":{}}`.
- MCP mounted: yes. The init event shows `locus-pro: connected`. MCP tools are deferred behind ToolSearch.
- Problems:
  - `--bare` cuts the tool set to Bash/Edit/Read and drops WebSearch/WebFetch, so it is not used. Isolation comes from HOME and CLAUDE_CONFIG_DIR instead.
  - Under `dontAsk`, tools not on the allow list (Bash, Write, etc.) are denied automatically.

## Codex CLI

- Install: `npm install --prefix harnesses/node @openai/codex` (codex-cli 0.160.0).
- Invocation (env: `HOME`, `CODEX_HOME=<home>/.codex`, `CODEX_API_KEY` and `OPENAI_API_KEY` set to the OpenAI key, `LOCUS_PRO_API_KEY` in the Locus arm only):
  ```
  codex exec --json --skip-git-repo-check --ephemeral --ignore-user-config --ignore-rules \
    -s read-only -m gpt-6.1-sol -o <trace>.last.txt \
    -c web_search="live" -c approval_policy="never" \
    [-c mcp_servers.locus-pro.url="$LOCUS_PRO_MCP_URL" \
     -c mcp_servers.locus-pro.bearer_token_env_var="LOCUS_PRO_API_KEY" \
     -c mcp_servers.locus-pro.tool_timeout_sec=300 \
     -c mcp_servers.locus-pro.default_tools_approval_mode="approve" \
     -c mcp_servers.locus-pro.required=true] \
    "<prompt>"
  ```
- MCP mounted: yes (`codex mcp list` shows it enabled with bearer auth, and calls show up as `mcp_tool_call` items with `server: locus-pro`). Codex always defers MCP tools: they are reached through `ALL_TOOLS` and `tools.*` inside `functions.exec`, not as top-level functions. The feature `tool_search_always_defer_mcp_tools` is on and has been removed as a toggle. Disabling `code_mode_host` does not change this.
- Problems: **without `required=true`, the first hinted run saw no Locus tools.** The model wrote "Locus-pro MCP tools weren't available in this session". `exec` started the turn before the HTTP MCP handshake finished. After `required=true` was added, the same prompt called Locus 7 times. Codex prints "Reading additional input from stdin..." to stderr, which is harmless because stdin is /dev/null.

## Gemini CLI

- Install: `npm install --prefix harnesses/node @google/gemini-cli` (0.62.0).
- Model: `gemini-3.1-pro-preview`, the newest pro model in the models API (`gemini-3-pro-preview` is the CLI's own preview constant; the CLI's latest flash is gemini-3.8-flash). The CLI also routes some internal calls to gemini-3-flash-preview, which appears in `usage.models`.
- Invocation (env: `HOME` and `GEMINI_CLI_HOME` set to `<home>`, `GEMINI_API_KEY` set to the Google key, `GEMINI_CLI_TRUST_WORKSPACE=true`, `LOCUS_PRO_API_KEY` in the Locus arm only):
  ```
  gemini -p "<prompt>" -o stream-json -m gemini-3.1-pro-preview --approval-mode yolo --skip-trust
  ```
  `<home>/.gemini/settings.json` sets `security.auth.selectedType=gemini-api-key`, telemetry and auto-update off, and `mcpServers` either `{}` or `{"locus-pro":{"httpUrl":$URL,"headers":{"Authorization":"Bearer $LOCUS_PRO_API_KEY"},"timeout":300000,"trust":true}}`.
- MCP mounted: yes. A tool-list probe shows 15 `mcp_locus-pro_*` tools exposed directly, with no deferral. The init event does not report MCP status, so `mcp_status` is None for Gemini.
- Problems: none blocking. Gemini's Locus tool list did not include `gtm_enrich`, `web_research`, `web_extract` or `router_web_search`. Those tools appear on other Locus Pro MCP connections, so this API key's tenant may not expose them. Check before the benchmark relies on them.

## Notes

- `harnesses/node/package.json` also lists `openclaw`. That was installed by a concurrent session, not this spike.
- Locus spend for the spike: about 7 billed `execute` calls across the three hinted runs (Brave and Hunter), in cents.
