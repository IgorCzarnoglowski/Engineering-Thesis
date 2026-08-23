from src.llm.client import chat
from src.llm.schemas import ImpactRatingResult


SYSTEM_PROMPT = """You are an expert financial analyst AI. Analyze the potential impact a news article could have on a company's stock price.

Consider sentiment, relevance, financial/operational implications, and investor behavior.

Rate impact from 1 to 10:
1 = No impact on stock price
10 = Extremely strong impact on stock price

If company is "Nan" or not applicable, return -1."""


def get_rate(title: str, news: str, company: str):
    if not company or company.strip().lower() == "nan":
        return "Nan"

    user_prompt = f"""Title: {title}
Content: {news}
Company: {company}"""

    result = chat(SYSTEM_PROMPT, user_prompt, response_schema=ImpactRatingResult)
    parsed = ImpactRatingResult.model_validate_json(result)

    if parsed.rating == -1:
        return "Nan"
    return str(max(1, min(10, parsed.rating)))
