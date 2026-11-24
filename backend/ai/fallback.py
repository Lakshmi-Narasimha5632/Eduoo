"""Intelligent local fallback AI provider operating deterministically without external keys."""

from __future__ import annotations

import re
from typing import Any, Dict
from .base import BaseAIProvider


class LocalFallbackProvider(BaseAIProvider):
    provider_name = "fallback"

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        prompt_lower = prompt.lower()
        if "question" in prompt_lower:
            return "Can you explain how you designed your most complex project, what architectural tradeoffs you made, and how you ensured database performance?"
        if "evaluat" in prompt_lower or "answer" in prompt_lower:
            return "Good structured explanation with clear project examples. Consider elaborating on how you handle edge cases and high-concurrency scaling."
        return "You have demonstrated solid engineering skills and clear communication. Focus on system design trade-offs to reach senior level."

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # Handle interview question generation request
        if "generate question" in prompt_lower or "question number" in prompt_lower or ("role:" in prompt_lower and "question" in prompt_lower):
            role_match = re.search(r"role:\s*([^\n\r,]+)", prompt, re.IGNORECASE)
            role_str = role_match.group(1).strip() if role_match else "Software Developer"
            q_num_match = re.search(r"question\s*(?:number|#)?\s*:?\s*(\d+)", prompt, re.IGNORECASE)
            q_num = int(q_num_match.group(1)) if q_num_match else 2

            templates = [
                f"Can you explain a high-impact project you delivered as a {role_str}, detailing your architectural decisions and technical trade-offs?",
                f"In your work as a {role_str}, how do you diagnose and resolve critical production bottlenecks, latency spikes, or bugs?",
                f"How do you design and structure a scalable, resilient system or pipeline tailored for modern {role_str} workflows?",
                f"What are the most crucial trade-offs you evaluate when choosing tools, libraries, or frameworks for {role_str} deliverables?",
                f"Describe a complex edge case you encountered in {role_str} practice and the exact methodology you used to verify its fix.",
            ]
            q_text = templates[(q_num - 2) % len(templates)]
            return {
                "question": q_text,
                "category": "technical",
                "difficulty": "intermediate",
                "expected_answer": f"Demonstrates strong technical competence in {role_str} practices, architecture, and edge-case handling.",
            }

        # Handle answer evaluation request
        if "evaluat" in prompt_lower or "score" in prompt_lower or "candidate" in prompt_lower:
            words = len(prompt.split())
            accuracy = min(95, max(60, 65 + min(25, words // 4)))
            comm = min(92, max(65, 68 + min(20, words // 5)))
            rel = min(94, max(65, 70 + min(20, words // 6)))
            conf = min(90, max(60, 65 + min(20, words // 5)))
            overall = int((accuracy * 0.4) + (comm * 0.3) + (rel * 0.2) + (conf * 0.1))

            return {
                "score": overall,
                "technical_accuracy": accuracy,
                "communication_score": comm,
                "relevance_score": rel,
                "confidence_score": conf,
                "strengths": [
                    "Structured presentation and logical progression",
                    "Good domain familiarity with tech stack concepts",
                ],
                "weaknesses": [
                    "Could specify more numerical metrics and performance benchmarks",
                    "Elaborate further on trade-offs when choosing specific architectures",
                ],
                "feedback": "Strong answer demonstrating practical familiarity. Enhance future answers by explicitly highlighting bottlenecks and how you resolved them.",
                "improvement_recommendation": "Practice articulating system design choices using time/space complexity and concurrency considerations.",
            }

        # Default fallback
        return {
            "question": "Can you explain how you handled state management and backend API latency in your main project?",
            "category": "technical",
            "difficulty": "medium",
            "expected_answer": "Candidate should mention caching, database query optimization, asynchronous processing, and clean client-side state handling.",
        }
