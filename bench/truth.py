"""Live truth capture for NumberGrader / SetGrader tasks.

Each grader's `capture` field names a function in this module; the grader calls it with
`capture_args` as keyword arguments within 10 minutes of the run and compares the answer to
the returned value. Every function reads a free, keyless source of record (the publisher of
the data, not an aggregator), so the truth never depends on any arm's tools.

Numbers come back as float. Sets come back as list[str].
"""

import os
import statistics
import xml.etree.ElementTree as ET
from datetime import UTC, date, datetime, timedelta
from urllib.parse import quote

import httpx

TIMEOUT = 30.0
UA = "agent-access-bench/0.1 truth-capture (public research benchmark)"
# SEC asks automated clients to identify themselves with a contact in the User-Agent.
SEC_UA = os.environ.get("SEC_USER_AGENT", UA)


def _get(url: str, *, ua: str = UA, params: dict | None = None) -> httpx.Response:
    r = httpx.get(
        url,
        params=params,
        headers={"User-Agent": ua, "Accept": "application/json, */*"},
        timeout=TIMEOUT,
        follow_redirects=True,
    )
    r.raise_for_status()
    return r


# --- FX: European Central Bank ------------------------------------------------------------


def ecb_reference_rate(*, quote_ccy: str) -> float:
    """Latest ECB euro foreign exchange reference rate: units of quote_ccy per 1 EUR."""
    root = ET.fromstring(_get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml").text)
    for cube in root.iter():
        if cube.attrib.get("currency") == quote_ccy:
            return float(cube.attrib["rate"])
    raise LookupError(f"ECB has no reference rate for {quote_ccy}")


# --- SEC EDGAR -----------------------------------------------------------------------------


def sec_recent_filing_dates(*, cik: int, form: str, n: int) -> list[str]:
    """Filing dates (YYYY-MM-DD) of the n most recent filings of exactly this form type."""
    j = _get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", ua=SEC_UA).json()
    recent = j["filings"]["recent"]
    dates = [d for f, d in zip(recent["form"], recent["filingDate"], strict=True) if f == form]
    return dates[:n]


def sec_latest_shares_outstanding(*, cik: int) -> float:
    """dei:EntityCommonStockSharesOutstanding from the most recently filed 10-K or 10-Q cover."""
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/dei/EntityCommonStockSharesOutstanding.json"
    facts = _get(url, ua=SEC_UA).json()["units"]["shares"]
    facts = [f for f in facts if f.get("form") in ("10-K", "10-Q")]
    latest = max(facts, key=lambda f: (f["filed"], f["end"]))
    return float(latest["val"])


# --- US Treasury ---------------------------------------------------------------------------


def treasury_total_public_debt() -> float:
    """Total public debt outstanding (USD) on the latest Debt to the Penny record date."""
    r = _get(
        "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny",
        params={"sort": "-record_date", "page[size]": "1"},
    )
    return float(r.json()["data"][0]["tot_pub_debt_out_amt"])


# --- GitHub --------------------------------------------------------------------------------


def github_open_issue_count(*, repo: str, label: str) -> float:
    """Open issues (not PRs) in repo carrying the label, per GitHub's issue search."""
    q = f'repo:{repo} is:issue is:open label:"{label}"'
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if tok := os.environ.get("GITHUB_TOKEN"):  # optional, only raises the rate limit
        headers["Authorization"] = f"Bearer {tok}"
    r = httpx.get(
        "https://api.github.com/search/issues",
        params={"q": q, "per_page": 1},
        headers=headers,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return float(r.json()["total_count"])


# --- Package registries --------------------------------------------------------------------


def npm_last_week_downloads(*, package: str) -> float:
    """npm's own 'last-week' download count (7 days ending on the latest complete day)."""
    return float(_get(f"https://api.npmjs.org/downloads/point/last-week/{package}").json()["downloads"])


def pypi_latest_version(*, package: str) -> list[str]:
    """Latest release on PyPI (info.version, which skips pre-releases and yanked files)."""
    return [_get(f"https://pypi.org/pypi/{package}/json").json()["info"]["version"]]


# --- USGS ----------------------------------------------------------------------------------


def usgs_quake_count_past_week(*, min_mag: str = "4.5") -> float:
    """Count of events in USGS's real-time 'past week' summary feed at the given magnitude tier."""
    url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{min_mag}_week.geojson"
    return float(_get(url).json()["metadata"]["count"])


# --- Wikimedia -----------------------------------------------------------------------------


def wikipedia_monthly_pageviews(*, article: str, month: str, project: str = "en.wikipedia") -> float:
    """Human ('user' agent), all-access pageviews for one calendar month (YYYY-MM)."""
    start = date.fromisoformat(f"{month}-01")
    end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    url = (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"{project}/all-access/user/{quote(article, safe='')}/monthly/"
        f"{start:%Y%m%d}00/{end:%Y%m%d}00"
    )
    items = _get(url).json()["items"]
    return float(sum(i["views"] for i in items))


# --- Coinbase Exchange (public market data) -----------------------------------------------


def coinbase_avg_daily_volume(*, product: str, days: int = 30) -> float:
    """Mean base-currency volume over the last `days` complete UTC daily candles."""
    candles = _get(
        f"https://api.exchange.coinbase.com/products/{product}/candles", params={"granularity": 86400}
    ).json()
    today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    complete = sorted((c for c in candles if c[0] < today), key=lambda c: c[0], reverse=True)[:days]
    if len(complete) < days:
        raise LookupError(f"only {len(complete)} complete daily candles returned")
    return float(statistics.fmean(c[5] for c in complete))


# --- NOAA / National Weather Service ------------------------------------------------------


def nws_latest_temp_f(*, station: str) -> float:
    """Most recent non-null air temperature (deg F) observed at an NWS/FAA station."""
    obs = _get(
        f"https://api.weather.gov/stations/{station}/observations", params={"limit": 6}
    ).json()["features"]
    for o in obs:  # newest first; the newest report sometimes has a null temperature
        c = o["properties"]["temperature"]["value"]
        if c is not None:
            return round(c * 9 / 5 + 32, 1)
    raise LookupError(f"no recent temperature at {station}")


# --- Retail (Shopify storefront product JSON, served by the retailer itself) -------------


def shopify_in_stock_variants(*, store: str, handle: str) -> list[str]:
    """Titles of variants (e.g. sizes) the retailer's own storefront marks available."""
    j = _get(f"https://{store}/products/{handle}.js").json()
    return [v["title"] for v in j["variants"] if v["available"]]


# --- Social (Bluesky public AppView) ------------------------------------------------------


def bluesky_follower_count(*, handle: str) -> float:
    r = _get("https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile", params={"actor": handle})
    return float(r.json()["followersCount"])


# --- Steam ---------------------------------------------------------------------------------


def steam_current_players(*, appid: int) -> float:
    r = _get(
        "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/",
        params={"appid": appid},
    )
    return float(r.json()["response"]["player_count"])


def steam_price_usd(*, appid: int) -> float:
    """Current US store price in dollars, after any active discount."""
    r = _get(
        "https://store.steampowered.com/api/appdetails",
        params={"appids": appid, "cc": "us", "filters": "price_overview"},
    )
    data = r.json()[str(appid)]["data"]
    return data["price_overview"]["final"] / 100 if data else 0.0

from bench.truth_paid import *  # noqa: F401,F403
