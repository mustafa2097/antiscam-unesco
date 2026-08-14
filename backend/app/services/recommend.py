from __future__ import annotations

from typing import Any

from sqlalchemy import and_, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity
from app.schemas import OpportunityPublic
from app.services.role_extractor import ROLE_KEYWORDS

# Curated fallback recommendations when the DB has few rows for a role.
CURATED: dict[str, dict[str, list[dict[str, str]]]] = {
    "developer": {
        "courses": [
            {
                "title_en": "Full-Stack Web Development (Free)",
                "title_ar": "تطوير ويب متكامل (مجاني)",
                "url": "https://www.freecodecamp.org/",
                "org": "freeCodeCamp",
            },
            {
                "title_en": "CS50 Introduction to Computer Science",
                "title_ar": "مقدمة في علوم الحاسوب CS50",
                "url": "https://cs50.harvard.edu/",
                "org": "Harvard / edX",
            },
        ],
        "jobs": [
            {
                "title_en": "Junior Frontend Developer",
                "title_ar": "مطور واجهات مبتدئ",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "designer": {
        "courses": [
            {
                "title_en": "Google UX Design Certificate",
                "title_ar": "شهادة جوجل لتصميم تجربة المستخدم",
                "url": "https://grow.google/uxdesign/",
                "org": "Google",
            },
            {
                "title_en": "Graphic Design Basics",
                "title_ar": "أساسيات التصميم الجرافيكي",
                "url": "https://www.coursera.org/",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "Junior UI Designer",
                "title_ar": "مصمم واجهات مبتدئ",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "marketing": {
        "courses": [
            {
                "title_en": "Google Digital Marketing & E-commerce",
                "title_ar": "التسويق الرقمي والتجارة الإلكترونية من جوجل",
                "url": "https://grow.google/digitalmarketing/",
                "org": "Google",
            },
        ],
        "jobs": [
            {
                "title_en": "Digital Marketing Assistant",
                "title_ar": "مساعد تسويق رقمي",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "data": {
        "courses": [
            {
                "title_en": "Google Data Analytics Certificate",
                "title_ar": "شهادة جوجل لتحليل البيانات",
                "url": "https://grow.google/dataanalytics/",
                "org": "Google",
            },
        ],
        "jobs": [
            {
                "title_en": "Junior Data Analyst",
                "title_ar": "محلل بيانات مبتدئ",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "teacher": {
        "courses": [
            {
                "title_en": "Teaching Skills for Educators",
                "title_ar": "مهارات التدريس للمعلمين",
                "url": "https://www.coursera.org/",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "Online Tutor",
                "title_ar": "مدرس أونلاين",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "accountant": {
        "courses": [
            {
                "title_en": "Financial Accounting Fundamentals",
                "title_ar": "أساسيات المحاسبة المالية",
                "url": "https://www.coursera.org/",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "Junior Accountant",
                "title_ar": "محاسب مبتدئ",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "hr": {
        "courses": [
            {
                "title_en": "Human Resources Management",
                "title_ar": "إدارة الموارد البشرية",
                "url": "https://www.coursera.org/",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "HR Coordinator",
                "title_ar": "منسق موارد بشرية",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "engineer": {
        "courses": [
            {
                "title_en": "Engineering Project Management",
                "title_ar": "إدارة المشاريع الهندسية",
                "url": "https://www.coursera.org/",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "Junior Engineer",
                "title_ar": "مهندس مبتدئ",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "nurse": {
        "courses": [
            {
                "title_en": "Nursing Continuing Education",
                "title_ar": "تعليم تمريض مستمر",
                "url": "https://www.coursera.org/",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "Clinic Nurse",
                "title_ar": "ممرض/ة عيادة",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
    "customer_support": {
        "courses": [
            {
                "title_en": "Customer Service Fundamentals",
                "title_ar": "أساسيات خدمة العملاء",
                "url": "https://www.coursera.org/",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "Customer Support Agent",
                "title_ar": "موظف دعم العملاء",
                "url": "https://www.linkedin.com/jobs/",
                "org": "Verified listings",
            },
        ],
    },
}

_DEFAULT = {
    "courses": [
        {
            "title_en": "Career Skills for Job Seekers",
            "title_ar": "مهارات مهنية للباحثين عن عمل",
            "url": "https://www.coursera.org/",
            "org": "Coursera",
        },
        {
            "title_en": "Google Career Certificates",
            "title_ar": "شهادات جوجل المهنية",
            "url": "https://grow.google/certificates/",
            "org": "Google",
        },
    ],
    "jobs": [
        {
            "title_en": "Browse verified opportunities",
            "title_ar": "تصفح الفرص الموثقة",
            "url": "#opportunities",
            "org": "Anti Scam",
        },
    ],
}


async def _db_by_role_and_category(
    db: AsyncSession,
    role: str,
    category: str,
    limit: int = 6,
) -> list[OpportunityPublic]:
    keywords = ROLE_KEYWORDS.get(role, (role,))
    role_clauses = []
    for kw in keywords:
        pattern = f"%{kw}%"
        role_clauses.extend(
            [
                Opportunity.position.ilike(pattern),
                Opportunity.title_en.ilike(pattern),
                Opportunity.title_ar.ilike(pattern),
            ]
        )

    stmt = (
        select(Opportunity)
        .where(
            and_(
                Opportunity.verified.is_(True),
                Opportunity.category == category,
                or_(*role_clauses) if role_clauses else true(),
            )
        )
        .order_by(Opportunity.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [OpportunityPublic.model_validate(row) for row in rows]


async def recommend_for_role(db: AsyncSession, role: str | None) -> dict[str, Any]:
    role_slug = (role or "").strip().lower() or None

    courses_db: list[OpportunityPublic] = []
    jobs_db: list[OpportunityPublic] = []
    if role_slug:
        courses_db = await _db_by_role_and_category(db, role_slug, "course")
        jobs_db = await _db_by_role_and_category(db, role_slug, "job")

    curated = CURATED.get(role_slug or "", _DEFAULT)

    return {
        "role": role_slug,
        "message_en": (
            f"This posting looks risky. Here are safer courses and jobs related to {role_slug or 'your field'}."
            if role_slug
            else "This posting looks risky. Explore verified courses and jobs below."
        ),
        "message_ar": (
            f"هذا الإعلان يبدو مشبوهاً. هذه دورات ووظائف موثوقة في مجال {role_slug or 'عملك'}."
            if role_slug
            else "هذا الإعلان يبدو مشبوهاً. تصفح الدورات والوظائف الموثقة أدناه."
        ),
        "courses": [c.model_dump(mode="json") for c in courses_db],
        "jobs": [j.model_dump(mode="json") for j in jobs_db],
        "curated_courses": curated["courses"],
        "curated_jobs": curated["jobs"],
    }
