"""Skill domain services: gap analysis, taxonomy seeding, and explainable career readiness calculation."""

from __future__ import annotations

from typing import Any, Dict, List
from django.db.models import Sum

from platforms.models import ConnectedPlatform
from tasks.models import DailyTask, DailyTaskPlan
from .models import RoleRequirement, Skill, UserSkill
from .taxonomy import ROLE_REQUIREMENTS, SKILLS_CATALOG


class SkillService:
    @staticmethod
    def seed_taxonomy():
        """Ensure base skills catalog and role requirements exist in database."""
        for category, skills in SKILLS_CATALOG.items():
            for skill_name in skills:
                Skill.objects.get_or_create(name=skill_name, defaults={"category": category})

        for role, reqs in ROLE_REQUIREMENTS.items():
            for skill_name, config in reqs.items():
                skill = Skill.objects.filter(name=skill_name).first()
                if skill:
                    RoleRequirement.objects.get_or_create(
                        role_name=role,
                        skill=skill,
                        defaults={
                            "required_level": config["level"],
                            "is_mandatory": config["mandatory"],
                        },
                    )

    @staticmethod
    def get_or_infer_user_skills(user) -> Dict[str, int]:
        """Combine explicit UserSkill records with inferred evidence from connected platforms."""
        SkillService.seed_taxonomy()
        user_skills: Dict[str, int] = {}

        # 1. Explicit user skills
        for us in UserSkill.objects.filter(user=user):
            user_skills[us.skill.name] = us.current_level

        # 2. Inferred from LeetCode
        lc_record = ConnectedPlatform.objects.filter(user=user, platform="leetcode", connected=True).first()
        if lc_record:
            user_skills.setdefault("Data Structures & Algorithms", 2)
            user_skills.setdefault("Coding Round Prep", 2)

        # 3. Inferred from GitHub
        gh_record = ConnectedPlatform.objects.filter(user=user, platform="github", connected=True).first()
        if gh_record:
            user_skills.setdefault("Git", 2)

        # 4. Inferred from User target role defaults
        role = user.target_role or "Software Developer"
        if role in ["Full Stack Developer", "Frontend Developer"]:
            user_skills.setdefault("HTML/CSS", 2)
            user_skills.setdefault("JavaScript", 2)
        elif role in ["Backend Developer", "Python Developer"]:
            user_skills.setdefault("Python", 2)
            user_skills.setdefault("REST APIs", 2)

        return user_skills

    @staticmethod
    def analyze_skill_gaps(user) -> Dict[str, Any]:
        """Compare target role requirements vs user's current skills."""
        SkillService.seed_taxonomy()
        role = user.target_role or "Software Developer"
        reqs = ROLE_REQUIREMENTS.get(role, ROLE_REQUIREMENTS["Software Developer"])
        current_skills = SkillService.get_or_infer_user_skills(user)

        strong_skills = []
        weak_skills = []
        missing_skills = []

        for skill_name, config in reqs.items():
            required_level = config["level"]
            is_mandatory = config["mandatory"]
            user_level = current_skills.get(skill_name, 0)

            if user_level >= required_level:
                strong_skills.append({
                    "skill": skill_name,
                    "current_level": user_level,
                    "required_level": required_level,
                    "status": "strong",
                    "mandatory": is_mandatory,
                })
            elif user_level > 0:
                weak_skills.append({
                    "skill": skill_name,
                    "current_level": user_level,
                    "required_level": required_level,
                    "status": "needs_improvement",
                    "mandatory": is_mandatory,
                })
            else:
                missing_skills.append({
                    "skill": skill_name,
                    "current_level": 0,
                    "required_level": required_level,
                    "status": "missing",
                    "mandatory": is_mandatory,
                })

        # Generate recommended learning path
        learning_path = []
        for item in missing_skills:
            if item["mandatory"]:
                learning_path.append(f"Learn core {item['skill']} concepts and build a hands-on project.")
        for item in weak_skills:
            learning_path.append(f"Advance {item['skill']} to Level {item['required_level']} through practice.")

        if not learning_path:
            learning_path.append(f"Reinforce system design and mock interview depth for {role}.")

        total_tracked = len(reqs)
        coverage_pct = int(((len(strong_skills) * 1.0 + len(weak_skills) * 0.5) / max(1, total_tracked)) * 100)

        return {
            "target_role": role,
            "coverage_percentage": min(100, coverage_pct),
            "strong_skills": strong_skills,
            "weak_skills": weak_skills,
            "missing_skills": missing_skills,
            "recommended_learning_path": learning_path,
        }

    @staticmethod
    def calculate_career_readiness(user) -> Dict[str, Any]:
        """Explainable 6-factor Career Readiness Engine per Section 51."""
        gap_data = SkillService.analyze_skill_gaps(user)

        # 1. Technical Skills Score (based on mandatory skill coverage)
        strong_count = len(gap_data["strong_skills"])
        weak_count = len(gap_data["weak_skills"])
        total_req = max(1, strong_count + weak_count + len(gap_data["missing_skills"]))
        technical_score = int(((strong_count * 100 + weak_count * 50) / (total_req * 100)) * 100)
        technical_score = min(100, max(40, technical_score))

        # Get live platform analytics
        try:
            from platforms.services import PlatformService
            unified_summary = PlatformService.get_unified_analytics(user)
        except Exception:
            unified_summary = {}

        total_solved = int(unified_summary.get("total_problems_solved") or 0)
        total_repos = int(unified_summary.get("total_repositories") or 0)

        # 2. Projects Score (GitHub repos, stars, activity)
        gh_record = ConnectedPlatform.objects.filter(user=user, platform="github", connected=True).first()
        if gh_record and gh_record.username:
            if total_repos >= 20:
                projects_score = 90
            elif total_repos >= 8:
                projects_score = 80
            elif total_repos >= 3:
                projects_score = 70
            else:
                projects_score = 60
        else:
            projects_score = 45

        # 3. Problem Solving Score (LeetCode, HackerRank, CodeChef)
        lc_record = ConnectedPlatform.objects.filter(user=user, platform="leetcode", connected=True).first()
        cf_record = ConnectedPlatform.objects.filter(user=user, platform="codechef", connected=True).first()
        hr_record = ConnectedPlatform.objects.filter(user=user, platform="hackerrank", connected=True).first()
        ps_count = sum([bool(lc_record and lc_record.connected), bool(cf_record and cf_record.connected), bool(hr_record and hr_record.connected)])
        
        if total_solved >= 300:
            problem_solving_score = 92
        elif total_solved >= 150:
            problem_solving_score = 85
        elif total_solved >= 50:
            problem_solving_score = 78
        elif total_solved > 0:
            problem_solving_score = 68
        else:
            problem_solving_score = 50 + (ps_count * 10)

        # 4. Communication Score (Resume, Duolingo, general answers)
        duo_record = ConnectedPlatform.objects.filter(user=user, platform="duolingo", connected=True).first()
        communication_score = 65 + (10 if duo_record and duo_record.connected else 0)

        # 5. Interview Readiness Score
        interview_readiness_score = 65

        # 6. Consistency Score (based on daily tasks completion)
        completed_tasks = DailyTask.objects.filter(plan__user=user, status="completed").count()
        consistency_score = min(95, max(45, 45 + (completed_tasks * 5)))

        # Weighted Overall Career Readiness
        overall_readiness = int(
            technical_score * 0.25 +
            projects_score * 0.20 +
            problem_solving_score * 0.20 +
            communication_score * 0.10 +
            interview_readiness_score * 0.15 +
            consistency_score * 0.10
        )

        factors = [
            {"factor": "Technical Skills", "score": technical_score, "weight": "25%", "detail": f"{strong_count} strong skills for {gap_data['target_role']}."},
            {"factor": "Projects & Portfolio", "score": projects_score, "weight": "20%", "detail": f"GitHub linked with {total_repos} repositories." if gh_record and total_repos else ("GitHub account linked." if gh_record else "No active GitHub linked yet.")},
            {"factor": "Problem Solving", "score": problem_solving_score, "weight": "20%", "detail": f"{total_solved} problems solved across platforms." if total_solved > 0 else (f"{ps_count} coding platforms connected." if ps_count > 0 else "Connect LeetCode or CodeChef to boost score.")},
            {"factor": "Communication", "score": communication_score, "weight": "10%", "detail": "Foreign language practice and structured self-presentation."},
            {"factor": "Interview Readiness", "score": interview_readiness_score, "weight": "15%", "detail": "Initial technical and behavioral interview benchmark."},
            {"factor": "Study Consistency", "score": consistency_score, "weight": "10%", "detail": f"{completed_tasks} completed tasks on Eduoo."},
        ]

        return {
            "target_role": gap_data["target_role"],
            "overall_readiness": overall_readiness,
            "scores": {
                "technical_skills": technical_score,
                "projects": projects_score,
                "problem_solving": problem_solving_score,
                "communication": communication_score,
                "interview_readiness": interview_readiness_score,
                "consistency": consistency_score,
            },
            "factors": factors,
            "gaps": gap_data,
        }
