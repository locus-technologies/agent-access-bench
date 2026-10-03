# Task notes: control and pilot batteries

Written 2026-10-03, blind to any tool catalog. Nobody looked at the Locus repo and no Locus API or MCP was called. Every source of truth came from WebSearch, WebFetch, or a direct `curl` of a public dataset. These files contain no email addresses.

## Control battery (`tasks/control.jsonl`, 15 tasks)

### Selection method

- Every task can be fully answered with web search, web fetch, and Python. None of them needs paid data.
- Every fact dates from 2026, or is a 2025 dataset published in 2026. These are after the training cutoffs of the core models, so the agent has to search for them.
- Each answer is stable, meaning it won't change within roughly 3 weeks. There are no live captures. Python 3.15.0 was considered and rejected because its final release moved to 2026-10-09.
- Mix:
  - 6 short factual lookups with Exact or Number graders (01–05, 11).
  - 5 research syntheses with a Claims grader (06–10).
  - 4 compute tasks, where the agent fetches a public CSV or JSON and computes the answer (12–15). Task 14 uses SetGrader because its answer is a list.
- `harness_track=true` on 01, 06, 08, 12, and 14. These cover one lookup, two syntheses, and two compute tasks.
- `d_eligible=false` on all 15 tasks.

### Per-task truth method

| id | Gold | How it was verified |
|---|---|---|
| 01 | Ferran Torres | CBS News and Wikipedia. Also confirmed in the openfootball match JSON, which records the goal in the 106th minute. |
| 02 | 18 | NBC Olympics and CSMonitor both give Norway 18-12-11. Third place is not asked because Netherlands and Italy are tied on golds and sources order them differently. |
| 03 | Kenneth Walker III | ESPN and NBC. |
| 04 | 516 | eurovisionworld and Variety. The total is 204 jury points plus 312 televote points. |
| 05 | Remco Evenepoel | ProCyclingUK (+6:26) and NPR. |
| 06 | Claims | ESPN, the wimbledon.com draw PDF, and Wikipedia. |
| 07 | Claims | Wikipedia, ABC7, and NPR. The film won 6 Oscars in total. |
| 08 | Claims | Wikipedia and CNN. The Fidesz seat count is left out of the claims because sources disagree (52 vs 55). |
| 09 | Claims | Wikipedia, NASA, and Space.com. The splashdown date depends on time zone: 10 April in US time, 11 April in UTC. The claim says US time, and the notes say to accept either date if the answer states the time zone. |
| 10 | Claims | NBA.com and Wikipedia. |
| 11 | Magnifica humanitas | Vatican News and Villanova. |
| 12 | 26.34 ppm (abs_tol 0.05) | NOAA's CSV and TXT annual-mean files: 427.35 − 401.01. |
| 13 | 145 (abs_tol 1) | The USGS FDSN count API, cross-checked against the magnitude bands on Wikipedia: 1 + 15 + 129. |
| 14 | CA, HI, NM, VT, WV | Computed from the Census Vintage 2025 CSV. Matches the Census press release and The Hill. |
| 15 | 308 | Summed from the openfootball JSON (extra time included, shootouts excluded). Wikipedia also gives 308. |

## Pilot pool (`tasks/pilot.jsonl`, 10 tasks, never scored)

### Selection method

The pool mirrors the mix of the main batteries:

- 3 GTM-style tasks (01–03).
- 2 structured-data tasks with static gold (04–05).
- 2 multi-step claims tasks (06–07).
- 1 flight search (08).
- 2 control-style tasks (09–10).

The companies were picked to be mid-size and non-US, and to avoid overlap with the main batteries:

- Netlight (Sweden)
- Rimac Group (Croatia)
- Pennylane (France)

A grep of `structured`, `travel`, and `spend` found no topic overlap with these tasks. `d_eligible=true` on every task except 08, since the direct-vendor arm has no flight vendor.

### Per-task truth method

| id | Gold | How it was verified |
|---|---|---|
| 01 | Håkan Fältmars, CFO; netlight.com | PR Newswire release (effective 2026-03-30) and Breakit. |
| 02 | Matthias Wich, CFO; rimac-automobili.com or rimac-group.com | Rimac newsroom (effective Sept 2026), Autocar Pro, and tportal.hr. Both domains are accepted: the newsroom's press contact uses rimac-automobili.com, and the group site is rimac-group.com. |
| 03 | Maxime Baumard, CMO; pennylane.com | Planet-Fintech (appointment) and FrenchWeb (Sept 2025). **Weakest freshness:** no source is dated 2026. Re-check before the pilot runs. |
| 04 | 95.9% | electrive and CNBC: 172,233 of 179,550 cars. |
| 05 | 394,324 | Statistics Iceland and reykjavik.tours. The figure is internally consistent: 202,181 + 191,927 + 216. Wikipedia shows 394,234, which is a transposition, and must not be accepted. |
| 06 | Claims | Norway: electrive. Denmark: Mobility Denmark and bilstatistik.dk. Denmark's 2024 share is stated loosely because sources round it differently. |
| 07 | Claims | ProCyclingUK and CyclingUpToDate. |
| 08 | FlightGrader, LIS→FNC, 2026-11-12, nonstop | Truth is the fare snapshot taken in the same window as the run. The IATA codes are valid. |
| 09 | Jordan Staal | NHL.com and TSN. |
| 10 | Claims | olympics.com, giroditalia.it, and Domestique. |

## Fairness notes

- The control battery is heavy on sports (8 of 15 tasks). That makes it easy to search, which is the point of a control, but it is narrow in domain.
- In the GTM tasks, the person's identity is double-sourced, but whether the email is deliverable is decided only at grade time.
