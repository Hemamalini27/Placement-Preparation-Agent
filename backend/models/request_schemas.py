from pydantic import BaseModel, Field
from typing import Optional

class PlanRequest(BaseModel):
    role: str = Field(..., example="Software Engineer")
    skill_level: str = Field(..., example="Intermediate")
    hours_per_day: float = Field(..., example=4.0)
    target_date: Optional[str] = Field(default=None, example="2026-07-31")

class RecommendRequest(BaseModel):
    role: str = Field(..., example="Full-Stack Developer")
    level: str = Field(..., example="Medium")

class StartInterviewRequest(BaseModel):
    type: str = Field(..., example="tech")  # "tech" or "hr"
    role: str = Field(..., example="Backend Engineer")

class AnswerRequest(BaseModel):
    session_id: str = Field(...)
    answer: str = Field(...)

class HintRequest(BaseModel):
    session_id: str = Field(...)
