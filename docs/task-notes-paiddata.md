# Task notes: paiddata battery

Written 2026-10-03, before any arm-C run. Tasks were written blind to any tool catalog: no
Locus code, API, or MCP server was consulted. Prompts carry no data-vendor or tool names (brand
names of the businesses, products, and accounts being asked about are part of the question).

Files: `tasks/paiddata.jsonl` (12). Truth capture: `bench/truth_paid.py`, re-exported by the
last line of `bench/truth.py` so grader `capture` names resolve as usual. Live tests:
`bench/test_truth_paid.py` (`uv run --with pytest pytest bench/test_truth_paid.py`;
`BENCH_OFFLINE=1` skips; about $0.11 per full run).

## Selection method

The battery holds questions real marketers, founders, analysts, and ops people ask whose answer
sits behind a login, a paywall, or a bot wall. A stock agent (web search, plain fetch, Python)
usually gets a stale, rounded, or third-party estimate instead. Each candidate had to pass:

1. A real user would ask it in roughly these words.
2. The exact value is visible to a logged-in or paying human, but not to a plain HTTP client
   (Google Maps and Keyword Planner render in JS or need an Ads login; Amazon bot-blocks;
   X shows "3.1M" to logged-out viewers; audio has no published transcript).
3. A grader-only paid source can capture it, and a tolerance can separate "read the live
   source" from "guessed, recalled, or rounded".
4. The value does not move much within an hour (no viral accounts, no flash sales).

Grader-only keys (`DATAFORSEO_CREDENTIALS`, `X_API_BEARER_TOKEN`) are loaded by
`bench.secrets.load_secrets()` and are never given to any agent arm. The audio gold was set with
`DEEPGRAM_API_KEY` and `OPENAI_API_KEY`, read once from the same secret at authoring time; it is
static, so no capture needs them at grade time.

## Change from the suggested mix: Google organic ranking dropped

The plan called for three "which domains rank top 3 on Google US desktop for X" tasks. They were
written, then dropped, because the truth could not be captured robustly:

- 24 candidate queries were sampled 4 to 8 times back to back (location United States, en,
  desktop). Only 2 returned one top-3 set across 4 samples, and neither held at 6 samples.
  Most returned 2 to 6 distinct top-3 sets. Even government-dominated queries ("federal minimum wage", "how to renew a us
  passport") had no domain common to every sample.
- The splits were not noise around one answer. They were distinct result sets served side by
  side (for "what is gross margin": bdc.ca / investopedia.com / salesforce.com vs
  morningstar.com / shopify.com / plus500.com, with reported result counts of ~134 vs ~121,000).
  A city-level location (New York) did not help.
- A 5-sample consensus capture still flipped between two captures minutes apart for 4 of 5
  queries. With a recall-only set grader, any fixed gold would fail an agent that correctly
  reported the variant Google showed it.

Replacement, keeping the "Google search data" theme: two Keyword Planner monthly-volume tasks
(01, 02). Planner data needs a Google Ads login, third-party SEO tools publish different
estimates, and a closed month never changes, so the gold is static and exact. The third slot
went to a non-US Google Maps listing (03).

Final mix: 2 Google Ads keyword volume, 3 Google Maps review counts (US x2, UK x1), 2 Amazon
(price, ratings count), 2 X (follower count, most-liked post in a closed month), 3 audio
transcription.

## Truth method and robustness per task

Values below were captured on 2026-10-03.

| Task | Asks | Truth | Value | Tolerance and why |
|---|---|---|---|---|
| 01 | Aug 2026 US Google searches for "payroll software" | static; Google Ads search volume (`google_ads_monthly_search_volume`) | 14,800 | exact. Planner buckets are discrete; 12-mo avg and July are 33,100, so the wrong figure fails |
| 02 | Aug 2026 US Google searches for "standing desk" | static, as 01 | 165,000 | exact. 12-mo avg and July are 135,000 |
| 03 | Google review count, Dishoom Covent Garden (London) | live `google_maps_review_count`, by CID, UK location | 29,831 | rel 1% (~±300). Grows a few per day; rounded "29K" or "30K" fails |
| 04 | Google review count, Franklin Barbecue (Austin) | live, by CID | 7,287 | rel 1% (~±73) |
| 05 | Google review count, Lou Malnati's 439 N Wells St (Chicago) | live, by CID (flagship, not other locations) | 13,585 | rel 1% |
| 06 | Current amazon.com price, Lodge 10.25" skillet B00006JSUA | live `amazon_price_usd` (buy-box price, not list) | $20.92 (list $24.90) | abs $0.05. Prices move, but the capture runs within 10 min of the run |
| 07 | amazon.com ratings count, Atomic Habits hardcover 0735211299 | live `amazon_ratings_count` | 150,069 | rel 1% (~±1,500). Slow-growing backlist title |
| 08 | @NWS follower count on X | live `x_follower_count` (API v2 public_metrics) | 3,168,985 | rel 0.5% (~±16K). Logged-out "3.1M" fails |
| 09 | @stripe's most-liked original post, Sept 2026 (UTC) | live `x_most_liked_post` (replies and reposts excluded) | post 2101121486316884279 (861 likes) | ID must appear (in the link). Closed window; runner-up has 503 likes, so the ranking is stable |
| 10 | Reporter who signs off a 1970 AFVN newscast | static, two ASR passes | "Dave Youngman" | normalized match on "Youngman" |
| 11 | Storm diameter given in a 1948 CBC science segment | static, two ASR passes | 1,500 miles | exact |
| 12 | War brides and children escorted by the Canadian Red Cross, 1947 CBC report | static, two ASR passes | 61,000 | exact. Commonly cited history figures differ (about 48,000 brides plus 22,000 children), so a recalled number fails |

Notes on the live-capture tasks:

- **Maps (03 to 05).** The listing is searched by name and address, then matched by Google CID,
  so a different branch can never be returned as gold. Review counts only grow, by a handful per
  day. The 1% band admits a capture-to-answer lag of days, not a rounded figure. Address numbers
  in the prompts (12, 900, 439) are far outside each band, so they cannot match by accident.
- **Amazon (06, 07).** The Amazon product endpoint is queue-based; the capture posts at high
  priority and polls (10 to 30 seconds in testing, 7-minute ceiling). 06 asks for the price
  shown "today, not the list price"; an answer that also mentions the list price still passes if
  it contains the current price. Books were avoided for the price task because their page price
  depends on which format is selected.
- **X (08, 09).** API v2 with an app-only bearer token. 09 uses a closed calendar month, so only
  like counts move, and the top post leads by 70%. The grader matches the numeric post ID inside
  any link form (x.com or twitter.com).

## Audio tasks (10 to 12)

Source: the Internet Archive item `NewsFromThe30sThroughThe70s`, marked with the Creative
Commons Public Domain Mark 1.0. Direct MP3 URLs (`archive.org/download/...`) resolve with a
redirect to a mirror and return 200. The item ships MP3, OGG, waveform PNG, and spectrogram
files only; there is no transcript or caption file on the item, and the clips are obscure enough
that no transcript was found elsewhere. Clips are short (about 2 to 3 minutes).

Gold was set from two independent ASR passes on the same file: Deepgram nova-3 (smart_format) and
OpenAI gpt-4o-transcribe. Each chosen fact had to read the same in both:

- 10: both read "Air Force Sergeant Dave Youngman reporting". Where the two passes disagreed
  (Deepgram: "Associated Price", "October four two", "Robert French"; OpenAI: "Associated
  Press", "October 14th", "Robert Finch"), those facts were not used.
- 11: "about 1,500 miles in diameter" (Deepgram) and "about fifteen hundred miles in diameter"
  (OpenAI).
- 12: "more than 61,000 war brides and their children" in both.

The reporter's surname in 12 is spelled two ways by the two passes (Kesten, Keston), so it was
not used as a question.

## d_eligible and harness track

`d_eligible` is true for the Amazon tasks (06, 07; a scraping API can plausibly fetch an Amazon
product page) and the audio tasks (10 to 12; a code sandbox with internet access can install an
open-source speech model and transcribe a 2 to 3 minute clip). It is false for Keyword Planner
(01, 02; needs a Google Ads account), Google Maps (03 to 05; JS-rendered, and none of the arm-D
vendors return Maps listing data), and X (08, 09; scrapers are blocked and exact counts need the
API).

Harness track (4): 01, 04, 06, 09, one each from Keyword Planner, Maps, Amazon, and X.

## Spend

Authoring and verification cost about $1.05: $0.94 of DataForSEO (mostly the discarded SERP
stability study and three $0.09 keyword-volume calls) and under $0.10 of ASR. Per
grading call: Maps $0.002, Amazon $0.003, X API free under the plan quota. 01, 02, and 10 to 12
are static and cost nothing at grade time.
