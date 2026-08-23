"""Secure AI Interview Question Generator with Local PII Scrubbing & Schema Validation.

Implements zero-egress PII sanitization (OWASP LLM01 mitigation), structured Pydantic schemas,
and deterministic evaluation rubrics for candidate interviews.
"""

import os
import re
import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("SecureQuestionGenerator")


# =============================================================================
# 1. DETERMINISTIC VALIDATION SCHEMAS
# =============================================================================
class InterviewQuestion(BaseModel):
    question: str = Field(..., description="The behavioral or technical interview question.")
    target_competency: str = Field(..., description="The specific skill or competency being evaluated.")
    expected_answer_signals: List[str] = Field(default_factory=list, description="Key points or keywords to look for in a strong response.")
    red_flags: List[str] = Field(default_factory=list, description="Indicators of a poor or disqualifying response.")


class InterviewGuide(BaseModel):
    role_title: str = Field(default="Software Engineer", description="The anonymized title of the role.")
    difficulty_level: str = Field(default="Mid", description="Junior, Mid, Senior, or Lead.")
    questions: List[InterviewQuestion] = Field(default_factory=list, description="List of structured interview questions.")


# =============================================================================
# 2. LOCAL PII SCRUBBING LAYER
# =============================================================================
class PIIScrubber:
    """Surgical PII removal before data hits any model boundary."""
    EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE)
    PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    LINKEDIN_REGEX = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)
    GITHUB_REGEX = re.compile(r'github\.com/[\w-]+', re.IGNORECASE)

    @classmethod
    def scrub(cls, text: str) -> str:
        if not text:
            return ""
        scrubbed = text
        scrubbed = cls.EMAIL_REGEX.sub("[REDACTED_EMAIL]", scrubbed)
        scrubbed = cls.PHONE_REGEX.sub("[REDACTED_PHONE]", scrubbed)
        scrubbed = cls.LINKEDIN_REGEX.sub("[REDACTED_LINKEDIN]", scrubbed)
        scrubbed = cls.GITHUB_REGEX.sub("[REDACTED_GITHUB]", scrubbed)
        return scrubbed


# =============================================================================
# 3. SECURE QUESTION GENERATOR ENGINE
# =============================================================================
class SecureQuestionGenerator:
    """Generates structured, PII-scrubbed technical & behavioral interview guides."""

    def __init__(self, model_name: str = "phi3:latest"):
        self.model_name = model_name

    def generate_guide(
        self,
        raw_job_desc: str,
        raw_candidate_profile: str,
        difficulty: str = "Senior",
    ) -> InterviewGuide:
        """Scrubs PII, invokes model/heuristics, validates schema, and returns InterviewGuide."""
        # 1. Scrub PII
        clean_jd = PIIScrubber.scrub(raw_job_desc)
        clean_profile = PIIScrubber.scrub(raw_candidate_profile)

        # 2. Extract key competencies & skills
        competencies = self._extract_competencies(clean_jd, clean_profile)

        # 3. Generate structured questions
        questions = []
        for comp in competencies[:4]:
            q = self._create_question_for_competency(comp, difficulty)
            questions.append(q)

        # Add culture / behavioral question
        questions.append(
            InterviewQuestion(
                question=f"Describe a situation where you had to debug a critical production issue under tight deadlines. How did you diagnose and resolve it?",
                target_competency="Production Problem Solving & Resilience",
                expected_answer_signals=[
                    "Systematic root cause analysis",
                    "Monitoring & structured log inspection",
                    "Clear stakeholder communication",
                    "Post-mortem prevention planning",
                ],
                red_flags=[
                    "Blaming teammates or lack of accountability",
                    "Cowboy deployments without testing",
                    "Panic without structured troubleshooting",
                ],
            )
        )

        return InterviewGuide(
            role_title=self._extract_role_title(clean_jd),
            difficulty_level=difficulty,
            questions=questions,
        )

    def _extract_role_title(self, jd_text: str) -> str:
        for line in jd_text.splitlines():
            line_str = line.strip()
            if any(k in line_str.lower() for k in ("engineer", "developer", "architect", "lead", "manager", "specialist")):
                return line_str[:50]
        return "Senior Technical Role"

    def _extract_competencies(self, jd_text: str, profile_text: str) -> List[str]:
        common_skills = [
            ("Python & Backend Architecture", ["python", "django", "fastapi", "flask", "backend", "api"]),
            ("Database Optimization & SQL", ["postgres", "postgresql", "sql", "supabase", "database", "redis"]),
            ("AI & Machine Learning Systems", ["llm", "ai", "machine learning", "rag", "embeddings", "nlp", "langchain"]),
            ("Cloud Infrastructure & DevOps", ["docker", "kubernetes", "aws", "gcp", "ci/cd", "devops", "cloud"]),
            ("Frontend State & Modern UI", ["react", "typescript", "javascript", "vue", "nextjs", "tailwind"]),
            ("System Design & Distributed Scalability", ["microservices", "kafka", "scalability", "distributed", "grpc"]),
        ]
        
        combined = (jd_text + " " + profile_text).lower()
        matched = []
        for name, keywords in common_skills:
            if any(k in combined for k in keywords):
                matched.append(name)
        
        if not matched:
            matched = ["Core System Architecture", "Data Structures & Algorithmic Efficiency", "API Design & Integration"]
        return matched

    def _create_question_for_competency(self, competency: str, difficulty: str) -> InterviewQuestion:
        templates = {
            "Python & Backend Architecture": {
                "question": "How do you design asynchronous background tasks and worker queues in Python to prevent blocking the main HTTP event loop?",
                "signals": ["FastAPI background tasks or Celery/Redis", "Asyncio event loop mechanics", "Dead letter queue & retry policies"],
                "flags": ["Blocking sync operations in async endpoints", "No idempotency or error retry strategy"],
            },
            "Database Optimization & SQL": {
                "question": "How would you optimize a slow PostgreSQL query involving millions of candidate records with joins across applications and scorecards?",
                "signals": ["EXPLAIN ANALYZE execution plan inspection", "Composite indexes & partial indexes", "Connection pooling (PgBouncer) & partitioning"],
                "flags": ["Adding indexes blindly without looking at query plans", "Unindexed full table scans"],
            },
            "AI & Machine Learning Systems": {
                "question": "When building an agentic RAG system, how do you mitigate hallucination and protect against indirect prompt injection from untrusted user documents?",
                "signals": ["Strict Pydantic JSON output validation", "Isolating untrusted text into user context", "Deterministic guardrails & citations"],
                "flags": ["Interpolating raw candidate text directly into system instructions", "Trusting LLM raw text output without schema gates"],
            },
            "Cloud Infrastructure & DevOps": {
                "question": "How do you implement zero-downtime rolling deployments with automated health checks and instant canary rollbacks?",
                "signals": ["Blue/green or rolling update strategies", "Liveness and readiness probes", "Automated telemetry-triggered rollbacks"],
                "flags": ["Manual server SSH deployments", "No staging parity or health probes"],
            },
            "Frontend State & Modern UI": {
                "question": "How do you manage complex real-time Kanban board state with optimistic UI updates and websocket conflict resolution?",
                "signals": ["Optimistic UI mutation with rollback on failure", "Normalized state management", "Debounced server sync"],
                "flags": ["Full page reloads on drag events", "No error rollback state on network timeout"],
            },
        }

        entry = templates.get(competency, {
            "question": f"Can you walk through your technical approach to scaling and securing {competency} in high-throughput environments?",
            "signals": ["Clear trade-off analysis", "Security & boundary validation", "Modular architecture"],
            "flags": ["Vague buzzwords without concrete trade-offs", "Ignoring failure modes"],
        })

        return InterviewQuestion(
            question=f"[{difficulty}] {entry['question']}",
            target_competency=competency,
            expected_answer_signals=entry["signals"],
            red_flags=entry["flags"],
        )


DEFAULT_SECURE_QUESTION_GENERATOR = SecureQuestionGenerator()
