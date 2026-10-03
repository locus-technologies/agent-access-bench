"""Headless adapters for real agent CLIs, run with and without the Locus Pro MCP.

Each harness runs in an isolated HOME / config dir under .harness-home/<name>/ so
nothing touches the user's real ~/.claude, ~/.codex, ~/.gemini or ~/.config.
Secrets come from bench.secrets.load_secrets() and are passed via the child env
only (the MCP bearer token is referenced by env var name, never written to disk).

    run_harness("claude-code", prompt, with_locus=True, model=None)
    run_harness("claude-code", prompt, with_locus=True, model=None, locus_mode="mcp+skill")
    -> {"final_answer", "tool_calls", "raw_trace_path", "exit_code", "duration_s", "usage", ...}

Baseline arm (with_locus=False) keeps each CLI's built-in web search / fetch
tools enabled and mounts no MCP servers.

locus_mode refines with_locus: "none" (baseline), "mcp" (Locus Pro MCP only, the
default when with_locus=True) or "mcp+skill" (MCP plus the official Locus skills,
installed per harness the way the Locus docs say; see docs/harness-track.md).
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from pathlib import Path

from bench.secrets import load_secrets

ROOT = Path(__file__).resolve().parent.parent
HOME_ROOT = ROOT / ".harness-home"
NODE_BIN = ROOT / "harnesses" / "node" / "node_modules" / ".bin"
TRACE_ROOT = ROOT / "results" / "raw" / "harness"

LOCUS_SERVER = "locus-pro"
LOCUS_MODES = ("none", "mcp", "mcp+skill")
# Official Locus plugin repo (github.com/locus-technologies/locus-pro-plugin), cloned read-only.
LOCUS_PLUGIN_DIR = ROOT / "harnesses" / "locus-pro-plugin"
LOCUS_SKILLS = ("locus", "locus-setup", "locus-workflows")

DEFAULT_MODELS = {
    "claude-code": "claude-sonnet-5-5",
    "codex": "gpt-6.1-sol",
    "gemini-cli": "gemini-3.1-pro-preview",
}

# Built-in tools each CLI gets in both arms (the realistic stock agent).
CLAUDE_BUILTIN_TOOLS = ["WebSearch", "WebFetch", "ToolSearch"]


def _base_env(home: Path) -> dict[str, str]:
    """Minimal child env: PATH + isolated HOME, no inherited config dirs."""
    keep = ("PATH", "LANG", "LC_ALL", "TERM", "TMPDIR", "USER", "SHELL")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    env["HOME"] = str(home)
    env["XDG_CONFIG_HOME"] = str(home / ".config")
    env["XDG_CACHE_HOME"] = str(home / ".cache")
    env["XDG_DATA_HOME"] = str(home / ".local" / "share")
    env["NO_COLOR"] = "1"
    return env


def _arm_label(locus_mode: str) -> str:
    return {"none": "baseline", "mcp": "locus", "mcp+skill": "locus-skill"}[locus_mode]


def _fresh_dirs(name: str, locus_mode: str) -> tuple[Path, Path, Path]:
    """(home, workdir, trace_path) for one run. Home persists per harness+arm; workdir is fresh.

    Each locus_mode gets its own home, so skills installed for "mcp+skill" never leak into
    the baseline or MCP-only arms."""
    arm = _arm_label(locus_mode)
    home = HOME_ROOT / name / arm
    run_id = time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    work = HOME_ROOT / name / "work" / f"{arm}-{run_id}"
    work.mkdir(parents=True, exist_ok=True)
    trace_dir = TRACE_ROOT / name
    trace_dir.mkdir(parents=True, exist_ok=True)
    home.mkdir(parents=True, exist_ok=True)
    return home, work, trace_dir / f"{arm}-{run_id}.jsonl"


def _run(cmd: list[str], env: dict[str, str], cwd: Path, trace_path: Path, timeout_s: int) -> tuple[int, str, float]:
    t0 = time.monotonic()
    with open(trace_path, "w") as out, open(trace_path.with_suffix(".stderr.txt"), "w") as err:
        try:
            proc = subprocess.run(
                cmd, env=env, cwd=cwd, stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=timeout_s, check=False
            )
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code = 124
    return code, trace_path.read_text(), time.monotonic() - t0


def _install_quiet(cmd: list[str], env: dict[str, str]) -> None:
    proc = subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=300, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"install step failed: {' '.join(cmd[:4])}: {proc.stderr[-500:]}")


def _jsonl(text: str) -> list[dict]:
    events = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


# --------------------------------------------------------------------------- claude code


def _ensure_claude_plugin(env: dict[str, str]) -> None:
    """Official route (Locus docs): `/plugin marketplace add locus-technologies/locus-pro-plugin`
    then `/plugin install locus@locus`, done here with the CLI equivalents against the read-only
    clone, inside the isolated CLAUDE_CONFIG_DIR. The plugin's own MCP entry (OAuth, alias
    `locus`) is excluded by --strict-mcp-config; the bearer-auth server below is the connection."""
    marker = Path(env["CLAUDE_CONFIG_DIR"]) / "plugins" / "installed_plugins.json"
    if marker.exists() and "locus@locus" in marker.read_text():
        return
    claude = str(NODE_BIN / "claude")
    _install_quiet([claude, "plugin", "marketplace", "add", str(LOCUS_PLUGIN_DIR)], env)
    _install_quiet([claude, "plugin", "install", "locus@locus"], env)


def _claude(prompt: str, locus_mode: str, model: str, timeout_s: int) -> dict:
    with_locus = locus_mode != "none"
    home, work, trace = _fresh_dirs("claude-code", locus_mode)
    env = _base_env(home)
    env["CLAUDE_CONFIG_DIR"] = str(home / ".claude")
    env["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]
    env["DISABLE_AUTOUPDATER"] = "1"
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    allowed = list(CLAUDE_BUILTIN_TOOLS)
    mcp_config = {"mcpServers": {}}
    if with_locus:
        env["LOCUS_PRO_API_KEY"] = os.environ["LOCUS_PRO_API_KEY"]
        mcp_config["mcpServers"][LOCUS_SERVER] = {
            "type": "http",
            "url": os.environ["LOCUS_PRO_MCP_URL"],
            "headers": {"Authorization": "Bearer ${LOCUS_PRO_API_KEY}"},  # expanded by claude from env
        }
        allowed.append(f"mcp__{LOCUS_SERVER}")
    if locus_mode == "mcp+skill":
        _ensure_claude_plugin(env)
        allowed.append("Skill")  # plugin skills are invoked through the Skill tool
    mcp_path = home / f"mcp-{'locus' if with_locus else 'none'}.json"
    mcp_path.write_text(json.dumps(mcp_config))

    cmd = [
        str(NODE_BIN / "claude"),  # local 2.1.288; the global 2.1.231 breaks WebSearch on sonnet-5-5
        "-p", prompt,
        # Not --bare: bare mode (CLAUDE_CODE_SIMPLE) strips the tool set to Bash/Edit/Read,
        # dropping WebSearch/WebFetch. Isolation comes from HOME + CLAUDE_CONFIG_DIR instead.
        "--output-format", "stream-json", "--verbose",
        "--model", model,
        "--strict-mcp-config", "--mcp-config", str(mcp_path),
        "--permission-mode", "dontAsk",
        "--allowedTools", ",".join(allowed),
        "--no-session-persistence",
    ]
    code, text, dur = _run(cmd, env, work, trace, timeout_s)
    events = _jsonl(text)

    tool_calls, final, usage, mcp_status = [], "", {}, None
    for ev in events:
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            mcp_status = ev.get("mcp_servers")
        if ev.get("type") == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") in ("tool_use", "server_tool_use"):
                    tool_calls.append({"name": block.get("name"), "args": block.get("input")})
        if ev.get("type") == "result":
            final = ev.get("result") or ""
            usage = {**(ev.get("usage") or {}), "total_cost_usd": ev.get("total_cost_usd"),
                     "num_turns": ev.get("num_turns"), "is_error": ev.get("is_error")}
    return _result(final, tool_calls, trace, code, dur, usage, model, mcp_status)


# --------------------------------------------------------------------------- codex


def _ensure_codex_plugin(env: dict[str, str]) -> None:
    """Official route (Locus docs): `codex plugin marketplace add locus-technologies/locus-pro-plugin`
    then `codex plugin add locus@locus`, run against the read-only clone inside the isolated
    CODEX_HOME. This writes only the marketplace and plugin entries to <CODEX_HOME>/config.toml."""
    cfg = Path(env["CODEX_HOME"]) / "config.toml"
    if cfg.exists() and 'plugins."locus@locus"' in cfg.read_text():
        return
    codex = str(NODE_BIN / "codex")
    _install_quiet([codex, "plugin", "marketplace", "add", str(LOCUS_PLUGIN_DIR)], env)
    _install_quiet([codex, "plugin", "add", "locus@locus"], env)


def _codex(prompt: str, locus_mode: str, model: str, timeout_s: int) -> dict:
    with_locus = locus_mode != "none"
    home, work, trace = _fresh_dirs("codex", locus_mode)
    env = _base_env(home)
    env["CODEX_HOME"] = str(home / ".codex")
    (home / ".codex").mkdir(parents=True, exist_ok=True)
    env["CODEX_API_KEY"] = os.environ["OPENAI_API_KEY"]
    env["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]

    # The plugin's own MCP entry is named `locus` and uses OAuth, which cannot complete headlessly.
    # In mcp+skill the bearer-auth entry takes that same name, which replaces the plugin's entry
    # (verified: no AuthRequired error, calls show server "locus"). The plugin is read from the
    # isolated CODEX_HOME config, so --ignore-user-config is dropped in that arm only.
    server = "locus" if locus_mode == "mcp+skill" else LOCUS_SERVER
    overrides = ['web_search="live"', 'approval_policy="never"']
    if with_locus:
        env["LOCUS_PRO_API_KEY"] = os.environ["LOCUS_PRO_API_KEY"]
        url = os.environ["LOCUS_PRO_MCP_URL"]
        overrides += [
            f'mcp_servers.{server}.url="{url}"',
            f'mcp_servers.{server}.bearer_token_env_var="LOCUS_PRO_API_KEY"',
            f"mcp_servers.{server}.tool_timeout_sec=300",
            f'mcp_servers.{server}.default_tools_approval_mode="approve"',
            # Without required=true codex exec may start the first turn before the HTTP MCP
            # handshake finishes, and the model then sees no locus tools (observed in the spike).
            f"mcp_servers.{server}.required=true",
        ]
    if locus_mode == "mcp+skill":
        _ensure_codex_plugin(env)
    last_msg = trace.with_suffix(".last.txt")
    cmd = [str(NODE_BIN / "codex"), "exec", "--json", "--skip-git-repo-check", "--ephemeral",
           *([] if locus_mode == "mcp+skill" else ["--ignore-user-config"]),
           "--ignore-rules", "-s", "read-only", "-m", model,
           "-o", str(last_msg)]
    for o in overrides:
        cmd += ["-c", o]
    cmd.append(prompt)
    code, text, dur = _run(cmd, env, work, trace, timeout_s)
    events = _jsonl(text)

    tool_calls, usage, mcp_status, final = [], {}, None, ""
    for ev in events:
        item = ev.get("item") or {}
        if ev.get("type") == "item.completed":
            t = item.get("type")
            if t == "mcp_tool_call":
                tool_calls.append({"name": f"mcp__{item.get('server')}__{item.get('tool')}",
                                   "args": item.get("arguments"), "status": item.get("status")})
            elif t == "web_search":
                tool_calls.append({"name": "web_search", "args": {"query": item.get("query"),
                                                                  "action": item.get("action")}})
            elif t == "command_execution":
                tool_calls.append({"name": "shell", "args": {"command": item.get("command")}})
            elif t == "agent_message":
                final = item.get("text") or final
        if ev.get("type") == "turn.completed":
            u = ev.get("usage") or {}
            for k, v in u.items():
                usage[k] = usage.get(k, 0) + v if isinstance(v, (int, float)) else v
        if ev.get("type") in ("error", "turn.failed"):
            usage.setdefault("errors", []).append(ev.get("message") or ev.get("error"))
    if last_msg.exists() and last_msg.read_text().strip():
        final = last_msg.read_text().strip()
    return _result(final, tool_calls, trace, code, dur, usage, model, mcp_status)


# --------------------------------------------------------------------------- gemini cli


def _ensure_gemini_skills(env: dict[str, str]) -> None:
    """Gemini CLI has native Agent Skills (`gemini skills install <path>`). Locus docs route
    skill-capable clients without a plugin to the three released skills (`npx skills add
    locus-technologies/locus-pro-plugin`); this is the same install, done with Gemini's own
    installer into the isolated GEMINI_CLI_HOME (user scope)."""
    root = Path(env["GEMINI_CLI_HOME"]) / ".gemini" / "skills"
    for skill in LOCUS_SKILLS:
        if not (root / skill / "SKILL.md").exists():
            _install_quiet([str(NODE_BIN / "gemini"), "skills", "install", str(LOCUS_PLUGIN_DIR / "skills" / skill),
                            "--scope", "user", "--consent"], env)


def _gemini(prompt: str, locus_mode: str, model: str, timeout_s: int) -> dict:
    with_locus = locus_mode != "none"
    home, work, trace = _fresh_dirs("gemini-cli", locus_mode)
    env = _base_env(home)
    env["GEMINI_CLI_HOME"] = str(home)
    env["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
    env["GEMINI_CLI_TRUST_WORKSPACE"] = "true"

    settings: dict = {
        "security": {"auth": {"selectedType": "gemini-api-key"}, "folderTrust": {"enabled": False}},
        "general": {"disableAutoUpdate": True, "disableUpdateNag": True},
        "privacy": {"usageStatisticsEnabled": False},
        "telemetry": {"enabled": False},
        "mcpServers": {},
    }
    if with_locus:
        env["LOCUS_PRO_API_KEY"] = os.environ["LOCUS_PRO_API_KEY"]
        settings["mcpServers"][LOCUS_SERVER] = {
            "httpUrl": os.environ["LOCUS_PRO_MCP_URL"],
            "headers": {"Authorization": "Bearer $LOCUS_PRO_API_KEY"},  # expanded by gemini from env
            "timeout": 300000,
            "trust": True,
        }
    gdir = home / ".gemini"
    gdir.mkdir(parents=True, exist_ok=True)
    (gdir / "settings.json").write_text(json.dumps(settings, indent=2))
    if locus_mode == "mcp+skill":
        _ensure_gemini_skills(env)

    cmd = [str(NODE_BIN / "gemini"), "-p", prompt, "-o", "stream-json", "-m", model,
           "--approval-mode", "yolo", "--skip-trust"]
    code, text, dur = _run(cmd, env, work, trace, timeout_s)
    events = _jsonl(text)

    tool_calls, usage, final_parts, mcp_status = [], {}, [], None
    for ev in events:
        t = ev.get("type")
        if t == "init":
            mcp_status = ev.get("mcp_servers") or ev.get("mcpServers")
        elif t == "tool_use":
            tool_calls.append({"name": ev.get("tool_name"), "args": ev.get("parameters")})
        elif t == "message" and ev.get("role") == "assistant":
            final_parts.append(ev.get("content") or "")
        elif t == "result":
            usage = ev.get("stats") or {}
            if ev.get("status") != "success":
                usage["error"] = ev.get("error")
    return _result("".join(final_parts).strip(), tool_calls, trace, code, dur, usage, model, mcp_status)


# --------------------------------------------------------------------------- entry point


def _result(final, tool_calls, trace, code, dur, usage, model, mcp_status) -> dict:
    return {
        "final_answer": final,
        "tool_calls": tool_calls,
        "raw_trace_path": str(trace),
        "exit_code": code,
        "duration_s": round(dur, 2),
        "usage": usage,
        "model": model,
        "mcp_status": mcp_status,
    }


HARNESSES = {"claude-code": _claude, "codex": _codex, "gemini-cli": _gemini}
ALIASES = {"claude": "claude-code", "gemini": "gemini-cli"}


def resolve_locus_mode(with_locus: bool, locus_mode: str | None) -> str:
    """locus_mode wins when given; otherwise with_locus=True means MCP only (the spike arm)."""
    mode = locus_mode or ("mcp" if with_locus else "none")
    if mode not in LOCUS_MODES:
        raise ValueError(f"locus_mode must be one of {LOCUS_MODES}, got {mode!r}")
    return mode


def run_harness(name: str, prompt: str, with_locus: bool, model: str | None, timeout_s: int = 900,
                locus_mode: str | None = None) -> dict:
    name = ALIASES.get(name, name)
    if name not in HARNESSES:
        raise ValueError(f"unknown harness {name!r}; expected one of {sorted(HARNESSES)}")
    load_secrets()
    mode = resolve_locus_mode(with_locus, locus_mode)
    out = HARNESSES[name](prompt, mode, model or DEFAULT_MODELS[name], timeout_s)
    out["locus_mode"] = mode
    return out


def locus_calls(result: dict) -> list[dict]:
    """Tool calls that went to the Locus Pro MCP server."""
    # claude/codex: mcp__locus-pro__<tool> (codex mcp+skill: mcp__locus__<tool>); gemini: mcp_locus-pro_<tool>
    return [c for c in result["tool_calls"] if (c.get("name") or "").startswith(("mcp__locus", "mcp_locus"))]


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("prompt")
    ap.add_argument("--locus", action="store_true")
    ap.add_argument("--locus-mode", choices=LOCUS_MODES)
    ap.add_argument("--model")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    r = run_harness(a.name, a.prompt, a.locus, a.model, a.timeout, locus_mode=a.locus_mode)
    print(json.dumps(r, indent=2, default=str))
