import pandas as pd

from src.llm.client import chat
from src.llm.schemas import ImpactRatingResult


SYSTEM_PROMPT = """You are an expert financial analyst AI. Rate the impact a news article could have on the company's stock price on a signed scale from -10 to +10.

The sign is the direction of the price move, the magnitude is how strong the move is:
  +10 / -10  market-moving surprise, price should react by several percent within the hour
   +7 / -7   clearly material: earnings surprise, guidance change, large contract, M&A, regulatory ruling
   +3 / -3   mildly relevant: routine results in line with expectations, small contract, analyst note
        0    no impact: administrative filings, AGM notices, shareholder meeting resolutions, name changes,
             or news that is not really about this company

Most corporate filings are 0. Do not inflate the score to look decisive, and do not lean positive by default.
Judge the price reaction, not whether the news sounds good.

Consider sentiment, relevance, financial/operational implications, and investor behavior.
"""


def is_blank(value) -> bool:
    return pd.isna(value) or str(value).strip().lower() in ("", "nan")


def get_rate(title: str, news: str, company: str):
    """Signed impact rating in [-10, 10], or None when there is nothing to rate.

    None means missing data (no company matched), which is not the same as 0 (neutral news).
    """
    if is_blank(company) or is_blank(news):
        return None

    user_prompt = f"""Title: {title}
Content: {news}
Company: {company}"""

    result = chat(SYSTEM_PROMPT, user_prompt, response_schema=ImpactRatingResult)
    parsed = ImpactRatingResult.model_validate_json(result)

    return max(-10, min(10, parsed.rating))
