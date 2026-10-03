"""Offline unit tests for bench/analyze.py on synthetic data.

Run:   uv run --with pytest pytest bench/test_analyze.py -v
"""

import numpy as np
import pytest

from bench.analyze import (
    apply_flight_rule,
    battery_of,
    bootstrap_contrast,
    bootstrap_ratio,
    call_cost,
    contrast,
    extract_price,
    load_prices,
    parse_amount,
    pooled_mean,
    resample_counts,
    seed_int,
    usage_cost,
    wilson,
)

# --- bootstrap ------------------------------------------------------------------------------


def _synthetic_runs(rng, n_tasks=60, models=("m1", "m2", "m3"), effect=0.2, epochs=3):
    """Per-task base rates vary (clustered); arm C adds `effect` to every task's rate."""
    runs = []
    for t in range(n_tasks):
        base = rng.uniform(0.1, 0.7)
        for m in models:
            for arm, p in (("B", base), ("C", min(1.0, base + effect))):
                for e in range(epochs):
                    runs.append({"model": m, "arm": arm, "task": f"t{t:02d}", "epoch": e, "success": int(rng.random() < p)})
    return runs


def test_seed_is_fixed():
    assert seed_int() == seed_int("agent-access-bench-v1")
    assert seed_int() != seed_int("other")


def test_resample_counts_shape_and_determinism():
    W1, W2 = resample_counts(7, 100), resample_counts(7, 100)
    assert W1.shape == (100, 7) and np.all(W1.sum(axis=1) == 7)
    assert np.array_equal(W1, W2)


def test_pooled_mean_weights_models_equally():
    # model 1: 4 tasks all +1; model 2: 1 task at 0 (others missing). Equal weight -> 0.5, not 0.8.
    D = np.array([[1.0, 0.0], [1.0, np.nan], [1.0, np.nan], [1.0, np.nan]])
    assert pooled_mean(D) == pytest.approx(0.5)
    W = np.ones((1, 4))
    assert pooled_mean(D, W)[0] == pytest.approx(0.5)


def test_bootstrap_recovers_known_effect():
    runs = _synthetic_runs(np.random.default_rng(1), effect=0.2)
    out = contrast(runs, "C", "B", n_boot=2000)
    pooled = out["pooled"]
    assert pooled["n_tasks"] == 60 and pooled["n_models"] == 3
    assert abs(pooled["estimate"] - 0.2) < 0.06
    assert pooled["ci_low"] < 0.2 < pooled["ci_high"]
    assert pooled["ci_low"] > 0  # a 20-point effect on 60 tasks is detectable
    assert set(out["per_model"]) == {"m1", "m2", "m3"}


def test_bootstrap_null_effect_ci_spans_zero():
    runs = _synthetic_runs(np.random.default_rng(2), effect=0.0)
    pooled = contrast(runs, "C", "B", n_boot=2000)["pooled"]
    assert pooled["ci_low"] < 0 < pooled["ci_high"]


def test_bootstrap_ci_coverage_is_near_nominal():
    """Task-level differences ~ N(0.1, 0.3); 95% percentile CI should cover 0.1 roughly 95%
    of the time (percentile bootstrap undercovers slightly at n=40)."""
    rng = np.random.default_rng(3)
    hits, trials = 0, 300
    for i in range(trials):
        D = rng.normal(0.1, 0.3, size=(40, 1))
        r = bootstrap_contrast(D, n_boot=1000, seed=i)
        hits += r["ci_low"] <= 0.1 <= r["ci_high"]
    assert 0.88 <= hits / trials <= 0.99


def test_bootstrap_ignores_unpaired_tasks():
    runs = [
        {"model": "m", "arm": "C", "task": "t1", "success": 1},
        {"model": "m", "arm": "B", "task": "t1", "success": 0},
        {"model": "m", "arm": "C", "task": "t2", "success": 1},  # no B run: not paired
    ]
    pooled = contrast(runs, "C", "B", n_boot=200)["pooled"]
    assert pooled["n_tasks"] == 1 and pooled["estimate"] == 1.0


def test_epochs_averaged_within_task_first():
    # t1: C passes 1 of 3 epochs; B 0 of 1. t2: both pass. Mean of task diffs = (1/3 + 0) / 2.
    runs = [{"model": "m", "arm": "C", "task": "t1", "success": s} for s in (1, 0, 0)]
    runs += [{"model": "m", "arm": "B", "task": "t1", "success": 0}]
    runs += [{"model": "m", "arm": a, "task": "t2", "success": 1} for a in ("B", "C")]
    assert contrast(runs, "C", "B", n_boot=50)["pooled"]["estimate"] == pytest.approx(1 / 6)


def test_wilson_known_values():
    lo, hi = wilson(5, 10)
    assert lo == pytest.approx(0.2366, abs=1e-4) and hi == pytest.approx(0.7634, abs=1e-4)
    assert wilson(0, 0) == (None, None)
    lo, hi = wilson(10, 10)
    assert hi == pytest.approx(1.0) and lo == pytest.approx(0.7225, abs=1e-4)


def test_bootstrap_ratio_cost_per_success():
    cost, succ = np.array([1.0, 2.0, 3.0]), np.array([1.0, 0.0, 2.0])
    out = bootstrap_ratio(cost, succ, n_boot=500)
    assert out["estimate"] == pytest.approx(2.0)
    assert out["ci_low"] <= 2.0 <= out["ci_high"]
    assert bootstrap_ratio(np.array([1.0]), np.array([0.0]), n_boot=10)["estimate"] is None


# --- cost math ------------------------------------------------------------------------------

PRICES = load_prices()


def test_prices_cover_core_models():
    for m in ("anthropic/claude-opus-5-5", "anthropic/claude-sonnet-5-5", "anthropic/claude-haiku-4-5",
              "openai/gpt-6.1-sol", "openai/gpt-6-luna", "google/gemini-3.1-pro-preview", "google/gemini-3.8-flash",
              "grok/grok-4.7", "openrouter/deepseek/deepseek-v4-pro-0813"):
        assert PRICES[m]["input"] is not None and PRICES[m]["output"] is not None, m


def test_anthropic_cache_math():
    # Sonnet 5.5: $2 in, $10 out, $2.50 cache write, $0.20 cache read.
    u = {"input_tokens": 1_000_000, "output_tokens": 100_000, "input_tokens_cache_write": 200_000,
         "input_tokens_cache_read": 2_000_000, "reasoning_tokens": 50_000, "total_tokens": 3_300_000}
    # reasoning is inside output_tokens here (total = in + out + cw + cr), so not added again
    assert call_cost(u, PRICES["anthropic/claude-sonnet-5-5"]) == pytest.approx(2.0 + 1.0 + 0.5 + 0.4)


def test_reasoning_outside_output_is_billed_at_output_rate():
    # xAI reports reasoning outside completion tokens: total = in + out + cr + reasoning.
    u = {"input_tokens": 97, "output_tokens": 1, "input_tokens_cache_read": 1152, "reasoning_tokens": 53, "total_tokens": 1303}
    expected = (97 * 2.0 + (1 + 53) * 6.0 + 1152 * 0.5) / 1e6
    assert call_cost(u, PRICES["grok/grok-4.7"]) == pytest.approx(expected)


def test_reasoning_inside_output_not_double_counted():
    u = {"input_tokens": 83, "output_tokens": 333, "reasoning_tokens": 213, "total_tokens": 416}
    assert call_cost(u, PRICES["openai/gpt-6.1-sol"]) == pytest.approx((83 * 2.0 + 333 * 10.0) / 1e6)


def test_long_context_tier_per_call():
    p = PRICES["openai/gpt-6.1-sol"]  # >272K prompt: $4 in / $15 out / $0.20 read
    short = {"input_tokens": 272_000, "output_tokens": 0, "total_tokens": 272_000}
    long = {"input_tokens": 100_000, "input_tokens_cache_read": 172_001, "output_tokens": 1_000, "total_tokens": 273_001}
    assert call_cost(short, p) == pytest.approx(272_000 * 2.0 / 1e6)
    assert call_cost(long, p) == pytest.approx((100_000 * 4.0 + 172_001 * 0.2 + 1_000 * 15.0) / 1e6)
    g = PRICES["grok/grok-4.7"]  # inclusive threshold at 200K
    assert call_cost({"input_tokens": 200_000, "total_tokens": 200_000}, g) == pytest.approx(200_000 * 4.0 / 1e6)


def test_usage_cost_only_counts_agent_model():
    calls = [("anthropic/claude-sonnet-5-5", {"input_tokens": 1_000_000, "total_tokens": 1_000_000}),
             ("openai/gpt-5.5", {"input_tokens": 1_000_000, "total_tokens": 1_000_000})]
    assert usage_cost(calls, "anthropic/claude-sonnet-5-5", PRICES)["agent_usd"] == pytest.approx(2.0)
    assert usage_cost(calls, "unknown/model", PRICES)["agent_usd"] is None


# --- flight rule ------------------------------------------------------------------------------


@pytest.mark.parametrize("text,amount,cur", [
    ("Ryanair FR88, departs 10:55, €61.99 one-way", 61.99, "EUR"),
    ("price USD 83 total incl. taxes", 83.0, "USD"),
    ("**US$83.00** one-way", 83.0, "USD"),
    ("about $66 USD one-way", 66.0, "USD"),
    ("fare: 61,99 € per person", 61.99, "EUR"),
    ("Total 1,234.50 USD", 1234.5, "USD"),
    ("total £120", 120.0, "GBP"),
    ("EUR 1.234,56", 1234.56, "EUR"),
])
def test_extract_price_formats(text, amount, cur):
    p = extract_price(text)
    assert p["amount"] == pytest.approx(amount) and p["currency"] == cur


def test_extract_price_takes_first_and_handles_none():
    assert extract_price("Best: $210 on UA 123. Alternatives: $190 (2 stops)")["amount"] == 210
    assert extract_price("I can't look up live fares for Nov 12, 2026.") is None


def test_parse_amount():
    assert parse_amount("1.234") == 1234 and parse_amount("12.34") == 12.34 and parse_amount("1,234") == 1234


def _flight(arm, raw, answer, model="m"):
    return {"task": "travel-x", "grader_type": "flight", "model": model, "arm": arm, "epoch": 1,
            "success_raw": raw, "success": raw, "answer": answer, "cheapest_within": 0.10}


def test_flight_rule_cross_arm_minimum_and_fx():
    fx = {"USD": 1.0, "EUR": 1.1}
    runs = [
        _flight("B", 1, "€60 on FR88"),        # $66.00 -> the minimum
        _flight("C", 1, "USD 72.60 total"),    # exactly 1.10 x min -> passes
        _flight("D", 1, "$73 on U2"),          # over the threshold
        _flight("C", 0, "$10 on a fake flight"),  # failed constraints: not in the minimum, stays 0
        _flight("D", 1, "the cheapest flight is on TAP"),  # no price: fails, flagged for review
        _flight("B", 1, "CHF 50"),             # no FX rate: fails, flagged
        {"task": "other", "grader_type": "exact", "success_raw": 1, "success": 1},
    ]
    audit = apply_flight_rule(runs, fx)["travel-x"]
    assert audit["min_usd"] == pytest.approx(66.0)
    assert [r["success"] for r in runs[:6]] == [1, 1, 0, 0, 0, 0]
    assert audit["raw_pass"] == 5 and audit["final_pass"] == 2 and audit["needs_review"] == 2
    assert runs[6]["success"] == 1  # non-flight runs untouched


def test_flight_rule_no_eligible_runs():
    runs = [_flight("B", 0, "$100"), _flight("C", 0, "")]
    audit = apply_flight_rule(runs, {"USD": 1.0})["travel-x"]
    assert audit["min_usd"] is None and all(r["success"] == 0 for r in runs)


# --- task classification --------------------------------------------------------------------


def test_structured_split():
    assert battery_of("structured-11", "structured") == "structured-public"
    assert battery_of("structured-12", "structured") == "structured-hostile"
    assert battery_of("gtm-03", "gtm") == "gtm"
