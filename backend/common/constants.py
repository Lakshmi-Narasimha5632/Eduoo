"""Constants for Eduoo platform."""

PLATFORMS = {
    "LEETCODE": "leetcode",
    "GITHUB": "github",
    "DUOLINGO": "duolingo",
    "LINKEDIN": "linkedin",
    "HACKERRANK": "hackerrank",
    "CODECHEF": "codechef",
}

PLATFORM_CHOICES = [
    ("leetcode", "LeetCode"),
    ("github", "GitHub"),
    ("duolingo", "Duolingo"),
    ("linkedin", "LinkedIn"),
    ("hackerrank", "HackerRank"),
    ("codechef", "CodeChef"),
]

SUPPORTED_PLATFORMS = list(PLATFORMS.values())

TARGET_ROLES = [
    "Software Developer",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Python Developer",
    "Data Scientist",
    "Data Analyst",
    "AI Engineer",
    "ML Engineer",
    "DevOps Engineer",
]

SKILL_CATEGORIES = [
    "Programming",
    "Frontend",
    "Backend",
    "Database",
    "DevOps",
    "Cloud",
    "AI",
    "ML",
    "Data Science",
    "Data Analytics",
    "Communication",
    "Interview",
    "Languages",
]

INTERVIEW_TYPES = [
    ("technical", "Technical"),
    ("behavioral", "HR / Behavioral"),
    ("resume", "Resume-Based"),
    ("mixed", "Mixed"),
]

INTERVIEW_DIFFICULTIES = [
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
]

AI_AGENT_PERSONAS = [
    ("alex_architect", "Alex Chen - Staff Systems Architect (Google)"),
    ("sophia_algorithms", "Dr. Sophia Lin - Principal Algorithm Lead (DeepMind)"),
    ("marcus_director", "Marcus Vance - VP of Engineering & Bar Raiser (Stripe)"),
    ("elena_fullstack", "Elena Rostova - Principal Full Stack Architect (Vercel)"),
]

AI_AGENT_STRICTNESS = [
    ("supportive", "Supportive & Mentorship"),
    ("balanced", "Standard FAANG Industry Standard"),
    ("rigorous", "Rigorous Bar Raiser"),
]
