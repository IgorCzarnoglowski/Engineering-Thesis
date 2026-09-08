from src.scrapers import bankier, pap_biznes, wykop
from src import pipeline
import pandas as pd
import os

RAW_CSV = 'data/news_output.csv'
ENRICHED_CSV = 'data/news_enriched.csv'


def scrape():
    df_pap = pap_biznes.main()
    df_bankier = bankier.main()

    df_wykop = wykop.main()

    valid_dfs = [df for df in [df_pap, df_bankier, df_wykop] if not df.empty]

    if valid_dfs:
        df_new = pd.concat(valid_dfs, ignore_index=True)
    else:
        df_new = pd.DataFrame()

    if os.path.exists(RAW_CSV) and not df_new.empty:
        df_existing = pd.read_csv(RAW_CSV)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(inplace=True)
    else:
        df_combined = df_new

    for col in df_combined.select_dtypes(include='object').columns:
        df_combined[col] = df_combined[col].str.replace(r'[\r\n]+', ' ', regex=True)
    df_combined.to_csv(RAW_CSV, index=False, encoding='utf-8-sig')
    print(f"Saved {len(df_combined)} rows to {RAW_CSV}")


def enrich():
    source = ENRICHED_CSV if os.path.exists(ENRICHED_CSV) else RAW_CSV
    df = pd.read_csv(source)
    df = pipeline.enrich_dataframe(df)
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.replace(r'[\r\n]+', ' ', regex=True)
    df.to_csv(ENRICHED_CSV, index=False, encoding='utf-8-sig')
    print(f"Saved {len(df)} rows to {ENRICHED_CSV}")


if __name__ == "__main__":
    scrape()
    #enrich()
