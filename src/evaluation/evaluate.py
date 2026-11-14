from scipy.stats import spearmanr
import pandas as pd
import os
from sklearn.metrics import classification_report, f1_score


DIRECTORY = '../../data/enriched'
DATA_ARRAY = []

for file in os.listdir(DIRECTORY):
    file_path = os.path.join(DIRECTORY, file)
    DATA_ARRAY.append(pd.read_csv(file_path))

compacted_data = pd.concat(DATA_ARRAY)


def evaluate_spearman(df: pd.DataFrame):
    price_cols = ['initial price', '+5 min', '+10 min', '+15 min', '+30 min', '+60 min']
    minutes = [0, 5, 10, 15, 30, 60]
    new_df = df.dropna(subset=['rate'] + price_cols, how="any").copy()
    ret_cols = []
    for c, m in zip(price_cols[1:], minutes[1:]):
        col = f'ret_{m}m'
        new_df[col] = (new_df[c] / new_df['initial price'] - 1) * 100
        ret_cols.append(col)
    for c in ret_cols:
        r, p = spearmanr(new_df['rate'], new_df[c])
        print(c, round(r, 3), round(p, 4))


def evaluate_directional_accuracy(df: pd.DataFrame):
    price_cols = ['initial price', '+5 min', '+10 min', '+15 min', '+30 min', '+60 min']
    minutes = [5, 10, 15, 30, 60]

    new_df = df.dropna(subset=['rate'] + price_cols, how="any").copy()

    predicted_up = new_df['rate'] > 0

    for c, m in zip(price_cols[1:], minutes):
        ret = (new_df[c] / new_df['initial price'] - 1)

        mask = (new_df['rate'] != 0) & (ret != 0)
        pred = predicted_up[mask]
        actual_up = ret[mask] > 0

        acc = (pred == actual_up).mean()
        n = mask.sum()
        print(f"ret_{m}m: {round(acc * 100, 1)}%  (n={n})")


if __name__ == "__main__":
    evaluate_spearman(compacted_data)
    evaluate_directional_accuracy(compacted_data)


def evaluate_f1_macro(df: pd.DataFrame):
    true = df["company_name"]
    predicted = df["company_name_predicted"].fillna("Nan")
    labels = sorted(true.dropna().unique())

    print("Company breakdown:\n", classification_report(true, predicted, labels=labels, zero_division=0))
    print("Macro F1:", f1_score(true, predicted, labels=labels, average='macro', zero_division=0))

