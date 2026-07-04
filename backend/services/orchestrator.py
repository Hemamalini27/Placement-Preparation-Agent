import uuid
import logging
from typing import Dict, Any, List, Optional
from backend.database import db
from backend.services.agents import PlannerAgent, RecommenderAgent, InterviewerAgent, EvaluatorAgent
from backend.models.response_schemas import StudyPlan, CodingArenaRecommendations, InterviewQuestion, EvaluationResult

logger = logging.getLogger("orchestrator")

class OrchestratorService:
    @staticmethod
    async def generate_study_plan(role: str, skill_level: str, hours_per_day: float, target_date: Optional[str]) -> StudyPlan:
        agent_name = "PlannerAgent"
        input_params = {
            "role": role,
            "skill_level": skill_level,
            "hours_per_day": hours_per_day,
            "target_date": target_date
        }
        try:
            # Execute Planner Agent
            plan: StudyPlan = await PlannerAgent.run(role, skill_level, hours_per_day, target_date or "")
            
            # Telemetry Log
            await db.save_agent_log(
                agent_name=agent_name,
                status="success",
                input_params=input_params,
                output_response=plan.dict()
            )
            
            # Save to Completion History
            await db.save_history(
                item_type="study_plan",
                role=role,
                details=plan.dict()
            )
            
            return plan
        except Exception as e:
            logger.error(f"PlannerAgent execution error: {e}")
            await db.save_agent_log(
                agent_name=agent_name,
                status="failure",
                input_params=input_params,
                output_response=None,
                error=str(e)
            )
            raise e

    @staticmethod
    async def recommend_problems(role: str, level: str) -> List[Dict[str, Any]]:
        agent_name = "RecommenderAgent"
        input_params = {"role": role, "level": level}
        try:
            # Execute Recommender Agent
            recs: CodingArenaRecommendations = await RecommenderAgent.run(role, level)
            challenges_list = [c.dict() for c in recs.challenges]
            
            # Telemetry Log
            await db.save_agent_log(
                agent_name=agent_name,
                status="success",
                input_params=input_params,
                output_response=challenges_list
            )
            
            # Save to Completion History
            await db.save_history(
                item_type="problems",
                role=role,
                details={"level": level, "challenges": challenges_list}
            )
            
            return challenges_list
        except Exception as e:
            logger.error(f"RecommenderAgent execution error: {e}")
            await db.save_agent_log(
                agent_name=agent_name,
                status="failure",
                input_params=input_params,
                output_response=None,
                error=str(e)
            )
            raise e

    @staticmethod
    async def start_interview(interview_type: str, role: str) -> Dict[str, Any]:
        agent_name = "InterviewerAgent"
        input_params = {"type": interview_type, "role": role}
        try:
            # Execute Interviewer Agent
            question_data: InterviewQuestion = await InterviewerAgent.run(interview_type, role)
            
            # Generate Session ID
            session_id = str(uuid.uuid4())
            
            # Telemetry Log
            await db.save_agent_log(
                agent_name=agent_name,
                status="success",
                input_params=input_params,
                output_response=question_data.dict()
            )
            
            # Create session document
            session_data = {
                "session_id": session_id,
                "type": interview_type,
                "role": role,
                "current_question": question_data.question,
                "hint": question_data.hint,
                "completed": False,
                "chat_history": [
                    {"role": "interviewer", "content": question_data.question}
                ],
                "evaluation": None
            }
            await db.save_session(session_id, session_data)
            
            return {
                "session_id": session_id,
                "question": question_data.question
            }
        except Exception as e:
            logger.error(f"InterviewerAgent execution error: {e}")
            await db.save_agent_log(
                agent_name=agent_name,
                status="failure",
                input_params=input_params,
                output_response=None,
                error=str(e)
            )
            raise e

    @staticmethod
    async def submit_answer(session_id: str, answer: str) -> EvaluationResult:
        agent_name = "EvaluatorAgent"
        input_params = {"session_id": session_id, "answer": answer}
        try:
            # Retrieve interview session
            session = await db.get_session(session_id)
            if not session:
                raise ValueError("Interview session not found or expired.")
            
            if session.get("completed"):
                raise ValueError("This interview session has already been evaluated and closed.")
            
            question = session.get("current_question", "")
            role = session.get("role", "Software Engineer")
            interview_type = session.get("type", "tech")
            
            # Execute Evaluator Agent
            evaluation: EvaluationResult = await EvaluatorAgent.run(
                question=question,
                answer=answer,
                role=role,
                interview_type=interview_type
            )
            
            # Update session history and completion state
            session["chat_history"].append({"role": "candidate", "content": answer})
            session["completed"] = True
            session["evaluation"] = evaluation.dict()
            await db.save_session(session_id, session)
            
            # Telemetry Log
            await db.save_agent_log(
                agent_name=agent_name,
                status="success",
                input_params=input_params,
                output_response=evaluation.dict()
            )
            
            # Save to Completion History
            await db.save_history(
                item_type="interview",
                role=role,
                details={
                    "type": interview_type,
                    "question": question,
                    "answer": answer,
                    "score": evaluation.score,
                    "evaluation": evaluation.dict()
                }
            )
            
            return evaluation
        except Exception as e:
            logger.error(f"EvaluatorAgent execution error: {e}")
            await db.save_agent_log(
                agent_name=agent_name,
                status="failure",
                input_params=input_params,
                output_response=None,
                error=str(e)
            )
            raise e

    @staticmethod
    async def request_hint(session_id: str) -> str:
        # Simple lookup in DB, no Gemini call required directly, but we fetch the hint.
        session = await db.get_session(session_id)
        if not session:
            raise ValueError("Interview session not found.")
        
        hint = session.get("hint", "No hint available for this question.")
        
        # Log the transaction as agent_log for transparency
        await db.save_agent_log(
            agent_name="OrchestratorHintLookup",
            status="success",
            input_params={"session_id": session_id},
            output_response={"hint": hint}
        )
        return hint
