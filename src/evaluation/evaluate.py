from scipy.stats import spearmanr
import pandas as pd
import os
from sklearn.metrics import classification_report, f1_score
import numpy as np


DIRECTORY = '../../data/enriched'
DATA_ARRAY = []

for file in os.listdir(DIRECTORY):
    file_path = os.path.join(DIRECTORY, file)
    DATA_ARRAY.append(pd.read_csv(file_path))

compacted_data = pd.concat(DATA_ARRAY, ignore_index=True)


def evaluate_spearman(df: pd.DataFrame):
    price_cols = ['initial price', '+5 min', '+10 min', '+15 min', '+30 min', '+60 min']
    minutes = [0, 5, 10, 15, 30, 60]
    new_df = df.dropna(subset=['rate', '+60 min'])
    new_df[price_cols] = new_df[price_cols].ffill(axis=1)
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


def evaluate_f1_macro(df: pd.DataFrame):
    true = df["company_name"]
    predicted = df["company_name_predicted"].fillna("Nan")
    labels = sorted(true.dropna().unique())

    print("Company breakdown:\n", classification_report(true, predicted, labels=labels, zero_division=0))
    print("Macro F1:", f1_score(true, predicted, labels=labels, average='macro', zero_division=0))


def evaluate_transfer_entropy(df: pd.DataFrame):
    price_cols = ['initial price', '+5 min', '+10 min', '+15 min', '+30 min', '+60 min']
    df = df.dropna(subset=['rate', '+60 min']).copy()# remove empty rate which means no company classification and empty +60 min which means end of sesion
    df[price_cols] = df[price_cols].ffill(axis=1)

    #Dividing rate values into discrete values
    rate_bins = [-10,-4,3,10]
    labels = [-1,0,1]
    df['rate'] = pd.cut(df['rate'], bins=rate_bins, labels=labels, include_lowest=True).copy()

    #Making price states
    df[price_cols[1:]] = df[price_cols].pct_change(axis=1)[price_cols[1:]].copy()
    price_bins = [-np.inf, -0.005, 0.005,np.inf]
    df[price_cols[1:]] = df[price_cols[1:]].apply(lambda col: pd.cut(col, bins=price_bins, labels=labels, include_lowest=True)).copy()
    # Modelling the logaritmic function for transfer entropy
    #for i in range(1, len(price_cols[1:])):
        #print(calculate_te(df, price_cols[i], price_cols[i+1]))

    # Shuffle data to check results
    df_shuffled = df.copy()

    for x in range(100):
        df_shuffled['rate'] = df_shuffled['rate'].sample(frac=1).to_numpy()
        print('-----------------------')
        for i in range(1, len(price_cols[1:])):
            print(calculate_te(df_shuffled, price_cols[i], price_cols[i+1]))


def calculate_te(df, y_past_col, y_future_col):
    p_cond_with_r =  pd.crosstab([df[y_past_col], df['rate']], df[y_future_col], normalize='index')
    p_cond_without_r = pd.crosstab(df[y_past_col], df[y_future_col], normalize='index')
    p_linked =  pd.crosstab([df[y_past_col], df['rate']], df[y_future_col], normalize=True)

    te = p_linked * np.log2(p_cond_with_r.div(p_cond_without_r, level=0).replace(0,1))
    return te.sum().sum()


if __name__ == "__main__":
    evaluate_transfer_entropy(compacted_data)

