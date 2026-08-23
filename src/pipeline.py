import pandas as pd
from src.llm.company_matcher import get_company_name_from_content, map_company_to_ticker
from src.llm.impact_rater import get_rate
from src.market.stock_data import get_stock_data


def enrich_dataframe(df):
    for idx, row in df.iterrows():
        ticker_val = row.get("ticker") if "ticker" in df.columns else None
        if pd.notna(ticker_val) and str(ticker_val).strip().lower() not in ("", "nan"):
            continue

        company_name = get_company_name_from_content(row["content"])
        ticker = map_company_to_ticker(company_name)
        rate = get_rate(row["title"], row["content"], company_name)

        df.at[idx, "company_name"] = company_name
        df.at[idx, "ticker"] = ticker
        df.at[idx, "rate"] = rate

    return _get_stock_price_for_companies(df)


def _get_stock_price_for_companies(df):
    for idx, row in df.iterrows():
        tck = row.ticker if "ticker" in df.columns else None
        if not tck or tck.lower() == "nan":
            continue
        prices = get_stock_data(tck, row.date)
        for label, value in prices.items():
            df.loc[idx, label] = value
    return df
