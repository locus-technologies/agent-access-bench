# Agent access bench: analysis tables

> **INCLUDES THE PILOT BATTERY (--include-pilot). Not a headline result.**

Logs: 8. Runs: 80. Models: anthropic/claude-sonnet-5-5, openai/gpt-6.1-sol. Arms: A, B, C, D. Bootstrap: 10,000 cluster resamples over tasks, seed sha256('agent-access-bench-v1') = 1056477527888400723. Differences are in percentage points.

Runs per scope: {"h1": 80, "structured-public": 0, "control": 0, "d_subset": 72, "spend": 0}. Pilot runs excluded: 0. Grading (judge) cost, not counted in any arm: $0.1929.

## H1 (primary): access batteries, C - B

Rule: pooled C-B 95% CI lower bound > 0. Supported: **False**.

| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |
|---|---|---|---|---|
| C-B pooled (models equal weight) | +0.0 | [-30.0, +30.0] | 10 | 2 |
| C-B anthropic/claude-sonnet-5-5 | +0.0 | [-30.0, +30.0] | 10 | 1 |
| C-B openai/gpt-6.1-sol | +0.0 | [-30.0, +30.0] | 10 | 1 |
| C-B battery pilot | +0.0 | [-30.0, +30.0] | 10 | 2 |

## Structured public (01-11), C - B (not in H1)

| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |
|---|---|---|---|---|
| C-B pooled (models equal weight) | n/a | [n/a, n/a] | 0 | 0 |

## H2: control battery, C - B

Rule: pooled C-B 95% CI lower bound > -5 pp. Supported: **None**.

| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |
|---|---|---|---|---|
| C-B pooled (models equal weight) | n/a | [n/a, n/a] | 0 | 0 |

## H3: D-eligible tasks, C - D

Rule: pooled C-D 95% CI lower bound > -5 pp and C tool-definition tokens < D. Success part: **True**. Tokens part: **True** (C 17104 vs D 79648).

| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |
|---|---|---|---|---|
| C-D pooled (models equal weight) | +0.0 | [+0.0, +0.0] | 9 | 2 |
| C-D anthropic/claude-sonnet-5-5 | +0.0 | [+0.0, +0.0] | 9 | 1 |
| C-D openai/gpt-6.1-sol | +0.0 | [+0.0, +0.0] | 9 | 1 |

## H4: spend safety

Arm C spend of record is the Locus ledger (allocated minus settled end-user balance). Arm D spend is ESTIMATED at vendor list prices. Arm B has no paid tools.

| Source | Arm | Model | Runs | Breaches | $ over budget (total) | $ spent (total) |
|---|---|---|---|---|---|---|
| ledger | C | (all) | 1 | 0 | | $0.0605 of $3.0000 budget |

## Success rates (Wilson 95% CI over runs) and efficiency

| Scope | Model | Arm | Runs | Success | Wilson 95% | Wall p50 / p95 (s) | Tool calls (mean) | Tool-def tokens |
|---|---|---|---|---|---|---|---|---|
| h1 | anthropic/claude-sonnet-5-5 | A | 10 | 20.0% | [5.7%, 51.0%] | 8 / 14 | 0.0 | 0 |
| h1 | anthropic/claude-sonnet-5-5 | B | 10 | 90.0% | [59.6%, 98.2%] | 28 / 60 | 4.3 | 763 |
| h1 | anthropic/claude-sonnet-5-5 | C | 10 | 90.0% | [59.6%, 98.2%] | 38 / 76 | 4.2 | 17104 |
| h1 | anthropic/claude-sonnet-5-5 | D | 10 | 100.0% | [72.2%, 100.0%] | 27 / 72 | 3.5 | 79648 |
| h1 | openai/gpt-6.1-sol | A | 10 | 20.0% | [5.7%, 51.0%] | 9 / 16 | 0.0 | 0 |
| h1 | openai/gpt-6.1-sol | B | 10 | 90.0% | [59.6%, 98.2%] | 64 / 107 | 7.3 | 763 |
| h1 | openai/gpt-6.1-sol | C | 10 | 90.0% | [59.6%, 98.2%] | 30 / 92 | 5.9 | 17104 |
| h1 | openai/gpt-6.1-sol | D | 10 | 100.0% | [72.2%, 100.0%] | 36 / 69 | 4.1 | 79648 |
| d_subset | anthropic/claude-sonnet-5-5 | A | 9 | 22.2% | [6.3%, 54.7%] | 7 / 14 | 0.0 | 0 |
| d_subset | anthropic/claude-sonnet-5-5 | B | 9 | 88.9% | [56.5%, 98.0%] | 28 / 52 | 2.9 | 763 |
| d_subset | anthropic/claude-sonnet-5-5 | C | 9 | 100.0% | [70.1%, 100.0%] | 36 / 69 | 3.8 | 17104 |
| d_subset | anthropic/claude-sonnet-5-5 | D | 9 | 100.0% | [70.1%, 100.0%] | 26 / 52 | 2.9 | 79648 |
| d_subset | openai/gpt-6.1-sol | A | 9 | 22.2% | [6.3%, 54.7%] | 9 / 16 | 0.0 | 0 |
| d_subset | openai/gpt-6.1-sol | B | 9 | 88.9% | [56.5%, 98.0%] | 61 / 108 | 6.2 | 763 |
| d_subset | openai/gpt-6.1-sol | C | 9 | 100.0% | [70.1%, 100.0%] | 29 / 93 | 6.2 | 17104 |
| d_subset | openai/gpt-6.1-sol | D | 9 | 100.0% | [70.1%, 100.0%] | 35 / 71 | 4.0 | 79648 |

## Cost per successful task (model + Locus + D vendor estimate)

Model cost from list prices in prereg/model-prices.json. D vendor spend is an ESTIMATE at list prices. Judge (grading) cost is excluded.

| Scope | Model | Arm | Model $ | Locus $ | D vendor $ (est.) | Total $ | $/success | 95% CI |
|---|---|---|---|---|---|---|---|---|
| h1 | anthropic/claude-sonnet-5-5 | A | $0.0617 | $0.0000 | $0.0000 | $0.0617 | $0.0308 | [$0.0131, $0.0691] |
| h1 | anthropic/claude-sonnet-5-5 | B | $0.3586 | $0.0000 | $0.0000 | $0.3586 | $0.0398 | [$0.0224, $0.0663] |
| h1 | anthropic/claude-sonnet-5-5 | C | $0.4574 | $0.0765 | $0.0000 | $0.5339 | $0.0593 | [$0.0297, $0.1182] |
| h1 | anthropic/claude-sonnet-5-5 | D | $1.5391 | $0.0000 | $0.1543 | $1.6934 | $0.1693 | [$0.0885, $0.2574] |
| h1 | openai/gpt-6.1-sol | A | $0.0274 | $0.0000 | $0.0000 | $0.0274 | $0.0137 | [$0.0059, $0.0314] |
| h1 | openai/gpt-6.1-sol | B | $0.3366 | $0.0000 | $0.0000 | $0.3366 | $0.0374 | [$0.0239, $0.0578] |
| h1 | openai/gpt-6.1-sol | C | $0.3174 | $0.0643 | $0.0000 | $0.3817 | $0.0424 | [$0.0258, $0.0681] |
| h1 | openai/gpt-6.1-sol | D | $0.4864 | $0.0000 | $0.0983* | $0.5847 | $0.0585 | [$0.0377, $0.0858] |
| d_subset | anthropic/claude-sonnet-5-5 | A | $0.0556 | $0.0000 | $0.0000 | $0.0556 | $0.0278 | [$0.0119, $0.0627] |
| d_subset | anthropic/claude-sonnet-5-5 | B | $0.2433 | $0.0000 | $0.0000 | $0.2433 | $0.0304 | [$0.0201, $0.0476] |
| d_subset | anthropic/claude-sonnet-5-5 | C | $0.3523 | $0.0260 | $0.0000 | $0.3783 | $0.0420 | [$0.0259, $0.0607] |
| d_subset | anthropic/claude-sonnet-5-5 | D | $1.1438 | $0.0000 | $0.1367 | $1.2805 | $0.1423 | [$0.0741, $0.2209] |
| d_subset | openai/gpt-6.1-sol | A | $0.0244 | $0.0000 | $0.0000 | $0.0244 | $0.0122 | [$0.0053, $0.0281] |
| d_subset | openai/gpt-6.1-sol | B | $0.2826 | $0.0000 | $0.0000 | $0.2826 | $0.0353 | [$0.0218, $0.0580] |
| d_subset | openai/gpt-6.1-sol | C | $0.2880 | $0.0390 | $0.0000 | $0.3270 | $0.0363 | [$0.0225, $0.0514] |
| d_subset | openai/gpt-6.1-sol | D | $0.4340 | $0.0000 | $0.0855 | $0.5195 | $0.0577 | [$0.0353, $0.0884] |

`*` some runs' vendor estimate is a lower bound (unpriced or variable-price calls).

## Travel: cheapest_within audit

**pilot-08**: min constraint-passing price $66.0000, threshold $72.6000 (x1.10); raw pass 6/8, final pass 4/8, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 0 | 83.0 USD | $83.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | B | 1 | 1 | 1 | 61.99 EUR | $69.5838 | within |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 1 | 1 | 61.99 EUR | $69.5838 | within |
| anthropic/claude-sonnet-5-5 | D | 1 | 1 | 1 | 66.0 USD | $66.0000 | within |
| openai/gpt-6.1-sol | C | 1 | 1 | 0 | 83.0 USD | $83.0000 | over 1.10 x min |
| openai/gpt-6.1-sol | D | 1 | 1 | 1 | 62.0 EUR | $69.5950 | within |
