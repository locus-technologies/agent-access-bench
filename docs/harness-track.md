# Harness track: arms, Locus install per harness, runner

Runner: `bench/harness_track.py`. Adapters: `bench/harnesses.py` (Claude Code, Codex CLI,
Gemini CLI) and `bench/harnesses_extra.py` (OpenClaw, Hermes Agent, OpenAI Agents SDK). Both
take `locus_mode: "none" | "mcp" | "mcp+skill"`; the old `with_locus` flag still works and
means `"mcp"`.

```
uv run python -m bench.harness_track --harnesses claude-code,codex,gemini-cli,openclaw,hermes,openai-agents \
    --arms B,C,C-mcp-only --epochs 3 --batteries gtm,paiddata,structured,multistep,travel,control,spend
```

## Arms

| Arm | locus_mode | What the harness gets |
|---|---|---|
| B | none | The harness as shipped: its built-in web tools, no MCP servers, no Locus skill |
| C | mcp+skill | B + the Locus Pro MCP server + the official Locus skills, installed the way the Locus docs say for that harness |
| C-mcp-only | mcp | B + the Locus Pro MCP server alone |

Every C and C-mcp-only run uses the same prod MCP URL and tenant bearer key (`LOCUS_PRO_MCP_URL`,
`LOCUS_PRO_API_KEY`, passed by env var name only). The Locus docs specify browser OAuth for
interactive clients. A headless benchmark cannot complete OAuth, so the bearer key replaces it in
both Locus arms. That is the only deviation from the documented install.

## Where the official install method comes from

- Locus docs (`apps/backend/src/modules/credits/docs/docs.service.ts`, MCP section): the plugin
  for Claude Code and Codex (`/plugin marketplace add locus-technologies/locus-pro-plugin`,
  `/plugin install locus@locus`; `codex plugin marketplace add …`, `codex plugin add locus@locus`).
  OpenClaw and Hermes are pointed at the bootstrap `https://paywithlocus.com/SKILL.md`.
- Plugin repo README (`github.com/locus-technologies/locus-pro-plugin`, cloned read-only to
  `harnesses/locus-pro-plugin`, commit `5397409`, plugin 0.3.37): other skill-capable clients
  install the three skills with `npx skills add locus-technologies/locus-pro-plugin`.
- Bootstrap `skills/locus-pro/SKILL.md` and the plugin's host guides
  (`skills/locus-setup/references/hosts/{openclaw,hermes}.md`): the exact skill roots for OpenClaw
  and Hermes.

The three skills are `locus` (operating guide: routing, idempotency keys, quotes, errors),
`locus-setup` and `locus-workflows`. All three are installed, as the docs require.

## Per harness (arm C)

| Harness | Skill route | Where it lands | Notes |
|---|---|---|---|
| Claude Code | Native plugin: `claude plugin marketplace add <clone>` + `claude plugin install locus@locus` | `.harness-home/claude-code/locus-skill/.claude/plugins` | The plugin's own MCP entry (OAuth) is excluded by `--strict-mcp-config`; init shows only `locus-pro: connected` plus skills `locus:locus`, `locus:locus-setup`, `locus:locus-workflows`. `Skill` is added to `--allowedTools` in this arm, since plugin skills load through it. |
| Codex CLI | Native plugin: `codex plugin marketplace add <clone>` + `codex plugin add locus@locus` | `.harness-home/codex/locus-skill/.codex` | Plugin state lives in `<CODEX_HOME>/config.toml`, so this arm drops `--ignore-user-config` (the home is isolated and the file holds only the marketplace/plugin entries). The plugin's MCP entry is named `locus` and uses OAuth; the bearer server is registered under that same name, which replaces it (no AuthRequired error; calls show server `locus`). Tool names are therefore `mcp__locus__*` in C and `mcp__locus-pro__*` in C-mcp-only. |
| Gemini CLI | Native Agent Skills: `gemini skills install <clone>/skills/<skill> --scope user --consent` (same three skills `npx skills add` installs) | `.harness-home/gemini-cli/locus-skill/.gemini/skills` | Loaded through Gemini's `activate_skill`. |
| OpenClaw | Host guide: `openclaw skills install <abs skill dir> --force` for each skill | `<run state>/workspace/skills` (fresh per run) | `agent exec --cwd` sets the agent workspace, so this arm runs in the run's own workspace; the shared work dir would leak skills into other arms. `openclaw skills info locus` reports "Visible to model: yes". |
| Hermes Agent | Host guide: complete copy of each released tree at `<HERMES_HOME>/skills/<skill>` | `.harness-home/hermes-locus-skill/.hermes/skills` | Uses the repo's Hermes build (`agents/hermes/skills`, descriptions trimmed to Hermes's 60-char limit). |
| OpenAI Agents SDK | No skills mechanism on a plain `Agent` (the SDK's Skills capability is for `SandboxAgent`, which would change the B baseline) | Agent `instructions` (system prompt) | Appends the `locus` SKILL.md body (frontmatter stripped). Only `locus`: setup/workflows are about installing and authoring, not using. Unlike the other harnesses, the full text is in context from turn one rather than loaded on demand. |

Each arm has its own isolated home, so skills installed for C never reach B or C-mcp-only. Nothing
is written under the user's real `~/.claude`, `~/.codex`, `~/.gemini`, `~/.openclaw` or `~/.hermes`.

## Runner output

`results/raw/harness/<run-id>.jsonl`, one line per run: harness, arm, locus_mode, model (with
provider prefix, used to pick the cross-family judge), task_id, battery, epoch, score, grader_detail,
answer (first 4,000 chars), tool_calls (names), locus_calls, locus_tools, locus_usd, skill_loads,
duration_s, exit_code, error, usage, trace_path.

- `locus_usd` sums `usd_charged` from Locus tool results found in the raw trace, deduplicated by the
  `credits_balance` printed next to each charge. It is 0.0 when only free meta-tools were called and
  null when a billable Locus tool was called but the trace shows no charge.
- `skill_loads` counts calls that load a Locus skill (Skill / activate_skill / skill_view, or a read
  of a Locus SKILL.md). Diagnostic only.
- Task pool: `harness_track=true` tasks in the requested batteries. Pilot tasks carry no flag, so
  `--batteries pilot` uses the whole pilot pool; `--tasks` narrows any pool.
- At most two runs execute at once (shared prod vendor keys). Timeout is 900 s per run.
- Adapter crashes and grader errors are recorded as failed runs, never dropped.
