"""Helper utilities for Eduoo."""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict


def get_current_utc() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def sanitize_username(username: str | None) -> str | None:
    """Clean username by stripping whitespace and invalid characters."""
    if not username:
        return None
    cleaned = re.sub(r"[^\w\-.]", "", username.strip())
    return cleaned if cleaned else None


def hash_token(token: str) -> str:
    """Generate a SHA-256 hash of a token for lookup/comparison."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def safe_int(value: Any, default: int = 0) -> int:
    """Safely cast a value to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely cast a value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
