"""Self-check for enrich_dataframe branching. Run: python test_pipeline.py"""
import numpy as np
import pandas as pd

from src import pipeline

calls = {"match": 0, "rate": 0}


def fake_match(content):
    calls["match"] += 1
    return "kghm"


def fake_rate(title, content, company):
    calls["rate"] += 1
    return "7"


def test_enrich():
    pipeline.get_company_name_from_content = fake_match
    pipeline.get_rate = fake_rate
    pipeline._get_stock_price_for_companies = lambda df: df

    df = pd.DataFrame([
        {"title": "a", "content": "x", "company_name": "pepco", "ticker": "PCO.WA"},
        {"title": "b", "content": "y", "company_name": "Nan", "ticker": "Nan"},
        {"title": "c", "content": "z", "company_name": np.nan, "ticker": np.nan},
    ])
    out = pipeline.enrich_dataframe(df)

    assert calls["match"] == 2, calls                      # only the Nan/NaN tickers
    assert out.loc[0, "ticker"] == "PCO.WA"                 # existing ticker untouched
    assert out.loc[1, "ticker"] == out.loc[2, "ticker"] == "KGH.WA"
    assert calls["rate"] == 3, calls                        # every row rated
    assert list(out["rate"]) == ["7", "7", "7"]

    # rows with an existing rate are not re-rated
    calls["rate"] = 0
    out2 = pipeline.enrich_dataframe(out)
    assert calls["rate"] == 0, calls
    assert list(out2["rate"]) == ["7", "7", "7"]


if __name__ == "__main__":
    test_enrich()
    print("ok")
