from pydantic import BaseModel, ConfigDict


class CodeReviewResult(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    overall_score: str
    found_issues: list[str]
    improved_code: str


class ReviewRequest(BaseModel):
    code: str
    language: str = "Python"
    score_scale: str = "1-10"
    model: str = "qwen2.5-coder:7b"
