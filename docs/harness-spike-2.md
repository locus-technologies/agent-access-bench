# Harness spike 2: OpenClaw, Hermes Agent, OpenAI Agents SDK

Date: 2026-10-03. Adapter: `bench/harnesses_extra.py`, function
`run_harness(name, prompt, with_locus, model=None, timeout_s=900, builtin_web=True)`.

Test prompt: "Find the current CEO of Ramp (the fintech company, ramp.com) and return
their name and a professional email address for them. Use your tools."

Emails in answers are redacted to the domain. Raw outputs are in `results/raw/spike2/*.json`.
Full traces are in `results/raw/harness_traces/<harness>/<stamp>_<arm>_<id>/`.

## How the arms are defined

- **Baseline** (`with_locus=False`): the harness's built-in web search and fetch. No MCP servers.
- **Locus** (`with_locus=True`): the same harness plus the Locus Pro MCP server. Built-in
  tools stay on, so this arm measures what adding Locus changes, not a swap of one tool set for another.
- **Locus-only** (`with_locus=True, builtin_web=False`): built-in web search and fetch are
  turned off. Shell, exec and browser tools stay on, as each harness ships them. This arm is
  optional. It was added after Hermes and the SDK both ignored Locus in the additive arm (see below).

Both CLIs need a search backend for their built-in `web_search`. Both are pinned to
**Tavily** (`BASELINE_WEB_PROVIDER`), so their baselines use the same search engine.
The SDK baseline uses OpenAI's hosted `WebSearchTool`.

The isolation rules are the same for every harness:
- Each CLI gets `HOME` and its state dir under `.harness-home/<name>/`.
- Each CLI gets a minimal environment: PATH plus only the keys it needs. Locus keys are
  passed only on Locus arms, so no search provider gets auto-detected from stray keys.
- Configs reference secrets as `${VAR}`, and the harness resolves them at connect time.
- After the runs, a grep of `results/raw`, `.harness-home`, `docs` and `bench` found none
  of the key values.

## Results

| Harness | Arm | Exit | Duration | Locus calls | Tools called | Answer |
|---|---|---|---|---|---|---|
| OpenClaw | baseline | 0 | 18.5s | 0 | exec, web_search | Eric Glyman, CEO (notes co-CEO); `@ramp.com` from Clay |
| OpenClaw | locus | 0 | 52.4s | 6 | search_apis, describe_api, estimate_cost, get_balance, execute x2 (Hunter email-finder) + web_search | Glyman and Atiyeh, co-CEOs; both `@ramp.com` via Hunter |
| Hermes | baseline | 0 | 19.9s | 0 | web_search x2, web_extract x2 | Co-CEOs Glyman and Atiyeh; `@ramp.com` from Clay |
| Hermes | locus | 0 | 25.7s | **0** | web_search x4, web_extract | Same as baseline. Locus was mounted but not used |
| Hermes | locus-only | 0 | 50.9s | 5 | search_apis x2, get_balance, describe_api, execute (Hunter) + terminal, browser_exec | Glyman, CEO; `@ramp.com` via Hunter (confidence 80, accept-all domain) |
| OpenAI Agents SDK | baseline | 0 | 12.1s | 0 | web_search x2 (hosted) | Glyman, co-CEO; `@ramp.com` from Clay |
| OpenAI Agents SDK | locus | 0 | 13.8s | **0** | web_search x2 (hosted) | Same as baseline. 15 Locus tools were mounted but not used |
| OpenAI Agents SDK | locus-only | 0 | 63.8s | 10 | search_apis x3, describe_api x2, execute x5 | Glyman, co-CEO; `@ramp.com` via Hunter |

Cost and usage, as each harness reports it:
- OpenClaw: $0.056 baseline, $0.126 with Locus (`usage.cost`).
- Hermes: 82k tokens baseline, 146k with Locus, 156k Locus-only (total, mostly cache reads).
- SDK: 21k tokens baseline, 142k Locus-only (9 requests).
- Locus charges for the Hunter lookups were about $0.013 each, as the agents reported them.

**Main finding.** With built-in web search available, only OpenClaw reached for Locus.
Hermes and the SDK answered from Clay's public page through their own search and never
touched the MCP server. Turning off built-in web made both use Locus correctly. Decide
which arm is the headline comparison before the main run.

## OpenClaw

- **Install:** `npm install --prefix harnesses/node openclaw@2026.9.8`.
  - It needs Node `>=24.16 <25` or `>=26.1`. The system Node is 26.0.0, so the adapter
    runs `/opt/homebrew/opt/node@24/bin/node` (24.20).
  - npm 11 skipped the package install scripts. It runs fine without them.
  - Tavily is an external plugin. Install it once into the isolated state dir:
    `HOME=.harness-home/openclaw OPENCLAW_STATE_DIR=.harness-home/openclaw/state node …/openclaw.mjs plugins install @openclaw/tavily-plugin@2026.9.8`.
- **Invocation:** `node openclaw.mjs agent exec --config <run>/openclaw.json --state-dir <run> --json --model anthropic/claude-sonnet-5-5 --cwd .harness-home/openclaw/work --timeout <s> --message-file prompt.txt`.
  - Env: `HOME`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`.
  - `agent exec` is an embedded, headless single turn. It needs no gateway or daemon, and no process is left running.
- **MCP:** `mcp.servers.locus-pro = {url, transport: "streamable-http", headers: {Authorization: "Bearer ${LOCUS_PRO_API_KEY}"}}`.
  - `openclaw mcp probe` reported 15 tools.
  - Tool names appear as `locus-pro__<tool>`.
- **Trace:**
  - The `--json` envelope gives `final`, `usage` (with USD cost), `toolSummary` and `bridgeCalls`.
  - Tool calls with args come from `trajectory_runtime_events` (`type == "tool.call"`) in `<run>/agents/main/agent/openclaw-agent.sqlite`.
  - The adapter dumps `trajectory.json` and `transcript.json`.
  - Code mode (the default) wraps tools in an `exec` JS bridge. Nested MCP calls are still logged by name.
- **Problems and workarounds:**
  - `--config` cannot be combined with `--auth-env-only`, so the adapter omits that flag. Isolation comes from the clean HOME and env instead.
  - The plugin is installed in the shared state dir, but every run gets a fresh `--state-dir`. The adapter therefore loads the plugin by path through `plugins.load.paths`.
  - The trajectory redacts the `code` argument of `exec` calls as `[Malfo…ted]`.

## Hermes Agent

- **Install:** `git clone --depth 1 https://github.com/NousResearch/hermes-agent harnesses/hermes/src`, then:
  - `uv venv --python 3.14 harnesses/hermes/.venv`. Core dependencies are gated on Python 3.14 or later.
  - `uv pip install -e "harnesses/hermes/src[anthropic,mcp]"`.
  - The official `curl | bash` installer was not used.
  - The first run in each HERMES_HOME prepares its own runtime (it installs Python dependencies) and takes about 10s longer.
- **Invocation:** `hermes chat --query-file prompt.txt --format stream-json --yolo --in <work> --run-budget <s>`, with `HOME` and `HERMES_HOME=.harness-home/hermes-{base,locus}/.hermes`.
  - The adapter writes `config.yaml` before every run with: `model.default`, `model.provider: anthropic`, `web.backend: tavily`, `mcp_servers`, and `agent.disabled_toolsets: [web]` for the Locus-only arm.
- **MCP:** `mcp_servers.locus-pro: {url: "${LOCUS_PRO_MCP_URL}", headers: {Authorization: "Bearer ${LOCUS_PRO_API_KEY}"}}`.
  - A `get_balance` probe worked.
  - Tools are named `mcp__locus_pro__<tool>`.
  - MCP tools sit behind Hermes's `tool_search`/`tool_describe` deferral and are not in the prompt up front. That likely explains why the model chose its built-in `web_search` in the additive arm.
- **Trace:** the stream-json JSONL has `tool_use` events (name and input), `tool_result`, and a final `result` (text, tokens, exit code). It is saved as `events.jsonl`.
- **Problems:**
  - Hermes's built-in `browser_exec` fails with "AF_UNIX path too long". Chrome's socket path under `.harness-home/.../.hermes/cache/browser-use/workspace/<uuid>` is too deep. This affects every arm. A shorter HERMES_HOME would fix it if browser use matters.
  - No gateway is needed.

## OpenAI Agents SDK

- **Install:** `uv add openai-agents` (0.23.1).
- **Invocation:** in-process `Runner.run(Agent(model="gpt-6.1-sol", tools=[WebSearchTool()], mcp_servers=[...]), prompt, max_turns=60)`.
  - It runs under `asyncio.wait_for(timeout_s)`.
  - The adapter falls back to `gpt-5.5` on model-not-found. That was not needed, because gpt-6.1-sol worked.
- **MCP:** `MCPServerStreamableHttp(name="locus-pro", params={url, headers: {Authorization: Bearer …}, timeout: 300}, client_session_timeout_seconds=300)`. `list_tools()` returned 15 tools.
- **Trace:**
  - `result.new_items` is saved to `items.json`.
  - `function_call` items map to MCP tool calls, and `web_search_call` items map to hosted search.
  - Usage comes from `context_wrapper.usage`.
  - SDK tracing upload is turned off.
- **Problems:** a second run in the same process failed with "Event loop is closed". The SDK's shared default client binds to the first event loop. The fix is a fresh `AsyncOpenAI` client per run, passed through `RunConfig(model_provider=OpenAIProvider(...))`.
