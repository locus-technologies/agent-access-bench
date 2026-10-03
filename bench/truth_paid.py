"""Truth capture for the paiddata battery (Google Ads keyword volume, Google Maps, Amazon, X).

These sources have no free, keyless source of record that a grader can read reliably: Google
and Amazon bot-block plain HTTP clients, Google Maps renders in JavaScript, and X hides exact
counts from logged-out viewers. So truth comes from grader-only paid keys that are never given
to any agent arm:

- DATAFORSEO_CREDENTIALS ("login:password", HTTP Basic) for Google Ads keyword volume, Google
  Maps SERP, and Amazon product pages.
- X_API_BEARER_TOKEN (app-only bearer) for X API v2.

Both are loaded by `bench.secrets.load_secrets()`. bench/truth.py re-exports this module, so
grader `capture` names resolve via `getattr(bench.truth, name)` as for every other capture.

Numbers come back as float. Sets come back as list[str].

Google organic ranking ("which domains rank top 3") was tried and dropped: on 2026-10-03,
back-to-back live captures of the same query returned two to six different top-3 sets, so no
single capture is a fair gold. See docs/task-notes-paiddata.md.
"""

import os
import time

import httpx

# Only capture functions are re-exported into bench.truth (keeps its TIMEOUT etc. intact).
__all__ = [
    "amazon_price_usd",
    "amazon_ratings_count",
    "google_ads_monthly_search_volume",
    "google_maps_review_count",
    "x_follower_count",
    "x_most_liked_post",
]

TIMEOUT = 120.0
DFS = "https://api.dataforseo.com/v3"
X_API = "https://api.x.com/2"
US = 2840  # DataForSEO location_code for the United States

def _ensure_secrets(*names: str) -> None:
    if all(os.environ.get(n) for n in names):
        return
    from bench.secrets import load_secrets

    load_secrets()
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise RuntimeError(f"grader keys missing: {missing}")


def _dfs_auth() -> tuple[str, str]:
    _ensure_secrets("DATAFORSEO_CREDENTIALS")
    login, password = os.environ["DATAFORSEO_CREDENTIALS"].split(":", 1)
    return login, password


def _dfs_task(resp: httpx.Response) -> dict:
    resp.raise_for_status()
    body = resp.json()
    if body.get("status_code") != 20000:
        raise RuntimeError(f"DataForSEO error {body.get('status_code')}: {body.get('status_message')}")
    return body["tasks"][0]


def _dfs_live(path: str, payload: dict) -> dict:
    task = _dfs_task(httpx.post(f"{DFS}/{path}", auth=_dfs_auth(), json=[payload], timeout=TIMEOUT))
    if task["status_code"] != 20000:
        raise RuntimeError(f"DataForSEO task error {task['status_code']}: {task['status_message']}")
    return task["result"][0]


# --- Google Ads keyword volume (Keyword Planner data) -------------------------------------


def google_ads_monthly_search_volume(*, keyword: str, year: int, month: int, location_code: int = US) -> float:
    """Google Ads (Keyword Planner) search volume for one exact keyword in one calendar month.

    Closed months do not change once published, so tasks carry this as static gold; the
    function exists to re-verify it. One call costs about $0.09.
    """
    task = _dfs_task(
        httpx.post(
            f"{DFS}/keywords_data/google_ads/search_volume/live",
            auth=_dfs_auth(),
            json=[{"keywords": [keyword], "location_code": location_code, "language_code": "en"}],
            timeout=TIMEOUT,
        )
    )
    if task["status_code"] != 20000:
        raise RuntimeError(f"DataForSEO task error {task['status_code']}: {task['status_message']}")
    for row in task["result"] or []:
        for m in row.get("monthly_searches") or []:
            if m["year"] == year and m["month"] == month:
                return float(m["search_volume"])
    raise LookupError(f"no {year}-{month:02d} volume for {keyword!r}")


# --- Google Maps ---------------------------------------------------------------------------


def google_maps_review_count(*, keyword: str, cid: str, location_code: int = US) -> float:
    """Google review count on the Maps listing with this CID, found by searching `keyword`."""
    result = _dfs_live(
        "serp/google/maps/live/advanced",
        {"keyword": keyword, "location_code": location_code, "language_code": "en", "device": "desktop", "depth": 20},
    )
    for item in result["items"] or []:
        if str(item.get("cid")) == str(cid):
            return float(item["rating"]["votes_count"])
    raise LookupError(f"Maps listing cid={cid} not in results for {keyword!r}")


# --- Amazon (amazon.com product page) -----------------------------------------------------


def _amazon_product(asin: str, *, max_wait_s: int = 420) -> dict:
    """Product page fields for one ASIN. The Amazon endpoint is queue-based, so post at high
    priority and poll (typically ready in 10 to 30 seconds)."""
    auth = _dfs_auth()
    task = _dfs_task(
        httpx.post(
            f"{DFS}/merchant/amazon/asin/task_post",
            auth=auth,
            json=[{"asin": asin, "location_code": US, "language_code": "en_US", "priority": 2}],
            timeout=TIMEOUT,
        )
    )
    deadline = time.monotonic() + max_wait_s
    while time.monotonic() < deadline:
        time.sleep(8)
        got = _dfs_task(httpx.get(f"{DFS}/merchant/amazon/asin/task_get/advanced/{task['id']}", auth=auth, timeout=TIMEOUT))
        if got["status_code"] == 20000:
            items = got["result"][0]["items"] or []
            if not items:
                raise LookupError(f"no product data for ASIN {asin}")
            return items[0]
        if got["status_code"] not in (40601, 40602):  # task handed / in queue
            raise RuntimeError(f"DataForSEO task error {got['status_code']}: {got['status_message']}")
    raise TimeoutError(f"Amazon ASIN {asin} not ready after {max_wait_s}s")


def amazon_price_usd(*, asin: str) -> float:
    """Current buy-box price on amazon.com (US), in dollars."""
    item = _amazon_product(asin)
    if item.get("price_from") is None:
        raise LookupError(f"ASIN {asin} shows no price")
    return float(item["price_from"])


def amazon_ratings_count(*, asin: str) -> float:
    """Number of global ratings shown on the amazon.com product page."""
    return float(_amazon_product(asin)["rating"]["votes_count"])


# --- X (Twitter) API v2 -------------------------------------------------------------------


def _x_get(path: str, params: dict | None = None) -> dict:
    _ensure_secrets("X_API_BEARER_TOKEN")
    r = httpx.get(
        f"{X_API}/{path}",
        params=params,
        headers={"Authorization": f"Bearer {os.environ['X_API_BEARER_TOKEN']}"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def _x_user_id(username: str) -> str:
    return _x_get(f"users/by/username/{username}")["data"]["id"]


def x_follower_count(*, username: str) -> float:
    j = _x_get(f"users/by/username/{username}", {"user.fields": "public_metrics"})
    return float(j["data"]["public_metrics"]["followers_count"])


def x_most_liked_post(*, username: str, start: str, end: str) -> list[str]:
    """ID of the account's most-liked original post (replies and reposts excluded; quote posts
    count) created in [start, end), both RFC 3339 UTC timestamps."""
    uid = _x_user_id(username)
    params = {
        "max_results": 100,
        "tweet.fields": "public_metrics,created_at",
        "exclude": "retweets,replies",
        "start_time": start,
        "end_time": end,
    }
    posts: list[dict] = []
    while True:
        j = _x_get(f"users/{uid}/tweets", params)
        posts += j.get("data", [])
        token = j.get("meta", {}).get("next_token")
        if not token:
            break
        params["pagination_token"] = token
    if not posts:
        raise LookupError(f"@{username} has no original posts in [{start}, {end})")
    return [max(posts, key=lambda p: p["public_metrics"]["like_count"])["id"]]
