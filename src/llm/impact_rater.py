from src.llm.client import chat


def get_rate(title: str, news: str, company: str):
    if not company or company.strip().lower() == "nan":
        return "Nan"

    prompt = f"""You are an expert financial analyst AI.

Given a news article's title, content, and the company name it is about, analyze the potential impact this news could have on the company's stock market price.
Consider sentiment, relevance, financial/operational implications, and investor behavior.

Output a single integer from 1 to 10, where:
1 = No impact on stock price
10 = Extremely strong impact on stock price

Do not provide any explanation or text besides the number.

If Company Name is "Nan", then respond with "Nan".

Input:
Title: {title}
Content: {news}
Company: {company}"""

    text = chat(prompt)

    token = text.split()[0] if text else "Nan"
    if token.isdigit() and 1 <= int(token) <= 10:
        return token
    if token.lower() == "nan":
        return "Nan"
    return "Nan"
