from src import BankierScraper as Bankier, PapBiznesScrapper as Pap, WykopScraper as Wykop
from src import utils
import pandas as pd

RAW_CSV = 'data/news_output.csv'
ENRICHED_CSV = 'data/news_enriched.csv'


def scrape():
    df_pap = Pap.main()
    df_bankier = Bankier.main()
    df_wykop = Wykop.main()

    valid_dfs = [df for df in [df_pap, df_bankier, df_wykop] if not df.empty]

    if valid_dfs:
        df_combined = pd.concat(valid_dfs, ignore_index=True)
    else:
        df_combined = pd.DataFrame()

    df_combined.to_csv(RAW_CSV, index=False)
    print(f"Saved {len(df_combined)} rows to {RAW_CSV}")


def enrich():
    df = pd.read_csv(RAW_CSV)

    for idx, row in df.iterrows():
        company_name = utils.get_company_name_from_content(row["content"])
        ticker = utils.map_company_to_ticker(company_name)
        rate = utils.get_rate(row["title"], row["content"], company_name)

        df.at[idx, "company_name"] = company_name
        df.at[idx, "ticker"] = ticker
        df.at[idx, "rate"] = rate

    df = utils.get_stock_price_for_companies(df)

    df.to_csv(ENRICHED_CSV, index=False)
    print(f"Saved {len(df)} rows to {ENRICHED_CSV}")


if __name__ == "__main__":
    scrape()
    enrich()