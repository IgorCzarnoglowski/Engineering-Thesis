from pydantic import BaseModel, Field


class CompanyMatchResult(BaseModel):
    company_name: str = Field(description="Company name from the WIG20 list, or 'Nan' if none matches")


class ImpactRatingResult(BaseModel):
    rating: int = Field(
        ge=-10,
        le=10,
        description="Signed impact on the stock price: -10 = extreme negative, 0 = neutral / no impact, +10 = extreme positive",
    )
