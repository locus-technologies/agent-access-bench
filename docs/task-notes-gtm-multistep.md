# Task notes: GTM and multistep batteries

Written and truth-checked on 2026-10-03. Files: `tasks/gtm.jsonl` (15) and `tasks/multistep.jsonl` (12).

## How tasks were selected

- **Written blind to the tool catalog.** I did not open the Locus repo or call any Locus API or MCP while writing these. Truth was established with plain web search and fetch, raw `curl` of public pages, the public UK company register, public job-board feeds, and the GitHub API. No prompt names a vendor or data tool.
- **GTM companies.** I picked mid-size private companies, mostly 75 to 2,000 staff, with no megacaps. They span Denmark, Bulgaria/UK, the Netherlands, the UK, Czechia, Ireland, Latvia/Sweden, Indonesia, Australia, Nigeria, Japan and Chile.
- **GTM roles.** Mostly CEO, plus two CTOs and one sales leader (CRO), so the set isn't only "find the founder".
- **Person rule.** A person was kept only if at least two independent public sources named them in the role. Truth is the current role holder. Where a predecessor or co-founder is a likely wrong answer, the task notes say so.
- **Multistep tasks** mix three kinds:
  - fixed-gold fact gathering (registry, funding, tech stack, GitHub, a Japanese-language brief)
  - open-ended list building, where each claim is phrased as "every listed X satisfies Y" so a grader can check it without a gold list
  - freshness traps (recent CEO changes, a fabricated aggregator round, a misleading security page)
- **Privacy.** No personal email addresses are recorded anywhere. Graders get names and work domains only.
- **`d_eligible`.** True wherever contact enrichment, scraping or search could plausibly help. False only for multistep-03 (official UK register) and multistep-10 (GitHub API), where arm B's tools are the natural route.
- **`harness_track`.** 8 tasks: gtm-01, gtm-02, gtm-11, gtm-14, multistep-02, multistep-04, multistep-08 and multistep-11. They cover easy, medium and hard.

## Difficulty (my estimate)

| Level | GTM | Multistep |
|---|---|---|
| Easy | 01, 03, 04, 05, 08, 09 | 04, 10 |
| Medium | 02, 10, 13, 15 | 02, 03, 05, 06, 07, 09, 12 |
| Hard | 06, 07, 11, 12, 14 | 01, 08, 11 |

- The person tasks are graded mainly on the deliverable work email, and that part is hard for a search-only agent at every level.
- The name is easy for the easy tasks.

## Changes and drops during truth-checking

| Candidate | What happened |
|---|---|
| Factorial CTO | Dropped. Sources disagree: Pau Ramon (co-founder, CTO until about Sep 2023) vs Ilya Zayats, with no firm 2025-26 date for either. |
| Tines "CTO" | Re-targeted. Tines has no CTO, and Thomas Kinsella is co-founder and CCO. The task now asks for the sales leader (CRO Terry Tripp). |
| Mews CTO | Dropped. The role is Chief Product and Technical Officer, which is ambiguous for grading. |
| PostHog CTO | Dropped as a GTM task. Tim Glaser is now Co-CEO. This is used as a scored claim in multistep-06 instead. |
| Lokalise CRO | Dropped. Conflicting signals: own about page vs a profile showing another current CRO role. Replaced by Lokalise CTO. |
| Payhawk CRO | Not used. The only source was a 2025 announcement. |
| Weaviate "Series C, Oct 2025" | Not used as fact. Only an aggregator reports it and no primary source exists. It became the trap in multistep-12. |
| Mews HQ | Not scored. Mews's own site says Prague, while press says Amsterdam. |
| Payhawk accounts status | Not scored. The register showed accounts due 30 Sep 2026, which is unstable around the run window. |
| Kuda | Kept, with a caveat. It has the weakest dating: Wikipedia, Crunchbase and TheOrg agree, but there is no fetched 2026 primary source. |
| Employment Hero | Kept. The 2026 company blog post now returns 404, so I relied on the EY page, London Tech Week and the company author page. |

## Per-task truth

### GTM

| ID | Truth | How established |
|---|---|---|
| gtm-01 | Pleo CEO: Jeppe Rindom (pleo.io) | Pleo about page (co-founder), Crunchbase, and a 2026-06-11 BusinessWire release quoting him as CEO. |
| gtm-02 | Payhawk CTO: Boyko Karadzhov (payhawk.com) | payhawk.com/team ("Co-founder & CTO"), Crunchbase, Endeavor Bulgaria, and the Companies House officer list. |
| gtm-03 | Weaviate CEO: Bob van Luijt (weaviate.io) | Ricoh release 2026-06-16, Crunchbase, Wikipedia. |
| gtm-04 | Juro CEO: Richard Mabey (juro.com) | Juro author page, Legal IT Insider 2025-08-28, Companies House (director since 2015). |
| gtm-05 | Mews CEO: Matt (Matthijs) Welle (mews.com) | mews.com/about-us, Hotel Dive 2026-01-23, EY WEOY 2026 Netherlands page. |
| gtm-06 | Tines CRO: Terry Tripp (tines.com) | tines.com/about (fetched 2026-10-03), Contrary Research 2025-08-07. |
| gtm-07 | Lokalise CTO: Magnus Slind-Näslund (lokalise.com) | lokalise.com/about, TheOrg, MarTech Edge quote as CTO. |
| gtm-08 | Xendit CEO: Moses Lo (xendit.co) | Fortune press release 2026-09-23, Crunchbase, Gold House. |
| gtm-09 | Employment Hero CEO: Ben Thompson (employmenthero.com) | EY Australia finalist page, company author page, London Tech Week speaker page. |
| gtm-10 | Kuda CEO: Babs (Babatunde) Ogundeyi (kuda.com) | Wikipedia, Crunchbase, TheOrg. |
| gtm-11 | SmartHR CEO: 芹澤雅人 / Masato Serizawa (smarthr.co.jp) | smarthr.co.jp/company, release 2026-07-07, press release 2026-04-15. |
| gtm-12 | Buk CEO: Jaime Arrieta (buk.cl and country domains) | Endeavor Chile, Forbes Chile 2026-03-30, Buk's own CEO interview post. |
| gtm-13 | Payhawk snapshot (claims) | payhawk.com/team, GlobeNewswire 2026-09-30 boilerplate (London HQ, nearly 7,000 customers, more than $100M ARR), Payhawk ARR announcement July 2026. |
| gtm-14 | LatAm HR/payroll list (open) | Feasibility checked (Buk qualifies). The grader verifies each entry against public pages. |
| gtm-15 | Juro firmographics (claims) | Juro Series B post ($23M, Eight Roads, Jan 2022, $38M total), Companies House (incorporated 2015), Tracxn (about 120 staff, Jul 2026). |

### Multistep

| ID | Truth | How established |
|---|---|---|
| multistep-01 | Berlin climate startups (open) | Feasibility from funding coverage and a directory (Ucaneo, forward earth, Scale Energy, Deutsche Sanierungsberatung). |
| multistep-02 | Tech stack | Raw homepage HTML fetched with curl on 2026-10-03, grepping for script hosts. See the task notes for exact signatures. The grader should re-fetch at run time. |
| multistep-03 | UK register details | Companies House overview and officers pages for 09684844 and 11747263. |
| multistep-04 | Mews brief | Mews about page, Hotel Dive, Yahoo Finance and Skift coverage of the $300M Series D (EQT Growth lead, Jan 2026, $2.5B valuation). |
| multistep-05 | Security claims | Each vendor's own page, fetched: Juro (SOC 2 Type II), Lokalise (SOC 2 Type II, ISO 27001/27017), Payhawk (trust portal and blog: ISO 27001, SOC 2 Type 2), Factorial (SOC 2 Type 2, ISO 27001:2022). |
| multistep-06 | PostHog roles | Public job-board feed snapshot (5 engineering roles). The handbook page shows "Tim (Co-CEO)" and "James (Co-CEO)". |
| multistep-07 | Lagos/Nairobi fintechs (open) | Feasibility only (Mono, Kuda, Moniepoint, Carbon). |
| multistep-08 | Dutch logistics software (open) | Feasibility only (Sendcloud, Shypple and others). |
| multistep-09 | CLM competitors | Ironclad (Dan Springer CEO since Apr 2025), Icertis (interim co-CEOs since Jul 2026), and Agiloft, from company announcements and press. |
| multistep-10 | Supabase GitHub | GitHub API on 2026-10-03: supabase/supabase, Apache-2.0, 111,054 stars, CLI v2.119.0. |
| multistep-11 | SmartHR brief | SmartHR company page and release 2026-07-07 (ARR ¥30B; prior milestones ¥10B Feb 2023 and ¥20B Apr 2025). |
| multistep-12 | Weaviate funding | PR Newswire Series A ($16M, NEA and Cortical, Feb 2022; seed led by Zetta; founded 2019), PR Newswire and SiliconANGLE Series B ($50M, Index, Apr 2023). No primary source for any Series C. |

## Fairness concerns

- **The GTM battery is mostly CEOs at well-covered companies.** A search-only agent will usually get the name, so the battery largely measures access to a deliverable email. That is the intended contrast, but say so when reporting.
- **Several truths are time-sensitive.** These include job listings, director lists, tech stacks, the CLI release tag, star counts and the Payhawk customer count. Each such claim tells the grader to re-check live at grading time, and that check should be run in the same window as the agent run.
- **Open-ended claims (gtm-14, multistep-01, 07, 08, 09) depend on judge diligence.** The human audit should over-sample them.
- **Some sources the grader may need to re-check block bots** (Crunchbase, GeekWire, EU-Startups). Every person task also has at least one fetchable source.
- **Payhawk, Juro, Mews and Lokalise each appear in more than one task.** This is a mild overlap but not leakage, because no task's answer is in another task's prompt. Runs are independent, so there is no carryover.
