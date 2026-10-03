# Task notes: structured, travel, spend batteries

Written 2026-10-03, before any arm-C run. Tasks were written blind to any tool catalog: no
vendor catalog, API, or MCP server was consulted. Prompts carry no vendor or tool names.

Files: `tasks/structured.jsonl` (15), `tasks/travel.jsonl` (8), `tasks/spend.jsonl` (5).
Truth capture: `bench/truth.py`. Live tests: `bench/test_truth.py`
(`uv run --with pytest pytest bench/test_truth.py`; `BENCH_OFFLINE=1` skips).

## Selection method

**Structured.** Each candidate question had to pass three checks before inclusion:

1. A real user would ask it in roughly these words.
2. The publisher of the data (not an aggregator) exposes it through a free, keyless endpoint
   that `bench/truth.py` can read within 10 minutes of a run.
3. A tolerance can be set that separates "read the live source" from "guessed or recalled".

Two groups:

- (a) Source-of-record data a plain web agent can reach with effort: ECB, SEC EDGAR, US
  Treasury, GitHub, npm, PyPI, USGS, Wikimedia, Coinbase Exchange, NWS. (01–11)
- (b) Data usually behind scraping-hostile or JavaScript-only pages: retailer stock, social
  follower counts, live game player counts, store prices with regional pricing and sales.
  (12–15) Each has a truth source run by the same company that renders the page.

Candidates dropped because truth could not be captured reliably:

- App Store ratings (iTunes lookup API): `itunes.apple.com` did not resolve from the capture
  host on 2026-10-03. Dropped rather than risk an ungradeable window.
- US unemployment rate (FRED CSV): timed out twice. Dropped.
- Reddit subscriber counts: `about.json` returned 403 without OAuth.
- Real-estate listings: no keyless source of record for listing status or price.
- Other retailers (Patagonia, Bombas): bot walls on their own product JSON.

Static gold is used only for structured-09 (a closed calendar month). Everything else is live
capture.

**Travel.** Eight one-way, one-adult economy searches, departing 3.7 to 7.0 weeks after
2026-10-03. Mix: three US domestic (01–03), two transatlantic (04–05), one transpacific
(06), one intra-Asia (07), one intra-Europe (08). Five require nonstop (01, 03, 04, 06, 08).
Four carry a price cap (02, 04, 07, 08). When the prompt names a city,
`destination`/`origin` lists every commercial airport for that city (New York: JFK/EWR/LGA;
London: LHR/LGW/STN/LTN/LCY/SEN; Paris: CDG/ORY; Tokyo: HND/NRT; Bangkok: BKK/DMK;
Chicago: ORD/MDW). When the prompt names an airport code, only that code is accepted.

**Spend.** Five open-ended requests that cannot be finished within the stated budget and that
invite looping (enumerate, then enrich every row; "keep searching until every one"). Each
prompt states one dollar figure and `budget_usd` equals it. Three carry a secondary
ClaimsGrader with deliberately modest claims (partial results plus an honest spend report);
two have no outcome grader because no stable truth set exists.

## Fairness notes

- The truth source is never the source an arm-C tool would be expected to return; it is the
  data's publisher. An arm that reaches the publisher directly with plain fetch can pass every
  structured task. That is deliberate: (a) tasks measure effort and accuracy, not access.
- (b) tasks favour arms with rendering or scraping, but the truth sources are public, keyless
  JSON endpoints that a capable arm-B agent could also discover. Results on (b) tasks should
  be reported separately from (a).
- All structured tasks are marked `d_eligible`: a developer wiring web search, a scraper and a
  sandbox could serve every one. No travel task is `d_eligible` (no flight vendor in arm D).
  All spend tasks are `d_eligible`.
- Travel `cheapest_within` is relative to the cheapest valid offer any arm found in the same
  window. An arm that alone finds a low fare raises the bar for every other arm in that
  window. If no arm finds a valid offer, the task scores as failed for all arms. Runs should
  be scheduled so all arms for one task share a window; fares move fast inside 4 weeks.
- Lead times shrink as runs slip. If the full run starts after 2026-10-15, travel-02 and
  travel-07 fall under 2 weeks out; the dates are frozen anyway and the shift is logged.
- Rolling-window tasks (06, 08, 10) carry tolerance for a one-day window shift so an agent
  that reads the same source a few minutes before the capture is not failed.
- Harness track (7): structured-02, 05, 12, 13; travel-01, 04; spend-02.

## Per-task truth method

Values captured 2026-10-03 are shown for audit only. The grader always re-captures.

| Task | Question | Capture | Source of record | Tolerance | 2026-10-03 value | Robustness |
|---|---|---|---|---|---|---|
| structured-01 | ECB EUR/JPY reference rate | `ecb_reference_rate(quote_ccy=JPY)` | ECB eurofxref-daily.xml | rel 0.05% | 176.99 | High. One value per business day. |
| structured-02 | NVIDIA last five 8-K dates | `sec_recent_filing_dates(cik=1045810, form=8-K, n=5)` | EDGAR submissions JSON | set, recall 0.8, 1 extra | 2026-09-03, 08-26, 08-17, 07-02, 06-30 | High. 8-K/A excluded. |
| structured-03 | Costco shares outstanding on latest 10-K/10-Q cover | `sec_latest_shares_outstanding(cik=909832)` | EDGAR XBRL companyconcept (dei) | rel 0.1% | 443,478,804 | High. Changes once per filing. |
| structured-04 | Total public debt outstanding | `treasury_total_public_debt()` | Fiscal Data, Debt to the Penny | rel 0.05% | $40,260,641,972,390.03 (2026-10-01) | High. One-business-day lag. |
| structured-05 | Open `bug` issues in microsoft/vscode | `github_open_issue_count(repo, label)` | GitHub search API | rel 1% | 6,104 | Medium. Unauthenticated search is 10 req/min; set `GITHUB_TOKEN` to raise. |
| structured-06 | zod npm downloads last week | `npm_last_week_downloads(package=zod)` | npm downloads API | rel 5% | 373,908,324 | High. |
| structured-07 | Latest stable pandas | `pypi_latest_version(package=pandas)` | PyPI JSON API | set, recall 1.0 | 3.0.6 | High. |
| structured-08 | M4.5+ quakes, past 7 days | `usgs_quake_count_past_week(min_mag=4.5)` | USGS real-time feed | abs 3 | 124 | High. |
| structured-09 | Python (programming language) human pageviews, Sept 2026 | static gold via `wikipedia_monthly_pageviews` | Wikimedia REST pageviews | rel 1% | 136,097 | High. Closed month. |
| structured-10 | BTC-USD 30-day avg daily volume on Coinbase Exchange | `coinbase_avg_daily_volume(product=BTC-USD, days=30)` | Coinbase Exchange public candles | rel 3% | 6,182.9 BTC | Medium. Today's partial candle excluded; window edge at 00:00 UTC. |
| structured-11 | Latest temperature at KORD | `nws_latest_temp_f(station=KORD)` | api.weather.gov observations | abs 2 F | 68.0 F | Medium. Third-party weather sites may show a different station or a stale report. |
| structured-12 | Allbirds Men's Wool Runner (Natural Grey) sizes in stock | `shopify_in_stock_variants(store, handle)` | Retailer storefront product JSON (`.js`) | set, recall 1.0, 1 extra | 9, 10, 11, 13 | Medium. Stock can change within minutes; the handle could be retired. Empty gold means sold out. |
| structured-13 | NYT followers on Bluesky | `bluesky_follower_count(handle=nytimes.com)` | Bluesky public AppView | rel 0.5% | 1,350,079 | High. |
| structured-14 | Counter-Strike 2 players now | `steam_current_players(appid=730)` | Steam Web API (keyless) | rel 8% | ~775k to 787k within minutes | Medium. Fast-moving; capture must sit within 10 min. |
| structured-15 | Hades US Steam price now | `steam_price_usd(appid=1145360)` | Steam storefront appdetails | abs $0.01 | $6.24 (75% off $24.99) | Medium. A sale boundary inside the 10-min window could split runs. |

Travel tasks: truth is the same-window fare snapshot the FlightGrader takes (constraint check,
flight existence, price within 10% of the cheapest valid offer any arm found). `truth_sources`
cite IATA code lookup for the airport sets.

Spend tasks: truth is each arm's own billing record for the run, compared with `budget_usd`.
spend-02 lists 40 large US public companies by name only; no individuals are named in prompts.
