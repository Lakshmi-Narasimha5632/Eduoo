"""LinkedIn platform connector supporting OAuth 2.0 authorization, token exchange, and profile retrieval."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode
import httpx

from .base import BasePlatformConnector


class LinkedInConnector(BasePlatformConnector):
    platform_name = "linkedin"
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    USERINFO_URL = "https://api.linkedin.com/v2/userinfo"

    def __init__(self, username: Optional[str] = None, access_token: Optional[str] = None, refresh_token: Optional[str] = None):
        super().__init__(username=username, access_token=access_token, refresh_token=refresh_token)

    @classmethod
    def get_authorization_url(cls, state: str = "eduoo_state") -> str:
        client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/platforms/linkedin/callback/")
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "openid profile email",
        }
        return f"{cls.AUTH_URL}?{urlencode(params)}"

    @classmethod
    def exchange_code_for_token(cls, code: str) -> Dict[str, Any]:
        client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
        redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/platforms/linkedin/callback/")

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }
        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(cls.TOKEN_URL, data=payload)
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return {}

    def _fetch_userinfo(self) -> Optional[Dict[str, Any]]:
        if not self.access_token:
            return None
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            with httpx.Client(timeout=6.0) as client:
                res = client.get(self.USERINFO_URL, headers=headers)
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def get_profile(self) -> Dict[str, Any]:
        info = self._fetch_userinfo()
        if info:
            name = info.get("name")
            given_name = info.get("given_name")
            family_name = info.get("family_name")
            email = info.get("email")
            picture = info.get("picture")
            return {
                "username": self.username or email or name,
                "display_name": name or self.username,
                "first_name": given_name,
                "last_name": family_name,
                "profile_picture": picture,
                "email": email,
                "headline": None,  # Restricted scope in openid
                "profile_url": f"https://www.linkedin.com/in/{self.username}/" if self.username else None,
                "available": True,
            }
        return {
            "username": self.username,
            "display_name": self.username,
            "first_name": None,
            "last_name": None,
            "profile_picture": None,
            "email": None,
            "headline": None,
            "profile_url": f"https://www.linkedin.com/in/{self.username}/" if self.username else None,
            "available": bool(self.username or self.access_token),
        }

    def get_analytics(self) -> Dict[str, Any]:
        profile = self.get_profile()
        has_token = bool(self.access_token)

        return {
            "connected": bool(self.username or has_token),
            "profile": profile,
            "analytics": {
                "profile_connected": bool(self.username or has_token),
                "connections": None,  # Restricted by LinkedIn API
                "posts_last_30_days": None,
                "profile_views": None,
            },
            "insights": {
                "profile_status": "Linked via OAuth" if has_token else ("Username linked" if self.username else "Not connected"),
                "visibility": "Ensure your headline reflects your target role" if (self.username or has_token) else None,
            },
            "recommendations": [
                "Keep your LinkedIn headline aligned with your target role.",
                "Share your latest GitHub projects as posts to increase recruiter visibility.",
            ],
        }

    def sync(self) -> Dict[str, Any]:
        analytics_result = self.get_analytics()
        return {
            "platform": self.platform_name,
            "connected": analytics_result["connected"],
            "profile": analytics_result["profile"],
            "analytics": analytics_result["analytics"],
            "insights": analytics_result["insights"],
            "recommendations": analytics_result["recommendations"],
            "last_synced_at": datetime.now(timezone.utc).isoformat(),
        }
