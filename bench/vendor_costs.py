"""ESTIMATED arm-D spend at vendor public list prices.

Arm D has no spend cap and no single bill, so its spend is estimated from the trace: each
vendor tool call is priced with the vendor's published credit cost for that endpoint times a
published $/credit. Prices, sources and the date they were read are in docs/vendor-pricing.md.
These are list-price estimates, not invoices: label them that way wherever they are shown.

Rules follow each vendor's own billing rules where the docs state them (for example Hunter
and Prospeo charge nothing when nothing is found; Apollo people search is free). Calls whose
price the vendor does not publish are listed under `unpriced` and contribute 0, so the total
is a lower bound whenever `unpriced` is non-empty.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import Callable

PRICES_READ_ON = "2026-10-03"

# $ per credit (or per unit), cheapest self-serve paid tier, see docs/vendor-pricing.md.
USD_PER_CREDIT = {
    "apollo": 49 * 12 / 30_000,  # Basic, $49/user/mo billed annually, 30,000 credits/yr
    "hunter": 49 / 2_000,  # Starter, $49/mo, 2,000 credits
    "prospeo": 49 / 2_000,  # Starter, $49/mo, 2,000 credits
    "firecrawl": 16 / 5_000,  # Hobby, $16/mo billed annually, 5,000 credits
    "tavily": 0.008,  # pay as you go
}
EXA_SEARCH_USD = 7 / 1000  # auto/fast search, up to 10 results
EXA_EXTRA_RESULT_USD = 1 / 1000  # each result above 10
EXA_CONTENT_PAGE_USD = 1 / 1000  # per page, per content type
EXA_DEFAULT_RESULTS = 8  # exa-mcp-server web_search_exa default numResults
E2B_USD_PER_SECOND = 0.000095  # default 2 vCPU / 4 GiB sandbox
E2B_ASSUMED_SECONDS = 30  # sandbox lifetime per call (create + run + kill); see docs

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+'-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+")


@dataclass
class Priced:
    vendor: str
    credits: float  # vendor units (credits, or $ for Exa/E2B where vendor == unit)
    usd: float
    rule: str


def _emails(text: str) -> int:
    return len(set(EMAIL_RE.findall(text)))


def _json(text: str):
    try:
        return json.loads(text)
    except ValueError:
        return None


def _credits_used(text: str) -> float | None:
    """Firecrawl responses often report the real credits charged; prefer them."""
    m = re.search(r'"creditsUsed"\s*:\s*(\d+(?:\.\d+)?)', text)
    return float(m.group(1)) if m else None


def _credit(vendor: str, credits: float, rule: str) -> Priced:
    return Priced(vendor, credits, credits * USD_PER_CREDIT[vendor], rule)


def _apollo(fn: str, args: dict, out: str) -> Priced | None:
    if fn in ("apollo_mixed_people_api_search", "apollo_webhook_result_show"):
        return _credit("apollo", 0, "free endpoint")
    if fn == "apollo_people_match":
        c = (1 if (_emails(out) or '"name"' in out) else 0) + (8 if args.get("reveal_phone_number") and "sanitized_number" in out else 0)
        return _credit("apollo", c, "1 credit if email/demographics returned, +8 if mobile")
    if fn == "apollo_people_bulk_match":
        data = _json(out) or {}
        n = len([m for m in data.get("matches", []) if m]) if isinstance(data, dict) else len(args.get("details", []))
        return _credit("apollo", n, "1 credit per matched person")
    if fn == "apollo_organizations_enrich":
        return _credit("apollo", 1, "1 credit per organization")
    if fn == "apollo_organizations_lookup":
        return _credit("apollo", 1, "ASSUMED 1 credit per call (not stated in docs)")
    if fn == "apollo_organizations_bulk_enrich":
        return _credit("apollo", len(args.get("domains", [])) or 1, "1 credit per organization")
    if fn == "apollo_mixed_companies_search":
        return _credit("apollo", 1, "1 credit per page")
    if fn == "apollo_organizations_job_postings":
        return _credit("apollo", 1, "ASSUMED 1 credit per call (not stated in docs)")
    return None


def _hunter(fn: str, args: dict, out: str) -> Priced | None:
    if fn in ("Find-Companies", "Find-People", "Email-Count"):
        return _credit("hunter", 0, "free (Discover / count)")
    if fn in ("Person-Enrichment", "Company-Enrichment", "Combined-Enrichment"):
        return _credit("hunter", 0, "included in plan per pricing page")
    if fn in ("Domain-Search", "Domain-Search-Found"):
        return _credit("hunter", 1 if _emails(out) else 0, "1 credit per search returning results")
    if fn == "Email-Finder":
        return _credit("hunter", 1 if _emails(out) else 0, "1 credit if an email is found")
    if fn == "Email-Verifier":
        return _credit("hunter", 0.5, "0.5 credit per verification")
    return None


def _prospeo(fn: str, args: dict, out: str) -> Priced | None:
    if fn in ("search_suggestions", "get_account_info"):
        return _credit("prospeo", 0, "free")
    if fn == "enrich_person":
        mobile = bool(args.get("enrich_mobile")) and "mobile" in out.lower() and "+" in out
        return _credit("prospeo", (10 if mobile else 1) if _emails(out) else 0, "1 credit per email found, 10 with mobile")
    if fn == "bulk_enrich_person":
        return _credit("prospeo", _emails(out), "1 credit per email found")
    if fn in ("search_person", "search_company"):
        found = "NO_RESULTS" not in out and '"error": true' not in out.lower()
        return _credit("prospeo", 1 if found else 0, "1 credit per results page")
    if fn in ("enrich_company", "bulk_enrich_company"):
        n = len(args.get("data", [])) if fn == "bulk_enrich_company" else 1
        return _credit("prospeo", n, "1 credit per company")
    return None


def _firecrawl(fn: str, args: dict, out: str) -> Priced | None:
    used = _credits_used(out)
    if used is not None:
        return _credit("firecrawl", used, "creditsUsed reported by Firecrawl")
    formats = json.dumps(args.get("formats", ""))
    if fn == "firecrawl_scrape":
        return _credit("firecrawl", 1 + (4 if "json" in formats else 0), "1 credit/page, +4 for JSON format")
    if fn in ("firecrawl_map", "firecrawl_parse"):
        return _credit("firecrawl", 1, "1 credit per call/page")
    if fn == "firecrawl_search":
        return _credit("firecrawl", 2 * math.ceil(int(args.get("limit", 5)) / 10), "2 credits per 10 results")
    if fn == "firecrawl_crawl":
        return _credit("firecrawl", 0, "billed per page at check_crawl_status")
    if fn == "firecrawl_check_crawl_status":
        data = _json(out) or {}
        pages = data.get("completed") or len(data.get("data", []) or []) if isinstance(data, dict) else 0
        return _credit("firecrawl", pages, "1 credit per crawled page")
    if fn == "firecrawl_interact":
        return _credit("firecrawl", 2, "2 credits per browser minute (1 minute assumed)")
    if fn in ("firecrawl_agent_status", "firecrawl_interact_stop"):
        return _credit("firecrawl", 0, "status call")
    return None  # agent, research_*, find_tools, developer_search: no published price


def _tavily(fn: str, args: dict, out: str) -> Priced | None:
    advanced = args.get("search_depth") == "advanced" or args.get("extract_depth") == "advanced"
    if fn == "tavily_search":
        return _credit("tavily", 2 if advanced else 1, "1 credit basic / 2 advanced")
    if fn == "tavily_extract":
        n = len(args.get("urls", [])) or 1
        return _credit("tavily", math.ceil(n / 5) * (2 if advanced else 1), "1 credit per 5 URLs (2 advanced)")
    if fn in ("tavily_map", "tavily_crawl"):
        pages = len(set(re.findall(r"https?://[^\s\"'<>]+", out))) or 1
        c = math.ceil(pages / 10) + (math.ceil(pages / 5) if fn == "tavily_crawl" else 0)
        return _credit("tavily", c, "map 1 credit/10 pages; crawl = map + extract")
    if fn == "tavily_research":
        return _credit("tavily", 4, "LOWER BOUND: research is 4-250 credits by model")
    return None


def _exa(fn: str, args: dict, out: str) -> Priced | None:
    if fn == "web_search_exa":
        n = int(args.get("numResults", EXA_DEFAULT_RESULTS))
        usd = EXA_SEARCH_USD + max(0, n - 10) * EXA_EXTRA_RESULT_USD + n * EXA_CONTENT_PAGE_USD
        return Priced("exa", usd, usd, "$7/1k searches + $1/1k extra results + $1/1k content pages")
    if fn == "web_fetch_exa":
        n = len(args.get("urls", [])) or 1
        return Priced("exa", n * EXA_CONTENT_PAGE_USD, n * EXA_CONTENT_PAGE_USD, "$1/1k content pages")
    return None


def _e2b(fn: str, args: dict, out: str) -> Priced | None:
    if fn == "e2b_run_code":
        usd = E2B_USD_PER_SECOND * E2B_ASSUMED_SECONDS
        return Priced("e2b", usd, usd, f"{E2B_ASSUMED_SECONDS}s assumed x $0.000095/s")
    return None


RULES: list[Callable[[str, dict, str], Priced | None]] = [_apollo, _hunter, _prospeo, _firecrawl, _tavily, _exa, _e2b]
# Tool names that belong to a vendor, so an unknown vendor tool is reported, never dropped.
VENDOR_PREFIXES = ("apollo_", "firecrawl_", "tavily_")
VENDOR_NAMES = {
    "Find-Companies", "Find-People", "Domain-Search", "Domain-Search-Found", "Email-Finder", "Email-Verifier",
    "Email-Count", "Person-Enrichment", "Company-Enrichment", "Combined-Enrichment", "search_suggestions",
    "enrich_person", "bulk_enrich_person", "enrich_company", "bulk_enrich_company", "search_person",
    "search_company", "get_account_info", "web_search_exa", "web_fetch_exa", "e2b_run_code",
}


def price_call(fn: str, args: dict, out: str) -> Priced | None:
    for rule in RULES:
        p = rule(fn, args, out)
        if p is not None:
            return p
    return None


def _text(msg) -> str:
    c = msg.content
    if isinstance(c, list):
        return "\n".join(getattr(x, "text", "") or "" for x in c)
    return str(c or "")


def estimate_trace_cost(messages) -> dict:
    """Estimated list-price cost of every vendor tool call in an Inspect message list."""
    results = {m.tool_call_id: _text(m) for m in messages if m.role == "tool"}
    errors = {m.tool_call_id for m in messages if m.role == "tool" and getattr(m, "error", None)}
    lines, unpriced = [], []
    for m in messages:
        if m.role != "assistant":
            continue
        for tc in m.tool_calls or []:
            fn = tc.function
            if not (fn.startswith(VENDOR_PREFIXES) or fn in VENDOR_NAMES):
                continue  # stock tools (web_search, web_fetch, python) are not vendor spend
            out = results.get(tc.id, "")
            if tc.id in errors:
                lines.append({"tool": fn, "vendor": None, "credits": 0, "usd": 0.0, "rule": "tool error: not billed"})
                continue
            p = price_call(fn, tc.arguments or {}, out)
            if p is None:
                unpriced.append(fn)
                continue
            lines.append({"tool": fn, "vendor": p.vendor, "credits": p.credits, "usd": round(p.usd, 6), "rule": p.rule})
    by_vendor: dict[str, float] = {}
    for ln in lines:
        if ln["vendor"]:
            by_vendor[ln["vendor"]] = round(by_vendor.get(ln["vendor"], 0) + ln["usd"], 6)
    return {
        "label": f"ESTIMATED list-price cost (prices read {PRICES_READ_ON}); not an invoice",
        "total_usd": round(sum(ln["usd"] for ln in lines), 6),
        "by_vendor": by_vendor,
        "calls": len(lines) + len(unpriced),
        "unpriced": unpriced,
        "is_lower_bound": bool(unpriced) or any("LOWER BOUND" in ln["rule"] for ln in lines),
        "lines": lines,
    }
