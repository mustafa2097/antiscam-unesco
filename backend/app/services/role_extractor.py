from __future__ import annotations

import re

ROLE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "lawyer": ("lawyer", "attorney", "advocate", "legal counsel", "محامي", "محاماة", "قانوني", "قانونية"),
    "doctor": ("doctor", "physician", "medical officer", "طبيب", "طبيبة", "دكتور"),
    "engineer": ("engineer", "engineering", "مهندس", "مهندسة", "هندسة"),
    "teacher": ("teacher", "tutor", "educator", "instructor", "معلم", "مدرس", "أستاذ", "استاذ"),
    "developer": ("developer", "programmer", "software engineer", "coder", "مطور", "مبرمج", "برمجة"),
    "designer": ("designer", "graphic designer", "ui designer", "ux designer", "مصمم", "مصممة", "تصميم"),
    "accountant": ("accountant", "accounting", "bookkeeper", "محاسب", "محاسبة"),
    "marketing": ("marketing", "seo", "digital marketing", "growth", "تسويق", "تسويقي"),
    "translator": ("translator", "translation", "interpreter", "مترجم", "مترجمة", "ترجمة"),
    "nurse": ("nurse", "nursing", "caregiver", "ممرض", "ممرضة", "تمريض"),
    "sales": ("sales", "salesperson", "sales rep", "مبيعات", "بائع"),
    "photographer": ("photographer", "photography", "videographer", "مصور", "تصوير"),
    "writer": ("writer", "copywriter", "editor", "journalist", "كاتب", "محرر", "صحفي"),
    "driver": ("driver", "delivery", "courier", "سائق", "توصيل"),
    "hr": ("human resources", "hr", "recruiter", "موارد بشرية", "توظيف"),
    "data": ("data analyst", "data scientist", "analytics", "تحليل بيانات", "محلل بيانات"),
    "customer_support": ("customer support", "customer service", "call center", "خدمة العملاء", "دعم العملاء"),
}

_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


def extract_role(text: str) -> str | None:
    if not text:
        return None

    lowered = text.lower()
    scores: dict[str, int] = {}

    for role, keywords in ROLE_KEYWORDS.items():
        for kw in keywords:
            if kw in lowered:
                scores[role] = scores.get(role, 0) + (2 if " " in kw else 1)

    if not scores:
        return None

    return max(scores.items(), key=lambda item: item[1])[0]
