from pydantic import BaseModel, Field


class CompanyMatchResult(BaseModel):
    company_name: str = Field(description="Company name from the WIG20 list, or 'Nan' if none matches")


class ImpactRatingResult(BaseModel):
    rating: int = Field(description="Impact score from -1 (extreme negative impact) to 10 (extreme positive impact), or Nan if not applicable")
