"""Google Gemini AI Provider with multi-model fallback and structured JSON output."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List
import httpx

from .base import BaseAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    provider_name = "gemini"
    DEFAULT_MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-pro", "gemini-2.0-flash"]

    _cooldown_until: float = 0.0

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        custom_model = (model or os.getenv("GEMINI_MODEL", "")).strip()
        if custom_model:
            self.models: List[str] = [custom_model] + [m for m in self.DEFAULT_MODELS if m != custom_model]
        else:
            self.models: List[str] = list(self.DEFAULT_MODELS)

    def _get_url(self, model: str) -> str:
        return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        import time
        if not self.api_key or time.time() < GeminiProvider._cooldown_until:
            from .fallback import LocalFallbackProvider
            return LocalFallbackProvider().generate_text(prompt, system_prompt)

        combined_text = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt.strip()
        payload = {
            "contents": [{"parts": [{"text": combined_text}]}],
            "generationConfig": {
                "temperature": 0.4,
            },
        }

        with httpx.Client(timeout=15.0) as client:
            for model_name in self.models:
                url = self._get_url(model_name)
                try:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()
                    elif res.status_code in (400, 401, 403, 429):
                        logger.warning("Gemini key/quota/auth error (%d). Halting model cascade to fallback.", res.status_code)
                        GeminiProvider._cooldown_until = time.time() + 120.0
                        break
                    elif res.status_code in (404, 503):
                        logger.warning(
                            "Gemini model %s returned status %d. Trying next candidate model...",
                            model_name,
                            res.status_code,
                        )
                        continue
                    else:
                        logger.error("Gemini API error (%d): %s", res.status_code, res.text[:200])
                except Exception as exc:
                    logger.warning("Gemini request failed for model %s: %s", model_name, exc)
                    continue

        from .fallback import LocalFallbackProvider
        return LocalFallbackProvider().generate_text(prompt, system_prompt)

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        import time
        if not self.api_key or time.time() < GeminiProvider._cooldown_until:
            from .fallback import LocalFallbackProvider
            return LocalFallbackProvider().generate_json(prompt, system_prompt)

        combined_text = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt.strip()
        payload = {
            "contents": [{"parts": [{"text": combined_text}]}],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }

        with httpx.Client(timeout=15.0) as client:
            for model_name in self.models:
                url = self._get_url(model_name)
                try:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                raw_json = parts[0].get("text", "").strip()
                                try:
                                    parsed = json.loads(raw_json)
                                    if isinstance(parsed, dict):
                                        return parsed
                                except Exception:
                                    json_match = re.search(r"\{.*\}", raw_json, re.DOTALL)
                                    if json_match:
                                        return json.loads(json_match.group(0))
                    elif res.status_code in (400, 401, 403, 429):
                        logger.warning("Gemini key/quota/auth error (%d). Halting model cascade to fallback.", res.status_code)
                        GeminiProvider._cooldown_until = time.time() + 120.0
                        break
                    elif res.status_code in (404, 503):
                        logger.warning(
                            "Gemini model %s returned %d for JSON request. Trying next model...",
                            model_name,
                            res.status_code,
                        )
                        continue
                except Exception as exc:
                    logger.warning("Gemini JSON request failed for model %s: %s", model_name, exc)
                    continue

        from .fallback import LocalFallbackProvider
        return LocalFallbackProvider().generate_json(prompt, system_prompt)
