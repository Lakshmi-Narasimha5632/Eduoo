"""Resume domain service handling upload, parsing, ATS checks, and editable data updates."""

from __future__ import annotations

from typing import Any, Dict
from .models import ResumeSnapshot
from .parser import ResumeParser


class ResumeService:
    @staticmethod
    def get_latest_snapshot(user) -> ResumeSnapshot:
        snapshot, created = ResumeSnapshot.objects.get_or_create(
            user=user,
            defaults={
                "target_role": user.target_role or "Full Stack Developer",
                "summary": user.bio or "Software engineering professional.",
                "strengths": ["Problem solving", "Python", "Data structures", "Project communication"],
                "skill_gaps": ["System design depth", "Advanced SQL"],
                "ats_score": 75,
                "parsed_data": {
                    "full_name": user.full_name or "Candidate",
                    "name": user.full_name or "Candidate",
                    "email": user.email,
                    "phone": getattr(user, "phone", "") or "",
                    "github": None,
                    "linkedin": None,
                    "contact": {
                        "email": user.email,
                        "phone": getattr(user, "phone", "") or "",
                        "github": None,
                        "linkedin": None,
                    },
                    "skills": ["Python", "JavaScript", "SQL", "Git"],
                    "education": [f"{user.college or 'Engineering College'} - {user.branch or 'Computer Science'} ({user.graduation_year or 2026})"],
                    "projects": ["Personal Portfolio Web App"],
                    "experience": [],
                },
            },
        )

        data = snapshot.parsed_data or {}
        contact = data.get("contact") or {}
        changed = False

        if not data.get("full_name"):
            data["full_name"] = data.get("name") or user.full_name or getattr(user, "username", "Candidate")
            changed = True
        if not data.get("email"):
            data["email"] = contact.get("email") or user.email
            changed = True
        if not data.get("phone"):
            data["phone"] = contact.get("phone") or getattr(user, "phone", "") or ""
            changed = True
        if not data.get("name"):
            data["name"] = data["full_name"]
            changed = True

        # If analysis is missing, run it on existing data
        if not snapshot.ats_analysis or not snapshot.ats_analysis.get("recommendations"):
            target_role = snapshot.target_role or user.target_role or "Full Stack Developer"
            snapshot.ats_analysis = ResumeParser.analyze_ats(data, target_role=target_role)
            snapshot.ats_score = snapshot.ats_analysis["ats_score"]
            snapshot.strengths = snapshot.ats_analysis["matched_skills"]
            snapshot.skill_gaps = snapshot.ats_analysis["missing_skills"]
            changed = True

        if changed:
            snapshot.parsed_data = data
            snapshot.save()

        return snapshot

    @staticmethod
    def process_file_upload(user, file_obj) -> ResumeSnapshot:
        file_bytes = file_obj.read()
        raw_text = ResumeParser.extract_text_from_pdf(file_bytes)
        parsed = ResumeParser.extract_entities(raw_text, user=user)

        target_role = user.target_role or "Full Stack Developer"
        ats_analysis = ResumeParser.analyze_ats(parsed, target_role=target_role)

        snapshot = ResumeService.get_latest_snapshot(user)
        snapshot.file = file_obj
        snapshot.raw_text = raw_text
        snapshot.parsed_data = parsed
        snapshot.ats_score = ats_analysis["ats_score"]
        snapshot.ats_analysis = ats_analysis
        snapshot.strengths = ats_analysis["matched_skills"]
        snapshot.skill_gaps = ats_analysis["missing_skills"]
        snapshot.target_role = target_role
        snapshot.save()

        # Update user profile full_name if extracted and not yet set
        if parsed.get("full_name") and parsed["full_name"] != "Candidate" and not user.full_name:
            user.full_name = parsed["full_name"]
            user.save(update_fields=["full_name"])

        return snapshot

    @staticmethod
    def update_parsed_data(user, data: Dict[str, Any]) -> ResumeSnapshot:
        snapshot = ResumeService.get_latest_snapshot(user)
        current = snapshot.parsed_data or {}
        current.update(data)

        # Sync contact subdict with root full_name, email, phone
        if "full_name" in current:
            current["name"] = current["full_name"]
        if "email" in current:
            if "contact" not in current or not isinstance(current["contact"], dict):
                current["contact"] = {}
            current["contact"]["email"] = current["email"]
        if "phone" in current:
            if "contact" not in current or not isinstance(current["contact"], dict):
                current["contact"] = {}
            current["contact"]["phone"] = current["phone"]
        if "github" in current:
            if "contact" not in current or not isinstance(current["contact"], dict):
                current["contact"] = {}
            current["contact"]["github"] = current["github"]
        if "linkedin" in current:
            if "contact" not in current or not isinstance(current["contact"], dict):
                current["contact"] = {}
            current["contact"]["linkedin"] = current["linkedin"]

        target_role = snapshot.target_role or user.target_role or "Full Stack Developer"
        ats_analysis = ResumeParser.analyze_ats(current, target_role=target_role)

        snapshot.parsed_data = current
        snapshot.ats_score = ats_analysis["ats_score"]
        snapshot.ats_analysis = ats_analysis
        snapshot.strengths = ats_analysis["matched_skills"]
        snapshot.skill_gaps = ats_analysis["missing_skills"]
        snapshot.save()

        # Update user profile full_name if provided
        if current.get("full_name") and current["full_name"] != getattr(user, "full_name", ""):
            user.full_name = current["full_name"]
            user.save(update_fields=["full_name"])

        return snapshot
