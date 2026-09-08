import pandas as pd
from src.llm.company_matcher import get_company_name_from_content, map_company_to_ticker
from src.llm.impact_rater import get_rate, is_blank
from src.market.stock_data import get_stock_data


def match_companies(df):
    """Fill company_name/ticker on rows whose ticker is still blank."""
    for idx, row in df.iterrows():
        if not is_blank(row.get("ticker")):
            continue
        company_name = get_company_name_from_content(row.get("content"))
        df.at[idx, "company_name"] = company_name
        df.at[idx, "ticker"] = map_company_to_ticker(company_name)
    return df


def rate_news(df):
    """Fill rate on rows that don't have one yet."""
    for idx, row in df.iterrows():
        if pd.isna(row.get("rate")):
            df.at[idx, "rate"] = get_rate(
                row.get("title"), row.get("content"), row.get("company_name")
            )
    return df


def add_stock_prices(df):
    for idx, row in df.iterrows():
        tck = row.get("ticker")
        if is_blank(tck):
            continue
        prices = get_stock_data(tck, row.date)
        for label, value in prices.items():
            df.loc[idx, label] = value
    return df


def enrich_dataframe(df):
    return add_stock_prices(rate_news(match_companies(df)))
