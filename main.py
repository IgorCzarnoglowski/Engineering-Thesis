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
        df_new = pd.concat(valid_dfs, ignore_index=True)
    else:
        df_new = pd.DataFrame()

    import os
    if os.path.exists(RAW_CSV) and not df_new.empty:
        df_existing = pd.read_csv(RAW_CSV)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(inplace=True)
    else:
        df_combined = df_new

    df_combined.to_csv(RAW_CSV, index=False)
    print(f"Saved {len(df_combined)} rows to {RAW_CSV}")


def enrich():
    import os
    source = ENRICHED_CSV if os.path.exists(ENRICHED_CSV) else RAW_CSV
    df = pd.read_csv(source)
    df = utils.enrich_dataframe(df)
    df.to_csv(ENRICHED_CSV, index=False)
    print(f"Saved {len(df)} rows to {ENRICHED_CSV}")


if __name__ == "__main__":
    scrape()
    #enrich()