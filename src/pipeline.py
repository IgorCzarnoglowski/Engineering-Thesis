import pandas as pd
from src.llm.company_matcher import get_company_name_from_content, map_company_to_ticker
from src.llm.impact_rater import get_rate, is_blank
from src.market.stock_data import get_stock_data


def enrich_dataframe(df):
    for idx, row in df.iterrows():
        if is_blank(row.get("ticker")):
            company_name = get_company_name_from_content(row.get("content"))
            df.at[idx, "company_name"] = company_name
            df.at[idx, "ticker"] = map_company_to_ticker(company_name)
        else:
            company_name = row.get("company_name")

        if pd.isna(row.get("rate")):
            df.at[idx, "rate"] = get_rate(row.get("title"), row.get("content"), company_name)

    return _get_stock_price_for_companies(df)


def _get_stock_price_for_companies(df):
    for idx, row in df.iterrows():
        tck = row.get("ticker")
        if is_blank(tck):
            continue
        prices = get_stock_data(tck, row.date)
        for label, value in prices.items():
            df.loc[idx, label] = value
    return df
