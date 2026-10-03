"""Count the tokens each arm's tool definitions cost per model request.

Materializes the exact tool list bench.arms.tools_for(arm) gives the model
(MCP servers are listed live via tools/list), serializes each tool the way
Inspect's Anthropic provider does (name, description, input_schema), and counts
tokens with Anthropic's count_tokens endpoint.

Token figures are deltas against the same one-message request with no tools,
so they include Anthropic's fixed tool-use system preamble once per arm.
Per-server figures are marginal: (stock tools + server) minus (stock tools).

    uv run python -m bench.tool_tokens            # writes results/tool-definition-tokens.json
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

import anthropic
from inspect_ai.tool import ToolDef, ToolSource
from inspect_ai.util._json import json_schema_dump

from bench.arms import stock_tools, tools_for
from bench.secrets import load_secrets

MODEL = "claude-sonnet-5-5"
ARMS = ("B", "C", "D")
OUT = Path(__file__).resolve().parent.parent / "results" / "tool-definition-tokens.json"
PROBE_MESSAGES = [{"role": "user", "content": "hi"}]


async def _defs(item) -> list[ToolDef]:
    if isinstance(item, ToolSource):  # MCPServer and mcp_tools(...) filters
        return [ToolDef(t) for t in await item.tools()]
    return [ToolDef(item)]


def _source_name(item) -> str:
    if isinstance(item, ToolSource):
        server = getattr(item, "_server", item)  # mcp_tools() wraps the server
        return getattr(server, "_name", None) or type(item).__name__
    return ToolDef(item).name


def _param(d: ToolDef) -> dict:
    return {"name": d.name, "description": d.description, "input_schema": json_schema_dump(d.parameters)}


async def materialize(arm: str) -> dict[str, list[dict]]:
    """{source name: [anthropic tool params]} in the order the arm sends them."""
    out: dict[str, list[dict]] = {}
    for item in tools_for(arm):
        out.setdefault(_source_name(item), []).extend(_param(d) for d in await _defs(item))
    return out


def _count(client: anthropic.Anthropic, tools: list[dict]) -> int:
    kwargs = {"model": MODEL, "messages": PROBE_MESSAGES}
    if tools:
        kwargs["tools"] = tools
    return client.messages.count_tokens(**kwargs).input_tokens


async def tool_definition_tokens_async(arm: str, client: anthropic.Anthropic | None = None) -> dict:
    client = client or anthropic.Anthropic()
    sources = await materialize(arm)
    stock_names = {_source_name(t) for t in stock_tools()}
    stock = [p for name, ps in sources.items() if name in stock_names for p in ps]
    all_tools = [p for ps in sources.values() for p in ps]
    base = _count(client, [])
    stock_tokens = _count(client, stock) - base
    servers = {}
    for name, params in sources.items():
        if name in stock_names:
            continue
        servers[name] = {
            "tool_count": len(params),
            "tools": [p["name"] for p in params],
            "json_chars": len(json.dumps(params)),
            "marginal_tokens": _count(client, stock + params) - base - stock_tokens,
        }
    return {
        "arm": arm,
        "tool_count": len(all_tools),
        "total_tokens": _count(client, all_tools) - base,
        "stock_tokens": stock_tokens,
        "stock_tools": [p["name"] for p in stock],
        "servers": servers,
    }


def tool_definition_tokens(arm: str) -> dict:
    return asyncio.run(tool_definition_tokens_async(arm))


def main() -> None:
    load_secrets()
    client = anthropic.Anthropic()

    async def run() -> dict:
        return {arm: await tool_definition_tokens_async(arm, client) for arm in ARMS}

    result = {
        "model": MODEL,
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "count_tokens(messages=[hi], tools=arm tools) minus count_tokens without tools",
        "arms": asyncio.run(run()),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    for arm, r in result["arms"].items():
        per = ", ".join(f"{k}={v['marginal_tokens']}" for k, v in r["servers"].items())
        print(f"arm {arm}: {r['tool_count']} tools, {r['total_tokens']} tokens (stock {r['stock_tokens']}; {per})")


if __name__ == "__main__":
    main()
