import logging
from backend.services.gemini_service import GeminiService
from backend.models.response_schemas import (
    StudyPlan, CodingArenaRecommendations, InterviewQuestion, EvaluationResult
)

logger = logging.getLogger("agents")

class PlannerAgent:
    @staticmethod
    async def run(role: str, skill_level: str, hours_per_day: float, target_date: str = "") -> StudyPlan:
        logger.info(f"Running Planner Agent for role={role}, skill_level={skill_level}")
        prompt = (
            f"System Instructions:\n"
            f"You are an expert study planner AI agent. Generate an unencapsulated, raw JSON structure conforming EXACTLY to the StudyPlan schema. Do not output markdown code blocks (e.g. ```json).\n\n"
            f"Prompt:\n"
            f"Create a granular 7-day study curriculum tailored to prepare a candidate for a '{role}' position.\n"
            f"Candidate skill level: {skill_level}\n"
            f"Available hours per day: {hours_per_day}\n"
            f"Target date for the placement: {target_date or 'Flexible'}\n"
            f"Make it comprehensive and actionable."
        )
        return await GeminiService.call_gemini(prompt, StudyPlan)

class RecommenderAgent:
    @staticmethod
    async def run(role: str, level: str) -> CodingArenaRecommendations:
        logger.info(f"Running Recommender Agent for role={role}, level={level}")
        prompt = (
            f"System Instructions:\n"
            f"You are an expert problem curation AI agent. Generate an unencapsulated, raw JSON structure conforming EXACTLY to the CodingArenaRecommendations schema. Do not output markdown code blocks (e.g. ```json).\n\n"
            f"Prompt:\n"
            f"Curate exactly 3 tailored coding challenges matching the role '{role}' and difficulty target '{level}'.\n"
            f"Provide diverse and realistic problems that test core skills for a '{role}' at this level."
        )
        return await GeminiService.call_gemini(prompt, CodingArenaRecommendations)

class InterviewerAgent:
    @staticmethod
    async def run(interview_type: str, role: str) -> InterviewQuestion:
        logger.info(f"Running Interviewer Agent for type={interview_type}, role={role}")
        prompt = (
            f"System Instructions:\n"
            f"You are an AI Interviewer Agent. Generate an unencapsulated, raw JSON structure conforming EXACTLY to the InterviewQuestion schema. Do not output markdown code blocks (e.g. ```json).\n\n"
            f"Prompt:\n"
            f"Generate one realistic, highly contextual mock interview question for the position '{role}'.\n"
            f"Interview format: {interview_type} (either 'tech' for technical, or 'hr' for human resources/behavioral).\n"
            f"Provide a helpful hidden hint that can guide a struggling candidate."
        )
        return await GeminiService.call_gemini(prompt, InterviewQuestion)

class EvaluatorAgent:
    @staticmethod
    async def run(question: str, answer: str, role: str, interview_type: str) -> EvaluationResult:
        logger.info(f"Running Evaluator Agent for role={role}, type={interview_type}")
        prompt = (
            f"System Instructions:\n"
            f"You are an AI Interview Evaluator Agent. Generate an unencapsulated, raw JSON structure conforming EXACTLY to the EvaluationResult schema. Do not output markdown code blocks (e.g. ```json).\n\n"
            f"Prompt:\n"
            f"Critically score the candidate's answer for the role of '{role}' during a '{interview_type}' interview.\n"
            f"Question asked: {question}\n"
            f"Candidate answer: {answer}\n"
            f"Rate the answer score from 1 (inadequate) to 10 (perfect). List constructive strengths, weaknesses, actionable tips for improvement, and dynamically suggest the next tier ('Easy', 'Medium', 'Hard')."
        )
        return await GeminiService.call_gemini(prompt, EvaluationResult)
