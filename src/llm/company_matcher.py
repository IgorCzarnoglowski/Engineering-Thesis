from config.companies import companies
from src.llm.client import chat


def get_company_name_from_content(news: str) -> str:
    company_list = "\n".join(
        f"{i}. {name}" for i, name in enumerate(companies.keys(), 1)
    )

    prompt = f"""Given the following list of companies from the WIG20 index:
{company_list}

You will receive a passage of text. Identify the single company that the passage is about—either mentioned directly or implied. If multiple companies are referenced, choose the one most central to the main topic. If no company fits, answer with the word Nan. Respond with only one word: the company name or Nan. Do not add any punctuation, explanation, extra characters or extra styling.

Output requirements:
- Respond with only one word – the company name or "Nan".
- Do not include any punctuation, explanation, or extra characters.

Text:
{news}"""

    text = chat(prompt)
    return text.split()[0] if text else "Nan"


def map_company_to_ticker(name: str) -> str:
    if not name:
        return "Nan"
    return companies.get(name.strip().lower(), ("", "Nan"))[1]
