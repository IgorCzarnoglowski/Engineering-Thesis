"""Self-check for the pipeline steps. Run: python test_pipeline.py"""
import numpy as np
import pandas as pd

from src import pipeline
from src.llm.impact_rater import is_blank

calls = {"match": 0, "rate": 0}


def fake_match(content):
    calls["match"] += 1
    return "kghm"


def fake_rate(title, content, company):
    calls["rate"] += 1
    return None if is_blank(company) else 7      # None = no company, distinct from a neutral 0


pipeline.get_company_name_from_content = fake_match
pipeline.get_rate = fake_rate


def sample():
    return pd.DataFrame([
        {"title": "a", "content": "x", "company_name": "pepco", "ticker": "PCO.WA"},
        {"title": "b", "content": "y", "company_name": "Nan", "ticker": "Nan"},
        {"title": "c", "content": "z", "company_name": np.nan, "ticker": np.nan},
    ])


def test_match_only():
    calls.update(match=0, rate=0)
    out = pipeline.match_companies(sample())

    assert calls == {"match": 2, "rate": 0}, calls          # only the blank tickers
    assert out.loc[0, "ticker"] == "PCO.WA"                 # existing ticker untouched
    assert out.loc[1, "ticker"] == out.loc[2, "ticker"] == "KGH.WA"
    assert "rate" not in out.columns                        # rating step not run


def test_rate_only():
    calls.update(match=0, rate=0)
    out = pipeline.rate_news(sample())

    assert calls == {"match": 0, "rate": 3}, calls          # every row rated, no matching
    assert out.loc[0, "rate"] == 7
    assert out["rate"].isna().tolist() == [False, True, True]   # unmatched rows stay missing, not 0
    assert out.loc[1, "ticker"] == "Nan"                    # tickers left alone

    calls["rate"] = 0                                       # a real rating is not redone
    out2 = pipeline.rate_news(out)
    assert out2.loc[0, "rate"] == 7
    assert calls["rate"] == 2, calls                         # only the two missing ones retried


def test_both():
    calls.update(match=0, rate=0)
    pipeline.add_stock_prices = lambda df: df
    out = pipeline.enrich_dataframe(sample())

    assert calls == {"match": 2, "rate": 3}, calls
    assert list(out["ticker"]) == ["PCO.WA", "KGH.WA", "KGH.WA"]
    assert list(out["rate"]) == [7, 7, 7]                   # matching first => every row rateable


if __name__ == "__main__":
    test_match_only()
    test_rate_only()
    test_both()
    print("ok")
