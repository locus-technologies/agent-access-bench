# Arm D: vendors wired directly

Arm D is the stock agent (arm B tools) plus seven vendors, each called with the
vendor's own key, wired the way a developer would do it today. Code:
`bench/direct_vendors.py` (`direct_vendor_tools()`), mounted by
`bench/arms.py::tools_for("D")`. Decisions were checked against vendor docs,
GitHub and npm on 2026-10-03.

Rule: use the vendor's own MCP server when the vendor publishes and maintains
one. Otherwise, write a thin wrapper over the vendor's official SDK.

## Choices

| Vendor | Wiring | Package / endpoint | Auth | Tools exposed to the model |
|---|---|---|---|---|
| Apollo | Official hosted MCP | `https://mcp.apollo.io/mcp` (streamable HTTP) | `X-Api-Key` header (master key; the documented headless option) | 9 of 85: `apollo_mixed_people_api_search`, `apollo_mixed_companies_search`, `apollo_organizations_lookup`, `apollo_organizations_enrich`, `apollo_organizations_bulk_enrich`, `apollo_organizations_job_postings`, `apollo_people_match`, `apollo_people_bulk_match`, `apollo_webhook_result_show` |
| Hunter | Official hosted MCP | `https://mcp.hunter.io/mcp` (streamable HTTP) | `X-API-Key` header | 10 of 102: `Find-Companies`, `Find-People`, `Domain-Search`, `Domain-Search-Found`, `Email-Finder`, `Email-Verifier`, `Email-Count`, `Person-Enrichment`, `Company-Enrichment`, `Combined-Enrichment` |
| Prospeo | Official MCP, stdio | `@prospeo/prospeo-mcp-server@1.1.0` (github.com/prospeo-v2/prospeo-mcp-server) | `PROSPEO_API_KEY` in child env | all 8: `search_suggestions`, `enrich_person`, `bulk_enrich_person`, `enrich_company`, `bulk_enrich_company`, `search_person`, `search_company`, `get_account_info` |
| Firecrawl | Official MCP, stdio | `firecrawl-mcp@3.27.3` (github.com/firecrawl/firecrawl-mcp-server) | `FIRECRAWL_API_KEY` in child env | 16 of 27: scrape, map, search, crawl, check_crawl_status, agent, agent_status, interact, interact_stop, parse, find_tools, research_search_papers, research_inspect_paper, research_related_papers, research_read_paper, developer_search (all `firecrawl_` prefixed) |
| Exa | Official MCP, stdio | `exa-mcp-server@3.4.1` (github.com/exa-labs/exa-mcp-server), default tool set | `EXA_API_KEY` in child env | 2: `web_search_exa`, `web_fetch_exa` |
| Tavily | Official MCP, stdio | `tavily-mcp@0.2.22` (github.com/tavily-ai/tavily-mcp) | `TAVILY_API_KEY` in child env | all 5: `tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map`, `tavily_research` |
| E2B | SDK wrapper (`@tool`) | `e2b-code-interpreter==2.10.1` (Python) | `E2B_API_KEY` | 1: `e2b_run_code(code, language="python")` |

npm packages are pinned exact in `harnesses/node/package.json` and run from
`harnesses/node/node_modules/.bin`. Nothing is installed globally. Keys go only
into the child process env or request headers. Nothing is written to disk.

### Notes on each choice

- **Apollo.** The hosted MCP is Apollo's official server. It supports OAuth for
  interactive clients and an `X-Api-Key` master key for headless clients.
  `apollo-mcp` on npm is a third-party package and was not used.
- **Hunter.** The stdio repo `hunter-io/hunter-mcp` was archived in July 2025
  and points to the hosted server, so the hosted server is the one in use.
- **Prospeo.** Prospeo also hosts the same server at `https://mcp.prospeo.io`.
  The pinned npm build was chosen so runs are reproducible.
- **Firecrawl, Exa, Tavily.** Each vendor also hosts a remote copy of its MCP.
  The pinned npm build was chosen for the same reason. Exa runs with its
  default tool set (search + fetch). Its docs say extra tools are opt-in.
- **E2B.** `@e2b/mcp-server` (github.com/e2b-dev/mcp-server) is archived and
  marked no longer maintained. E2B's current "MCP" docs cover running MCP
  servers inside sandboxes, not a code-execution MCP for agents. So arm D uses
  a thin wrapper with the same shape as the archived server's one tool
  (`run_code`): a fresh sandbox per call. Two small differences: the wrapper
  kills the sandbox after each call (the archived server leaked it until
  timeout), and it takes an optional `language`. Limits: 120 s per call,
  20,000 output characters.

### Read-only filtering (deviation from "mount everything")

The Apollo, Hunter and Firecrawl servers include tools that change the account
or keep spending money. Examples: CRM create/update, sequences,
`apollo_emailer_messages_send_now`, mailbox purchase, Hunter lead and list
CRUD, `Start-Sequence`, API-key creation, and Firecrawl recurring monitors.
The benchmark tasks only need lookups. A benchmark agent should never send
email or start billed recurring jobs. So these three servers are mounted with
`inspect_ai.tool.mcp_tools(server, tools=[...])`, which keeps only the
read-only search, enrichment, verification and retrieval tools listed above.
Firecrawl also drops `firecrawl_feedback`, `firecrawl_search_feedback` and
`firecrawl_credit_usage`. The tool descriptions are the vendors' own,
unchanged. Each factory takes `read_only=False` to get the full server.

## Tool-definition cost

`bench/tool_tokens.py` builds each arm's exact tool list (MCP servers are
listed live via `tools/list`). It serializes each tool the way Inspect's
Anthropic provider does and counts tokens with `count_tokens`
(`claude-sonnet-5-5`). Full output: `results/tool-definition-tokens.json`.

| Arm | Tools | Tool-definition tokens per request |
|---|---|---|
| B | 3 | 760 |
| C (B + Locus Pro) | 18 | 6,914 (Locus Pro: 15 tools, 6,154) |
| D (B + vendors) | 54 | 79,645 |

Arm D per server (tokens added on top of the stock tools): Apollo 31,501 (9
tools), Prospeo 20,925 (8), Firecrawl 16,984 (16), Hunter 5,714 (10), Tavily
2,860 (5), Exa 634 (2), E2B 267 (1). Most of Apollo's cost is in the schemas
of its two search tools.

## Auth check (2026-10-03)

This was one cheap call per vendor through the arm D tools, to confirm the key
and the wiring work. Pass means the call succeeded and the expected non-personal
marker appeared in the output. No response contents were kept. Total spend was
a few vendor credits.

| Vendor | Call | Result |
|---|---|---|
| Apollo | `apollo_organizations_enrich(domain="stripe.com")` | pass |
| Hunter | `Domain-Search(domain="stripe.com", limit=1)` | pass |
| Prospeo | `enrich_company(company_website="stripe.com")` | pass |
| Firecrawl | `firecrawl_scrape(url="https://example.com")` | pass |
| Exa | `web_search_exa(query=..., numResults=1)` | pass |
| Tavily | `tavily_search(query=..., max_results=1)` | pass |
| E2B | `e2b_run_code(code="print(1+1)")` | pass |

This only shows that auth and wiring work. It says nothing about answer quality
on the benchmark tasks.

One thing to watch: `apollo_organizations_enrich` on stripe.com returned about
58k characters. Large vendor outputs will raise arm D's context use beyond the
cost of the tool definitions.
