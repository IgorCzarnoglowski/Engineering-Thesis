from src import BankierScraper as Bankier, PapBiznesScrapper as Pap, WykopScraper as Wykop
import pandas as pd


def main():
    df_pap = Pap.main()
    df_bankier = Bankier.main()
    df_wykop = Wykop.main()

    valid_dfs = [df for df in [df_pap, df_bankier, df_wykop] if not df.empty]

    if valid_dfs:
        df_combined = pd.concat(valid_dfs, ignore_index=True)
    else:
        df_combined = pd.DataFrame()

    df_combined.to_csv('news_output.csv', index=False)
    print(f"Saved {len(df_combined)} rows to news_output.csv")


if __name__ == "__main__":
    main()
