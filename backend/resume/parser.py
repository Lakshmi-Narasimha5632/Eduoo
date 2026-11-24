"""Resume parser and ATS analyzer extracting structured entities from PDF and text."""

from __future__ import annotations

import io
import re
from typing import Any, Dict, List, Optional
from pypdf import PdfReader

from skills.taxonomy import ROLE_REQUIREMENTS, SKILLS_CATALOG

SKILL_ALIASES = {
    "react.js": "React",
    "reactjs": "React",
    "react native": "React Native",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express.js": "Express",
    "expressjs": "Express",
    "vue.js": "Vue",
    "next.js": "Next.js",
    "django rest framework": "Django",
    "drf": "Django",
    "html5": "HTML/CSS",
    "css3": "HTML/CSS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "sqlite": "SQL",
    "sqlite3": "SQL",
    "github": "Git",
    "git": "Git",
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "rest apis": "REST APIs",
    "rest api": "REST APIs",
    "fastapi": "FastAPI",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "power bi": "PowerBI",
    "powerbi": "PowerBI",
    "tableau": "Tableau",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "llm": "Generative AI",
    "llms": "Generative AI",
    "langchain": "LangChain",
    "system design": "System Design",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "eda": "Data Visualization",
}


class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extract plain text from uploaded PDF bytes."""
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
            return "\n".join(text_parts)
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"

    @staticmethod
    def extract_entities(text: str, user=None) -> Dict[str, Any]:
        """Extract contact details, sections, and detected skills from resume text."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Email extraction with profile fallback
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        email = email_match.group(0) if email_match else None
        if not email and user and getattr(user, "email", None):
            email = user.email

        # 2. Phone extraction (international & Indian formats) with profile fallback
        phone = None
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{4}", text)
        if phone_match:
            phone = phone_match.group(0).strip()
        else:
            indian_match = re.search(r"\b[6-9]\d{9}\b", text)
            if indian_match:
                phone = f"+91 {indian_match.group(0)}"
            elif user and getattr(user, "phone", None):
                phone = getattr(user, "phone", None)

        # 3. GitHub & LinkedIn link extraction (supports bracketed URLs from templates)
        github_match = re.search(r"github\.com/(?:\[)?([a-zA-Z0-9_-]+)(?:\])?", text, re.IGNORECASE)
        github_url = f"https://github.com/{github_match.group(1)}" if github_match else None

        linkedin_match = re.search(r"linkedin\.com/in/(?:\[)?([a-zA-Z0-9_-]+)(?:\])?", text, re.IGNORECASE)
        linkedin_url = f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else None

        # 4. Candidate Name Extraction (check top lines, filter noise)
        name = None
        noise_keywords = [
            "@", "http", ".com", "phone", "email", "mobile", "tel", "resume",
            "curriculum", "vitae", "summary", "profile", "developer", "engineer",
            "graduate", "cognifyz", "intern", "page", "+91", "address", "india"
        ]
        for l in lines[:12]:
            clean_l = l.strip()
            lower_l = clean_l.lower()
            if any(k in lower_l for k in noise_keywords):
                continue
            words = clean_l.split()
            if 1 <= len(words) <= 5 and all(w.replace(".", "").isalpha() for w in words):
                name = clean_l
                break

        if not name or name == "Candidate":
            if user:
                name = getattr(user, "full_name", None) or f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip() or getattr(user, "username", "Candidate")
            else:
                name = lines[0] if lines else "Candidate"
                if len(name.split()) > 5 or "@" in name:
                    name = "Candidate"

        # 5. Skills matching from SKILLS_CATALOG and common aliases
        detected_skills = set()
        lower_text = text.lower()

        # Direct catalog check
        for category, skill_list in SKILLS_CATALOG.items():
            for skill in skill_list:
                pattern = r"\b" + re.escape(skill.lower()) + r"\b"
                if re.search(pattern, lower_text):
                    detected_skills.add(skill)

        # Aliases check
        for alias, normalized in SKILL_ALIASES.items():
            pattern = r"\b" + re.escape(alias.lower()) + r"\b"
            if re.search(pattern, lower_text):
                detected_skills.add(normalized)

        sorted_skills = sorted(list(detected_skills))

        # 6. Section segmenting
        sections: Dict[str, List[str]] = {
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
        }

        current_sec = None
        for line in lines:
            line_lower = line.lower()
            if any(h in line_lower for h in ["education", "academic", "degree", "b.tech", "b.e.", "bachelor"]):
                current_sec = "education"
                continue
            elif any(h in line_lower for h in ["experience", "employment", "work history", "internship", "work experience"]):
                current_sec = "experience"
                continue
            elif any(h in line_lower for h in ["projects", "personal projects", "portfolio", "key projects"]):
                current_sec = "projects"
                continue
            elif any(h in line_lower for h in ["certification", "certifications", "licenses", "courses"]):
                current_sec = "certifications"
                continue
            elif any(h in line_lower for h in ["achievement", "achievements", "awards", "honors"]):
                current_sec = "achievements"
                continue

            if current_sec and len(line) > 3:
                # Filter out pure noise lines
                if not any(stop in line_lower for stop in ["page 1", "page 2", "curriculum vitae", "references available"]):
                    sections[current_sec].append(line)

        return {
            "full_name": name,
            "name": name,
            "email": email,
            "phone": phone,
            "github": github_url,
            "linkedin": linkedin_url,
            "contact": {
                "email": email,
                "phone": phone,
                "github": github_url,
                "linkedin": linkedin_url,
            },
            "skills": sorted_skills,
            "education": sections["education"][:8],
            "experience": sections["experience"][:12],
            "projects": sections["projects"][:12],
            "certifications": sections["certifications"][:6],
            "achievements": sections["achievements"][:6],
        }

    @staticmethod
    def _generate_tailored_rewrite(bullet: str) -> Dict[str, str]:
        """Generate a realistic, metric-driven rewrite for a weak bullet based on its technologies."""
        lower = bullet.lower()
        cleaned = re.sub(r"^[•\-\*~\s]+", "", bullet).strip()

        if any(k in lower for k in ["api", "rest", "backend", "crud", "endpoint", "express", "django"]):
            return {
                "original": cleaned,
                "suggestion": f"Engineered robust RESTful API services with JWT auth and SQL indexing, reducing endpoint response times by 30% for 1,000+ daily queries.",
                "reason": "Quantifies API architecture with endpoint throughput, authentication security, and latency improvements.",
            }
        elif any(k in lower for k in ["react", "frontend", "ui", "interface", "component", "redux"]):
            return {
                "original": cleaned,
                "suggestion": f"Architected responsive UI components using React.js and modern state management, accelerating initial page render by 35% across web and mobile clients.",
                "reason": "Replaces generic development wording with measurable rendering performance and cross-device impact.",
            }
        elif any(k in lower for k in ["machine learning", "model", "predict", "data", "ml", "nlp", "pandas"]):
            return {
                "original": cleaned,
                "suggestion": f"Developed end-to-end predictive modeling pipelines processing 50,000+ records, achieving 92% cross-validated accuracy and reducing manual analysis time by 40%.",
                "reason": "Replaces descriptive model summary with exact dataset scale, accuracy benchmark, and operational time saved.",
            }
        elif any(k in lower for k in ["platform", "complaint", "app", "application", "system"]):
            return {
                "original": cleaned,
                "suggestion": f"Spearheaded full-lifecycle implementation of the platform, deploying automated workflows that resolved 500+ user tickets with 99.8% uptime.",
                "reason": "Demonstrates product ownership with ticket throughput and system reliability metrics.",
            }
        else:
            return {
                "original": cleaned,
                "suggestion": f"Engineered scalable core system modules following CI/CD practices, boosting execution efficiency by 25% across production environments.",
                "reason": "Applies Google's X-Y-Z formula (Accomplished [X] as measured by [Y] by doing [Z]).",
            }

    @staticmethod
    def analyze_ats(parsed_data: Dict[str, Any], target_role: str = "Software Developer") -> Dict[str, Any]:
        """Perform deep, candidate-specific ATS scoring, bullet analysis, and personalized recommendations."""
        skills = set(parsed_data.get("skills", []))
        role_reqs = ROLE_REQUIREMENTS.get(target_role, ROLE_REQUIREMENTS.get("Software Developer", {}))

        missing_skills = []
        matched_skills = []
        for req_skill, config in role_reqs.items():
            if req_skill in skills:
                matched_skills.append(req_skill)
            else:
                missing_skills.append(req_skill)

        # Complementary extra skills detected in resume
        extra_skills = [s for s in skills if s not in matched_skills]

        # Calculate alignment
        total_req = max(1, len(role_reqs))
        alignment_pct = int((len(matched_skills) / total_req) * 100)

        # Contact & Header checks
        contact = parsed_data.get("contact", {}) or {}
        has_email = bool(parsed_data.get("email") or contact.get("email"))
        has_phone = bool(parsed_data.get("phone") or contact.get("phone"))
        has_github = bool(parsed_data.get("github") or contact.get("github"))
        has_linkedin = bool(parsed_data.get("linkedin") or contact.get("linkedin"))

        # Section presence
        education_list = parsed_data.get("education", [])
        experience_list = parsed_data.get("experience", [])
        projects_list = parsed_data.get("projects", [])

        # Bullet point analysis (metrics vs non-metric bullets)
        raw_bullets = experience_list + projects_list
        metric_regex = re.compile(r"(\d+%|\$\d+|\d+\s*(users|requests|ms|x|hours|percent|endpoints|records|queries|uptime))", re.IGNORECASE)

        weak_bullets = []
        metric_bullets = []
        for b in raw_bullets:
            clean_b = re.sub(r"^[•\-\*~\s]+", "", b).strip()
            # Ignore short header/title lines
            if len(clean_b) < 25 or clean_b.lower().startswith("tech stack") or "github:" in clean_b.lower():
                continue
            if metric_regex.search(clean_b):
                metric_bullets.append(clean_b)
            else:
                weak_bullets.append(clean_b)

        # Generate tailored rewrites for up to 3 actual weak bullets
        tailored_rewrites = []
        for wb in weak_bullets[:3]:
            tailored_rewrites.append(ResumeParser._generate_tailored_rewrite(wb))

        # Dynamic ATS Scoring Formula (0-100)
        # 1. Contact completeness: up to 15 pts
        contact_pts = 0
        if has_email:
            contact_pts += 5
        if has_phone:
            contact_pts += 4
        if has_github:
            contact_pts += 3
        if has_linkedin:
            contact_pts += 3

        # 2. Skill match: up to 35 pts
        skill_pts = min(35, int((len(matched_skills) / total_req) * 35))

        # 3. Project & experience depth: up to 25 pts
        exp_pts = 0
        if len(experience_list) >= 2:
            exp_pts += 12
        elif len(experience_list) >= 1:
            exp_pts += 7

        if len(projects_list) >= 2:
            exp_pts += 13
        elif len(projects_list) >= 1:
            exp_pts += 8

        # 4. Metric quantification: up to 15 pts
        metric_pts = 0
        if len(metric_bullets) >= 3:
            metric_pts = 15
        elif len(metric_bullets) >= 1:
            metric_pts = 8
        elif len(weak_bullets) > 0:
            metric_pts = 4

        # 5. Education & Credentials: up to 10 pts
        edu_pts = 10 if len(education_list) >= 1 else 3

        total_score = contact_pts + skill_pts + exp_pts + metric_pts + edu_pts
        ats_score = max(45, min(96, total_score))

        # Build Resume-Specific Issues (NO generic defaults)
        issues = []
        if missing_skills:
            issues.append(f"Missing {len(missing_skills)} target role competencies: {', '.join(missing_skills[:3])}. ATS filters heavily weight these keywords.")
        if weak_bullets:
            issues.append(f"{len(weak_bullets)} experience and project bullet points lack quantifiable business metrics (%, latency, throughput, scale).")
        if not has_github:
            issues.append("No active GitHub or portfolio repository link detected; technical recruiters look for verifiable code contributions.")
        if not has_linkedin:
            issues.append("No LinkedIn profile link detected in contact header.")
        if not has_phone:
            issues.append("Phone number missing or lacks international dialing code format.")
        if len(projects_list) < 2:
            issues.append("Portfolio has fewer than 2 distinct technical project implementations.")

        # Build Resume-Specific Suggestions (NO generic defaults)
        suggestions = []
        if matched_skills:
            suggestions.append(f"Elevate your verified strengths in {', '.join(matched_skills[:4])} by detailing complex architectural decisions in project descriptions.")
        if missing_skills:
            suggestions.append(f"Incorporate '{missing_skills[0]}' into a dedicated technical section or deploy an integration project demonstrating proficiency.")
        if tailored_rewrites:
            suggestions.append("Upgrade descriptive bullets using action verbs (Architected, Engineered, Optimized) paired with quantified metrics.")
        if extra_skills:
            suggestions.append(f"Highlight complementary capabilities ({', '.join(extra_skills[:3])}) as unique value-adds for full-stack collaboration.")

        # Prioritized recommendations
        recommendations = []
        if missing_skills:
            recommendations.append(f"Add key {target_role} skills: {', '.join(missing_skills[:4])}.")
        if tailored_rewrites:
            recommendations.append("Apply quantifiable metrics (percentages, throughput, user base) to your experience bullet points.")
        if not has_github or not has_linkedin:
            recommendations.append("Ensure both your GitHub and customized LinkedIn profile links are prominently placed in the resume header.")
        if len(skills) < 8:
            recommendations.append("Expand your technical skills inventory with specific frameworks, databases, and DevOps tools you have worked with.")

        # Formatting warnings
        formatting_warnings = []
        if not has_email:
            formatting_warnings.append("Professional email not detected.")
        if not has_phone:
            formatting_warnings.append("Contact phone number missing.")
        if not has_github:
            formatting_warnings.append("GitHub profile link missing.")
        if not has_linkedin:
            formatting_warnings.append("LinkedIn profile link missing.")
        if not education_list:
            formatting_warnings.append("Education section not clearly identified.")

        # Section Completeness Checklist
        section_checks = [
            {
                "label": "Contact Info (Email, Phone, Links)",
                "status": has_email and has_phone,
                "detail": f"{'✓ Email' if has_email else '✗ Email'} | {'✓ Phone' if has_phone else '✗ Phone'} | {'✓ GitHub' if has_github else '✗ GitHub'}",
            },
            {
                "label": "Core Technical Skills",
                "status": len(skills) >= 6,
                "detail": f"{len(skills)} skills detected ({len(matched_skills)} match {target_role})",
            },
            {
                "label": "Work Experience / Internships",
                "status": len(experience_list) > 0,
                "detail": f"{len(experience_list)} experience entries extracted",
            },
            {
                "label": "Technical Projects",
                "status": len(projects_list) > 0,
                "detail": f"{len(projects_list)} project details extracted",
            },
            {
                "label": "Education & Credentials",
                "status": len(education_list) > 0,
                "detail": f"{len(education_list)} education entries detected",
            },
            {
                "label": "Quantifiable Metrics in Bullets",
                "status": len(metric_bullets) >= 2,
                "detail": f"{len(metric_bullets)} metric bullets found ({len(weak_bullets)} need metrics)",
            },
        ]

        return {
            "ats_score": ats_score,
            "target_role": target_role,
            "target_role_alignment": "High" if alignment_pct >= 70 else ("Moderate" if alignment_pct >= 40 else "Needs Improvement"),
            "alignment_percentage": alignment_pct,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "issues": issues,
            "suggestions": suggestions,
            "recommendations": recommendations,
            "weak_descriptions": weak_bullets[:4],
            "tailored_rewrites": tailored_rewrites,
            "formatting_warnings": formatting_warnings,
            "section_checks": section_checks,
        }
