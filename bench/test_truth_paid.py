"""Live checks for bench/truth_paid.py. One paid call per capture function (about $0.11 total).

Run:   uv run --with pytest pytest bench/test_truth_paid.py -v
Skip:  BENCH_OFFLINE=1 (all tests here need the network and grader-only keys)
"""

import os
import re

import pytest

from bench import truth, truth_paid

pytestmark = pytest.mark.skipif(os.environ.get("BENCH_OFFLINE") == "1", reason="live network test")


def test_reexported_from_truth():
    for name in truth_paid.__all__:
        assert getattr(truth, name) is getattr(truth_paid, name)
    assert truth.TIMEOUT == 30.0  # the star import must not clobber truth.py's own globals


def test_google_ads_monthly_search_volume():
    # paiddata-01 static gold; closed month, so this must match exactly.
    assert truth.google_ads_monthly_search_volume(keyword="payroll software", year=2026, month=8) == 14_800


def test_google_maps_review_count():
    n = truth.google_maps_review_count(keyword="Franklin Barbecue 900 E 11th St Austin TX", cid="3579139785445756036")
    assert 1_000 < n < 100_000


def test_amazon_price_usd():
    assert 5 < truth.amazon_price_usd(asin="B00006JSUA") < 100


def test_amazon_ratings_count():
    assert 50_000 < truth.amazon_ratings_count(asin="0735211299") < 1_000_000


def test_x_follower_count():
    assert truth.x_follower_count(username="NWS") > 1_000_000


def test_x_most_liked_post():
    (post_id,) = truth.x_most_liked_post(username="stripe", start="2026-09-01T00:00:00Z", end="2026-10-01T00:00:00Z")
    assert re.match(r"^\d{15,20}$", post_id)
