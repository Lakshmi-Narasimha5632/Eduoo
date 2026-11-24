"""OpenAI-compatible AI Provider."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict
import httpx

from .base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    provider_name = "openai"
    ENDPOINT = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key:
            from .fallback import LocalFallbackProvider
            return LocalFallbackProvider().generate_text(prompt, system_prompt)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(
                    self.ENDPOINT,
                    headers=headers,
                    json={"model": self.model, "messages": messages, "temperature": 0.3},
                )
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
        except Exception:
            pass

        from .fallback import LocalFallbackProvider
        return LocalFallbackProvider().generate_text(prompt, system_prompt)

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        text = self.generate_text(prompt, system_prompt)
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except Exception:
                pass

        from .fallback import LocalFallbackProvider
        return LocalFallbackProvider().generate_json(prompt, system_prompt)
