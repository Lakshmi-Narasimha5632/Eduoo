"""Platform insights module exports."""

from .base import BasePlatformInsights
from .codechef import CodeChefInsights
from .duolingo import DuolingoInsights
from .github import GitHubInsights
from .hackerrank import HackerRankInsights
from .leetcode import LeetCodeInsights
from .linkedin import LinkedInInsights

INSIGHTS_MAP = {
    "leetcode": LeetCodeInsights,
    "github": GitHubInsights,
    "duolingo": DuolingoInsights,
    "linkedin": LinkedInInsights,
    "hackerrank": HackerRankInsights,
    "codechef": CodeChefInsights,
}


def get_platform_insights_generator(platform_name: str) -> BasePlatformInsights | None:
    cls = INSIGHTS_MAP.get(platform_name)
    return cls() if cls else None
