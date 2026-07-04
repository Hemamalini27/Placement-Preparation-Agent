from fastapi import APIRouter, HTTPException
from backend.models.request_schemas import (
    PlanRequest, RecommendRequest, StartInterviewRequest, AnswerRequest, HintRequest
)
from backend.models.response_schemas import StandardResponse
from backend.services.orchestrator import OrchestratorService
from backend.database import db

router = APIRouter(prefix="/api")

@router.post("/generate-study-plan", response_model=StandardResponse)
async def generate_study_plan(payload: PlanRequest):
    try:
        plan = await OrchestratorService.generate_study_plan(
            role=payload.role,
            skill_level=payload.skill_level,
            hours_per_day=payload.hours_per_day,
            target_date=payload.target_date
        )
        return StandardResponse(status="success", message="Study plan generated successfully", data=plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend-problems", response_model=StandardResponse)
async def recommend_problems(payload: RecommendRequest):
    try:
        problems = await OrchestratorService.recommend_problems(
            role=payload.role,
            level=payload.level
        )
        return StandardResponse(status="success", message="Coding challenges recommended successfully", data=problems)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-interview", response_model=StandardResponse)
async def start_interview(payload: StartInterviewRequest):
    try:
        interview_session = await OrchestratorService.start_interview(
            interview_type=payload.type,
            role=payload.role
        )
        return StandardResponse(status="success", message="Interview started successfully", data=interview_session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-answer", response_model=StandardResponse)
async def submit_answer(payload: AnswerRequest):
    try:
        evaluation = await OrchestratorService.submit_answer(
            session_id=payload.session_id,
            answer=payload.answer
        )
        return StandardResponse(status="success", message="Answer evaluated successfully", data=evaluation)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-hint", response_model=StandardResponse)
async def request_hint(payload: HintRequest):
    try:
        hint = await OrchestratorService.request_hint(session_id=payload.session_id)
        return StandardResponse(status="success", message="Hint retrieved successfully", data={"hint": hint})
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", response_model=StandardResponse)
async def get_dashboard():
    try:
        metrics = await db.get_dashboard_metrics()
        return StandardResponse(status="success", message="Dashboard metrics retrieved successfully", data=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=StandardResponse)
async def get_history(limit: int = 50):
    try:
        history = await db.get_history(limit=limit)
        return StandardResponse(status="success", message="Completion history retrieved successfully", data=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-logs", response_model=StandardResponse)
async def get_agent_logs(limit: int = 50):
    try:
        logs = await db.get_agent_logs(limit=limit)
        return StandardResponse(status="success", message="Agent telemetry logs retrieved successfully", data=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
