# Agent access bench: analysis tables

Logs: 81. Runs: 7857. Models: anthropic/claude-haiku-4-5, anthropic/claude-opus-5-5, anthropic/claude-sonnet-5-5, google/gemini-3.8-flash, grok/grok-4.7, openai/gpt-6-luna, openai/gpt-6.1-sol, openrouter/deepseek/deepseek-v4-pro-0813, openrouter/google/gemini-3.1-pro-preview. Arms: A, B, C, D. Bootstrap: 10,000 cluster resamples over tasks, seed sha256('agent-access-bench-v1') = 1056477527888400723. Differences are in percentage points.

Runs per scope: {"h1": 5049, "structured-public": 1188, "control": 1215, "d_subset": 4860, "spend": 405}. Pilot runs excluded: 0. Grading (judge) cost, not counted in any arm: $26.8680.

## H1 (primary): access batteries, C - B

Rule: pooled C-B 95% CI lower bound > 0. Supported: **True**.

| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |
|---|---|---|---|---|
| C-B pooled (models equal weight) | +27.1 | [+18.4, +35.8] | 51 | 9 |
| C-B anthropic/claude-haiku-4-5 | +23.5 | [+10.5, +35.9] | 51 | 1 |
| C-B anthropic/claude-opus-5-5 | +30.1 | [+17.0, +43.1] | 51 | 1 |
| C-B anthropic/claude-sonnet-5-5 | +37.9 | [+24.2, +51.0] | 51 | 1 |
| C-B google/gemini-3.8-flash | +25.5 | [+13.7, +37.9] | 51 | 1 |
| C-B grok/grok-4.7 | +20.9 | [+11.1, +31.4] | 51 | 1 |
| C-B openai/gpt-6-luna | +27.5 | [+15.0, +39.9] | 51 | 1 |
| C-B openai/gpt-6.1-sol | +38.6 | [+26.1, +51.0] | 51 | 1 |
| C-B openrouter/deepseek/deepseek-v4-pro-0813 | +22.2 | [+11.1, +34.0] | 51 | 1 |
| C-B openrouter/google/gemini-3.1-pro-preview | +17.6 | [+7.8, +27.5] | 51 | 1 |
| C-B battery gtm | +41.7 | [+24.0, +59.3] | 15 | 9 |
| C-B battery paiddata | +31.8 | [+18.8, +44.1] | 12 | 9 |
| C-B battery multistep | +4.0 | [-3.1, +12.0] | 12 | 9 |
| C-B battery travel | +40.3 | [+13.4, +62.5] | 8 | 9 |
| C-B battery structured-hostile | +0.9 | [-4.6, +5.6] | 4 | 9 |

## Structured public (01-11), C - B (not in H1)

| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |
|---|---|---|---|---|
| C-B pooled (models equal weight) | -1.3 | [-5.1, +2.4] | 11 | 9 |
| C-B anthropic/claude-haiku-4-5 | +3.0 | [-21.2, +24.2] | 11 | 1 |
| C-B anthropic/claude-opus-5-5 | +0.0 | [+0.0, +0.0] | 11 | 1 |
| C-B anthropic/claude-sonnet-5-5 | +3.0 | [+0.0, +9.1] | 11 | 1 |
| C-B google/gemini-3.8-flash | -6.1 | [-15.2, +0.0] | 11 | 1 |
| C-B grok/grok-4.7 | +9.1 | [+0.0, +18.2] | 11 | 1 |
| C-B openai/gpt-6-luna | -9.1 | [-18.2, +0.0] | 11 | 1 |
| C-B openai/gpt-6.1-sol | +0.0 | [+0.0, +0.0] | 11 | 1 |
| C-B openrouter/deepseek/deepseek-v4-pro-0813 | +0.0 | [+0.0, +0.0] | 11 | 1 |
| C-B openrouter/google/gemini-3.1-pro-preview | -12.1 | [-27.3, +0.0] | 11 | 1 |

## H2: control battery, C - B

Rule: pooled C-B 95% CI lower bound > -5 pp. Supported: **True**.

| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |
|---|---|---|---|---|
| C-B pooled (models equal weight) | -1.0 | [-3.7, +2.2] | 15 | 9 |
| C-B anthropic/claude-haiku-4-5 | +0.0 | [-13.3, +13.3] | 15 | 1 |
| C-B anthropic/claude-opus-5-5 | +0.0 | [+0.0, +0.0] | 15 | 1 |
| C-B anthropic/claude-sonnet-5-5 | -2.2 | [-6.7, +0.0] | 15 | 1 |
| C-B google/gemini-3.8-flash | +4.4 | [+0.0, +11.1] | 15 | 1 |
| C-B grok/grok-4.7 | +2.2 | [+0.0, +6.7] | 15 | 1 |
| C-B openai/gpt-6-luna | +0.0 | [-11.1, +8.9] | 15 | 1 |
| C-B openai/gpt-6.1-sol | +0.0 | [+0.0, +0.0] | 15 | 1 |
| C-B openrouter/deepseek/deepseek-v4-pro-0813 | +2.2 | [+0.0, +6.7] | 15 | 1 |
| C-B openrouter/google/gemini-3.1-pro-preview | -15.6 | [-33.3, +0.0] | 15 | 1 |

## H3: D-eligible tasks, C - D

Rule: pooled C-D 95% CI lower bound > -5 pp and C tool-definition tokens < D. Success part: **True**. Tokens part: **True** (C 17104 vs D 79648).

| Contrast | Estimate (pp) | 95% CI (pp) | Tasks | Models |
|---|---|---|---|---|
| C-D pooled (models equal weight) | +1.4 | [-3.2, +6.2] | 45 | 9 |
| C-D anthropic/claude-haiku-4-5 | +5.9 | [-3.7, +15.6] | 45 | 1 |
| C-D anthropic/claude-opus-5-5 | +1.5 | [-3.7, +8.1] | 45 | 1 |
| C-D anthropic/claude-sonnet-5-5 | -0.0 | [-6.7, +6.7] | 45 | 1 |
| C-D google/gemini-3.8-flash | -6.7 | [-17.8, +4.4] | 45 | 1 |
| C-D grok/grok-4.7 | -5.9 | [-16.3, +4.4] | 45 | 1 |
| C-D openai/gpt-6-luna | +5.2 | [-5.9, +16.3] | 45 | 1 |
| C-D openai/gpt-6.1-sol | +10.4 | [+3.0, +19.3] | 45 | 1 |
| C-D openrouter/deepseek/deepseek-v4-pro-0813 | +0.7 | [-7.4, +9.6] | 45 | 1 |
| C-D openrouter/google/gemini-3.1-pro-preview | +1.5 | [-5.2, +8.9] | 45 | 1 |

## H4: spend safety

Arm C spend of record is the Locus ledger (allocated minus settled end-user balance). Arm D spend is ESTIMATED at vendor list prices. Arm B has no paid tools.

| Source | Arm | Model | Runs | Breaches | $ over budget (total) | $ spent (total) |
|---|---|---|---|---|---|---|
| logs | B | anthropic/claude-haiku-4-5 | 15 | 0 | $0.0000 | $0.0000 |
| logs | B | anthropic/claude-opus-5-5 | 15 | 0 | $0.0000 | $0.0000 |
| logs | B | anthropic/claude-sonnet-5-5 | 15 | 0 | $0.0000 | $0.0000 |
| logs | B | google/gemini-3.8-flash | 15 | 0 | $0.0000 | $0.0000 |
| logs | B | grok/grok-4.7 | 15 | 0 | $0.0000 | $0.0000 |
| logs | B | openai/gpt-6-luna | 15 | 0 | $0.0000 | $0.0000 |
| logs | B | openai/gpt-6.1-sol | 15 | 0 | $0.0000 | $0.0000 |
| logs | B | openrouter/deepseek/deepseek-v4-pro-0813 | 15 | 0 | $0.0000 | $0.0000 |
| logs | B | openrouter/google/gemini-3.1-pro-preview | 15 | 0 | $0.0000 | $0.0000 |
| logs | C | anthropic/claude-haiku-4-5 | 15 | 0 | $0.0000 | $0.9109 |
| logs | C | anthropic/claude-opus-5-5 | 14 | 0 | $0.0000 | $5.6111 |
| logs | C | anthropic/claude-sonnet-5-5 | 13 | 0 | $0.0000 | $5.6760 |
| logs | C | google/gemini-3.8-flash | 15 | 0 | $0.0000 | $1.9788 |
| logs | C | grok/grok-4.7 | 15 | 0 | $0.0000 | $3.2167 |
| logs | C | openai/gpt-6-luna | 15 | 0 | $0.0000 | $8.9859 |
| logs | C | openai/gpt-6.1-sol | 14 | 0 | $0.0000 | $15.2737 |
| logs | C | openrouter/deepseek/deepseek-v4-pro-0813 | 13 | 0 | $0.0000 | $3.3262 |
| logs | C | openrouter/google/gemini-3.1-pro-preview | 15 | 0 | $0.0000 | $3.2981 |
| logs | D | anthropic/claude-haiku-4-5 | 15 | 0 | $0.0000 | $2.8112 |
| logs | D | anthropic/claude-opus-5-5 | 15 | 0 | $0.0000 | $4.6334 |
| logs | D | anthropic/claude-sonnet-5-5 | 15 | 0 | $0.0000 | $4.7724 |
| logs | D | google/gemini-3.8-flash | 15 | 0 | $0.0000 | $3.0760 |
| logs | D | grok/grok-4.7 | 14 | 0 | $0.0000 | $2.5952 |
| logs | D | openai/gpt-6-luna | 15 | 0 | $0.0000 | $2.8756 |
| logs | D | openai/gpt-6.1-sol | 14 | 0 | $0.0000 | $1.2825 |
| logs | D | openrouter/deepseek/deepseek-v4-pro-0813 | 14 | 0 | $0.0000 | $1.2807 |
| logs | D | openrouter/google/gemini-3.1-pro-preview | 15 | 0 | $0.0000 | $5.3350 |
| ledger | C | (all) | 140 | 0 | | $54.1838 of $280.5000 budget |

## Success rates (Wilson 95% CI over runs) and efficiency

| Scope | Model | Arm | Runs | Success | Wilson 95% | Wall p50 / p95 (s) | Tool calls (mean) | Tool-def tokens |
|---|---|---|---|---|---|---|---|---|
| h1 | anthropic/claude-haiku-4-5 | A | 153 | 0.0% | [0.0%, 2.4%] | 5 / 353 | 0.0 | 0 |
| h1 | anthropic/claude-haiku-4-5 | B | 153 | 37.9% | [30.6%, 45.8%] | 38 / 115 | 11.5 | 763 |
| h1 | anthropic/claude-haiku-4-5 | C | 153 | 61.4% | [53.5%, 68.8%] | 34 / 129 | 5.8 | 17104 |
| h1 | anthropic/claude-haiku-4-5 | D | 102 | 52.0% | [42.4%, 61.4%] | 28 / 99 | 5.5 | 79648 |
| h1 | anthropic/claude-opus-5-5 | A | 153 | 7.8% | [4.5%, 13.2%] | 11 / 35 | 0.0 | 0 |
| h1 | anthropic/claude-opus-5-5 | B | 153 | 50.3% | [42.5%, 58.1%] | 22 / 164 | 4.9 | 763 |
| h1 | anthropic/claude-opus-5-5 | C | 153 | 80.4% | [73.4%, 85.9%] | 29 / 123 | 5.1 | 17104 |
| h1 | anthropic/claude-opus-5-5 | D | 102 | 85.3% | [77.1%, 90.9%] | 34 / 146 | 4.2 | 79648 |
| h1 | anthropic/claude-sonnet-5-5 | A | 153 | 2.0% | [0.7%, 5.6%] | 10 / 258 | 0.0 | 0 |
| h1 | anthropic/claude-sonnet-5-5 | B | 153 | 41.2% | [33.7%, 49.1%] | 23 / 127 | 6.0 | 763 |
| h1 | anthropic/claude-sonnet-5-5 | C | 153 | 79.1% | [72.0%, 84.8%] | 30 / 156 | 5.6 | 17104 |
| h1 | anthropic/claude-sonnet-5-5 | D | 102 | 84.3% | [76.0%, 90.1%] | 37 / 183 | 6.2 | 79648 |
| h1 | google/gemini-3.8-flash | A | 153 | 15.7% | [10.8%, 22.3%] | 13 / 344 | 0.0 | 0 |
| h1 | google/gemini-3.8-flash | B | 153 | 38.6% | [31.2%, 46.5%] | 65 / 166 | 12.1 | 763 |
| h1 | google/gemini-3.8-flash | C | 153 | 64.1% | [56.2%, 71.2%] | 59 / 140 | 9.8 | 17104 |
| h1 | google/gemini-3.8-flash | D | 102 | 74.5% | [65.3%, 82.0%] | 68 / 193 | 9.0 | 79648 |
| h1 | grok/grok-4.7 | A | 153 | 0.7% | [0.1%, 3.6%] | 5 / 12 | 0.0 | 0 |
| h1 | grok/grok-4.7 | B | 153 | 34.6% | [27.6%, 42.5%] | 74 / 167 | 16.0 | 763 |
| h1 | grok/grok-4.7 | C | 153 | 55.6% | [47.6%, 63.2%] | 85 / 217 | 15.2 | 17104 |
| h1 | grok/grok-4.7 | D | 102 | 70.6% | [61.1%, 78.6%] | 78 / 311 | 13.1 | 79648 |
| h1 | openai/gpt-6-luna | A | 153 | 10.5% | [6.5%, 16.3%] | 8 / 32 | 0.0 | 0 |
| h1 | openai/gpt-6-luna | B | 153 | 40.5% | [33.1%, 48.4%] | 54 / 142 | 16.0 | 763 |
| h1 | openai/gpt-6-luna | C | 153 | 68.0% | [60.2%, 74.8%] | 45 / 144 | 8.7 | 17104 |
| h1 | openai/gpt-6-luna | D | 102 | 72.5% | [63.2%, 80.3%] | 49 / 179 | 8.9 | 79648 |
| h1 | openai/gpt-6.1-sol | A | 153 | 7.8% | [4.5%, 13.2%] | 10 / 249 | 0.0 | 0 |
| h1 | openai/gpt-6.1-sol | B | 153 | 49.0% | [41.2%, 56.9%] | 34 / 137 | 10.7 | 763 |
| h1 | openai/gpt-6.1-sol | C | 153 | 87.6% | [81.4%, 91.9%] | 32 / 133 | 7.3 | 17104 |
| h1 | openai/gpt-6.1-sol | D | 102 | 80.4% | [71.6%, 86.9%] | 47 / 113 | 7.3 | 79648 |
| h1 | openrouter/deepseek/deepseek-v4-pro-0813 | A | 153 | 7.8% | [4.5%, 13.2%] | 9 / 62 | 0.0 | 0 |
| h1 | openrouter/deepseek/deepseek-v4-pro-0813 | B | 153 | 45.1% | [37.4%, 53.0%] | 54 / 210 | 12.1 | 763 |
| h1 | openrouter/deepseek/deepseek-v4-pro-0813 | C | 153 | 67.3% | [59.5%, 74.2%] | 42 / 143 | 8.4 | 17104 |
| h1 | openrouter/deepseek/deepseek-v4-pro-0813 | D | 102 | 75.5% | [66.3%, 82.8%] | 42 / 202 | 7.6 | 79648 |
| h1 | openrouter/google/gemini-3.1-pro-preview | A | 153 | 2.0% | [0.7%, 5.6%] | 8 / 25 | 0.0 | 0 |
| h1 | openrouter/google/gemini-3.1-pro-preview | B | 153 | 48.4% | [40.6%, 56.2%] | 56 / 135 | 8.9 | 763 |
| h1 | openrouter/google/gemini-3.1-pro-preview | C | 153 | 66.0% | [58.2%, 73.0%] | 45 / 128 | 7.0 | 17104 |
| h1 | openrouter/google/gemini-3.1-pro-preview | D | 102 | 78.4% | [69.5%, 85.3%] | 52 / 390 | 5.5 | 79648 |
| structured-public | anthropic/claude-haiku-4-5 | A | 33 | 0.0% | [0.0%, 10.4%] | 2 / 110 | 0.0 | 0 |
| structured-public | anthropic/claude-haiku-4-5 | B | 33 | 63.6% | [46.6%, 77.8%] | 15 / 118 | 6.9 | 763 |
| structured-public | anthropic/claude-haiku-4-5 | C | 33 | 66.7% | [49.6%, 80.2%] | 16 / 120 | 3.3 | 17104 |
| structured-public | anthropic/claude-haiku-4-5 | D | 33 | 75.8% | [59.0%, 87.2%] | 18 / 81 | 3.4 | 79648 |
| structured-public | anthropic/claude-opus-5-5 | A | 33 | 0.0% | [0.0%, 10.4%] | 7 / 10 | 0.0 | 0 |
| structured-public | anthropic/claude-opus-5-5 | B | 33 | 93.9% | [80.4%, 98.3%] | 9 / 21 | 2.2 | 763 |
| structured-public | anthropic/claude-opus-5-5 | C | 33 | 93.9% | [80.4%, 98.3%] | 10 / 28 | 1.8 | 17104 |
| structured-public | anthropic/claude-opus-5-5 | D | 33 | 90.9% | [76.4%, 96.9%] | 15 / 94 | 1.8 | 79648 |
| structured-public | anthropic/claude-sonnet-5-5 | A | 33 | 0.0% | [0.0%, 10.4%] | 6 / 125 | 0.0 | 0 |
| structured-public | anthropic/claude-sonnet-5-5 | B | 33 | 97.0% | [84.7%, 99.5%] | 8 / 20 | 2.6 | 763 |
| structured-public | anthropic/claude-sonnet-5-5 | C | 33 | 100.0% | [89.6%, 100.0%] | 10 / 26 | 2.7 | 17104 |
| structured-public | anthropic/claude-sonnet-5-5 | D | 33 | 100.0% | [89.6%, 100.0%] | 15 / 57 | 2.4 | 79648 |
| structured-public | google/gemini-3.8-flash | A | 33 | 9.1% | [3.1%, 23.6%] | 9 / 71 | 0.0 | 0 |
| structured-public | google/gemini-3.8-flash | B | 33 | 84.8% | [69.1%, 93.3%] | 25 / 118 | 6.9 | 763 |
| structured-public | google/gemini-3.8-flash | C | 33 | 78.8% | [62.2%, 89.3%] | 33 / 59 | 7.3 | 17104 |
| structured-public | google/gemini-3.8-flash | D | 33 | 90.9% | [76.4%, 96.9%] | 54 / 105 | 7.5 | 79648 |
| structured-public | grok/grok-4.7 | A | 33 | 0.0% | [0.0%, 10.4%] | 2 / 9 | 0.0 | 0 |
| structured-public | grok/grok-4.7 | B | 33 | 75.8% | [59.0%, 87.2%] | 36 / 102 | 10.6 | 763 |
| structured-public | grok/grok-4.7 | C | 33 | 84.8% | [69.1%, 93.3%] | 31 / 107 | 8.0 | 17104 |
| structured-public | grok/grok-4.7 | D | 33 | 84.8% | [69.1%, 93.3%] | 43 / 120 | 7.5 | 79648 |
| structured-public | openai/gpt-6-luna | A | 33 | 0.0% | [0.0%, 10.4%] | 7 / 14 | 0.0 | 0 |
| structured-public | openai/gpt-6-luna | B | 33 | 90.9% | [76.4%, 96.9%] | 14 / 83 | 4.3 | 763 |
| structured-public | openai/gpt-6-luna | C | 33 | 81.8% | [65.6%, 91.4%] | 21 / 68 | 4.0 | 17104 |
| structured-public | openai/gpt-6-luna | D | 33 | 69.7% | [52.7%, 82.6%] | 29 / 59 | 2.8 | 79648 |
| structured-public | openai/gpt-6.1-sol | A | 33 | 0.0% | [0.0%, 10.4%] | 6 / 23 | 0.0 | 0 |
| structured-public | openai/gpt-6.1-sol | B | 33 | 90.9% | [76.4%, 96.9%] | 11 / 29 | 3.2 | 763 |
| structured-public | openai/gpt-6.1-sol | C | 33 | 90.9% | [76.4%, 96.9%] | 13 / 26 | 2.9 | 17104 |
| structured-public | openai/gpt-6.1-sol | D | 33 | 90.9% | [76.4%, 96.9%] | 24 / 41 | 2.7 | 79648 |
| structured-public | openrouter/deepseek/deepseek-v4-pro-0813 | A | 33 | 3.0% | [0.5%, 15.3%] | 5 / 34 | 0.0 | 0 |
| structured-public | openrouter/deepseek/deepseek-v4-pro-0813 | B | 33 | 90.9% | [76.4%, 96.9%] | 18 / 52 | 3.6 | 763 |
| structured-public | openrouter/deepseek/deepseek-v4-pro-0813 | C | 33 | 90.9% | [76.4%, 96.9%] | 11 / 78 | 3.1 | 17104 |
| structured-public | openrouter/deepseek/deepseek-v4-pro-0813 | D | 33 | 93.9% | [80.4%, 98.3%] | 22 / 52 | 3.1 | 79648 |
| structured-public | openrouter/google/gemini-3.1-pro-preview | A | 33 | 0.0% | [0.0%, 10.4%] | 8 / 42 | 0.0 | 0 |
| structured-public | openrouter/google/gemini-3.1-pro-preview | B | 33 | 97.0% | [84.7%, 99.5%] | 26 / 62 | 3.9 | 763 |
| structured-public | openrouter/google/gemini-3.1-pro-preview | C | 33 | 84.8% | [69.1%, 93.3%] | 27 / 49 | 3.3 | 17104 |
| structured-public | openrouter/google/gemini-3.1-pro-preview | D | 33 | 81.8% | [65.6%, 91.4%] | 46 / 155 | 3.6 | 79648 |
| control | anthropic/claude-haiku-4-5 | A | 45 | 0.0% | [0.0%, 7.9%] | 2 / 69 | 0.0 | 0 |
| control | anthropic/claude-haiku-4-5 | B | 45 | 84.4% | [71.2%, 92.3%] | 8 / 45 | 3.1 | 763 |
| control | anthropic/claude-haiku-4-5 | C | 45 | 84.4% | [71.2%, 92.3%] | 17 / 95 | 1.8 | 17104 |
| control | anthropic/claude-opus-5-5 | A | 45 | 2.2% | [0.4%, 11.6%] | 6 / 15 | 0.0 | 0 |
| control | anthropic/claude-opus-5-5 | B | 45 | 100.0% | [92.1%, 100.0%] | 7 / 78 | 1.5 | 763 |
| control | anthropic/claude-opus-5-5 | C | 45 | 100.0% | [92.1%, 100.0%] | 9 / 31 | 1.7 | 17104 |
| control | anthropic/claude-sonnet-5-5 | A | 45 | 6.7% | [2.3%, 17.9%] | 4 / 11 | 0.0 | 0 |
| control | anthropic/claude-sonnet-5-5 | B | 45 | 95.6% | [85.2%, 98.8%] | 6 / 32 | 1.7 | 763 |
| control | anthropic/claude-sonnet-5-5 | C | 45 | 93.3% | [82.1%, 97.7%] | 12 / 41 | 1.8 | 17104 |
| control | google/gemini-3.8-flash | A | 45 | 0.0% | [0.0%, 7.9%] | 7 / 15 | 0.0 | 0 |
| control | google/gemini-3.8-flash | B | 45 | 93.3% | [82.1%, 97.7%] | 18 / 112 | 5.0 | 763 |
| control | google/gemini-3.8-flash | C | 45 | 97.8% | [88.4%, 99.6%] | 19 / 64 | 4.9 | 17104 |
| control | grok/grok-4.7 | A | 45 | 0.0% | [0.0%, 7.9%] | 4 / 13 | 0.0 | 0 |
| control | grok/grok-4.7 | B | 45 | 93.3% | [82.1%, 97.7%] | 13 / 60 | 5.5 | 763 |
| control | grok/grok-4.7 | C | 45 | 95.6% | [85.2%, 98.8%] | 21 / 65 | 5.5 | 17104 |
| control | openai/gpt-6-luna | A | 45 | 2.2% | [0.4%, 11.6%] | 7 / 33 | 0.0 | 0 |
| control | openai/gpt-6-luna | B | 45 | 88.9% | [76.5%, 95.2%] | 17 / 46 | 4.2 | 763 |
| control | openai/gpt-6-luna | C | 45 | 88.9% | [76.5%, 95.2%] | 21 / 49 | 3.5 | 17104 |
| control | openai/gpt-6.1-sol | A | 45 | 2.2% | [0.4%, 11.6%] | 7 / 18 | 0.0 | 0 |
| control | openai/gpt-6.1-sol | B | 45 | 93.3% | [82.1%, 97.7%] | 13 / 52 | 3.3 | 763 |
| control | openai/gpt-6.1-sol | C | 45 | 93.3% | [82.1%, 97.7%] | 15 / 66 | 2.2 | 17104 |
| control | openrouter/deepseek/deepseek-v4-pro-0813 | A | 45 | 0.0% | [0.0%, 7.9%] | 4 / 68 | 0.0 | 0 |
| control | openrouter/deepseek/deepseek-v4-pro-0813 | B | 45 | 97.8% | [88.4%, 99.6%] | 11 / 66 | 2.3 | 763 |
| control | openrouter/deepseek/deepseek-v4-pro-0813 | C | 45 | 100.0% | [92.1%, 100.0%] | 11 / 40 | 2.6 | 17104 |
| control | openrouter/google/gemini-3.1-pro-preview | A | 45 | 0.0% | [0.0%, 7.9%] | 5 / 9 | 0.0 | 0 |
| control | openrouter/google/gemini-3.1-pro-preview | B | 45 | 84.4% | [71.2%, 92.3%] | 18 / 42 | 3.1 | 763 |
| control | openrouter/google/gemini-3.1-pro-preview | C | 45 | 68.9% | [54.3%, 80.5%] | 16 / 56 | 2.1 | 17104 |
| d_subset | anthropic/claude-haiku-4-5 | A | 135 | 0.0% | [0.0%, 2.8%] | 3 / 378 | 0.0 | 0 |
| d_subset | anthropic/claude-haiku-4-5 | B | 135 | 46.7% | [38.5%, 55.1%] | 27 / 104 | 9.3 | 763 |
| d_subset | anthropic/claude-haiku-4-5 | C | 135 | 63.7% | [55.3%, 71.3%] | 35 / 122 | 5.7 | 17104 |
| d_subset | anthropic/claude-haiku-4-5 | D | 135 | 57.8% | [49.3%, 65.8%] | 27 / 101 | 5.0 | 79648 |
| d_subset | anthropic/claude-opus-5-5 | A | 135 | 8.9% | [5.2%, 14.9%] | 10 / 36 | 0.0 | 0 |
| d_subset | anthropic/claude-opus-5-5 | B | 135 | 68.9% | [60.6%, 76.1%] | 18 / 177 | 4.2 | 763 |
| d_subset | anthropic/claude-opus-5-5 | C | 135 | 88.1% | [81.6%, 92.6%] | 24 / 112 | 4.4 | 17104 |
| d_subset | anthropic/claude-opus-5-5 | D | 135 | 86.7% | [79.9%, 91.4%] | 28 / 142 | 3.6 | 79648 |
| d_subset | anthropic/claude-sonnet-5-5 | A | 135 | 2.2% | [0.8%, 6.3%] | 7 / 183 | 0.0 | 0 |
| d_subset | anthropic/claude-sonnet-5-5 | B | 135 | 63.0% | [54.6%, 70.6%] | 15 / 132 | 5.3 | 763 |
| d_subset | anthropic/claude-sonnet-5-5 | C | 135 | 88.1% | [81.6%, 92.6%] | 24 / 178 | 4.9 | 17104 |
| d_subset | anthropic/claude-sonnet-5-5 | D | 135 | 88.1% | [81.6%, 92.6%] | 28 / 175 | 5.3 | 79648 |
| d_subset | google/gemini-3.8-flash | A | 135 | 20.0% | [14.1%, 27.5%] | 13 / 229 | 0.0 | 0 |
| d_subset | google/gemini-3.8-flash | B | 135 | 58.5% | [50.1%, 66.5%] | 59 / 162 | 10.5 | 763 |
| d_subset | google/gemini-3.8-flash | C | 135 | 71.9% | [63.7%, 78.8%] | 44 / 132 | 9.0 | 17104 |
| d_subset | google/gemini-3.8-flash | D | 135 | 78.5% | [70.9%, 84.6%] | 66 / 171 | 8.7 | 79648 |
| d_subset | grok/grok-4.7 | A | 135 | 0.7% | [0.1%, 4.1%] | 4 / 12 | 0.0 | 0 |
| d_subset | grok/grok-4.7 | B | 135 | 52.6% | [44.2%, 60.8%] | 63 / 164 | 13.7 | 763 |
| d_subset | grok/grok-4.7 | C | 135 | 68.1% | [59.9%, 75.4%] | 67 / 212 | 12.9 | 17104 |
| d_subset | grok/grok-4.7 | D | 135 | 74.1% | [66.1%, 80.7%] | 69 / 250 | 11.7 | 79648 |
| d_subset | openai/gpt-6-luna | A | 135 | 11.9% | [7.4%, 18.4%] | 8 / 33 | 0.0 | 0 |
| d_subset | openai/gpt-6-luna | B | 135 | 57.8% | [49.3%, 65.8%] | 41 / 142 | 12.7 | 763 |
| d_subset | openai/gpt-6-luna | C | 135 | 77.0% | [69.3%, 83.3%] | 35 / 141 | 8.1 | 17104 |
| d_subset | openai/gpt-6-luna | D | 135 | 71.9% | [63.7%, 78.8%] | 44 / 176 | 7.4 | 79648 |
| d_subset | openai/gpt-6.1-sol | A | 135 | 8.9% | [5.2%, 14.9%] | 9 / 178 | 0.0 | 0 |
| d_subset | openai/gpt-6.1-sol | B | 135 | 68.1% | [59.9%, 75.4%] | 28 / 137 | 8.9 | 763 |
| d_subset | openai/gpt-6.1-sol | C | 135 | 93.3% | [87.8%, 96.5%] | 24 / 130 | 6.4 | 17104 |
| d_subset | openai/gpt-6.1-sol | D | 135 | 83.0% | [75.7%, 88.4%] | 38 / 111 | 6.1 | 79648 |
| d_subset | openrouter/deepseek/deepseek-v4-pro-0813 | A | 135 | 9.6% | [5.7%, 15.8%] | 9 / 62 | 0.0 | 0 |
| d_subset | openrouter/deepseek/deepseek-v4-pro-0813 | B | 135 | 65.2% | [56.8%, 72.7%] | 32 / 200 | 9.1 | 763 |
| d_subset | openrouter/deepseek/deepseek-v4-pro-0813 | C | 135 | 80.7% | [73.3%, 86.5%] | 33 / 119 | 7.3 | 17104 |
| d_subset | openrouter/deepseek/deepseek-v4-pro-0813 | D | 135 | 80.0% | [72.5%, 85.9%] | 35 / 191 | 6.5 | 79648 |
| d_subset | openrouter/google/gemini-3.1-pro-preview | A | 135 | 2.2% | [0.8%, 6.3%] | 8 / 31 | 0.0 | 0 |
| d_subset | openrouter/google/gemini-3.1-pro-preview | B | 135 | 72.6% | [64.5%, 79.4%] | 32 / 116 | 6.8 | 763 |
| d_subset | openrouter/google/gemini-3.1-pro-preview | C | 135 | 80.7% | [73.3%, 86.5%] | 30 / 105 | 5.7 | 17104 |
| d_subset | openrouter/google/gemini-3.1-pro-preview | D | 135 | 79.3% | [71.7%, 85.2%] | 48 / 379 | 5.0 | 79648 |
| spend | anthropic/claude-haiku-4-5 | B | 15 | 46.7% | [24.8%, 69.9%] | 123 / 211 | 30.3 | 763 |
| spend | anthropic/claude-haiku-4-5 | C | 15 | 40.0% | [19.8%, 64.3%] | 123 / 242 | 29.7 | 17104 |
| spend | anthropic/claude-haiku-4-5 | D | 15 | 46.7% | [24.8%, 69.9%] | 112 / 213 | 20.3 | 79648 |
| spend | anthropic/claude-opus-5-5 | B | 15 | 46.7% | [24.8%, 69.9%] | 39 / 173 | 15.6 | 763 |
| spend | anthropic/claude-opus-5-5 | C | 15 | 53.3% | [30.1%, 75.2%] | 275 / 478 | 46.9 | 17104 |
| spend | anthropic/claude-opus-5-5 | D | 15 | 60.0% | [35.7%, 80.2%] | 189 / 535 | 24.5 | 79648 |
| spend | anthropic/claude-sonnet-5-5 | B | 15 | 40.0% | [19.8%, 64.3%] | 68 / 276 | 10.6 | 763 |
| spend | anthropic/claude-sonnet-5-5 | C | 15 | 46.7% | [24.8%, 69.9%] | 343 / 921 | 40.7 | 17104 |
| spend | anthropic/claude-sonnet-5-5 | D | 15 | 46.7% | [24.8%, 69.9%] | 241 / 682 | 32.8 | 79648 |
| spend | google/gemini-3.8-flash | B | 15 | 40.0% | [19.8%, 64.3%] | 35 / 635 | 16.3 | 763 |
| spend | google/gemini-3.8-flash | C | 15 | 40.0% | [19.8%, 64.3%] | 98 / 663 | 31.7 | 17104 |
| spend | google/gemini-3.8-flash | D | 15 | 40.0% | [19.8%, 64.3%] | 162 / 857 | 33.3 | 79648 |
| spend | grok/grok-4.7 | B | 15 | 66.7% | [41.7%, 84.8%] | 69 / 393 | 28.1 | 763 |
| spend | grok/grok-4.7 | C | 15 | 46.7% | [24.8%, 69.9%] | 483 / 1807 | 58.8 | 17104 |
| spend | grok/grok-4.7 | D | 15 | 60.0% | [35.7%, 80.2%] | 449 / 830 | 46.2 | 79648 |
| spend | openai/gpt-6-luna | B | 15 | 73.3% | [48.0%, 89.1%] | 75 / 253 | 38.8 | 763 |
| spend | openai/gpt-6-luna | C | 15 | 80.0% | [54.8%, 93.0%] | 142 / 467 | 44.3 | 17104 |
| spend | openai/gpt-6-luna | D | 15 | 53.3% | [30.1%, 75.2%] | 52 / 256 | 18.3 | 79648 |
| spend | openai/gpt-6.1-sol | B | 15 | 40.0% | [19.8%, 64.3%] | 26 / 405 | 27.5 | 763 |
| spend | openai/gpt-6.1-sol | C | 15 | 60.0% | [35.7%, 80.2%] | 408 / 971 | 73.5 | 17104 |
| spend | openai/gpt-6.1-sol | D | 15 | 40.0% | [19.8%, 64.3%] | 43 / 478 | 33.8 | 79648 |
| spend | openrouter/deepseek/deepseek-v4-pro-0813 | B | 15 | 46.7% | [24.8%, 69.9%] | 226 / 1048 | 39.0 | 763 |
| spend | openrouter/deepseek/deepseek-v4-pro-0813 | C | 15 | 40.0% | [19.8%, 64.3%] | 575 / 1158 | 55.3 | 17104 |
| spend | openrouter/deepseek/deepseek-v4-pro-0813 | D | 15 | 60.0% | [35.7%, 80.2%] | 332 / 1256 | 23.3 | 79648 |
| spend | openrouter/google/gemini-3.1-pro-preview | B | 15 | 46.7% | [24.8%, 69.9%] | 58 / 264 | 9.2 | 763 |
| spend | openrouter/google/gemini-3.1-pro-preview | C | 15 | 46.7% | [24.8%, 69.9%] | 113 / 538 | 27.6 | 17104 |
| spend | openrouter/google/gemini-3.1-pro-preview | D | 15 | 53.3% | [30.1%, 75.2%] | 141 / 404 | 25.9 | 79648 |

## Cost per successful task (model + Locus + D vendor estimate)

Model cost from list prices in prereg/model-prices.json. D vendor spend is an ESTIMATE at list prices. Judge (grading) cost is excluded.

| Scope | Model | Arm | Model $ | Locus $ | D vendor $ (est.) | Total $ | $/success | 95% CI |
|---|---|---|---|---|---|---|---|---|
| h1 | anthropic/claude-haiku-4-5 | A | $0.1856 | $0.0000 | $0.0000 | $0.1856 | n/a | [n/a, n/a] |
| h1 | anthropic/claude-haiku-4-5 | B | $6.2130 | $0.0000 | $0.0000 | $6.2130 | $0.1071 | [$0.0729, $0.1648] |
| h1 | anthropic/claude-haiku-4-5 | C | $4.3452 | $12.5871 | $0.0000 | $16.9323 | $0.1801 | [$0.1357, $0.2446] |
| h1 | anthropic/claude-haiku-4-5 | D | $6.5102 | $0.0000 | $5.5739* | $12.0841 | $0.2280 | [$0.1602, $0.3368] |
| h1 | anthropic/claude-opus-5-5 | A | $2.6982 | $0.0000 | $0.0000 | $2.6982 | $0.2249 | [$0.1205, $0.7087] |
| h1 | anthropic/claude-opus-5-5 | B | $13.5033 | $0.0000 | $0.0000 | $13.5033 | $0.1754 | [$0.1311, $0.2385] |
| h1 | anthropic/claude-opus-5-5 | C | $18.3683 | $10.5456 | $0.0000 | $28.9138 | $0.2351 | [$0.1791, $0.3047] |
| h1 | anthropic/claude-opus-5-5 | D | $15.3936 | $0.0000 | $1.9616 | $17.3552 | $0.1995 | [$0.1495, $0.2648] |
| h1 | anthropic/claude-sonnet-5-5 | A | $1.2940 | $0.0000 | $0.0000 | $1.2940 | $0.4313 | [$0.1553, $1.4272] |
| h1 | anthropic/claude-sonnet-5-5 | B | $8.8082 | $0.0000 | $0.0000 | $8.8082 | $0.1398 | [$0.0948, $0.2148] |
| h1 | anthropic/claude-sonnet-5-5 | C | $14.2639 | $14.5064 | $0.0000 | $28.7702 | $0.2378 | [$0.1743, $0.3197] |
| h1 | anthropic/claude-sonnet-5-5 | D | $16.1419 | $0.0000 | $2.2943 | $18.4362 | $0.2144 | [$0.1579, $0.2905] |
| h1 | google/gemini-3.8-flash | A | $0.5807 | $0.0000 | $0.0000 | $0.5807 | $0.0242 | [$0.0140, $0.0524] |
| h1 | google/gemini-3.8-flash | B | $12.5973 | $0.0000 | $0.0000 | $12.5973 | $0.2135 | [$0.1440, $0.3418] |
| h1 | google/gemini-3.8-flash | C | $12.2223 | $12.3676 | $0.0000 | $24.5899 | $0.2509 | [$0.1788, $0.3527] |
| h1 | google/gemini-3.8-flash | D | $9.7362 | $0.0000 | $5.2528 | $14.9890 | $0.1972 | [$0.1486, $0.2654] |
| h1 | grok/grok-4.7 | A | $0.4337 | $0.0000 | $0.0000 | $0.4337 | $0.4337 | [$0.1225, $0.5014] |
| h1 | grok/grok-4.7 | B | $17.8234 | $0.0000 | $0.0000 | $17.8234 | $0.3363 | [$0.2175, $0.5721] |
| h1 | grok/grok-4.7 | C | $29.7646 | $10.9611 | $0.0000 | $40.7257 | $0.4791 | [$0.3567, $0.6564] |
| h1 | grok/grok-4.7 | D | $31.0318 | $0.0000 | $3.7914* | $34.8232 | $0.4837 | [$0.3744, $0.6428] |
| h1 | openai/gpt-6-luna | A | $0.0748 | $0.0000 | $0.0000 | $0.0748 | $0.0047 | [$0.0027, $0.0113] |
| h1 | openai/gpt-6-luna | B | $0.5479 | $0.0000 | $0.0000 | $0.5479 | $0.0088 | [$0.0063, $0.0132] |
| h1 | openai/gpt-6-luna | C | $0.4562 | $20.4879 | $0.0000 | $20.9442 | $0.2014 | [$0.1169, $0.3323] |
| h1 | openai/gpt-6-luna | D | $0.6843 | $0.0000 | $7.3026* | $7.9868 | $0.1079 | [$0.0777, $0.1526] |
| h1 | openai/gpt-6.1-sol | A | $0.6361 | $0.0000 | $0.0000 | $0.6361 | $0.0530 | [$0.0315, $0.1391] |
| h1 | openai/gpt-6.1-sol | B | $7.5319 | $0.0000 | $0.0000 | $7.5319 | $0.1004 | [$0.0731, $0.1447] |
| h1 | openai/gpt-6.1-sol | C | $7.1679 | $11.4633 | $0.0000 | $18.6312 | $0.1390 | [$0.1040, $0.1826] |
| h1 | openai/gpt-6.1-sol | D | $6.5583 | $0.0000 | $1.3882* | $7.9464 | $0.0969 | [$0.0736, $0.1278] |
| h1 | openrouter/deepseek/deepseek-v4-pro-0813 | A | $0.5875 | $0.0000 | $0.0000 | $0.5875 | $0.0490 | [$0.0257, $0.1247] |
| h1 | openrouter/deepseek/deepseek-v4-pro-0813 | B | $3.9732 | $0.0000 | $0.0000 | $3.9732 | $0.0576 | [$0.0388, $0.0877] |
| h1 | openrouter/deepseek/deepseek-v4-pro-0813 | C | $3.9583 | $10.8953 | $0.0000 | $14.8536 | $0.1442 | [$0.1017, $0.2004] |
| h1 | openrouter/deepseek/deepseek-v4-pro-0813 | D | $6.1341 | $0.0000 | $2.2479* | $8.3820 | $0.1089 | [$0.0827, $0.1461] |
| h1 | openrouter/google/gemini-3.1-pro-preview | A | $0.6372 | $0.0000 | $0.0000 | $0.6372 | $0.2124 | [$0.0862, $0.7399] |
| h1 | openrouter/google/gemini-3.1-pro-preview | B | $14.9814 | $0.0000 | $0.0000 | $14.9814 | $0.2025 | [$0.1448, $0.2949] |
| h1 | openrouter/google/gemini-3.1-pro-preview | C | $16.3211 | $9.3561 | $0.0000 | $25.6772 | $0.2542 | [$0.1876, $0.3435] |
| h1 | openrouter/google/gemini-3.1-pro-preview | D | $21.1024 | $0.0000 | $3.8485 | $24.9509 | $0.3119 | [$0.2287, $0.4236] |
| structured-public | anthropic/claude-haiku-4-5 | A | $0.0338 | $0.0000 | $0.0000 | $0.0338 | n/a | [n/a, n/a] |
| structured-public | anthropic/claude-haiku-4-5 | B | $1.0155 | $0.0000 | $0.0000 | $1.0155 | $0.0484 | [$0.0243, $0.0939] |
| structured-public | anthropic/claude-haiku-4-5 | C | $0.5829 | $0.9456 | $0.0000 | $1.5286 | $0.0695 | [$0.0369, $0.1284] |
| structured-public | anthropic/claude-haiku-4-5 | D | $1.9856 | $0.0000 | $0.6341* | $2.6197 | $0.1048 | [$0.0692, $0.1593] |
| structured-public | anthropic/claude-opus-5-5 | A | $0.3727 | $0.0000 | $0.0000 | $0.3727 | n/a | [n/a, n/a] |
| structured-public | anthropic/claude-opus-5-5 | B | $1.5525 | $0.0000 | $0.0000 | $1.5525 | $0.0501 | [$0.0277, $0.0784] |
| structured-public | anthropic/claude-opus-5-5 | C | $1.5937 | $0.0000 | $0.0000 | $1.5937 | $0.0514 | [$0.0296, $0.0814] |
| structured-public | anthropic/claude-opus-5-5 | D | $2.2600 | $0.0000 | $0.0331 | $2.2931 | $0.0764 | [$0.0517, $0.1127] |
| structured-public | anthropic/claude-sonnet-5-5 | A | $0.1715 | $0.0000 | $0.0000 | $0.1715 | n/a | [n/a, n/a] |
| structured-public | anthropic/claude-sonnet-5-5 | B | $1.0071 | $0.0000 | $0.0000 | $1.0071 | $0.0315 | [$0.0190, $0.0459] |
| structured-public | anthropic/claude-sonnet-5-5 | C | $1.3492 | $0.0000 | $0.0000 | $1.3492 | $0.0409 | [$0.0246, $0.0602] |
| structured-public | anthropic/claude-sonnet-5-5 | D | $2.0346 | $0.0000 | $0.0456 | $2.0801 | $0.0630 | [$0.0502, $0.0769] |
| structured-public | google/gemini-3.8-flash | A | $0.1513 | $0.0000 | $0.0000 | $0.1513 | $0.0504 | [$0.0173, $0.0705] |
| structured-public | google/gemini-3.8-flash | B | $1.8783 | $0.0000 | $0.0000 | $1.8783 | $0.0671 | [$0.0405, $0.1043] |
| structured-public | google/gemini-3.8-flash | C | $2.3245 | $0.0000 | $0.0000 | $2.3245 | $0.0894 | [$0.0645, $0.1351] |
| structured-public | google/gemini-3.8-flash | D | $2.4529 | $0.0000 | $0.0848 | $2.5378 | $0.0846 | [$0.0627, $0.1186] |
| structured-public | grok/grok-4.7 | A | $0.0705 | $0.0000 | $0.0000 | $0.0705 | n/a | [n/a, n/a] |
| structured-public | grok/grok-4.7 | B | $3.1100 | $0.0000 | $0.0000 | $3.1100 | $0.1244 | [$0.0648, $0.2472] |
| structured-public | grok/grok-4.7 | C | $3.7840 | $0.0115 | $0.0000 | $3.7955 | $0.1356 | [$0.0773, $0.2361] |
| structured-public | grok/grok-4.7 | D | $8.4394 | $0.0000 | $0.0866* | $8.5260 | $0.3045 | [$0.2189, $0.4421] |
| structured-public | openai/gpt-6-luna | A | $0.0114 | $0.0000 | $0.0000 | $0.0114 | n/a | [n/a, n/a] |
| structured-public | openai/gpt-6-luna | B | $0.0511 | $0.0000 | $0.0000 | $0.0511 | $0.0017 | [$0.0009, $0.0033] |
| structured-public | openai/gpt-6-luna | C | $0.0490 | $0.4050 | $0.0000 | $0.4540 | $0.0168 | [$0.0093, $0.0337] |
| structured-public | openai/gpt-6-luna | D | $0.1216 | $0.0000 | $0.3743* | $0.4959 | $0.0216 | [$0.0121, $0.0423] |
| structured-public | openai/gpt-6.1-sol | A | $0.0723 | $0.0000 | $0.0000 | $0.0723 | n/a | [n/a, n/a] |
| structured-public | openai/gpt-6.1-sol | B | $0.7138 | $0.0000 | $0.0000 | $0.7138 | $0.0238 | [$0.0133, $0.0419] |
| structured-public | openai/gpt-6.1-sol | C | $0.6211 | $0.0000 | $0.0000 | $0.6211 | $0.0207 | [$0.0116, $0.0352] |
| structured-public | openai/gpt-6.1-sol | D | $0.8422 | $0.0000 | $0.0295 | $0.8717 | $0.0291 | [$0.0181, $0.0484] |
| structured-public | openrouter/deepseek/deepseek-v4-pro-0813 | A | $0.0678 | $0.0000 | $0.0000 | $0.0678 | $0.0678 | [$0.0241, $0.0887] |
| structured-public | openrouter/deepseek/deepseek-v4-pro-0813 | B | $0.2875 | $0.0000 | $0.0000 | $0.2875 | $0.0096 | [$0.0055, $0.0155] |
| structured-public | openrouter/deepseek/deepseek-v4-pro-0813 | C | $0.3657 | $0.0253 | $0.0000 | $0.3909 | $0.0130 | [$0.0087, $0.0189] |
| structured-public | openrouter/deepseek/deepseek-v4-pro-0813 | D | $1.2279 | $0.0000 | $0.0817* | $1.3096 | $0.0422 | [$0.0305, $0.0557] |
| structured-public | openrouter/google/gemini-3.1-pro-preview | A | $0.3107 | $0.0000 | $0.0000 | $0.3107 | n/a | [n/a, n/a] |
| structured-public | openrouter/google/gemini-3.1-pro-preview | B | $1.4959 | $0.0000 | $0.0000 | $1.4959 | $0.0467 | [$0.0279, $0.0734] |
| structured-public | openrouter/google/gemini-3.1-pro-preview | C | $1.7692 | $0.0530 | $0.0000 | $1.8222 | $0.0651 | [$0.0461, $0.0946] |
| structured-public | openrouter/google/gemini-3.1-pro-preview | D | $4.3343 | $0.0000 | $0.2380 | $4.5723 | $0.1693 | [$0.1194, $0.2597] |
| control | anthropic/claude-haiku-4-5 | A | $0.0369 | $0.0000 | $0.0000 | $0.0369 | n/a | [n/a, n/a] |
| control | anthropic/claude-haiku-4-5 | B | $0.7277 | $0.0000 | $0.0000 | $0.7277 | $0.0192 | [$0.0098, $0.0349] |
| control | anthropic/claude-haiku-4-5 | C | $0.4472 | $2.8041 | $0.0000 | $3.2513 | $0.0856 | [$0.0460, $0.1402] |
| control | anthropic/claude-opus-5-5 | A | $0.4725 | $0.0000 | $0.0000 | $0.4725 | $0.4725 | [$0.1228, $0.5729] |
| control | anthropic/claude-opus-5-5 | B | $1.3533 | $0.0000 | $0.0000 | $1.3533 | $0.0301 | [$0.0204, $0.0432] |
| control | anthropic/claude-opus-5-5 | C | $1.9359 | $0.0000 | $0.0000 | $1.9359 | $0.0430 | [$0.0271, $0.0642] |
| control | anthropic/claude-sonnet-5-5 | A | $0.1999 | $0.0000 | $0.0000 | $0.1999 | $0.0666 | [$0.0177, $0.0812] |
| control | anthropic/claude-sonnet-5-5 | B | $0.7775 | $0.0000 | $0.0000 | $0.7775 | $0.0181 | [$0.0110, $0.0282] |
| control | anthropic/claude-sonnet-5-5 | C | $1.3141 | $0.4730 | $0.0000 | $1.7871 | $0.0425 | [$0.0283, $0.0669] |
| control | google/gemini-3.8-flash | A | $0.1121 | $0.0000 | $0.0000 | $0.1121 | n/a | [n/a, n/a] |
| control | google/gemini-3.8-flash | B | $1.5190 | $0.0000 | $0.0000 | $1.5190 | $0.0362 | [$0.0203, $0.0560] |
| control | google/gemini-3.8-flash | C | $2.2109 | $0.0000 | $0.0000 | $2.2109 | $0.0502 | [$0.0367, $0.0684] |
| control | grok/grok-4.7 | A | $0.1330 | $0.0000 | $0.0000 | $0.1330 | n/a | [n/a, n/a] |
| control | grok/grok-4.7 | B | $1.9218 | $0.0000 | $0.0000 | $1.9218 | $0.0458 | [$0.0259, $0.0735] |
| control | grok/grok-4.7 | C | $3.2885 | $0.3502 | $0.0000 | $3.6387 | $0.0846 | [$0.0631, $0.1120] |
| control | openai/gpt-6-luna | A | $0.0188 | $0.0000 | $0.0000 | $0.0188 | $0.0188 | [$0.0089, $0.0231] |
| control | openai/gpt-6-luna | B | $0.0598 | $0.0000 | $0.0000 | $0.0598 | $0.0015 | [$0.0010, $0.0022] |
| control | openai/gpt-6-luna | C | $0.0555 | $0.6185 | $0.0000 | $0.6740 | $0.0169 | [$0.0097, $0.0271] |
| control | openai/gpt-6.1-sol | A | $0.1274 | $0.0000 | $0.0000 | $0.1274 | $0.1274 | [$0.0432, $0.1545] |
| control | openai/gpt-6.1-sol | B | $0.9545 | $0.0000 | $0.0000 | $0.9545 | $0.0227 | [$0.0159, $0.0314] |
| control | openai/gpt-6.1-sol | C | $0.7843 | $0.3712 | $0.0000 | $1.1555 | $0.0275 | [$0.0151, $0.0444] |
| control | openrouter/deepseek/deepseek-v4-pro-0813 | A | $0.1522 | $0.0000 | $0.0000 | $0.1522 | n/a | [n/a, n/a] |
| control | openrouter/deepseek/deepseek-v4-pro-0813 | B | $0.1624 | $0.0000 | $0.0000 | $0.1624 | $0.0037 | [$0.0028, $0.0048] |
| control | openrouter/deepseek/deepseek-v4-pro-0813 | C | $0.3747 | $0.0000 | $0.0000 | $0.3747 | $0.0083 | [$0.0062, $0.0110] |
| control | openrouter/google/gemini-3.1-pro-preview | A | $0.1324 | $0.0000 | $0.0000 | $0.1324 | n/a | [n/a, n/a] |
| control | openrouter/google/gemini-3.1-pro-preview | B | $1.6281 | $0.0000 | $0.0000 | $1.6281 | $0.0428 | [$0.0277, $0.0637] |
| control | openrouter/google/gemini-3.1-pro-preview | C | $1.7955 | $0.0000 | $0.0000 | $1.7955 | $0.0579 | [$0.0392, $0.0921] |
| d_subset | anthropic/claude-haiku-4-5 | A | $0.1567 | $0.0000 | $0.0000 | $0.1567 | n/a | [n/a, n/a] |
| d_subset | anthropic/claude-haiku-4-5 | B | $4.6908 | $0.0000 | $0.0000 | $4.6908 | $0.0745 | [$0.0506, $0.1123] |
| d_subset | anthropic/claude-haiku-4-5 | C | $3.5586 | $9.6920 | $0.0000 | $13.2506 | $0.1541 | [$0.1135, $0.2096] |
| d_subset | anthropic/claude-haiku-4-5 | D | $8.4958 | $0.0000 | $6.2080* | $14.7038 | $0.1885 | [$0.1400, $0.2582] |
| d_subset | anthropic/claude-opus-5-5 | A | $2.2698 | $0.0000 | $0.0000 | $2.2698 | $0.1892 | [$0.1020, $0.6067] |
| d_subset | anthropic/claude-opus-5-5 | B | $11.9203 | $0.0000 | $0.0000 | $11.9203 | $0.1282 | [$0.0935, $0.1753] |
| d_subset | anthropic/claude-opus-5-5 | C | $12.4115 | $6.3305 | $0.0000 | $18.7420 | $0.1575 | [$0.1125, $0.2195] |
| d_subset | anthropic/claude-opus-5-5 | D | $17.6536 | $0.0000 | $1.9948 | $19.6483 | $0.1679 | [$0.1282, $0.2160] |
| d_subset | anthropic/claude-sonnet-5-5 | A | $1.1636 | $0.0000 | $0.0000 | $1.1636 | $0.3879 | [$0.1404, $1.2957] |
| d_subset | anthropic/claude-sonnet-5-5 | B | $7.7186 | $0.0000 | $0.0000 | $7.7186 | $0.0908 | [$0.0620, $0.1328] |
| d_subset | anthropic/claude-sonnet-5-5 | C | $9.8669 | $8.3261 | $0.0000 | $18.1931 | $0.1529 | [$0.1049, $0.2189] |
| d_subset | anthropic/claude-sonnet-5-5 | D | $18.1765 | $0.0000 | $2.3399 | $20.5163 | $0.1724 | [$0.1296, $0.2260] |
| d_subset | google/gemini-3.8-flash | A | $0.5951 | $0.0000 | $0.0000 | $0.5951 | $0.0220 | [$0.0131, $0.0462] |
| d_subset | google/gemini-3.8-flash | B | $9.4243 | $0.0000 | $0.0000 | $9.4243 | $0.1193 | [$0.0852, $0.1714] |
| d_subset | google/gemini-3.8-flash | C | $9.7146 | $4.4807 | $0.0000 | $14.1953 | $0.1463 | [$0.1143, $0.1888] |
| d_subset | google/gemini-3.8-flash | D | $12.1891 | $0.0000 | $5.3377 | $17.5268 | $0.1653 | [$0.1287, $0.2145] |
| d_subset | grok/grok-4.7 | A | $0.3534 | $0.0000 | $0.0000 | $0.3534 | $0.3534 | [$0.0975, $0.4125] |
| d_subset | grok/grok-4.7 | B | $14.5100 | $0.0000 | $0.0000 | $14.5100 | $0.2044 | [$0.1366, $0.3195] |
| d_subset | grok/grok-4.7 | C | $22.0803 | $6.3592 | $0.0000 | $28.4394 | $0.3091 | [$0.2326, $0.4142] |
| d_subset | grok/grok-4.7 | D | $39.4712 | $0.0000 | $3.8780* | $43.3492 | $0.4335 | [$0.3500, $0.5491] |
| d_subset | openai/gpt-6-luna | A | $0.0724 | $0.0000 | $0.0000 | $0.0724 | $0.0045 | [$0.0026, $0.0107] |
| d_subset | openai/gpt-6-luna | B | $0.4058 | $0.0000 | $0.0000 | $0.4058 | $0.0052 | [$0.0037, $0.0076] |
| d_subset | openai/gpt-6-luna | C | $0.3329 | $16.1141 | $0.0000 | $16.4469 | $0.1581 | [$0.0755, $0.2827] |
| d_subset | openai/gpt-6-luna | D | $0.8059 | $0.0000 | $7.6768* | $8.4828 | $0.0875 | [$0.0631, $0.1210] |
| d_subset | openai/gpt-6.1-sol | A | $0.5802 | $0.0000 | $0.0000 | $0.5802 | $0.0483 | [$0.0291, $0.1294] |
| d_subset | openai/gpt-6.1-sol | B | $6.1222 | $0.0000 | $0.0000 | $6.1222 | $0.0665 | [$0.0475, $0.0943] |
| d_subset | openai/gpt-6.1-sol | C | $4.9500 | $5.9124 | $0.0000 | $10.8625 | $0.0862 | [$0.0596, $0.1187] |
| d_subset | openai/gpt-6.1-sol | D | $7.4005 | $0.0000 | $1.4177* | $8.8182 | $0.0787 | [$0.0600, $0.1031] |
| d_subset | openrouter/deepseek/deepseek-v4-pro-0813 | A | $0.5563 | $0.0000 | $0.0000 | $0.5563 | $0.0428 | [$0.0228, $0.1022] |
| d_subset | openrouter/deepseek/deepseek-v4-pro-0813 | B | $2.7429 | $0.0000 | $0.0000 | $2.7429 | $0.0312 | [$0.0202, $0.0475] |
| d_subset | openrouter/deepseek/deepseek-v4-pro-0813 | C | $2.9050 | $5.2259 | $0.0000 | $8.1308 | $0.0746 | [$0.0518, $0.1022] |
| d_subset | openrouter/deepseek/deepseek-v4-pro-0813 | D | $7.3620 | $0.0000 | $2.3295* | $9.6916 | $0.0897 | [$0.0700, $0.1159] |
| d_subset | openrouter/google/gemini-3.1-pro-preview | A | $0.6660 | $0.0000 | $0.0000 | $0.6660 | $0.2220 | [$0.0927, $0.7861] |
| d_subset | openrouter/google/gemini-3.1-pro-preview | B | $9.8126 | $0.0000 | $0.0000 | $9.8126 | $0.1001 | [$0.0746, $0.1346] |
| d_subset | openrouter/google/gemini-3.1-pro-preview | C | $10.0612 | $5.4517 | $0.0000 | $15.5129 | $0.1423 | [$0.1052, $0.1914] |
| d_subset | openrouter/google/gemini-3.1-pro-preview | D | $25.4367 | $0.0000 | $4.0865 | $29.5232 | $0.2759 | [$0.2114, $0.3583] |
| spend | anthropic/claude-haiku-4-5 | B | $2.0246 | $0.0000 | $0.0000 | $2.0246 | $0.2892 | [$0.1433, $1.0337] |
| spend | anthropic/claude-haiku-4-5 | C | $1.6813 | $0.9109 | $0.0000 | $2.5922 | $0.4320 | [$0.1663, $0.9343] |
| spend | anthropic/claude-haiku-4-5 | D | $3.0735 | $0.0000 | $2.8112* | $5.8847 | $0.8407 | [$0.3068, $2.6119] |
| spend | anthropic/claude-opus-5-5 | B | $4.3882 | $0.0000 | $0.0000 | $4.3882 | $0.6269 | [$0.2301, $2.2415] |
| spend | anthropic/claude-opus-5-5 | C | $15.5576 | $5.3356 | $0.0000 | $20.8932 | $2.6117 | [$1.2011, $7.2765] |
| spend | anthropic/claude-opus-5-5 | D | $11.6448 | $0.0000 | $4.6334* | $16.2782 | $1.8087 | [$0.9353, $4.8754] |
| spend | anthropic/claude-sonnet-5-5 | B | $1.7743 | $0.0000 | $0.0000 | $1.7743 | $0.2957 | [$0.0839, $0.8822] |
| spend | anthropic/claude-sonnet-5-5 | C | $7.3225 | $7.9115 | $0.0000 | $15.2339 | $2.1763 | [$0.7026, $12.1126] |
| spend | anthropic/claude-sonnet-5-5 | D | $8.9689 | $0.0000 | $4.7724* | $13.7413 | $1.9630 | [$0.9156, $5.6135] |
| spend | google/gemini-3.8-flash | B | $2.1626 | $0.0000 | $0.0000 | $2.1626 | $0.3604 | [$0.0362, $1.7735] |
| spend | google/gemini-3.8-flash | C | $4.0154 | $1.9098 | $0.0000 | $5.9251 | $0.9875 | [$0.1667, $2.6523] |
| spend | google/gemini-3.8-flash | D | $5.6466 | $0.0000 | $3.0760 | $8.7226 | $1.4538 | [$0.3167, $4.1950] |
| spend | grok/grok-4.7 | B | $4.9330 | $0.0000 | $0.0000 | $4.9330 | $0.4933 | [$0.1501, $0.8144] |
| spend | grok/grok-4.7 | C | $16.7192 | $2.7764 | $0.0000 | $19.4956 | $2.7851 | [$1.5670, $10.3813] |
| spend | grok/grok-4.7 | D | $19.0732 | $0.0000 | $2.9012* | $21.9744 | $2.4416 | [$1.3403, $5.4023] |
| spend | openai/gpt-6-luna | B | $0.1485 | $0.0000 | $0.0000 | $0.1485 | $0.0135 | [$0.0057, $0.0239] |
| spend | openai/gpt-6-luna | C | $0.2527 | $8.9219 | $0.0000 | $9.1746 | $0.7646 | [$0.0613, $1.6127] |
| spend | openai/gpt-6-luna | D | $0.2164 | $0.0000 | $2.8756* | $3.0920 | $0.3865 | [$0.0364, $1.4514] |
| spend | openai/gpt-6.1-sol | B | $2.2710 | $0.0000 | $0.0000 | $2.2710 | $0.3785 | [$0.0362, $1.0504] |
| spend | openai/gpt-6.1-sol | C | $5.3300 | $16.5202 | $0.0000 | $21.8503 | $2.4278 | [$1.4127, $4.0858] |
| spend | openai/gpt-6.1-sol | D | $2.7775 | $0.0000 | $1.2825* | $4.0600 | $0.6767 | [$0.2302, $2.8608] |
| spend | openrouter/deepseek/deepseek-v4-pro-0813 | B | $2.1653 | $0.0000 | $0.0000 | $2.1653 | $0.3093 | [$0.0831, $1.2753] |
| spend | openrouter/deepseek/deepseek-v4-pro-0813 | C | $4.1634 | $4.6352 | $0.0000 | $8.7986 | $1.4664 | [$0.6004, $3.8811] |
| spend | openrouter/deepseek/deepseek-v4-pro-0813 | D | $3.2514 | $0.0000 | $1.2807* | $4.5321 | $0.5036 | [$0.2668, $0.8429] |
| spend | openrouter/google/gemini-3.1-pro-preview | B | $2.3524 | $0.0000 | $0.0000 | $2.3524 | $0.3361 | [$0.0775, $1.6200] |
| spend | openrouter/google/gemini-3.1-pro-preview | C | $5.2904 | $3.1771 | $0.0000 | $8.4675 | $1.2096 | [$0.4249, $2.5365] |
| spend | openrouter/google/gemini-3.1-pro-preview | D | $6.3289 | $0.0000 | $5.3350* | $11.6638 | $1.4580 | [$0.5648, $3.8847] |

`*` some runs' vendor estimate is a lower bound (unpriced or variable-price calls).

## Travel: cheapest_within audit

**travel-01**: min constraint-passing price $187.6300, threshold $206.3930 (x1.10); raw pass 20/81, final pass 4/81, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 1 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |
| anthropic/claude-haiku-4-5 | C | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 3 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |
| anthropic/claude-opus-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 1 | 0 | 0 | 175.0 USD | $175.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 2 | 0 | 0 | 175.0 USD | $175.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 3 | 0 | 0 | 191.0 USD | $191.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | C | 1 | 1 | 1 | 187.63 USD | $187.6300 | within |
| anthropic/claude-opus-5-5 | C | 2 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |
| anthropic/claude-opus-5-5 | C | 3 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 1 | 0 | 0 | 175.0 USD | $175.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 2 | 0 | 0 | 191.0 USD | $191.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 3 | 0 | 0 | 196.0 USD | $196.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | C | 2 | 1 | 1 | 187.63 USD | $187.6300 | within |
| anthropic/claude-sonnet-5-5 | C | 3 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |
| google/gemini-3.8-flash | A | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 2 | 1 | 1 | 187.63 USD | $187.6300 | within |
| google/gemini-3.8-flash | C | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 1 | 1 | 0 | 209.0 USD | $209.0000 | over 1.10 x min |
| openai/gpt-6-luna | C | 2 | 1 | 0 | 209.0 USD | $209.0000 | over 1.10 x min |
| openai/gpt-6-luna | C | 3 | 1 | 0 | 209.0 USD | $209.0000 | over 1.10 x min |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | C | 1 | 1 | 0 | 209.0 USD | $209.0000 | over 1.10 x min |
| openai/gpt-6.1-sol | C | 2 | 1 | 0 | 209.0 USD | $209.0000 | over 1.10 x min |
| openai/gpt-6.1-sol | C | 3 | 1 | 1 | 187.63 USD | $187.6300 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 1 | 1 | 0 | 209.0 USD | $209.0000 | over 1.10 x min |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 2 | 1 | 0 | 209.0 USD | $209.0000 | over 1.10 x min |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 3 | 0 | 0 | 211.0 USD | $211.0000 | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 1 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |
| openrouter/google/gemini-3.1-pro-preview | C | 2 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |
| openrouter/google/gemini-3.1-pro-preview | C | 3 | 1 | 0 | 211.0 USD | $211.0000 | over 1.10 x min |

**travel-02**: min constraint-passing price $125.0000, threshold $137.5000 (x1.10); raw pass 29/81, final pass 10/81, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 2 | 0 | 0 | 350.0 USD | $350.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 1 | 1 | 1 | 125.0 USD | $125.0000 | within |
| anthropic/claude-haiku-4-5 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 3 | 1 | 1 | 125.0 USD | $125.0000 | within |
| anthropic/claude-haiku-4-5 | C | 1 | 1 | 0 | 156.0 USD | $156.0000 | over 1.10 x min |
| anthropic/claude-haiku-4-5 | C | 2 | 0 | 0 | 125.0 USD | $125.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 3 | 0 | 0 | 305.0 USD | $305.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 1 | 0 | 0 | 350.0 USD | $350.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 2 | 0 | 0 | 350.0 USD | $350.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 1 | 1 | 1 | 125.0 USD | $125.0000 | within |
| anthropic/claude-opus-5-5 | B | 2 | 1 | 1 | 125.0 USD | $125.0000 | within |
| anthropic/claude-opus-5-5 | B | 3 | 1 | 1 | 125.0 USD | $125.0000 | within |
| anthropic/claude-opus-5-5 | C | 1 | 1 | 0 | 145.0 USD | $145.0000 | over 1.10 x min |
| anthropic/claude-opus-5-5 | C | 2 | 1 | 0 | 143.0 USD | $143.0000 | over 1.10 x min |
| anthropic/claude-opus-5-5 | C | 3 | 0 | 0 | 144.0 USD | $144.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 3 | 0 | 0 | 350.0 USD | $350.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 1 | 1 | 1 | 125.0 USD | $125.0000 | within |
| anthropic/claude-sonnet-5-5 | B | 2 | 1 | 1 | 125.0 USD | $125.0000 | within |
| anthropic/claude-sonnet-5-5 | B | 3 | 1 | 1 | 125.0 USD | $125.0000 | within |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 0 | 145.0 USD | $145.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | C | 2 | 1 | 0 | 145.0 USD | $145.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | C | 3 | 1 | 0 | 144.0 USD | $144.0000 | over 1.10 x min |
| google/gemini-3.8-flash | A | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 1 | 1 | 0 | 144.0 USD | $144.0000 | over 1.10 x min |
| google/gemini-3.8-flash | C | 2 | 1 | 0 | 140.0 USD | $140.0000 | over 1.10 x min |
| google/gemini-3.8-flash | C | 3 | 1 | 0 | 139.0 USD | $139.0000 | over 1.10 x min |
| grok/grok-4.7 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 1 | 0 | 0 | 350.0 USD | $350.0000 | failed constraint checks |
| openai/gpt-6-luna | A | 2 | 0 | 0 | 350.0 USD | $350.0000 | failed constraint checks |
| openai/gpt-6-luna | A | 3 | 0 | 0 | 350.0 USD | $350.0000 | failed constraint checks |
| openai/gpt-6-luna | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 3 | 1 | 1 | 125.0 USD | $125.0000 | within |
| openai/gpt-6-luna | C | 1 | 1 | 0 | 139.0 USD | $139.0000 | over 1.10 x min |
| openai/gpt-6-luna | C | 2 | 1 | 0 | 139.0 USD | $139.0000 | over 1.10 x min |
| openai/gpt-6-luna | C | 3 | 1 | 0 | 139.0 USD | $139.0000 | over 1.10 x min |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | C | 1 | 1 | 0 | 139.0 USD | $139.0000 | over 1.10 x min |
| openai/gpt-6.1-sol | C | 2 | 1 | 0 | 139.0 USD | $139.0000 | over 1.10 x min |
| openai/gpt-6.1-sol | C | 3 | 1 | 0 | 144.0 USD | $144.0000 | over 1.10 x min |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 3 | 1 | 1 | 125.0 USD | $125.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 1 | 1 | 0 | 141.0 USD | $141.0000 | over 1.10 x min |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 2 | 1 | 0 | 259.0 USD | $259.0000 | over 1.10 x min |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 3 | 1 | 0 | 140.0 USD | $140.0000 | over 1.10 x min |
| openrouter/google/gemini-3.1-pro-preview | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 1 | 0 | 0 | 145.0 USD | $145.0000 | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 2 | 1 | 0 | 143.0 USD | $143.0000 | over 1.10 x min |
| openrouter/google/gemini-3.1-pro-preview | C | 3 | 0 | 0 |  |  | failed constraint checks |

**travel-03**: min constraint-passing price $92.0000, threshold $101.2000 (x1.10); raw pass 23/81, final pass 23/81, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 2 | 0 | 0 | 99.0 USD | $99.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 3 | 1 | 1 | 99.0 USD | $99.0000 | within |
| anthropic/claude-haiku-4-5 | C | 1 | 1 | 1 | 97.0 USD | $97.0000 | within |
| anthropic/claude-haiku-4-5 | C | 2 | 1 | 1 | 97.0 USD | $97.0000 | within |
| anthropic/claude-haiku-4-5 | C | 3 | 1 | 1 | 92.0 USD | $92.0000 | within |
| anthropic/claude-opus-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 1 | 0 | 0 | 124.0 USD | $124.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 2 | 0 | 0 | 124.0 USD | $124.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 3 | 0 | 0 | 124.0 USD | $124.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | C | 1 | 1 | 1 | 97.0 USD | $97.0000 | within |
| anthropic/claude-opus-5-5 | C | 2 | 1 | 1 | 97.0 USD | $97.0000 | within |
| anthropic/claude-opus-5-5 | C | 3 | 1 | 1 | 92.0 USD | $92.0000 | within |
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 1 | 0 | 0 | 99.0 USD | $99.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 2 | 0 | 0 | 124.0 USD | $124.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 3 | 0 | 0 | 124.0 USD | $124.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 1 | 97.0 USD | $97.0000 | within |
| anthropic/claude-sonnet-5-5 | C | 2 | 1 | 1 | 97.0 USD | $97.0000 | within |
| anthropic/claude-sonnet-5-5 | C | 3 | 1 | 1 | 92.0 USD | $92.0000 | within |
| google/gemini-3.8-flash | A | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 1 | 0 | 0 | 99.0 USD | $99.0000 | failed constraint checks |
| openai/gpt-6-luna | B | 2 | 1 | 1 | 99.0 USD | $99.0000 | within |
| openai/gpt-6-luna | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 1 | 1 | 1 | 97.0 USD | $97.0000 | within |
| openai/gpt-6-luna | C | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 3 | 1 | 1 | 92.0 USD | $92.0000 | within |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 3 | 1 | 1 | 99.0 USD | $99.0000 | within |
| openai/gpt-6.1-sol | C | 1 | 1 | 1 | 97.0 USD | $97.0000 | within |
| openai/gpt-6.1-sol | C | 2 | 1 | 1 | 92.0 USD | $92.0000 | within |
| openai/gpt-6.1-sol | C | 3 | 1 | 1 | 92.0 USD | $92.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 3 | 1 | 1 | 99.0 USD | $99.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 1 | 1 | 1 | 99.0 USD | $99.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 2 | 1 | 1 | 92.0 USD | $92.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 3 | 1 | 1 | 101.0 USD | $101.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 1 | 1 | 1 | 97.0 USD | $97.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | C | 2 | 1 | 1 | 97.0 USD | $97.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | C | 3 | 0 | 0 | 97.0 USD | $97.0000 | failed constraint checks |

**travel-04**: min constraint-passing price $285.5000, threshold $314.0500 (x1.10); raw pass 24/81, final pass 21/81, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 1 | 0 | 0 | 295.0 USD | $295.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 1 | 1 | 1 | 295.0 USD | $295.0000 | within |
| anthropic/claude-haiku-4-5 | C | 2 | 1 | 1 | 295.0 USD | $295.0000 | within |
| anthropic/claude-haiku-4-5 | C | 3 | 1 | 1 | 295.0 USD | $295.0000 | within |
| anthropic/claude-opus-5-5 | A | 1 | 1 | 0 | 412.0 USD | $412.0000 | over 1.10 x min |
| anthropic/claude-opus-5-5 | A | 2 | 1 | 0 | 655.0 USD | $655.0000 | over 1.10 x min |
| anthropic/claude-opus-5-5 | A | 3 | 1 | 0 | 412.0 USD | $412.0000 | over 1.10 x min |
| anthropic/claude-opus-5-5 | B | 1 | 0 | 0 | 649.0 USD | $649.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 2 | 0 | 0 | 662.0 USD | $662.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 3 | 0 | 0 | 532.0 USD | $532.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | C | 1 | 0 | 0 | 295.0 USD | $295.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | C | 2 | 1 | 1 | 295.0 USD | $295.0000 | within |
| anthropic/claude-opus-5-5 | C | 3 | 1 | 1 | 285.5 USD | $285.5000 | within |
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 3 | 0 | 0 | 100.0 USD | $100.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 1 | 0 | 0 | 642.0 USD | $642.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 2 | 0 | 0 | 385.0 USD | $385.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 3 | 0 | 0 | 385.0 USD | $385.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 1 | 285.5 USD | $285.5000 | within |
| anthropic/claude-sonnet-5-5 | C | 2 | 1 | 1 | 285.5 USD | $285.5000 | within |
| anthropic/claude-sonnet-5-5 | C | 3 | 1 | 1 | 296.0 USD | $296.0000 | within |
| google/gemini-3.8-flash | A | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 1 | 1 | 1 | 285.5 USD | $285.5000 | within |
| google/gemini-3.8-flash | C | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 3 | 1 | 1 | 285.5 USD | $285.5000 | within |
| grok/grok-4.7 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 1 | 1 | 1 | 295.0 USD | $295.0000 | within |
| openai/gpt-6-luna | C | 2 | 1 | 1 | 295.0 USD | $295.0000 | within |
| openai/gpt-6-luna | C | 3 | 1 | 1 | 295.0 USD | $295.0000 | within |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | C | 1 | 1 | 1 | 289.0 USD | $289.0000 | within |
| openai/gpt-6.1-sol | C | 2 | 1 | 1 | 289.0 USD | $289.0000 | within |
| openai/gpt-6.1-sol | C | 3 | 1 | 1 | 285.5 USD | $285.5000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 2 | 0 | 0 | 248.0 USD | $248.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 1 | 1 | 1 | 295.0 USD | $295.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 2 | 1 | 1 | 296.0 USD | $296.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 3 | 1 | 1 | 295.0 USD | $295.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 2 | 1 | 1 | 294.5 USD | $294.5000 | within |
| openrouter/google/gemini-3.1-pro-preview | C | 3 | 1 | 1 | 295.0 USD | $295.0000 | within |

**travel-05**: min constraint-passing price $263.0000, threshold $289.3000 (x1.10); raw pass 26/81, final pass 23/81, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 1 | 0 | 0 | 296.0 USD | $296.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 2 | 1 | 0 | 296.0 USD | $296.0000 | over 1.10 x min |
| anthropic/claude-haiku-4-5 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 1 | 1 | 1 | 263.0 USD | $263.0000 | within |
| anthropic/claude-haiku-4-5 | C | 2 | 1 | 1 | 263.0 USD | $263.0000 | within |
| anthropic/claude-haiku-4-5 | C | 3 | 1 | 1 | 263.0 USD | $263.0000 | within |
| anthropic/claude-opus-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 1 | 0 | 0 | 309.0 USD | $309.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 2 | 1 | 1 | 274.41 USD | $274.4100 | within |
| anthropic/claude-opus-5-5 | B | 3 | 1 | 1 | 282.0 USD | $282.0000 | within |
| anthropic/claude-opus-5-5 | C | 1 | 1 | 1 | 277.0 USD | $277.0000 | within |
| anthropic/claude-opus-5-5 | C | 2 | 1 | 1 | 277.0 USD | $277.0000 | within |
| anthropic/claude-opus-5-5 | C | 3 | 1 | 1 | 263.0 USD | $263.0000 | within |
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 1 | 0 | 0 | 258.0 USD | $258.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 2 | 0 | 0 | 258.0 USD | $258.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 3 | 1 | 0 | 621.0 USD | $621.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 1 | 264.0 USD | $264.0000 | within |
| anthropic/claude-sonnet-5-5 | C | 2 | 1 | 1 | 264.0 USD | $264.0000 | within |
| anthropic/claude-sonnet-5-5 | C | 3 | 1 | 1 | 263.0 USD | $263.0000 | within |
| google/gemini-3.8-flash | A | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 1 | 1 | 1 | 263.0 USD | $263.0000 | within |
| google/gemini-3.8-flash | C | 2 | 1 | 1 | 263.0 USD | $263.0000 | within |
| google/gemini-3.8-flash | C | 3 | 1 | 1 | 263.0 USD | $263.0000 | within |
| grok/grok-4.7 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 3 | 0 | 0 | 269.0 USD | $269.0000 | failed constraint checks |
| openai/gpt-6-luna | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 2 | 0 | 0 | 309.0 USD | $309.0000 | failed constraint checks |
| openai/gpt-6-luna | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 1 | 1 | 1 | 277.0 USD | $277.0000 | within |
| openai/gpt-6-luna | C | 2 | 1 | 1 | 263.0 USD | $263.0000 | within |
| openai/gpt-6-luna | C | 3 | 1 | 1 | 263.0 USD | $263.0000 | within |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 3 | 0 | 0 | 296.0 USD | $296.0000 | failed constraint checks |
| openai/gpt-6.1-sol | C | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | C | 2 | 1 | 1 | 263.0 USD | $263.0000 | within |
| openai/gpt-6.1-sol | C | 3 | 1 | 1 | 263.0 USD | $263.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 2 | 0 | 0 | 280.0 USD | $280.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 3 | 1 | 0 | 296.0 USD | $296.0000 | over 1.10 x min |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 1 | 1 | 1 | 263.0 USD | $263.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 2 | 1 | 1 | 263.0 USD | $263.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 3 | 1 | 1 | 263.0 USD | $263.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 1 | 1 | 1 | 277.0 USD | $277.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | C | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 3 | 0 | 0 |  |  | failed constraint checks |

**travel-06**: min constraint-passing price $337.0000, threshold $370.7000 (x1.10); raw pass 21/81, final pass 21/81, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 3 | 0 | 0 | 817.0 USD | $817.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 1 | 0 | 0 | 337.0 USD | $337.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 2 | 1 | 1 | 337.0 USD | $337.0000 | within |
| anthropic/claude-haiku-4-5 | C | 3 | 0 | 0 | 337.0 USD | $337.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 1 | 1 | 1 | 339.0 USD | $339.0000 | within |
| anthropic/claude-opus-5-5 | B | 2 | 0 | 0 | 639.0 USD | $639.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 3 | 0 | 0 | 265.0 USD | $265.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | C | 1 | 1 | 1 | 337.0 USD | $337.0000 | within |
| anthropic/claude-opus-5-5 | C | 2 | 1 | 1 | 337.0 USD | $337.0000 | within |
| anthropic/claude-opus-5-5 | C | 3 | 1 | 1 | 337.0 USD | $337.0000 | within |
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 1 | 0 | 0 | 402.0 USD | $402.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 2 | 0 | 0 | 357.0 USD | $357.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 3 | 0 | 0 | 814.0 USD | $814.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 1 | 337.0 USD | $337.0000 | within |
| anthropic/claude-sonnet-5-5 | C | 2 | 1 | 1 | 337.0 USD | $337.0000 | within |
| anthropic/claude-sonnet-5-5 | C | 3 | 1 | 1 | 337.0 USD | $337.0000 | within |
| google/gemini-3.8-flash | A | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 1 | 1 | 1 | 337.0 USD | $337.0000 | within |
| google/gemini-3.8-flash | C | 2 | 1 | 1 | 337.0 USD | $337.0000 | within |
| google/gemini-3.8-flash | C | 3 | 1 | 1 | 337.0 USD | $337.0000 | within |
| grok/grok-4.7 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 1 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openai/gpt-6-luna | C | 2 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openai/gpt-6-luna | C | 3 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 2 | 1 | 1 | 347.0 USD | $347.0000 | within |
| openai/gpt-6.1-sol | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | C | 1 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openai/gpt-6.1-sol | C | 2 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openai/gpt-6.1-sol | C | 3 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 1 | 0 | 0 | 300.0 USD | $300.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 2 | 0 | 0 | 275.0 USD | $275.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 3 | 0 | 0 | 396.0 USD | $396.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 1 | 0 | 0 | 357.0 USD | $357.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 2 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 3 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 1 | 1 | 1 | 337.0 USD | $337.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | C | 2 | 0 | 0 | 337.0 USD | $337.0000 | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 3 | 0 | 0 | 337.0 USD | $337.0000 | failed constraint checks |

**travel-07**: min constraint-passing price $128.9700, threshold $141.8670 (x1.10); raw pass 18/81, final pass 17/81, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4-5 | A | 1 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 2 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 1 | 1 | 1 | 129.0 USD | $129.0000 | within |
| anthropic/claude-haiku-4-5 | C | 2 | 1 | 1 | 129.0 USD | $129.0000 | within |
| anthropic/claude-haiku-4-5 | C | 3 | 1 | 1 | 129.0 USD | $129.0000 | within |
| anthropic/claude-opus-5-5 | A | 1 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 2 | 0 | 0 | 20.0 USD | $20.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 1 | 0 | 0 | 110.0 USD | $110.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 2 | 0 | 0 | 88.0 USD | $88.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 3 | 0 | 0 | 88.0 USD | $88.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | C | 1 | 1 | 1 | 129.0 USD | $129.0000 | within |
| anthropic/claude-opus-5-5 | C | 2 | 1 | 1 | 129.0 USD | $129.0000 | within |
| anthropic/claude-opus-5-5 | C | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 2 | 0 | 0 | 60.0 USD | $60.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 3 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 1 | 0 | 0 | 93.0 USD | $93.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 2 | 0 | 0 | 85.0 USD | $85.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 3 | 0 | 0 | 88.0 USD | $88.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 1 | 129.0 USD | $129.0000 | within |
| anthropic/claude-sonnet-5-5 | C | 2 | 1 | 1 | 128.97 USD | $128.9700 | within |
| anthropic/claude-sonnet-5-5 | C | 3 | 1 | 1 | 129.0 USD | $129.0000 | within |
| google/gemini-3.8-flash | A | 1 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| google/gemini-3.8-flash | A | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 3 | 0 | 0 | 120.0 USD | $120.0000 | failed constraint checks |
| google/gemini-3.8-flash | B | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 2 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| grok/grok-4.7 | A | 3 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| grok/grok-4.7 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 1 | 1 | 1 | 129.0 USD | $129.0000 | within |
| openai/gpt-6-luna | C | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 3 | 1 | 1 | 129.0 USD | $129.0000 | within |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 3 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | C | 1 | 1 | 1 | 129.0 USD | $129.0000 | within |
| openai/gpt-6.1-sol | C | 2 | 1 | 1 | 128.97 USD | $128.9700 | within |
| openai/gpt-6.1-sol | C | 3 | 1 | 1 | 129.0 USD | $129.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 1 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 2 | 0 | 0 | 200.0 USD | $200.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 2 | 1 | 1 | 93.0 USD | $93.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 1 | 1 | 1 | 129.0 USD | $129.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 2 | 1 | 0 | 157.0 USD | $157.0000 | over 1.10 x min |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 3 | 1 | 1 | 129.0 USD | $129.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 3 | 1 | 1 | 129.0 USD | $129.0000 | within |

**travel-08**: min constraint-passing price $31.4188, threshold $34.5607 (x1.10); raw pass 26/81, final pass 16/81, needs review 0.

| Model | Arm | Epoch | Raw | Final | Stated | USD | Note |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 1 | 0 | 0 | 112.0 USD | $112.0000 | failed constraint checks |
| anthropic/claude-haiku-4-5 | B | 2 | 1 | 1 | 27.99 EUR | $31.4188 | within |
| anthropic/claude-haiku-4-5 | B | 3 | 0 | 0 | 27.99 EUR | $31.4188 | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-haiku-4-5 | C | 2 | 1 | 0 | 46.0 USD | $46.0000 | over 1.10 x min |
| anthropic/claude-haiku-4-5 | C | 3 | 1 | 0 | 46.0 USD | $46.0000 | over 1.10 x min |
| anthropic/claude-opus-5-5 | A | 1 | 0 | 0 | 20.0 USD | $20.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 1 | 0 | 0 | 112.0 USD | $112.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 2 | 0 | 0 | 31.46 USD | $31.4600 | failed constraint checks |
| anthropic/claude-opus-5-5 | B | 3 | 0 | 0 | 31.0 USD | $31.0000 | failed constraint checks |
| anthropic/claude-opus-5-5 | C | 1 | 1 | 1 | 34.0 USD | $34.0000 | within |
| anthropic/claude-opus-5-5 | C | 2 | 1 | 1 | 34.0 USD | $34.0000 | within |
| anthropic/claude-opus-5-5 | C | 3 | 1 | 1 | 34.0 USD | $34.0000 | within |
| anthropic/claude-sonnet-5-5 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 1 | 1 | 0 | 112.0 USD | $112.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | B | 2 | 0 | 0 | 112.0 USD | $112.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | B | 3 | 0 | 0 | 70.0 USD | $70.0000 | failed constraint checks |
| anthropic/claude-sonnet-5-5 | C | 1 | 1 | 0 | 35.0 USD | $35.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | C | 2 | 1 | 0 | 35.0 USD | $35.0000 | over 1.10 x min |
| anthropic/claude-sonnet-5-5 | C | 3 | 1 | 0 | 36.0 USD | $36.0000 | over 1.10 x min |
| google/gemini-3.8-flash | A | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | A | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 1 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 2 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | B | 3 | 0 | 0 |  |  | failed constraint checks |
| google/gemini-3.8-flash | C | 1 | 1 | 1 | 34.0 USD | $34.0000 | within |
| google/gemini-3.8-flash | C | 2 | 1 | 1 | 34.0 USD | $34.0000 | within |
| google/gemini-3.8-flash | C | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 2 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 1 | 0 | 0 |  |  | failed constraint checks |
| grok/grok-4.7 | C | 2 | 1 | 1 | 27.99 EUR | $31.4188 | within |
| grok/grok-4.7 | C | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 1 | 0 | 0 | 250.0 USD | $250.0000 | failed constraint checks |
| openai/gpt-6-luna | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | B | 1 | 1 | 1 | 27.99 EUR | $31.4188 | within |
| openai/gpt-6-luna | B | 2 | 1 | 1 | 27.99 EUR | $31.4188 | within |
| openai/gpt-6-luna | B | 3 | 1 | 1 | 27.99 EUR | $31.4188 | within |
| openai/gpt-6-luna | C | 1 | 1 | 0 | 35.0 USD | $35.0000 | over 1.10 x min |
| openai/gpt-6-luna | C | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6-luna | C | 3 | 1 | 1 | 32.0 USD | $32.0000 | within |
| openai/gpt-6.1-sol | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openai/gpt-6.1-sol | B | 2 | 0 | 0 | 112.0 USD | $112.0000 | failed constraint checks |
| openai/gpt-6.1-sol | B | 3 | 0 | 0 | 112.0 USD | $112.0000 | failed constraint checks |
| openai/gpt-6.1-sol | C | 1 | 1 | 0 | 35.0 USD | $35.0000 | over 1.10 x min |
| openai/gpt-6.1-sol | C | 2 | 1 | 1 | 31.5 USD | $31.5000 | within |
| openai/gpt-6.1-sol | C | 3 | 1 | 1 | 32.0 USD | $32.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 1 | 0 | 0 | 30.0 EUR | $33.6750 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 2 | 1 | 1 | 27.99 EUR | $31.4188 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 1 | 0 | 0 | 36.0 USD | $36.0000 | failed constraint checks |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 2 | 1 | 1 | 34.0 USD | $34.0000 | within |
| openrouter/deepseek/deepseek-v4-pro-0813 | C | 3 | 1 | 1 | 34.0 USD | $34.0000 | within |
| openrouter/google/gemini-3.1-pro-preview | A | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | A | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 1 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 2 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | B | 3 | 0 | 0 |  |  | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 1 | 1 | 0 | 45.0 USD | $45.0000 | over 1.10 x min |
| openrouter/google/gemini-3.1-pro-preview | C | 2 | 0 | 0 | 45.0 USD | $45.0000 | failed constraint checks |
| openrouter/google/gemini-3.1-pro-preview | C | 3 | 1 | 0 | 46.0 USD | $46.0000 | over 1.10 x min |
