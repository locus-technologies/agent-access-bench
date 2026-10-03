"""Tool sets for each arm. Only the tools differ between arms."""

import asyncio
import os
import re

import httpx
from inspect_ai.tool import Tool, mcp_server_http, python, tool

SYSTEM_PROMPT = (
    "You are a capable assistant completing a task for a user. Use the tools available to you "
    "when they help. When you are done, give your final answer clearly. If you cannot complete "
    "the task, say so plainly instead of guessing."
)

FETCH_MAX_CHARS = 20_000

# The stock search uses a dedicated benchmark key (1,000 req/min). Cap concurrency for the whole
# process (all arms and models run in one process) and back off on 429.
SEARCH_CONCURRENCY = 8
_search_gate = asyncio.Semaphore(SEARCH_CONCURRENCY)


@tool
def web_search() -> Tool:
    async def execute(query: str) -> str:
        """Search the web. Returns the top results with titles, URLs and snippets.

        Args:
            query: The search query.
        """
        async with _search_gate:
            for attempt in range(5):
                async with httpx.AsyncClient(timeout=60) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={"query": query, "max_results": 8},
                        headers={"Authorization": "Bearer " + os.environ["TAVILY_API_KEY"]},
                    )
                if resp.status_code != 429:
                    break
                await asyncio.sleep(5 * 2**attempt)
        if resp.status_code != 200:
            return f"Search failed (HTTP {resp.status_code}). Try again later or another approach."
        results = resp.json().get("results", [])
        return "\n\n".join(f"{r.get('title')}\n{r.get('url')}\n{r.get('content', '')[:500]}" for r in results) or "No results."

    return execute


@tool
def web_fetch() -> Tool:
    async def execute(url: str) -> str:
        """Fetch a URL and return its text content (HTML tags stripped, truncated).

        Args:
            url: The absolute http(s) URL to fetch.
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                resp = await client.get(url, headers={"user-agent": "Mozilla/5.0 agent-access-bench"})
        except httpx.HTTPError as e:
            return f"Fetch failed: {type(e).__name__}"
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", resp.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return f"HTTP {resp.status_code}\n{text[:FETCH_MAX_CHARS]}"

    return execute


def stock_tools() -> list:
    # One fixed search provider for every model, called directly (never through Locus).
    return [web_search(), web_fetch(), python(timeout=120)]


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
