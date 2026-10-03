"""Snapshot each MCP server's own `instructions` (sent at initialize) to a frozen file.

Real MCP clients (Claude Code, Codex, Gemini CLI) pass server instructions to the model.
Inspect does not, so the core matrix appends the frozen snapshot to the system prompt for
whichever servers an arm mounts. Every arm gets its servers' official text, nothing more.
"""

import asyncio
import json
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx

from bench.direct_vendors import NODE_BIN, _key
from bench.secrets import load_secrets

SNAPSHOT = Path(__file__).resolve().parent.parent / "prereg" / "server-instructions.json"


def server_specs() -> dict:
    return {
        "locus-pro": ("http", os.environ["LOCUS_PRO_MCP_URL"], {"Authorization": "Bearer " + os.environ["LOCUS_PRO_API_KEY"]}),
        "apollo": ("http", "https://mcp.apollo.io/mcp", {"X-Api-Key": _key("APOLLO_API_KEY")}),
        "hunter": ("http", "https://mcp.hunter.io/mcp", {"X-API-Key": _key("HUNTER_API_KEY")}),
        "firecrawl": ("stdio", "firecrawl-mcp", {"FIRECRAWL_API_KEY": _key("FIRECRAWL_API_KEY")}),
        "exa": ("stdio", "exa-mcp-server", {"EXA_API_KEY": _key("EXA_API_KEY")}),
        "tavily": ("stdio", "tavily-mcp", {"TAVILY_API_KEY": _key("TAVILY_API_KEY")}),
        "prospeo": ("stdio", "prospeo-mcp-server", {"PROSPEO_API_KEY": _key("PROSPEO_API_KEY")}),
    }


async def fetch(kind: str, target: str, extra: dict) -> str:
    if kind == "http":
        # Raw JSON-RPC initialize: only the instructions field is needed.
        body = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "agent-access-bench", "version": "1"}}}
        headers = {**extra, "content-type": "application/json", "accept": "application/json, text/event-stream"}
        async with httpx.AsyncClient(timeout=60) as client:
            text = (await client.post(target, json=body, headers=headers)).text
        if "data:" in text[:50]:
            text = [ln[5:] for ln in text.splitlines() if ln.startswith("data:")][-1]
        return json.loads(text)["result"].get("instructions") or ""
    else:
        params = StdioServerParameters(command=str(NODE_BIN / target), args=[], env={**os.environ, **extra})
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                init = await s.initialize()
    return init.instructions or ""


async def main() -> None:
    load_secrets()
    out = {}
    for name, (kind, target, extra) in server_specs().items():
        try:
            out[name] = await asyncio.wait_for(fetch(kind, target, extra), 60)
        except Exception as e:
            out[name] = ""
            print(name, "error:", repr(e)[:120])
        print(f"{name:10s} {len(out[name])} chars")
    SNAPSHOT.write_text(json.dumps(out, indent=1))


def instructions_for(names: list[str]) -> str:
    snap = json.loads(SNAPSHOT.read_text())
    parts = [f"## {n}\n{snap[n].strip()}" for n in names if snap.get(n, "").strip()]
    return "\n\nConnected tool servers and their instructions:\n\n" + "\n\n".join(parts) if parts else ""


if __name__ == "__main__":
    asyncio.run(main())
