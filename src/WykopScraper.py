import requests
import pandas as pd
from datetime import datetime, timedelta


def get_data(cutoff):
    url = 'https://wykop.pl/api/v3/auth'
    data = {
        'key': 'w5e64b789f84f9dade6f1cc93cae52fb80',
        'secret': '9a5dd04db73ab3315461138e5c51342c'
    }

    response = requests.post(
        url,
        json={'data': data},
        headers={'Accept': 'application/json', 'Content-Type': 'application/json'}
    )
    jwt = response.json()['data']['token']

    tagi = {
        'finanse': 'https://wykop.pl/api/v3/tags/finanse/stream?page=1&limit=40&sort=best&type=all&multimedia=false',
        'technologia': 'https://wykop.pl/api/v3/tags/technologia/stream?page=1&limit=40&sort=best&type=all&multimedia=false',
        'inwestycje': 'https://wykop.pl/api/v3/tags/inwestycje/stream?page=1&limit=40&sort=best&type=all&multimedia=false',
        'gospodarka': 'https://wykop.pl/api/v3/tags/gospodarka/stream?page=1&limit=40&sort=best&type=all&multimedia=false'
    }

    all_dfs = []

    for tag, tag_url in tagi.items():
        response = requests.get(
            tag_url,
            json={'data': data},
            headers={'Accept': 'application/json', 'Authorization': f'Bearer {jwt}'}
        )
        resp_data = response.json()
        df = pd.json_normalize(resp_data['data'])
        df_filtered = df[["created_at", "title", "description", "source.url"]].copy()

        df_filtered["created_at"] = pd.to_datetime(df_filtered["created_at"])
        df_filtered = df_filtered[df_filtered["created_at"] >= cutoff]

        df_filtered = df_filtered.rename(columns={
            "created_at": "date",
            "description": "content",
            "source.url": "link"
        })

        df_filtered["company_name"] = None
        df_filtered["ticker"] = None
        df_filtered["category"] = tag
        df_filtered["source"] = "wykop"

        all_dfs.append(df_filtered)

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()


def main():
    target_day = datetime.today()
    cutoff = target_day - timedelta(days=5)

    df = get_data(cutoff)
    return df


if __name__ == "__main__":
    main()
