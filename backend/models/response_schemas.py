from pydantic import BaseModel, Field
from typing import List, Any, Optional

# --- Agent Output Schemas ---

class StudyDay(BaseModel):
    day: str = Field(..., description="Day number or day label, e.g., 'Day 1'")
    topics: List[str] = Field(..., description="List of topics to cover")
    practice_tasks: List[str] = Field(..., description="Coding tasks or practical exercises")
    revision: str = Field(..., description="Key concept or revision target for the day")

class StudyPlan(BaseModel):
    role: str = Field(..., description="Target role name")
    estimated_hours: float = Field(..., description="Total estimated prep hours")
    days: List[StudyDay] = Field(..., description="Granular 7-day study curriculum details")

class CodingChallenge(BaseModel):
    name: str = Field(..., description="Problem/Challenge title")
    difficulty: str = Field(..., description="Easy, Medium, or Hard")
    topic: str = Field(..., description="Topic of the challenge")
    description: str = Field(..., description="Detailed problem statement")
    reason: str = Field(..., description="Why this question is recommended for the role")

# Wrapper class for Gemini API schema parser
class CodingArenaRecommendations(BaseModel):
    challenges: List[CodingChallenge] = Field(...)

class InterviewQuestion(BaseModel):
    question: str = Field(..., description="Mock interview question")
    hint: str = Field(..., description="Hidden helpful hint for the user")

class EvaluationResult(BaseModel):
    score: int = Field(..., description="Performance score from 1 to 10")
    strengths: List[str] = Field(..., description="Strengths identified in the candidate's answer")
    weaknesses: List[str] = Field(..., description="Gaps or weaknesses identified in the candidate's answer")
    tips: List[str] = Field(..., description="Actionable tips for improvement")
    next_difficulty: str = Field(..., description="Recommended next difficulty: Easy, Medium, or Hard")

# --- API Response Wrappers ---

class StandardResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
    data: Any
