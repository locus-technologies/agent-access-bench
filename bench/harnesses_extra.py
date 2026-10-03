"""Headless adapters for OpenClaw, Hermes Agent, and the OpenAI Agents SDK.

    run_harness(name, prompt, with_locus, model=None, timeout_s=900) -> dict

Arms:
  with_locus=False  the harness's own built-in web tools, no MCP servers.
  with_locus=True   the same harness plus the Locus Pro MCP server (streamable HTTP,
                    bearer auth). Built-in tools stay on, so the arm measures what
                    adding Locus does, not a tool swap.
  locus_mode        "none" | "mcp" | "mcp+skill" refines with_locus; "mcp+skill" also
                    installs the official Locus skills (OpenClaw: `openclaw skills
                    install`; Hermes: <HERMES_HOME>/skills; Agents SDK: skill text in
                    the agent instructions). See docs/harness-track.md.
  builtin_web=False (optional) drops the built-in web search/fetch tools, e.g. a
                    Locus-only arm. Shell/exec tools stay, as each harness ships them.

Each tool_calls entry is {"name", "args", "locus": bool}; "locus_tool_calls" counts
the calls that went to the Locus Pro MCP server.

Isolation: every CLI runs with HOME and its state dir under .harness-home/<name>/,
and gets a minimal environment (PATH plus only the keys that harness needs), so
nothing leaks in from the user's real config and no web-search provider is
auto-detected from stray keys. Configs reference secrets as ${VAR}; the harness
resolves them from the child env at connect time, so no key is written to disk.

Built-in web search needs a backend in both CLIs. Both are pinned to Tavily
(BASELINE_WEB_PROVIDER) so the baseline is the same search engine across them.
The OpenAI Agents SDK baseline uses its hosted WebSearchTool.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import os
import signal
import sqlite3
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HARNESS_HOME = ROOT / ".harness-home"
TRACE_ROOT = ROOT / "results" / "raw" / "harness_traces"

NODE24_BIN = Path("/opt/homebrew/opt/node@24/bin")  # openclaw needs node 24.16+ or 26.1+
OPENCLAW_ENTRY = ROOT / "harnesses" / "node" / "node_modules" / "openclaw" / "openclaw.mjs"
HERMES_BIN = ROOT / "harnesses" / "hermes" / ".venv" / "bin" / "hermes"

BASELINE_WEB_PROVIDER = "tavily"
DEFAULT_MODELS = {
    "openclaw": "anthropic/claude-sonnet-5-5",
    "hermes": "claude-sonnet-5-5",
    "openai-agents": "gpt-6.1-sol",
}
OPENAI_AGENTS_FALLBACK_MODEL = "gpt-5.5"
LOCUS_SERVER_NAME = "locus-pro"
LOCUS_MODES = ("none", "mcp", "mcp+skill")
LOCUS_PLUGIN_DIR = ROOT / "harnesses" / "locus-pro-plugin"  # read-only clone of the official plugin repo
LOCUS_SKILLS = ("locus", "locus-setup", "locus-workflows")
LOCUS_ENV = ("LOCUS_PRO_MCP_URL", "LOCUS_PRO_API_KEY")
PASSTHROUGH_ENV = ("LANG", "LC_ALL", "TMPDIR", "USER", "LOGNAME", "SHELL")

_secrets_loaded = False


def _ensure_secrets() -> None:
    """Load keys once, in this process, before any child gets an isolated HOME."""
    global _secrets_loaded
    if _secrets_loaded:
        return
    from bench.secrets import load_secrets

    cwd = os.getcwd()
    os.chdir(ROOT)  # load_secrets reads a relative .env
    try:
        load_secrets()
    finally:
        os.chdir(cwd)
    missing = [k for k in LOCUS_ENV if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"missing env: {missing}")
    _secrets_loaded = True


def _child_env(home: Path, keys: tuple[str, ...], with_locus: bool, extra: dict[str, str]) -> dict[str, str]:
    env = {k: os.environ[k] for k in PASSTHROUGH_ENV if k in os.environ}
    env["PATH"] = f"{NODE24_BIN}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    env["HOME"] = str(home)
    env["TERM"] = "dumb"
    env["NO_COLOR"] = "1"
    wanted = keys + (LOCUS_ENV if with_locus else ())
    env.update({k: os.environ[k] for k in wanted if os.environ.get(k)})
    env.update(extra)
    return env


def _run_cli(cmd: list[str], env: dict[str, str], cwd: Path, timeout_s: int) -> tuple[int, str, str]:
    """Run in its own process group so a timeout kills the whole tree."""
    proc = subprocess.Popen(
        cmd, env=env, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, start_new_session=True,
    )
    try:
        out, err = proc.communicate(timeout=timeout_s)
        return proc.returncode, out, err
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        return 124, out, err + f"\n[harnesses_extra] killed after {timeout_s}s timeout"


def _trace_dir(name: str, locus_mode: str, builtin_web: bool) -> Path:
    stamp = time.strftime("%Y%m%dT%H%M%S")
    arm = {"none": "base", "mcp": "locus", "mcp+skill": "locus-skill"}[locus_mode] + ("" if builtin_web else "-noweb")
    d = TRACE_ROOT / name / f"{stamp}_{arm}_{uuid.uuid4().hex[:6]}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, default=str))


# ---------------------------------------------------------------- OpenClaw


def _openclaw_config(with_locus: bool, builtin_web: bool) -> dict:
    # The tavily web_search provider is an external plugin, installed once into the
    # shared state dir (`openclaw plugins install @openclaw/tavily-plugin`). Each run
    # gets a fresh --state-dir, so the plugin is loaded by explicit path.
    plugin_dirs = sorted((HARNESS_HOME / "openclaw" / "state" / "npm" / "projects").glob(
        f"openclaw-{BASELINE_WEB_PROVIDER}-plugin-*/node_modules/@openclaw/{BASELINE_WEB_PROVIDER}-plugin"))
    if not plugin_dirs:
        raise RuntimeError(f"openclaw {BASELINE_WEB_PROVIDER} plugin not installed; see docs/harness-spike-2.md")
    cfg: dict[str, Any] = {
        "tools": {"web": {"search": {"provider": BASELINE_WEB_PROVIDER, "enabled": builtin_web},
                          "fetch": {"enabled": builtin_web}}},
        "plugins": {"load": {"paths": [str(plugin_dirs[-1])]},
                    "entries": {BASELINE_WEB_PROVIDER: {"enabled": True}}},
    }
    if with_locus:
        cfg["mcp"] = {"servers": {LOCUS_SERVER_NAME: {
            "url": "${LOCUS_PRO_MCP_URL}",
            "transport": "streamable-http",
            "headers": {"Authorization": "Bearer ${LOCUS_PRO_API_KEY}"},
            "requestTimeoutMs": 300_000,
        }}}
    return cfg


def _sqlite_rows(db: Path, sql: str) -> list[dict]:
    if not db.exists():
        return []
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return [json.loads(r[0]) for r in con.execute(sql) if r[0]]
    finally:
        con.close()


def _install_openclaw_skills(env: dict[str, str], cfg_path: Path, run_state: Path) -> None:
    """The Locus OpenClaw host guide installs each released skill tree with
    `openclaw skills install <absolute-skill-dir> --force`. Each run has a fresh state dir,
    so the install runs per run, into that run's agent workspace (<state>/workspace/skills)."""
    ienv = {**env, "OPENCLAW_STATE_DIR": str(run_state), "OPENCLAW_CONFIG_PATH": str(cfg_path)}
    for skill in LOCUS_SKILLS:
        proc = subprocess.run(
            [str(NODE24_BIN / "node"), str(OPENCLAW_ENTRY), "skills", "install",
             str(LOCUS_PLUGIN_DIR / "skills" / skill), "--force"],
            env=ienv, cwd=run_state, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"openclaw skills install {skill} failed: {proc.stderr[-400:]}")


def _run_openclaw(prompt: str, locus_mode: str, model: str | None, timeout_s: int, trace: Path,
                  builtin_web: bool) -> dict:
    with_locus = locus_mode != "none"
    home = HARNESS_HOME / "openclaw"
    run_state = home / "runs" / trace.name
    work = home / "work"
    for d in (run_state, work):
        d.mkdir(parents=True, exist_ok=True)
    cfg_path = run_state / "openclaw.json"
    _write_json(cfg_path, _openclaw_config(with_locus, builtin_web))
    prompt_file = trace / "prompt.txt"
    prompt_file.write_text(prompt)

    model = model or DEFAULT_MODELS["openclaw"]
    if "/" not in model:
        model = f"anthropic/{model}"
    keys = ("TAVILY_API_KEY", "OPENROUTER_API_KEY" if model.startswith("openrouter/") else "ANTHROPIC_API_KEY")
    env = _child_env(home, keys, with_locus, {
        "OPENCLAW_STATE_DIR": str(home / "state"),
        "OPENCLAW_CONFIG_PATH": str(cfg_path),
    })
    if locus_mode == "mcp+skill":
        _install_openclaw_skills(env, cfg_path, run_state)
        # `agent exec --cwd` sets the agent workspace, and workspace skills load from
        # <workspace>/skills. The shared work dir would leak skills into other arms, so this
        # arm runs in the run's own workspace, where `skills install` put them.
        work = run_state / "workspace"
    cmd = [
        str(NODE24_BIN / "node"), str(OPENCLAW_ENTRY), "agent", "exec",
        "--config", str(cfg_path), "--state-dir", str(run_state), "--json",
        "--model", model, "--cwd", str(work), "--timeout", str(timeout_s),
        "--message-file", str(prompt_file),
    ]
    code, out, err = _run_cli(cmd, env, work, timeout_s + 60)
    (trace / "stdout.json").write_text(out)
    (trace / "stderr.log").write_text(err)

    try:
        envelope = json.loads(out)
    except json.JSONDecodeError:
        envelope = {}
    agent_db = run_state / "agents" / "main" / "agent" / "openclaw-agent.sqlite"
    trajectory = _sqlite_rows(agent_db, "select event_json from trajectory_runtime_events order by seq")
    transcript = _sqlite_rows(agent_db, "select event_json from transcript_events where event_json is not null order by seq")
    _write_json(trace / "trajectory.json", trajectory)
    _write_json(trace / "transcript.json", transcript)

    tool_calls = [
        {"name": e["data"].get("name"), "args": e["data"].get("args"),
         "locus": str(e["data"].get("name", "")).startswith(f"{LOCUS_SERVER_NAME}__")}
        for e in trajectory if e.get("type") == "tool.call"
    ]
    usage = dict(envelope.get("usage") or {})
    usage.update({k: envelope[k] for k in ("costUsd", "toolSummary", "bridgeCalls", "assistantTurns") if k in envelope})
    if not envelope.get("ok", False) and code == 0:
        code = 1
    return {
        "final_answer": envelope.get("final") or "",
        "tool_calls": tool_calls,
        "raw_trace_path": str(trace),
        "exit_code": code,
        "usage": usage,
        "model": envelope.get("model") or model,
        "error": (envelope.get("error") or {}).get("message"),
    }


# ---------------------------------------------------------------- Hermes


def _hermes_config(with_locus: bool, model: str, provider: str, builtin_web: bool) -> str:
    lines = [
        "model:",
        f"  default: {json.dumps(model)}",
        f"  provider: {provider}",
        "web:",
        f"  backend: {BASELINE_WEB_PROVIDER}",
    ]
    if not builtin_web:
        lines += ["agent:", "  disabled_toolsets:", "    - web"]
    if with_locus:
        lines += [
            "mcp_servers:",
            f"  {LOCUS_SERVER_NAME}:",
            '    url: "${LOCUS_PRO_MCP_URL}"',
            "    headers:",
            '      Authorization: "Bearer ${LOCUS_PRO_API_KEY}"',
            "    timeout: 300",
        ]
    return "\n".join(lines) + "\n"


def _install_hermes_skills(hermes_home: Path) -> None:
    """Locus Hermes host guide: activate each released tree at <HERMES_HOME>/skills/<skill>,
    as a complete copy. The plugin repo ships the Hermes build of the trees (descriptions
    trimmed to Hermes's 60-char limit) under agents/hermes/skills."""
    import shutil

    for skill in LOCUS_SKILLS:
        dest = hermes_home / "skills" / skill
        if not (dest / "SKILL.md").exists():
            shutil.copytree(LOCUS_PLUGIN_DIR / "agents" / "hermes" / "skills" / skill, dest, dirs_exist_ok=True)


def _run_hermes(prompt: str, locus_mode: str, model: str | None, timeout_s: int, trace: Path,
                builtin_web: bool) -> dict:
    with_locus = locus_mode != "none"
    suffix = {"none": "base", "mcp": "locus", "mcp+skill": "locus-skill"}[locus_mode]
    home = HARNESS_HOME / f"hermes-{suffix}"
    hermes_home = home / ".hermes"
    work = home / "work"
    for d in (hermes_home, work):
        d.mkdir(parents=True, exist_ok=True)
    if locus_mode == "mcp+skill":
        _install_hermes_skills(hermes_home)

    model = model or DEFAULT_MODELS["hermes"]
    provider = "anthropic"
    if model.startswith("openrouter/"):
        provider, model = "openrouter", model.removeprefix("openrouter/")
    elif model.startswith("anthropic/"):
        model = model.removeprefix("anthropic/")
    (hermes_home / "config.yaml").write_text(_hermes_config(with_locus, model, provider, builtin_web))
    prompt_file = trace / "prompt.txt"
    prompt_file.write_text(prompt)

    keys = ("TAVILY_API_KEY", "OPENROUTER_API_KEY" if provider == "openrouter" else "ANTHROPIC_API_KEY")
    env = _child_env(home, keys, with_locus, {"HERMES_HOME": str(hermes_home)})
    cmd = [
        str(HERMES_BIN), "chat", "--query-file", str(prompt_file), "--format", "stream-json",
        "--yolo", "--in", str(work), "--run-budget", str(timeout_s),
    ]
    code, out, err = _run_cli(cmd, env, work, timeout_s + 60)
    (trace / "events.jsonl").write_text(out)
    (trace / "stderr.log").write_text(err)

    events = []
    for line in out.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    hermes_prefix = "mcp__" + LOCUS_SERVER_NAME.replace("-", "_") + "__"
    tool_calls = [
        {"name": e.get("name"), "args": e.get("input"), "locus": str(e.get("name", "")).startswith(hermes_prefix)}
        for e in events if e.get("type") == "tool_use"
    ]
    final = result.get("text") or "".join(e.get("text", "") for e in events if e.get("type") == "text")
    if result and code == 0:
        code = int(result.get("exit_code") or 0)
    return {
        "final_answer": final,
        "tool_calls": tool_calls,
        "raw_trace_path": str(trace),
        "exit_code": code if result else (code or 1),
        "usage": result.get("tokens") or {},
        "model": f"{provider}/{model}",
        "session_id": result.get("session_id"),
    }


# ---------------------------------------------------------------- OpenAI Agents SDK


def _item_to_call(raw: Any, locus_names: set[str]) -> dict:
    data = raw.model_dump(exclude_none=True) if hasattr(raw, "model_dump") else dict(raw)
    kind = data.get("type")
    if kind == "function_call":
        try:
            args = json.loads(data.get("arguments") or "{}")
        except json.JSONDecodeError:
            args = data.get("arguments")
        return {"name": data.get("name"), "args": args, "locus": data.get("name") in locus_names}
    if kind == "web_search_call":
        return {"name": "web_search", "args": data.get("action"), "locus": False}
    return {"name": kind, "args": None, "locus": False}


BASE_INSTRUCTIONS = "You are a helpful research assistant. Use your tools to answer accurately."


def locus_skill_text() -> str:
    """The official `locus` operating skill, frontmatter stripped. The plain Agents SDK Agent has
    no skills mechanism (the SDK's Skills capability belongs to SandboxAgent), so mcp+skill
    appends this text to the agent's instructions, the SDK's system prompt."""
    text = (LOCUS_PLUGIN_DIR / "skills" / "locus" / "SKILL.md").read_text()
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.strip()


async def _openai_agents_async(prompt: str, locus_mode: str, model: str, timeout_s: int,
                               builtin_web: bool) -> tuple[Any, str, set[str]]:
    with_locus = locus_mode != "none"
    from agents import (
        Agent,
        OpenAIProvider,
        RunConfig,
        Runner,
        WebSearchTool,
        set_tracing_disabled,
    )
    from agents.mcp import MCPServerStreamableHttp
    from openai import AsyncOpenAI

    set_tracing_disabled(True)  # keep traces local; we write our own
    servers = []
    if with_locus:
        servers.append(MCPServerStreamableHttp(
            name=LOCUS_SERVER_NAME,
            params={
                "url": os.environ["LOCUS_PRO_MCP_URL"],
                "headers": {"Authorization": "Bearer " + os.environ["LOCUS_PRO_API_KEY"]},
                "timeout": 300,
                "sse_read_timeout": 300,
            },
            client_session_timeout_seconds=300,
            cache_tools_list=True,
        ))
    locus_names: set[str] = set()
    for s in servers:
        await s.connect()
        locus_names |= {t.name for t in await s.list_tools()}
    # A fresh client per run: the SDK's shared default client binds its connection
    # pool to the first event loop and fails with "Event loop is closed" on reuse.
    run_config = RunConfig(model_provider=OpenAIProvider(openai_client=AsyncOpenAI()))
    instructions = BASE_INSTRUCTIONS
    if locus_mode == "mcp+skill":
        instructions += "\n\n" + locus_skill_text()
    try:
        last_err: Exception | None = None
        for m in dict.fromkeys([model, OPENAI_AGENTS_FALLBACK_MODEL]):
            agent = Agent(
                name="assistant",
                instructions=instructions,
                model=m,
                tools=[WebSearchTool()] if builtin_web else [],
                mcp_servers=servers,
            )
            try:
                res = await asyncio.wait_for(Runner.run(agent, prompt, max_turns=60, run_config=run_config), timeout=timeout_s)
                return res, m, locus_names
            except Exception as e:  # model-not-found -> try fallback; anything else re-raises
                if "model" in str(e).lower() and ("not found" in str(e).lower() or "does not exist" in str(e).lower()):
                    last_err = e
                    continue
                raise
        raise last_err or RuntimeError("no model ran")
    finally:
        for s in servers:
            await s.cleanup()


def _run_openai_agents(prompt: str, locus_mode: str, model: str | None, timeout_s: int, trace: Path,
                       builtin_web: bool) -> dict:
    model = model or DEFAULT_MODELS["openai-agents"]

    def _go():
        return asyncio.run(_openai_agents_async(prompt, locus_mode, model, timeout_s, builtin_web))

    try:
        asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(1) as ex:  # caller already has a loop
            res, used_model, locus_names = ex.submit(_go).result()
    except RuntimeError as e:
        if "no running event loop" not in str(e):
            raise
        res, used_model, locus_names = _go()

    from agents.items import ToolCallItem

    tool_calls = [_item_to_call(i.raw_item, locus_names) for i in res.new_items if isinstance(i, ToolCallItem)]
    _write_json(trace / "items.json", [
        {"item_type": i.type, "raw": (i.raw_item.model_dump() if hasattr(i.raw_item, "model_dump") else i.raw_item)}
        for i in res.new_items
    ])
    u = res.context_wrapper.usage
    usage = {"requests": u.requests, "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
             "total_tokens": u.total_tokens}
    return {
        "final_answer": str(res.final_output or ""),
        "tool_calls": tool_calls,
        "raw_trace_path": str(trace),
        "exit_code": 0,
        "usage": usage,
        "model": used_model,
        "locus_tools_mounted": sorted(locus_names),
    }


# ---------------------------------------------------------------- entry point

_RUNNERS = {"openclaw": _run_openclaw, "hermes": _run_hermes, "openai-agents": _run_openai_agents}


def run_harness(name: str, prompt: str, with_locus: bool, model: str | None = None, timeout_s: int = 900,
                builtin_web: bool = True, locus_mode: str | None = None) -> dict:
    """locus_mode: "none" | "mcp" | "mcp+skill"; when omitted, with_locus picks "mcp" or "none"."""
    if name not in _RUNNERS:
        raise ValueError(f"unknown harness {name!r}; expected one of {sorted(_RUNNERS)}")
    mode = locus_mode or ("mcp" if with_locus else "none")
    if mode not in LOCUS_MODES:
        raise ValueError(f"locus_mode must be one of {LOCUS_MODES}, got {mode!r}")
    with_locus = mode != "none"
    _ensure_secrets()
    trace = _trace_dir(name, mode, builtin_web)
    t0 = time.monotonic()
    try:
        out = _RUNNERS[name](prompt, mode, model, timeout_s, trace, builtin_web)
    except Exception as e:  # report, don't crash a sweep
        out = {"final_answer": "", "tool_calls": [], "raw_trace_path": str(trace), "exit_code": 1,
               "usage": {}, "error": f"{type(e).__name__}: {e}"}
    out["duration_s"] = round(time.monotonic() - t0, 2)
    out["harness"] = name
    out["with_locus"] = with_locus
    out["locus_mode"] = mode
    out["builtin_web"] = builtin_web
    out["locus_tool_calls"] = sum(1 for c in out["tool_calls"] if c.get("locus"))
    _write_json(trace / "result.json", out)
    return out


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("name", choices=sorted(_RUNNERS))
    p.add_argument("prompt")
    p.add_argument("--locus", action="store_true")
    p.add_argument("--model")
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--no-builtin-web", action="store_true")
    p.add_argument("--locus-mode", choices=LOCUS_MODES)
    a = p.parse_args()
    r = run_harness(a.name, a.prompt, a.locus, a.model, a.timeout, builtin_web=not a.no_builtin_web,
                    locus_mode=a.locus_mode)
    print(json.dumps(r, indent=2, default=str))
