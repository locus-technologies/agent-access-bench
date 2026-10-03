"""Live checks for bench/truth.py. Each test hits its source of record once.

Run:   uv run --with pytest pytest bench/test_truth.py -v
Skip:  BENCH_OFFLINE=1 (all tests here need the network)
"""

import json
import os
import re
from pathlib import Path

import pytest

from bench import truth
from bench.task_schema import NumberGrader, SetGrader, Task

pytestmark = pytest.mark.skipif(os.environ.get("BENCH_OFFLINE") == "1", reason="live network test")

TASKS_DIR = Path(__file__).resolve().parent.parent / "tasks"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def test_ecb_reference_rate():
    assert 100 < truth.ecb_reference_rate(quote_ccy="JPY") < 300


def test_sec_recent_filing_dates():
    dates = truth.sec_recent_filing_dates(cik=1045810, form="8-K", n=5)
    assert len(dates) == 5 and all(DATE.match(d) for d in dates)
    assert dates == sorted(dates, reverse=True)


def test_sec_latest_shares_outstanding():
    assert 1e8 < truth.sec_latest_shares_outstanding(cik=909832) < 1e9


def test_treasury_total_public_debt():
    assert 3e13 < truth.treasury_total_public_debt() < 6e13


def test_github_open_issue_count():
    assert truth.github_open_issue_count(repo="microsoft/vscode", label="bug") > 100


def test_npm_last_week_downloads():
    assert truth.npm_last_week_downloads(package="zod") > 1e6


def test_pypi_latest_version():
    (v,) = truth.pypi_latest_version(package="pandas")
    assert re.match(r"^\d+\.\d+\.\d+$", v)


def test_usgs_quake_count_past_week():
    assert 20 < truth.usgs_quake_count_past_week(min_mag="4.5") < 1000


def test_wikipedia_monthly_pageviews():
    assert truth.wikipedia_monthly_pageviews(article="Python_(programming_language)", month="2026-09") > 10_000


def test_coinbase_avg_daily_volume():
    assert 100 < truth.coinbase_avg_daily_volume(product="BTC-USD", days=30) < 1e6


def test_nws_latest_temp_f():
    assert -40 < truth.nws_latest_temp_f(station="KORD") < 120


def test_shopify_in_stock_variants():
    sizes = truth.shopify_in_stock_variants(store="www.allbirds.com", handle="mens-wool-runners")
    assert isinstance(sizes, list) and all(isinstance(s, str) for s in sizes)


def test_bluesky_follower_count():
    assert truth.bluesky_follower_count(handle="nytimes.com") > 10_000


def test_steam_current_players():
    assert truth.steam_current_players(appid=730) > 10_000


def test_steam_price_usd():
    assert 0 <= truth.steam_price_usd(appid=1145360) < 100


def _capture_tasks():
    for path in sorted(TASKS_DIR.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            if line.strip():
                t = Task.model_validate(json.loads(line))
                if isinstance(t.grader, NumberGrader | SetGrader) and t.grader.capture:
                    yield t


@pytest.mark.parametrize("task", list(_capture_tasks()), ids=lambda t: t.id)
def test_every_task_capture_resolves(task):
    """Each task's capture name exists in truth.py and returns the grader's type."""
    value = getattr(truth, task.grader.capture)(**task.grader.capture_args)
    if isinstance(task.grader, NumberGrader):
        assert isinstance(value, float)
    else:
        assert isinstance(value, list) and all(isinstance(v, str) for v in value)
