from typing import Dict, Any, List

class Recommender:
    def generate_learning_roadmap(self, missing_skills_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        roadmap = []
        for index, item in enumerate(missing_skills_info, 1):
            skill_name = item.get("name", "")
            category = item.get("category", "General")
            resources = item.get("resources", {})
            
            course = resources.get("course", f"Mastering {skill_name} Fundamentals")
            doc = resources.get("doc", f"https://www.google.com/search?q={skill_name}+documentation")

            project_idea = f"Build a mini project integrating {skill_name} (e.g., a sample CRUD app or service pipeline)"

            roadmap.append({
                "step": index,
                "skill": skill_name,
                "category": category,
                "priority": "High" if index <= 3 else ("Medium" if index <= 6 else "Bonus"),
                "recommended_course": course,
                "documentation_link": doc,
                "hands_on_project": project_idea,
                "estimated_time": "1-2 Weeks" if index <= 3 else "3-5 Days"
            })
        return roadmap

    def enhance_bullet_point(self, weak_bullet: str) -> Dict[str, Any]:
        cleaned = weak_bullet.strip()
        if not cleaned:
            return {"original": "", "enhanced": "", "tips": []}

        # Analyze bullet structure
        words = cleaned.split()
        first_word = words[0].lower() if words else ""

        # Map common weak starters to strong action verbs
        action_verb_map = {
            "worked": "Architected & Implemented",
            "made": "Engineered",
            "developed": "Developed & Deployed",
            "helped": "Spearheaded",
            "responsible": "Led end-to-end execution of",
            "handled": "Orchestrated",
            "used": "Leveraged",
            "managed": "Directed & Scaled",
            "created": "Pioneered & Built"
        }

        strong_verb = action_verb_map.get(first_word, "Spearheaded")

        # Build enhanced bullet structure
        if first_word in action_verb_map:
            # Replace weak verb with strong action verb
            rest = " ".join(words[1:])
            enhanced = f"{strong_verb} {rest}, driving measurable performance improvements and optimizing system efficiency."
        else:
            enhanced = f"{strong_verb} {cleaned[0].lower() + cleaned[1:] if len(cleaned) > 1 else cleaned}, improving workflow throughput by 25%."

        tips = [
            "Use the STAR method (Situation, Task, Action, Result).",
            "Include specific numeric metrics (e.g., %, $, throughput, speedups).",
            "Highlight modern frameworks or tools used in the action phase."
        ]

        return {
            "original": weak_bullet,
            "enhanced": enhanced,
            "tips": tips
        }
