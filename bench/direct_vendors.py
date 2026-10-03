"""Arm D: stock agent + vendors wired directly, with each vendor's own key.

Each vendor is mounted the way a developer would do it today: the vendor's own
MCP server where the vendor publishes and maintains one, otherwise a thin
wrapper over the vendor's official SDK. Choices, versions and exposed tools are
documented in docs/arm-d-vendors.md.

Keys are read from os.environ (populate it with bench.secrets.load_secrets()).
They are passed to stdio servers via the child env and to hosted servers via
request headers only; nothing is written to disk.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from inspect_ai.tool import Tool, ToolError, mcp_server_http, mcp_server_stdio, mcp_tools, tool

ROOT = Path(__file__).resolve().parent.parent
NODE_BIN = ROOT / "harnesses" / "node" / "node_modules" / ".bin"

MCP_TIMEOUT_S = 120

# Some vendor MCPs expose account-mutating tools (CRM writes, sequences, email
# sends, lead lists, recurring monitors). The benchmark only needs lookups, so
# those servers are filtered to their read-only search / enrichment /
# verification / retrieval tools. Names come from each server's tools/list
# (2026-10-03); see docs/arm-d-vendors.md for what was left out.
APOLLO_READ_TOOLS = [
    "apollo_mixed_people_api_search",
    "apollo_mixed_companies_search",
    "apollo_organizations_lookup",
    "apollo_organizations_enrich",
    "apollo_organizations_bulk_enrich",
    "apollo_organizations_job_postings",
    "apollo_people_match",
    "apollo_people_bulk_match",
    "apollo_webhook_result_show",
]
HUNTER_READ_TOOLS = [
    "Find-Companies",
    "Find-People",
    "Domain-Search",
    "Domain-Search-Found",
    "Email-Finder",
    "Email-Verifier",
    "Email-Count",
    "Person-Enrichment",
    "Company-Enrichment",
    "Combined-Enrichment",
]
FIRECRAWL_TOOLS = [
    "firecrawl_scrape",
    "firecrawl_map",
    "firecrawl_search",
    "firecrawl_crawl",
    "firecrawl_check_crawl_status",
    "firecrawl_agent",
    "firecrawl_agent_status",
    "firecrawl_interact",
    "firecrawl_interact_stop",
    "firecrawl_parse",
    "firecrawl_find_tools",
    "firecrawl_research_search_papers",
    "firecrawl_research_inspect_paper",
    "firecrawl_research_related_papers",
    "firecrawl_research_read_paper",
    "firecrawl_developer_search",
]

E2B_TIMEOUT_S = 120
E2B_MAX_OUTPUT_CHARS = 20_000


def _key(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set; call bench.secrets.load_secrets() first")
    return value


def _stdio(name: str, binary: str, env: dict[str, str]):
    return mcp_server_stdio(name=name, command=str(NODE_BIN / binary), args=[], env=env)


# --- official vendor MCP servers -------------------------------------------------


def firecrawl_server(read_only: bool = True):
    # firecrawl-mcp (github.com/firecrawl/firecrawl-mcp-server), pinned in harnesses/node.
    # read_only drops monitor CRUD (recurring billed jobs) and feedback/credit tools.
    server = _stdio("firecrawl", "firecrawl-mcp", {"FIRECRAWL_API_KEY": _key("FIRECRAWL_API_KEY")})
    return mcp_tools(server, tools=FIRECRAWL_TOOLS) if read_only else server


def exa_server():
    # exa-mcp-server (github.com/exa-labs/exa-mcp-server), default tool set.
    return _stdio("exa", "exa-mcp-server", {"EXA_API_KEY": _key("EXA_API_KEY")})


def tavily_server():
    # tavily-mcp (github.com/tavily-ai/tavily-mcp).
    return _stdio("tavily", "tavily-mcp", {"TAVILY_API_KEY": _key("TAVILY_API_KEY")})


def prospeo_server():
    # @prospeo/prospeo-mcp-server (github.com/prospeo-v2/prospeo-mcp-server).
    return _stdio("prospeo", "prospeo-mcp-server", {"PROSPEO_API_KEY": _key("PROSPEO_API_KEY")})


def apollo_server(read_only: bool = True):
    # Apollo's hosted MCP; headless clients authenticate with a master key in X-Api-Key.
    server = mcp_server_http(
        name="apollo",
        url="https://mcp.apollo.io/mcp",
        headers={"X-Api-Key": _key("APOLLO_API_KEY")},
        timeout=MCP_TIMEOUT_S,
    )
    return mcp_tools(server, tools=APOLLO_READ_TOOLS) if read_only else server


def hunter_server(read_only: bool = True):
    # Hunter's hosted MCP (the stdio hunter-io/hunter-mcp repo is archived); key in X-API-Key.
    server = mcp_server_http(
        name="hunter",
        url="https://mcp.hunter.io/mcp",
        headers={"X-API-Key": _key("HUNTER_API_KEY")},
        timeout=MCP_TIMEOUT_S,
    )
    return mcp_tools(server, tools=HUNTER_READ_TOOLS) if read_only else server


# --- SDK wrapper (no maintained vendor MCP) -------------------------------------


@tool
def e2b_run_code() -> Tool:
    async def execute(code: str, language: str = "python") -> str:
        """Run code in a fresh, isolated E2B cloud sandbox and return its output.

        Each call starts a new sandbox, so variables and files do not persist
        between calls. Python runs in a Jupyter-style kernel (the value of the
        last expression is returned). The sandbox has internet access and
        common data packages preinstalled; use `!pip install x` for others.

        Args:
            code: The code to execute.
            language: "python" (default), "javascript", "r", "java" or "bash".
        """
        from e2b_code_interpreter import AsyncSandbox

        sandbox = await AsyncSandbox.create(api_key=_key("E2B_API_KEY"), timeout=E2B_TIMEOUT_S + 60)
        try:
            execution = await sandbox.run_code(
                code, language=None if language == "python" else language, timeout=E2B_TIMEOUT_S
            )
        except Exception as e:
            raise ToolError(f"E2B sandbox error: {e}") from e
        finally:
            await sandbox.kill()
        out = {
            "stdout": "".join(execution.logs.stdout),
            "stderr": "".join(execution.logs.stderr),
            "results": [r.text for r in execution.results if r.text is not None],
            "error": None
            if execution.error is None
            else f"{execution.error.name}: {execution.error.value}\n{execution.error.traceback}",
        }
        return json.dumps(out)[:E2B_MAX_OUTPUT_CHARS]

    return execute


# server name -> factory; tool_tokens.py iterates this to count per server.
VENDOR_SOURCES = {
    "apollo": apollo_server,
    "hunter": hunter_server,
    "prospeo": prospeo_server,
    "firecrawl": firecrawl_server,
    "exa": exa_server,
    "tavily": tavily_server,
    "e2b": e2b_run_code,
}


def direct_vendor_tools() -> list:
    return [factory() for factory in VENDOR_SOURCES.values()]
