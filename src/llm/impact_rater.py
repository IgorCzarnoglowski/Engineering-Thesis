from src.llm.client import chat
from src.llm.schemas import ImpactRatingResult


SYSTEM_PROMPT = """You are an expert financial analyst AI. Analyze the potential impact a news article could have on a company's stock price.

Consider sentiment, relevance, financial/operational implications, and investor behavior.
"""


def get_rate(title: str, news: str, company: str):
    if not company or company.strip().lower() == "nan":
        return "Nan"

    user_prompt = f"""Title: {title}
Content: {news}
Company: {company}"""

    result = chat(SYSTEM_PROMPT, user_prompt, response_schema=ImpactRatingResult)
    parsed = ImpactRatingResult.model_validate_json(result)

    return str(max(1, min(10, parsed.rating)))
