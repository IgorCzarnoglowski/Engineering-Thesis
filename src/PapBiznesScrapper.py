import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import random
import time

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.12.388 Version/12.18',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
]

companies = {
    "mbank": ("109", "MBK.WA"),
    "budimex": ("112", "BDX.WA"),
    "sanpl": ("117", "SPL.WA"),
    "ccc": ("456", "CCC.WA"),
    "kety": ("274", "KTY.WA"),
    "kghm": ("350", "KGH.WA"),
    "lpp": ("380", "LPP.WA"),
    "cdprojekt": ("476", "CDR.WA"),
    "pekao": ("76", "PEO.WA"),
    "pknorlen": ("511", "PKN.WA"),
    "pkobp": ("512", "PKO.WA"),
    "orangepl": ("636", "OPL.WA"),
    "pge": ("503", "PGE.WA"),
    "pzu": ("558", "PZU.WA"),
    "kruk": ("558", "KRU.WA"),
    "alior": ("1180", "ALR.WA"),
    "dinopl": ("1431", "DNP.WA"),
    "pepco": ("1593", "PCO.WA"),
    "zabka": ("1737", "ZAB.WA"),
    "allegro": ("1559", "ALE.WA")
}


def parse(url, page_number=None):
    time.sleep(2)
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=2, status_forcelist=[503, 502, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    if page_number is None:
        page = session.get(f'{url}', headers={'User-Agent': random.choice(user_agents)})
    else:
        page = session.get(f'{url}{page_number}', headers={'User-Agent': random.choice(user_agents)})
    print(page)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup


def gather_content(anchor, date, ticker='Nan', name='Nan'):
    url = f'https://biznes.pap.pl{anchor["href"]}'
    print(url)
    page_content = parse(url)
    main_content_tag = page_content.find('article', id='article')

    title = main_content_tag.find('span', class_='field--name-title').text

    text_paragraphs = main_content_tag.find_all('p', class_='selectionShareable')

    content = ''
    for paragraph in text_paragraphs:
        content += paragraph.text + ' '

    return {'date': date, 'link': url, 'title': title, 'content': content, 'company_name': name, 'ticker': ticker}


def company_profiles_scraping(cutoff):
    all_data = []

    for company, data in companies.items():
        code = data[0]
        ticker = data[1]
        baseurl = f"https://biznes.pap.pl/wiadomosci/firma/{code}?page="
        break_flag = False

        for page in range(99):
            page_content = parse(baseurl, page)
            articles_list_tag = page_content.find('ul', class_='newsList')
            articles_tag = articles_list_tag.find_all('li', class_='news')

            for article in articles_tag:
                wrapper = article.find('div', class_='textWrapper')
                anchor = wrapper.find('a', recursive=False)
                if anchor:
                    post_date = wrapper.find('div', class_='date').text
                    post_date_formatted = datetime.strptime(post_date, "%Y-%m-%d %H:%M")
                    if post_date_formatted < cutoff:
                        break_flag = True
                        break
                    else:
                        all_data.append(gather_content(anchor, post_date_formatted, ticker, company))
                else:
                    print(article)
                    print('No anchor for this news (Pap)')
            if break_flag:
                break

    df_news = pd.DataFrame(all_data)
    df_news["category"] = "profiles"
    df_news["source"] = "pap"
    return df_news


def category_scraping(cutoff):
    all_dfs = []
    categories = {
        "market": "https://biznes.pap.pl/kategoria/rynki?page=",
        "economy": "https://biznes.pap.pl/kategoria/gospodarka?page="
    }
    for category, url in categories.items():
        break_flag = False
        all_data = []
        for page in range(99):
            page_content = parse(url, page)
            articles_list_tag = page_content.find('ul', class_='newsList')
            articles_tag = articles_list_tag.find_all('li', class_='news')

            for article in articles_tag:
                wrapper = article.find('div', class_='textWrapper')
                anchor = wrapper.find('a', recursive=False)
                if anchor:
                    post_date = wrapper.find('div', class_='date').text
                    post_date_formatted = datetime.strptime(post_date, "%Y-%m-%d %H:%M")
                    if post_date_formatted < cutoff:
                        break_flag = True
                        break
                    else:
                        all_data.append(gather_content(anchor, post_date_formatted))
                else:
                    print(article)
                    print('No anchor for this news (Pap)')
            if break_flag:
                break

        df_news = pd.DataFrame(all_data)
        df_news["category"] = category
        all_dfs.append(df_news)

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df["source"] = "pap"
    return final_df


def main():
    target_day = datetime.today()
    cutoff = target_day - timedelta(days=5)

    df_profiles = company_profiles_scraping(cutoff)
    df_categories = category_scraping(cutoff)

    valid_dfs = [df for df in [df_profiles, df_categories] if not df.empty]

    if valid_dfs:
        df_combined = pd.concat(valid_dfs, ignore_index=True)
    else:
        df_combined = pd.DataFrame()

    return df_combined


if __name__ == "__main__":
    main()
