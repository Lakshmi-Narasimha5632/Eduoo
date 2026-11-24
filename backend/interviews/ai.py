"""AI interface for interviews delegating to the application AIService."""

# pyrefly: ignore [missing-import]
from ai.services import AIService


class InterviewAIService:
    @staticmethod
    def is_live_ai_available() -> bool:
        return AIService.is_live_ai_available()

    @staticmethod
    def generate_json(prompt: str, system_prompt: str = ""):
        return AIService.generate_json(prompt, system_prompt)

    @staticmethod
    def generate_text(prompt: str, system_prompt: str = ""):
        return AIService.generate_text(prompt, system_prompt)
