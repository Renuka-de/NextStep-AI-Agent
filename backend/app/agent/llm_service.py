"""
LLM Service — abstraction layer supporting Gemini, OpenAI, and Mock (demo mode).
Import and call: llm_service.generate(prompt) -> str
"""
import json
import re
from typing import Optional
from app.core.config import settings


class MockLLMService:
    """
    Deterministic fallback for demo mode when no API key is configured.
    Produces realistic-sounding but template-based responses.
    """

    NEXT_STEP_TEMPLATES = {
        "mern": [
            "Initialize your Node.js project: run `npm init -y` in your project folder.",
            "Install core dependencies: `npm install express mongoose dotenv cors jsonwebtoken bcryptjs`",
            "Create your folder structure: `mkdir routes models middleware controllers`",
            "Write your first Mongoose schema for the User model with name, email, and password fields.",
            "Implement the `/api/auth/register` POST endpoint with bcrypt password hashing.",
            "Build the `/api/auth/login` endpoint that returns a signed JWT token.",
            "Create the `authMiddleware.js` that verifies JWT on protected routes.",
            "Design the Expense schema with amount, category, date, and description fields.",
            "Build CRUD endpoints: GET /expenses, POST /expenses, PUT /expenses/:id, DELETE /expenses/:id",
            "Initialize the React frontend with Vite: `npm create vite@latest client -- --template react`",
        ],
        "dsa": [
            "Start with Arrays — solve 'Two Sum' on LeetCode (problem #1).",
            "Solve 'Best Time to Buy and Sell Stock' — practice sliding window thinking.",
            "Move to Strings — solve 'Valid Anagram' and 'Longest Substring Without Repeating Characters'.",
            "Study Linked Lists — implement a singly linked list from scratch (insert, delete, reverse).",
            "Solve 'Reverse Linked List' on LeetCode (#206).",
            "Learn Binary Search — implement it from scratch on a sorted array.",
            "Solve 'Find Minimum in Rotated Sorted Array' to apply binary search on modified arrays.",
            "Study Stacks — implement a stack and solve 'Valid Parentheses' (#20).",
            "Learn Queues and solve 'Number of Islands' using BFS.",
            "Study Trees — implement in-order, pre-order, post-order traversal.",
        ],
        "ml": [
            "Review NumPy basics — practice array creation, slicing, and broadcasting.",
            "Study Pandas — load a CSV, inspect with `.head()`, `.info()`, `.describe()`.",
            "Implement Linear Regression from scratch using the normal equation.",
            "Use scikit-learn's LinearRegression to fit the Boston Housing dataset.",
            "Study the bias-variance tradeoff — understand underfitting vs overfitting.",
            "Implement Gradient Descent manually for a simple 2D dataset.",
            "Learn Logistic Regression — implement sigmoid function and binary cross-entropy loss.",
            "Study Decision Trees — understand information gain and Gini impurity.",
            "Implement k-Nearest Neighbors from scratch and evaluate on Iris dataset.",
            "Practice cross-validation with StratifiedKFold from scikit-learn.",
        ],
        "general": [
            "Break your goal into 3-5 concrete milestones. Write them down.",
            "Focus on milestone 1 first. What is the smallest possible first step you can take right now?",
            "Set a 25-minute Pomodoro timer and work without distractions.",
            "After completing a step, write a brief note about what you learned.",
            "Review your progress and identify any blockers before the next session.",
            "Research and collect the key resources (tutorials, docs, papers) you'll need.",
            "Set up your development environment before writing any code.",
            "Build the simplest possible working version first (MVP), then improve it.",
            "Write tests for what you built before moving to the next step.",
            "Document what you built — even 3 bullet points helps future you.",
        ],
    }

    def _detect_category(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["mern", "express", "mongo", "node", "react"]):
            return "mern"
        if any(w in text_lower for w in ["dsa", "leetcode", "algorithm", "data structure"]):
            return "dsa"
        if any(w in text_lower for w in ["ml", "machine learning", "model", "neural", "deep learning", "sklearn"]):
            return "ml"
        return "general"

    def generate_plan(self, goal_title: str, goal_description: str) -> dict:
        category = self._detect_category(goal_title + " " + goal_description)
        templates = self.NEXT_STEP_TEMPLATES.get(category, self.NEXT_STEP_TEMPLATES["general"])

        milestones = []
        chunks = [templates[i:i+3] for i in range(0, len(templates), 3)]
        phase_names = ["Foundation", "Core Implementation", "Advanced Topics", "Review & Practice"]

        for i, chunk in enumerate(chunks[:4]):
            phase = phase_names[i] if i < len(phase_names) else f"Phase {i+1}"
            tasks = []
            for j, task_title in enumerate(chunk):
                tasks.append({
                    "title": task_title,
                    "description": f"Focus on understanding and implementing: {task_title}",
                    "estimated_minutes": 30 + (j * 15),
                    "difficulty": ["easy", "medium", "hard"][min(j, 2)],
                    "order_index": j,
                })
            milestones.append({
                "title": phase,
                "description": f"Complete the {phase.lower()} tasks for your goal.",
                "order_index": i,
                "tasks": tasks,
            })

        return {
            "milestones": milestones,
            "rationale": f"This plan will guide you step-by-step through '{goal_title}' with focus on practical, hands-on progress.",
            "estimated_hours": len(templates) * 0.75,
        }

    def select_next_task(self, goal_title: str, completed_tasks: list, pending_tasks: list) -> dict:
        if not pending_tasks:
            return {"task_id": None, "rationale": "All tasks completed! Great work!"}

        next_task = pending_tasks[0]
        rationale = (
            f"You've completed {len(completed_tasks)} task(s). "
            f"The next step is: **{next_task['title']}**. "
            f"This builds directly on what you've already done."
        )
        return {"task_id": next_task["id"], "rationale": rationale}

    def analyze_stuck(self, task_title: str, student_message: str) -> dict:
        return {
            "diagnosis": "It seems you're finding this task challenging. That's completely normal!",
            "suggestion": f"Try breaking '{task_title}' into even smaller sub-steps. Start with just the first 10 minutes of work.",
            "alternatives": [
                "Take a 5-minute break and come back fresh.",
                "Search for a tutorial or example specifically for this step.",
                "Try explaining the problem out loud (rubber duck debugging).",
            ],
        }

    def observe_progress(self, task_title: str, student_message: str) -> dict:
        return {
            "assessment": "Great progress! You've completed this step.",
            "insights": [f"You successfully completed: {task_title}"],
            "next_hint": "Move on to the next task — keep the momentum going!",
        }

    def generate(self, prompt: str) -> str:
        return "I'm running in demo mode without an LLM API key. Please set GEMINI_API_KEY in your .env file for AI-powered responses."


class GeminiLLMService:
    """Gemini API powered LLM service using google-genai SDK."""

    def __init__(self):
        from google import genai
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.LLM_MODEL

    def generate(self, prompt: str) -> str:
        interaction = self.client.interactions.create(
            model=self.model,
            input=prompt,
        )
        return interaction.output_text or ""

    def generate_plan(self, goal_title: str, goal_description: str) -> dict:
        prompt = f"""You are NextStep, an AI agent that creates structured learning/project plans for students.

Goal: {goal_title}
Description: {goal_description}

Create a practical step-by-step plan. Return ONLY valid JSON (no markdown fences) in this exact format:
{{
  "milestones": [
    {{
      "title": "Milestone name",
      "description": "What this phase covers",
      "order_index": 0,
      "tasks": [
        {{
          "title": "Specific actionable task",
          "description": "What to do exactly",
          "estimated_minutes": 30,
          "difficulty": "easy|medium|hard",
          "order_index": 0
        }}
      ]
    }}
  ],
  "rationale": "Why this plan works",
  "estimated_hours": 20
}}

Rules:
- 3-5 milestones
- 3-6 tasks per milestone  
- Tasks must be specific and actionable (not vague like "learn JavaScript")
- Estimated minutes should be realistic (15-90 per task)
- Return ONLY JSON, no other text
"""
        response = self.generate(prompt)
        # Strip markdown fences if present
        response = re.sub(r"```json\s*", "", response)
        response = re.sub(r"```\s*", "", response)
        return json.loads(response.strip())

    def select_next_task(self, goal_title: str, completed_tasks: list, pending_tasks: list) -> dict:
        if not pending_tasks:
            return {"task_id": None, "rationale": "All tasks completed! Excellent work!"}

        completed_str = "\n".join(f"  ✅ {t['title']}" for t in completed_tasks[-5:]) or "  (none yet)"
        pending_str = "\n".join(f"  {i+1}. [{t['id']}] {t['title']}" for i, t in enumerate(pending_tasks[:8]))

        prompt = f"""You are NextStep, an AI agent guiding a student ONE STEP AT A TIME.

Goal: {goal_title}

Recently completed tasks:
{completed_str}

Pending tasks (with IDs):
{pending_str}

Select the single best next task for the student to work on right now.
Return ONLY valid JSON:
{{
  "task_id": "<exact task id from the list above>",
  "rationale": "Brief, encouraging explanation of why this is the right next step (1-2 sentences)"
}}"""

        response = self.generate(prompt)
        response = re.sub(r"```json\s*", "", response)
        response = re.sub(r"```\s*", "", response)
        data = json.loads(response.strip())
        # Validate task_id exists
        valid_ids = {t["id"] for t in pending_tasks}
        if data.get("task_id") not in valid_ids:
            data["task_id"] = pending_tasks[0]["id"]
        return data

    def observe_progress(self, task_title: str, student_message: str) -> dict:
        prompt = f"""Student just completed the task: "{task_title}"
Their note: "{student_message}"

Provide brief, encouraging feedback. Return ONLY valid JSON:
{{
  "assessment": "Encouraging feedback (1 sentence)",
  "insights": ["Key insight from completing this task"],
  "next_hint": "Brief hint about what's coming next (1 sentence)"
}}"""
        response = self.generate(prompt)
        response = re.sub(r"```json\s*", "", response)
        response = re.sub(r"```\s*", "", response)
        return json.loads(response.strip())

    def analyze_stuck(self, task_title: str, student_message: str) -> dict:
        prompt = f"""Student is stuck on task: "{task_title}"
Their message: "{student_message}"

Help them get unstuck. Return ONLY valid JSON:
{{
  "diagnosis": "What might be causing the struggle (1 sentence)",
  "suggestion": "Most helpful immediate action (1 sentence)",
  "alternatives": ["Option 1", "Option 2", "Option 3"]
}}"""
        response = self.generate(prompt)
        response = re.sub(r"```json\s*", "", response)
        response = re.sub(r"```\s*", "", response)
        return json.loads(response.strip())


def get_llm_service():
    """Factory function — returns appropriate LLM service based on config."""
    provider = settings.LLM_PROVIDER.lower()
    if provider == "mock" or not settings.GEMINI_API_KEY:
        return MockLLMService()
    if provider == "gemini":
        try:
            return GeminiLLMService()
        except Exception:
            return MockLLMService()
    return MockLLMService()


# Singleton
_llm_service = None


def llm():
    global _llm_service
    if _llm_service is None:
        _llm_service = get_llm_service()
    return _llm_service
