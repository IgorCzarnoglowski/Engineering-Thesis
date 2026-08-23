import random
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
from playwright.sync_api import sync_playwright

from config.companies import companies

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.12.388 Version/12.18',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
]


def parse(url, browser, page_number=None):
    time.sleep(random.uniform(3, 8))
    target_url = url if page_number is None else f'{url}{page_number}'
    context = browser.new_context(user_agent=random.choice(user_agents))
    page = context.new_page()
    response = page.goto(target_url)
    page.wait_for_load_state()

    if response.status in (403, 429):
        print(f"Blocked (status {response.status}), backing off: {target_url}")
        page.close()
        context.close()
        time.sleep(random.uniform(60, 120))
        return parse(url, browser, page_number)

    soup = BeautifulSoup(page.content(), 'html.parser')
    page.close()
    context.close()
    return soup


def gather_content(anchor, date, browser, ticker='Nan', name='Nan'):
    url = f'https://biznes.pap.pl{anchor["href"]}'
    print(url)
    page_content = parse(url, browser)
    main_content_tag = page_content.find('article', id='article')
    if main_content_tag is None:
        print(f"Possible block (no article content): {url}")
        time.sleep(random.uniform(60, 120))
        page_content = parse(url, browser)
        main_content_tag = page_content.find('article', id='article')
        if main_content_tag is None:
            raise RuntimeError(f"Still blocked or page structure changed: {url}")

    title = main_content_tag.find('span', class_='field--name-title').text

    text_paragraphs = main_content_tag.find_all('p', class_='selectionShareable')

    content = ''
    for paragraph in text_paragraphs:
        content += paragraph.text + ' '

    return {'date': date, 'link': url, 'title': title, 'content': content, 'company_name': name, 'ticker': ticker}


def company_profiles_scraping(cutoff, browser):
    all_data = []

    for company, data in companies.items():
        code = data[0]
        ticker = data[1]
        baseurl = f"https://biznes.pap.pl/wiadomosci/firma/{code}?page="
        break_flag = False

        for page_number in range(99):
            page_content = parse(baseurl,browser, page_number)
            articles_list_tag = page_content.find('ul', class_='newsList')
            if articles_list_tag is None:
                print(f"Possible block (200 but no newsList) at {baseurl}{page_number}, backing off")
                time.sleep(random.uniform(60, 120))
                break_flag = True
                break
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
                        all_data.append(gather_content(anchor, post_date_formatted, browser, ticker, company))
                else:
                    print(article)
                    print('No anchor for this news (Pap)')
            if break_flag:
                break

    df_news = pd.DataFrame(all_data)
    df_news["category"] = "profiles"
    df_news["source"] = "pap"
    return df_news


def category_scraping(cutoff, browser):
    all_dfs = []
    categories = {
        "market": "https://biznes.pap.pl/kategoria/rynki?page=",
        "economy": "https://biznes.pap.pl/kategoria/gospodarka?page="
    }
    for category, url in categories.items():
        break_flag = False
        all_data = []
        for page_number in range(99):
            page_content = parse(url, browser, page_number)
            articles_list_tag = page_content.find('ul', class_='newsList')
            if articles_list_tag is None:
                print(f"Possible block (200 but no newsList) at {url}{page_number}, backing off")
                time.sleep(random.uniform(60, 120))
                break_flag = True
                break
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
                        all_data.append(gather_content(anchor, post_date_formatted, browser))
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
    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch()
        target_day = datetime.today()
        cutoff = target_day - timedelta(days=5)

        df_profiles = company_profiles_scraping(cutoff, browser)
        df_categories = category_scraping(cutoff, browser)
        browser.close()

    valid_dfs = [df for df in [df_profiles, df_categories] if not df.empty]

    if valid_dfs:
        df_combined = pd.concat(valid_dfs, ignore_index=True)
    else:
        df_combined = pd.DataFrame()

    return df_combined


if __name__ == "__main__":
    main()
