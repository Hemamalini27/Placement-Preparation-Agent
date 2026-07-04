import asyncio
import json
import logging
import random
from typing import Type, Any, Dict, List
import google.generativeai as genai
from backend.config import settings
from backend.models.response_schemas import (
    StudyPlan, StudyDay, CodingChallenge, CodingArenaRecommendations,
    InterviewQuestion, EvaluationResult
)

logger = logging.getLogger("gemini_service")

# Flag indicating if Gemini client has been configured and is likely functional
is_gemini_available = False
if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        is_gemini_available = True
        logger.info("Google Generative AI configured successfully.")
    except Exception as e:
        logger.error(f"Error configuring Google Generative AI: {e}. Fallback to mock data will be used.")
else:
    logger.warning("GEMINI_API_KEY not configured. Running in offline/mock mode.")

class GeminiService:
    @staticmethod
    async def call_gemini(prompt: str, response_schema: Type[Any]) -> Any:
        """
        Calls Gemini API with the specified prompt and output schema.
        Falls back to mock data if not configured or in case of error.
        """
        if is_gemini_available:
            try:
                # Use the recommended gemini-1.5-flash model
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Configure generation with schema enforcement
                generation_config = genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.7
                )
                
                # Execute blocking Gemini call in a separate thread executor to keep FastAPI async loop free
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(prompt, generation_config=generation_config)
                )
                
                if response and response.text:
                    logger.info("Successfully fetched response from Gemini API.")
                    # Parse output JSON into response_schema
                    data = json.loads(response.text)
                    return response_schema(**data)
                else:
                    logger.warning("Empty response received from Gemini API. Falling back to mock data.")
            except Exception as e:
                logger.error(f"Gemini API invocation error: {e}. Falling back to mock data.")
        
        # Graceful fallback logic
        return GeminiService.generate_mock_data(prompt, response_schema)

    @staticmethod
    def generate_mock_data(prompt: str, response_schema: Type[Any]) -> Any:
        """
        Generates realistic data structures matching the required Pydantic models.
        """
        logger.info(f"Generating mock data for schema: {response_schema.__name__}")
        
        # 1. Study Plan Mock Generator
        if response_schema == StudyPlan:
            # Simple heuristic extraction from prompt
            role = "Software Engineer"
            if "role" in prompt.lower():
                try:
                    # extract role from prompt
                    role = prompt.split("role '")[1].split("'")[0]
                except Exception:
                    pass
            
            days = []
            topics_pool = [
                ["Data Structures & Algorithms", "Big-O Notation", "Arrays & Hashing"],
                ["Linked Lists & Trees", "Recursion", "Binary Search Trees"],
                ["Dynamic Programming Basics", "Memoization", "Tabulation", "Greedy Algorithms"],
                ["System Design Fundamentals", "Scalability", "Load Balancers", "Caching"],
                ["Database Operations & Optimization", "SQL vs NoSQL", "Indexing", "Transactions"],
                ["API Design & Web Development", "REST APIs", "HTTP Protocols", "Security Concepts"],
                ["Behavioral Interview Preparation", "STAR Method", "Mock Coding Challenge Review", "Final Prep"]
            ]
            
            for i in range(1, 8):
                days.append(StudyDay(
                    day=f"Day {i}",
                    topics=topics_pool[i-1],
                    practice_tasks=[
                        f"Implement and solve 2 LeetCode problems related to {topics_pool[i-1][0]}",
                        f"Write a comprehensive summary of {topics_pool[i-1][1]} on a notepad"
                    ],
                    revision=f"Review key interview cheat sheets on {topics_pool[i-1][-1]} before bed."
                ))
            
            return StudyPlan(
                role=role,
                estimated_hours=28.0,
                days=days
            )

        # 2. Coding Arena Mock Generator
        elif response_schema == CodingArenaRecommendations:
            role = "Developer"
            if "role" in prompt.lower():
                try:
                    role = prompt.split("role '")[1].split("'")[0]
                except Exception:
                    pass

            level = "Medium"
            if "difficulty" in prompt.lower() or "level" in prompt.lower():
                for lvl in ["Easy", "Medium", "Hard"]:
                    if lvl.lower() in prompt.lower():
                        level = lvl
            
            challenges = [
                CodingChallenge(
                    name=f"Invert Binary Tree ({role} Prep)",
                    difficulty=level,
                    topic="Trees & Recursion",
                    description="Given the root of a binary tree, invert the tree, and return its root.",
                    reason=f"Commonly asked in {role} screening rounds to test understanding of tree structures."
                ),
                CodingChallenge(
                    name=f"LRU Cache Design",
                    difficulty="Hard" if level == "Hard" else "Medium",
                    topic="Design / Data Structures",
                    description="Design a data structure that follows the constraints of a Least Recently Used (LRU) cache with O(1) time complexity.",
                    reason="Assesses memory management, hash map, and doubly linked list synchronization skills."
                ),
                CodingChallenge(
                    name="Two Sum Variant",
                    difficulty="Easy" if level == "Easy" else "Medium",
                    topic="Arrays & Hashing",
                    description="Given an array of integers, return indices of the two numbers such that they add up to a specific target.",
                    reason="Tests basic algorithmic syntax and optimization from O(N^2) to O(N)."
                )
            ]
            return CodingArenaRecommendations(challenges=challenges[:3])

        # 3. Interview Question Mock Generator
        elif response_schema == InterviewQuestion:
            is_tech = "tech" in prompt.lower()
            role = "Software Engineer"
            if "role" in prompt.lower() or "position" in prompt.lower():
                try:
                    role = prompt.split("position '")[1].split("'")[0]
                except Exception:
                    try:
                        role = prompt.split("role '")[1].split("'")[0]
                    except Exception:
                        pass
            
            if is_tech:
                questions = [
                    f"Explain the difference between a process and a thread. How would you handle race conditions in a multi-threaded {role} application?",
                    f"What is database indexing, and how does it speed up queries? Are there scenarios where indexing might slow down write operations?",
                    f"Describe the difference between REST, GraphQL, and WebSockets. When would you use WebSockets over REST in a {role} environment?"
                ]
                hints = [
                    "Think about shared memory space vs isolated memory space, and sync constructs like Mutex or Semaphore.",
                    "Consider B-Trees/B+Trees and the overhead of maintaining the tree structure during insert/update operations.",
                    "Focus on bidirectional persistent connection requirements versus stateless request-response overhead."
                ]
            else:  # HR question
                questions = [
                    "Tell me about a time you faced a difficult conflict within a engineering team. How did you approach resolving it and what was the outcome?",
                    f"Why do you want to join this company as a {role}, and what strengths do you bring that align with our core engineering culture?",
                    "Describe a project you worked on that failed. What went wrong, what did you learn, and how did you apply that to future projects?"
                ]
                hints = [
                    "Use the STAR method (Situation, Task, Action, Result). Focus on constructive communication.",
                    "Research the company's core values. Focus on continuous learning, ownership, and collaboration.",
                    "Take ownership. Focus on transparency, root cause analysis, and the positive changes you implemented afterward."
                ]
            
            idx = random.randint(0, 2)
            return InterviewQuestion(
                question=questions[idx],
                hint=hints[idx]
            )

        # 4. Evaluation Result Mock Generator
        elif response_schema == EvaluationResult:
            score = random.randint(6, 9)
            
            # Simple grading heuristic based on length
            answer = ""
            if "answer: '" in prompt:
                answer = prompt.split("answer: '")[1].split("'")[0]
            
            if len(answer) < 20:
                score = random.randint(3, 5)

            strengths = [
                "Identified the core concept accurately",
                "Demonstrated a clear grasp of theoretical fundamentals"
            ]
            weaknesses = [
                "Lacked granular implementation details",
                "Did not address potential edge cases or optimization pathways"
            ]
            tips = [
                "Try to elaborate on real-world examples in your follow-ups",
                "Reference memory and time complexity constraints explicitly (e.g. Big-O notation)"
            ]
            
            next_diff = "Medium"
            if score >= 8:
                next_diff = "Hard"
                strengths.append("High levels of structural clarity in presentation")
            elif score <= 5:
                next_diff = "Easy"
                weaknesses.append("Answer is too brief or incomplete")
                tips.append("Try to structure your answer using the STAR framework or step-by-step logic")

            return EvaluationResult(
                score=score,
                strengths=strengths,
                weaknesses=weaknesses,
                tips=tips,
                next_difficulty=next_diff
            )
        
        raise ValueError(f"Unknown response schema: {response_schema}")

