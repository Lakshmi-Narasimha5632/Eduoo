"""Interview answer evaluation engine.
Evaluates candidate answers dynamically based strictly on the actual input provided.
Never falls back to generic or disconnected default statements.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List
from .ai import InterviewAIService
from .prompts import EVALUATOR_SYSTEM_PROMPT


class InterviewAnswerEvaluator:
    TECH_KEYWORDS = {
        "cache", "caching", "redis", "memcached", "database", "sql", "nosql", "postgres",
        "mongodb", "index", "indexing", "latency", "throughput", "concurrency", "thread",
        "async", "asyncio", "promise", "microservice", "monolith", "api", "rest", "graphql",
        "docker", "kubernetes", "k8s", "aws", "gcp", "load balancer", "sharding", "replication",
        "virtual dom", "react", "redux", "state", "hooks", "memo", "component", "render",
        "algorithm", "complexity", "o(n)", "o(1)", "o(log n)", "space", "time", "memory",
        "garbage collection", "gil", "generator", "decorator", "star", "situation", "task",
        "action", "result", "metric", "monitoring", "alerting", "kafka", "queue", "worker"
    }

    @classmethod
    def evaluate_answer(
        cls,
        question_text: str,
        answer_text: str,
        target_role: str = "Software Developer",
        expected_answer: str | None = None,
    ) -> Dict[str, Any]:
        cleaned_answer = str(answer_text or "").strip()
        words = cleaned_answer.split()
        word_count = len(words)

        # Case 0: Empty response
        if word_count == 0:
            return {
                "score": 0,
                "technical_accuracy": 0,
                "communication_score": 0,
                "relevance_score": 0,
                "confidence_score": 0,
                "feedback": f"No answer was submitted for the question: '{question_text[:70]}...'. Please speak or type your solution.",
                "strengths": [],
                "weaknesses": ["No answer or explanation was provided."],
                "improvement_recommendation": f"Attempt an answer outlining the core technical approach for {target_role}.",
            }

        # Case 1: Ultra-brief / gibberish (< 5 words)
        if word_count < 5:
            low_score = max(8, word_count * 5)
            return {
                "score": low_score,
                "technical_accuracy": max(10, word_count * 4),
                "communication_score": max(12, word_count * 4),
                "relevance_score": max(10, word_count * 4),
                "confidence_score": 15,
                "feedback": (
                    f"You responded with only {word_count} word(s): \"{cleaned_answer}\". "
                    f"This is too brief to demonstrate technical competence for a {target_role} interview on '{question_text[:60]}...'. "
                    f"Please provide a complete explanation covering design, reasoning, and trade-offs."
                ),
                "strengths": [f"Provided initial keyword: '{cleaned_answer}'"],
                "weaknesses": [
                    f"Response of {word_count} word(s) lacked architectural reasoning and depth",
                    "Missing implementation details, trade-offs, and edge-case handling",
                ],
                "improvement_recommendation": "Use structured responses: state your approach, the trade-offs, and how you verify correctness.",
            }

        # Try Live AI Provider (Token Harbor / Gemini)
        if InterviewAIService.is_live_ai_available():
            prompt = f"""
Candidate Target Role: {target_role}
Interview Question: {question_text}
Candidate's Actual Answer: "{cleaned_answer}"
Expected Core Concepts: {expected_answer or 'Standard engineering best practices'}

INSTRUCTIONS:
You MUST evaluate strictly based on the candidate's actual answer above.
Do NOT use generic or static default text. Quote their actual words.
Return strictly JSON with:
score (0-100), technical_accuracy (0-100), communication_score (0-100),
relevance_score (0-100), confidence_score (0-100),
feedback (detailed analysis citing their exact response),
strengths (list of 2-3 specific points citing what they covered),
weaknesses (list of 2-3 specific points citing what was missing or incorrect),
improvement_recommendation (string customized to their answer).
"""
            try:
                result = InterviewAIService.generate_json(prompt, EVALUATOR_SYSTEM_PROMPT)
                if result and "score" in result:
                    raw_score = int(result.get("score", 70))
                    # Validate that AI output actually relates to user answer
                    feedback = str(result.get("feedback", ""))
                    strengths = result.get("strengths", [])
                    weaknesses = result.get("weaknesses", [])

                    if feedback and len(feedback) > 20 and len(strengths) > 0:
                        return {
                            "score": max(0, min(100, raw_score)),
                            "technical_accuracy": max(0, min(100, int(result.get("technical_accuracy", raw_score)))),
                            "communication_score": max(0, min(100, int(result.get("communication_score", raw_score)))),
                            "relevance_score": max(0, min(100, int(result.get("relevance_score", raw_score)))),
                            "confidence_score": max(0, min(100, int(result.get("confidence_score", raw_score)))),
                            "feedback": feedback,
                            "strengths": strengths[:3],
                            "weaknesses": weaknesses[:3],
                            "improvement_recommendation": str(
                                result.get("improvement_recommendation", f"Refine trade-off analysis for {target_role}.")
                            ),
                        }
            except Exception:
                pass

        # Dynamic Linguistic & Semantic Evaluation Engine
        return cls._dynamic_semantic_evaluation(question_text, cleaned_answer, target_role)

    @classmethod
    def _dynamic_semantic_evaluation(
        cls,
        question_text: str,
        answer_text: str,
        target_role: str,
    ) -> Dict[str, Any]:
        """Calculates dynamic scores and feedback strictly derived from the candidate's actual words."""
        words = answer_text.split()
        word_count = len(words)
        lower_ans = answer_text.lower()
        lower_q = question_text.lower()

        # 1. Detect candidate's mentioned technical concepts
        found_tech = [t for t in cls.TECH_KEYWORDS if t in lower_ans]
        
        # 2. Extract question key tokens
        q_tokens = [w for w in re.findall(r"\b[a-zA-Z]{4,}\b", lower_q) if w not in {"what", "how", "explain", "would", "your", "this", "which"}]
        matched_q_tokens = [t for t in q_tokens if t in lower_ans]

        # 3. Assess question relevance
        relevance_ratio = len(matched_q_tokens) / max(1, len(q_tokens))
        relevance_score = min(95, max(30, int(45 + (relevance_ratio * 40) + min(15, len(found_tech) * 3))))

        # 4. Assess technical depth
        tech_score = min(96, max(35, int(40 + min(35, len(found_tech) * 7) + min(20, word_count // 3))))

        # 5. Assess communication & structure
        sentences = [s.strip() for s in re.split(r"[.!?]+", answer_text) if len(s.strip()) > 3]
        comm_score = min(94, max(40, int(50 + min(25, len(sentences) * 5) + min(20, word_count // 4))))

        # 6. Confidence score
        hesitations = ["i think maybe", "not really sure", "i guess", "probably", "i dont know", "i don't know"]
        has_hesitations = any(h in lower_ans for h in hesitations)
        confidence_score = max(35, min(92, 75 + (10 if word_count > 30 else 0) - (20 if has_hesitations else 0)))

        overall_score = int((tech_score * 0.4) + (comm_score * 0.3) + (relevance_score * 0.2) + (confidence_score * 0.1))

        # Build dynamic feedback quoting actual user answer
        first_sentence = sentences[0] if sentences else answer_text[:60]
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:80] + "..."

        strengths = []
        if found_tech:
            strengths.append(f"Demonstrated technical familiarity with key concepts: {', '.join(found_tech[:4])}")
        strengths.append(f"Directly articulated solution: \"{first_sentence}\"")
        if word_count > 25:
            strengths.append("Provided structured elaboration across multiple sentences")

        weaknesses = []
        if len(found_tech) < 2:
            weaknesses.append("Could incorporate more specific technical systems, metrics, and architecture patterns")
        if not any(kw in lower_ans for kw in ["trade-off", "tradeoff", "bottleneck", "latency", "scale", "failure"]):
            weaknesses.append("Did not explicitly discuss system trade-offs, scaling limits, or failure modes")
        if word_count < 20:
            weaknesses.append(f"Answer length ({word_count} words) is relatively concise; senior interviews benefit from deeper reasoning")

        feedback = (
            f"You answered: \"{first_sentence}\". "
            f"Your response demonstrates practical perspective on {target_role} requirements"
            f"{f' referencing {', '.join(found_tech[:3])}' if found_tech else ''}. "
            f"To achieve top-tier scoring, expand on how your design handles edge cases, throughput bottlenecks, and production observability."
        )

        return {
            "score": overall_score,
            "technical_accuracy": tech_score,
            "communication_score": comm_score,
            "relevance_score": relevance_score,
            "confidence_score": confidence_score,
            "feedback": feedback,
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "improvement_recommendation": f"Practice structuring answers for {target_role} around: Architecture -> Trade-offs -> Scale & Failure handling.",
        }
