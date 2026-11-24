"""Token Harbor AI Provider (OpenAI-compatible unified multi-model API gateway)."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any, Dict, List
import httpx

from .base import BaseAIProvider

logger = logging.getLogger(__name__)


class TokenHarborProvider(BaseAIProvider):
    provider_name = "token_harbor"
    DEFAULT_BASE_URL = "https://tokenharbor.ai/v1"
    DEFAULT_MODELS = ["deepseek-chat", "gpt-4o-mini", "gemini-2.5-flash", "deepseek-reasoner"]

    _cooldown_until: float = 0.0

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        raw_key = (
            api_key
            or os.getenv("TOKEN_HARBOR_API_KEY", "")
            or os.getenv("GEMINI_API_KEY", "")
            or os.getenv("OPENAI_API_KEY", "")
        )
        self.api_key = raw_key.strip()

        raw_base = base_url or os.getenv("TOKEN_HARBOR_BASE_URL", self.DEFAULT_BASE_URL)
        self.base_url = raw_base.strip().rstrip("/")
        if not self.base_url.endswith("/v1"):
            self.endpoint = f"{self.base_url}/v1/chat/completions"
        else:
            self.endpoint = f"{self.base_url}/chat/completions"

        custom_model = (model or os.getenv("TOKEN_HARBOR_MODEL", "")).strip()
        if custom_model:
            self.models: List[str] = [custom_model] + [m for m in self.DEFAULT_MODELS if m != custom_model]
        else:
            self.models: List[str] = list(self.DEFAULT_MODELS)

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or time.time() < TokenHarborProvider._cooldown_until:
            return self._fallback_generate_text(prompt, system_prompt)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=15.0) as client:
            for model_name in self.models:
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": 0.5,
                }
                try:
                    res = client.post(self.endpoint, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "")
                            if content:
                                return content.strip()
                    elif res.status_code in (401, 403, 429):
                        logger.warning(
                            "Token Harbor auth/quota/rate error (%d). Cooldown for 60s: %s",
                            res.status_code,
                            res.text[:180],
                        )
                        TokenHarborProvider._cooldown_until = time.time() + 60.0
                        break
                    elif res.status_code in (404, 502, 503):
                        logger.warning("Token Harbor model %s returned status %d. Trying next...", model_name, res.status_code)
                        continue
                    else:
                        logger.error("Token Harbor error (%d): %s", res.status_code, res.text[:200])
                except Exception as exc:
                    logger.warning("Token Harbor request failed for %s: %s", model_name, exc)
                    continue

        return self._fallback_generate_text(prompt, system_prompt)

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or time.time() < TokenHarborProvider._cooldown_until:
            return self._fallback_generate_json(prompt, system_prompt)

        json_system = (
            (system_prompt + "\n\nCRITICAL: Respond ONLY with valid JSON. Do not include markdown codeblocks.")
            if system_prompt
            else "Respond ONLY with a valid JSON object matching the requested schema."
        )

        text = self.generate_text(prompt, system_prompt=json_system)
        if text:
            # Strip potential ```json ... ``` fences
            cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            try:
                parsed = json.loads(cleaned)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                json_match = re.search(r"\{.*\}", text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except Exception:
                        pass

        return self._fallback_generate_json(prompt, system_prompt)

    def _fallback_generate_text(self, prompt: str, system_prompt: str = "") -> str:
        # Cascade to Gemini if configured
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if gemini_key:
            try:
                from .gemini import GeminiProvider
                return GeminiProvider().generate_text(prompt, system_prompt)
            except Exception:
                pass

        # Cascade to OpenAI if configured
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if openai_key:
            try:
                from .openai import OpenAIProvider
                return OpenAIProvider().generate_text(prompt, system_prompt)
            except Exception:
                pass

        from .fallback import LocalFallbackProvider
        return LocalFallbackProvider().generate_text(prompt, system_prompt)

    def _fallback_generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if gemini_key:
            try:
                from .gemini import GeminiProvider
                return GeminiProvider().generate_json(prompt, system_prompt)
            except Exception:
                pass

        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if openai_key:
            try:
                from .openai import OpenAIProvider
                return OpenAIProvider().generate_json(prompt, system_prompt)
            except Exception:
                pass

        from .fallback import LocalFallbackProvider
        return LocalFallbackProvider().generate_json(prompt, system_prompt)
