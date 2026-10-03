# Vendor list prices used for arm D spend estimates

Arm D calls vendors directly with our own keys, so there is no per-run bill and no cap.
`bench/vendor_costs.py` estimates each D run's spend from its trace: every vendor tool call
is priced at the vendor's published credit cost for that endpoint, times a published $/credit.
**These are estimated list-price costs, not invoices.** Our own accounts may be on different
plans or have free allowances; the estimate deliberately ignores that so a reader can
reproduce it.

Prices were read on **2026-10-03**.

## $/credit basis

Rule: the cheapest self-serve paid tier's price divided by its included credits. Where the
vendor publishes a pay-as-you-go or per-request price, that is used instead.

| Vendor | Basis | $/unit | Source |
|---|---|---|---|
| Apollo | Basic, $49/user/mo billed annually, 30,000 credits/yr. Apollo does not publish a top-up price. | $0.0196/credit | apollo.io/pricing; apollo.io/insights/more-information-on-what-they-are-paying-for-in-apollo-plan-detailsusage-walkthrough |
| Hunter | Starter, $49/mo (monthly), 2,000 credits | $0.0245/credit | hunter.io/pricing |
| Prospeo | Starter, $49/mo, 2,000 credits. Prospeo's own pricing page did not render for us; figure from third-party reviews that say they verified it in July 2026. **Lowest-confidence row.** | $0.0245/credit | emelia.io/hub/prospeo-pricing, coldiq.com/blog/prospeo-pricing |
| Firecrawl | Hobby, $16/mo billed annually, 5,000 credits | $0.0032/credit | firecrawl.dev/pricing |
| Tavily | Pay as you go | $0.008/credit | tavily.com/pricing |
| Exa | Per request | see below | exa.ai/pricing |
| E2B | Per second, default sandbox (2 vCPU, 4 GiB) | $0.000095/s | e2b.dev/pricing |

## Per-endpoint rules

| Tool (arm D name) | Charge | Source |
|---|---|---|
| `apollo_mixed_people_api_search` | 0 ("Credit usage: 0 credits") | docs.apollo.io/reference/people-api-search |
| `apollo_people_match` | 1 credit if email or demographics returned, +8 if a mobile is returned; 0 if nothing billable | docs.apollo.io/reference/people-enrichment |
| `apollo_people_bulk_match` | 1 credit per matched person | same |
| `apollo_organizations_enrich` | 1 credit per organization | docs.apollo.io/reference/organization-enrichment |
| `apollo_organizations_bulk_enrich` | 1 credit per domain | same |
| `apollo_mixed_companies_search` | 1 credit per page | docs.apollo.io/reference/organization-search |
| `apollo_organizations_lookup`, `apollo_organizations_job_postings` | **assumed** 1 credit per call (not stated) | none |
| Hunter `Find-Companies`, `Find-People`, `Email-Count` | 0 (Discover: "This call is free") | hunter.io/api-documentation/v2 |
| Hunter `Domain-Search` | 1 credit if it returns at least one result | same |
| Hunter `Email-Finder` | 1 credit if an email is found, else 0 | same |
| Hunter `Email-Verifier` | 0.5 credit | hunter.io/pricing |
| Hunter enrichment tools | 0 (pricing page: "Lead Enrichment: included with plan") | hunter.io/pricing |
| Prospeo `enrich_person` | 1 credit per verified email found, 10 with mobile; 0 on no match | prospeo.io/api-docs/enrich-person |
| Prospeo `bulk_enrich_person` | 1 credit per email found | same |
| Prospeo `search_person`, `search_company` | 1 credit per results page (25 rows) that returns results | prospeo.io/api-docs/search-person |
| Prospeo `enrich_company` | 1 credit per company | prospeo.io/api-docs |
| Firecrawl (any) | `creditsUsed` from the response when present, otherwise below | — |
| `firecrawl_scrape` | 1 credit/page, +4 with JSON format | firecrawl.dev/pricing |
| `firecrawl_map`, `firecrawl_parse` | 1 credit | same |
| `firecrawl_search` | 2 credits per 10 results | same |
| `firecrawl_crawl` / `check_crawl_status` | 1 credit per crawled page, counted at status | same |
| `firecrawl_interact` | 2 credits per browser minute (1 minute assumed) | same |
| `firecrawl_agent`, `firecrawl_research_*`, `firecrawl_find_tools`, `firecrawl_developer_search` | **unpriced** (dynamic or not published) | — |
| `tavily_search` | 1 credit basic, 2 advanced | docs.tavily.com/documentation/api-credits |
| `tavily_extract` | 1 credit per 5 URLs (2 advanced) | same |
| `tavily_map`, `tavily_crawl` | map 1 credit/10 pages; crawl = map + extract, pages counted from the result | same |
| `tavily_research` | **lower bound** 4 credits (4 to 250 by model) | same |
| `web_search_exa` | $7/1k searches + $1/1k results above 10 + $1/1k content pages (default 8 results) | exa.ai/pricing |
| `web_fetch_exa` | $1/1k pages | same |
| `e2b_run_code` | 30 s assumed per call x $0.000095/s (one fresh sandbox per call) | e2b.dev/pricing |

Calls that fail with a tool error are counted at 0. Calls with no published price are listed
in the estimate's `unpriced` field and add 0, and the estimate is flagged `is_lower_bound`.
