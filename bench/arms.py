"""Tool sets for each arm. Only the tools differ between arms."""

import os
import re

import httpx
from inspect_ai.tool import Tool, mcp_server_http, python, tool, web_search

SYSTEM_PROMPT = (
    "You are a capable assistant completing a task for a user. Use the tools available to you "
    "when they help. When you are done, give your final answer clearly. If you cannot complete "
    "the task, say so plainly instead of guessing."
)

FETCH_MAX_CHARS = 20_000


@tool
def web_fetch() -> Tool:
    async def execute(url: str) -> str:
        """Fetch a URL and return its text content (HTML tags stripped, truncated).

        Args:
            url: The absolute http(s) URL to fetch.
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(url, headers={"user-agent": "Mozilla/5.0 agent-access-bench"})
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", resp.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return f"HTTP {resp.status_code}\n{text[:FETCH_MAX_CHARS]}"

    return execute


def stock_tools() -> list:
    # One fixed search provider for every model, called directly (never through Locus).
    return [web_search(["tavily"]), web_fetch(), python(timeout=120)]


def locus_server():
    return mcp_server_http(
        name="locus-pro",
        url=os.environ["LOCUS_PRO_MCP_URL"],
        headers={"Authorization": "Bearer " + os.environ["LOCUS_PRO_API_KEY"]},
        timeout=120,
    )


def tools_for(arm: str) -> list:
    if arm == "A":
        return []
    if arm == "B":
        return stock_tools()
    if arm == "C":
        return stock_tools() + [locus_server()]
    if arm == "D":
        from bench.direct_vendors import direct_vendor_tools

        return stock_tools() + direct_vendor_tools()
    raise ValueError(f"unknown arm {arm}")
