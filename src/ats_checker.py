import re
from typing import Dict, Any, List

class ATSChecker:
    ACTION_VERBS = [
        "architected", "built", "created", "designed", "developed", "engineered",
        "implemented", "integrated", "launched", "lead", "led", "managed",
        "optimized", "orchestrated", "reduced", "scaled", "spearheaded", "transformed",
        "decreased", "increased", "maximized", "minimized", "streamlined", "automated"
    ]

    def analyze(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        raw_text = parsed_resume.get("raw_text", "")
        contact = parsed_resume.get("contact", {})
        sections = parsed_resume.get("sections", {})
        word_count = parsed_resume.get("word_count", 0)

        checks = []
        score_points = 0
        total_points = 100

        # Check 1: Contact Information (20 points max)
        contact_score = 0
        if contact.get("email"):
            contact_score += 8
        if contact.get("phone"):
            contact_score += 6
        if contact.get("linkedin") or contact.get("github"):
            contact_score += 6

        checks.append({
            "name": "Contact Details Completeness",
            "passed": contact_score >= 14,
            "score": contact_score,
            "max_score": 20,
            "details": f"Email: {'✓' if contact.get('email') else '✗'}, Phone: {'✓' if contact.get('phone') else '✗'}, Social: {'✓' if (contact.get('linkedin') or contact.get('github')) else '✗'}"
        })
        score_points += contact_score

        # Check 2: Core Sections Presence (25 points max)
        section_score = 0
        present_sections = []
        for sec in ["summary", "skills", "experience", "education"]:
            if sections.get(sec) and len(sections[sec].strip()) > 10:
                section_score += 6.25
                present_sections.append(sec.capitalize())

        checks.append({
            "name": "Key Section Structure",
            "passed": section_score >= 18.75,
            "score": round(section_score, 1),
            "max_score": 25,
            "details": f"Found sections: {', '.join(present_sections) if present_sections else 'None'}"
        })
        score_points += section_score

        # Check 3: Strong Action Verbs Usage (20 points max)
        words_lower = raw_text.lower().split()
        found_verbs = [v for v in self.ACTION_VERBS if v in words_lower]
        verb_score = min(20, len(found_verbs) * 3)

        checks.append({
            "name": "Impact Action Verbs",
            "passed": len(found_verbs) >= 4,
            "score": verb_score,
            "max_score": 20,
            "details": f"Detected {len(found_verbs)} strong action verbs (e.g. {', '.join(found_verbs[:4]) if found_verbs else 'None'})"
        })
        score_points += verb_score

        # Check 4: Quantifiable Achievements & Metrics (20 points max)
        metric_matches = re.findall(r'\b\d+(?:[\.,]\d+)?\s*(?:%|\$|k|m|million|billion|users|requests|x|x\b|years|yrs)?\b', raw_text, re.IGNORECASE)
        # Filter out numbers that look like phone or dates (like 2022, 2023)
        meaningful_metrics = [m for m in metric_matches if not re.match(r'^(19|20)\d\d$', m.strip())]
        metric_score = min(20, len(meaningful_metrics) * 4)

        checks.append({
            "name": "Quantifiable Achievements (Metrics & Data)",
            "passed": len(meaningful_metrics) >= 3,
            "score": metric_score,
            "max_score": 20,
            "details": f"Found {len(meaningful_metrics)} quantifiable metric references."
        })
        score_points += metric_score

        # Check 5: Length & Density (15 points max)
        length_score = 15
        length_status = "Optimal length"
        if word_count < 250:
            length_score = 7
            length_status = "Too short (< 250 words)"
        elif word_count > 1500:
            length_score = 10
            length_status = "Very long (> 1500 words)"

        checks.append({
            "name": "Resume Length & Formatting",
            "passed": length_score == 15,
            "score": length_score,
            "max_score": 15,
            "details": f"{word_count} words ({length_status})"
        })
        score_points += length_score

        ats_score = round(score_points, 1)

        # Generate Actionable Recommendations
        recommendations = []
        if not contact.get("email") or not contact.get("phone"):
            recommendations.append("Ensure your full contact info (Email, Phone Number) is prominently placed at the top.")
        if not contact.get("linkedin"):
            recommendations.append("Add a clean custom LinkedIn URL to enhance recruiter verification.")
        if len(found_verbs) < 4:
            recommendations.append("Incorporate more active power verbs (e.g., 'Spearheaded', 'Architected', 'Optimized') at the start of bullet points.")
        if len(meaningful_metrics) < 3:
            recommendations.append("Add measurable outcomes to your work bullets (e.g., 'Improved performance by 35%', 'Reduced latency by 120ms').")
        if not sections.get("summary"):
            recommendations.append("Include a 2-3 sentence Professional Summary tailored to your target job title.")

        return {
            "ats_score": ats_score,
            "passed_checks_count": sum(1 for c in checks if c["passed"]),
            "total_checks": len(checks),
            "checks": checks,
            "recommendations": recommendations
        }
