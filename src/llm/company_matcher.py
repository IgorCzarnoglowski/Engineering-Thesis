from config.companies import companies
from src.llm.client import chat
from src.llm.schemas import CompanyMatchResult


SYSTEM_PROMPT = """You are a company identification assistant. Given a list of WIG20 companies and a news article, identify which company the article is about.

Rules:
- Pick the single most central company
- If none match, return "Nan"
- Return only the company name from the provided list"""


def get_company_name_from_content(news: str) -> str:
    company_list = "\n".join(
        f"{i}. {name}" for i, name in enumerate(companies.keys(), 1)
    )

    user_prompt = f"""Companies:
{company_list}

Text:
{news}"""

    result = chat(SYSTEM_PROMPT, user_prompt, response_schema=CompanyMatchResult)
    parsed = CompanyMatchResult.model_validate_json(result)
    return parsed.company_name


def map_company_to_ticker(name: str) -> str:
    if not name:
        return "Nan"
    return companies.get(name.strip().lower(), ("", "Nan"))[1]
