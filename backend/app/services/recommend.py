from __future__ import annotations

from typing import Any

from sqlalchemy import and_, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity
from app.schemas import OpportunityPublic
from app.services.role_extractor import ROLE_KEYWORDS

# Curated fallback recommendations with direct enrollment/listing URLs.
CURATED: dict[str, dict[str, list[dict[str, str]]]] = {
    "developer": {
        "courses": [
            {
                "title_en": "Google IT Support Professional Certificate",
                "title_ar": "شهادة جوجل لدعم تقنية المعلومات",
                "url": "https://www.coursera.org/professional-certificates/google-it-support",
                "org": "Google / Coursera",
            },
            {
                "title_en": "CS50x — Introduction to Computer Science",
                "title_ar": "CS50x — مقدمة في علوم الحاسوب",
                "url": "https://cs50.harvard.edu/x/",
                "org": "Harvard",
            },
            {
                "title_en": "freeCodeCamp Responsive Web Design",
                "title_ar": "تصميم الويب المتجاوب — freeCodeCamp",
                "url": "https://www.freecodecamp.org/learn/responsive-web-design-v9/",
                "org": "freeCodeCamp",
            },
        ],
        "jobs": [
            {
                "title_en": "UNDP Current Vacancies",
                "title_ar": "الوظائف الحالية في UNDP",
                "url": "https://jobs.undp.org/cj_view_jobs.cfm",
                "org": "UNDP",
            },
        ],
    },
    "designer": {
        "courses": [
            {
                "title_en": "Google UX Design Professional Certificate",
                "title_ar": "شهادة جوجل لتصميم تجربة المستخدم",
                "url": "https://www.coursera.org/professional-certificates/google-ux-design",
                "org": "Google / Coursera",
            },
            {
                "title_en": "Meta Front-End Developer Certificate",
                "title_ar": "شهادة Meta لمطور الواجهات",
                "url": "https://www.coursera.org/professional-certificates/meta-front-end-developer",
                "org": "Meta / Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "UNESCO All Job Openings",
                "title_ar": "وظائف اليونسكو المفتوحة",
                "url": "https://careers.unesco.org/go/All-jobs-openings/784002/",
                "org": "UNESCO",
            },
        ],
    },
    "marketing": {
        "courses": [
            {
                "title_en": "Google Digital Marketing & E-commerce Certificate",
                "title_ar": "شهادة جوجل للتسويق الرقمي",
                "url": "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce",
                "org": "Google / Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "UNICEF Open Vacancies",
                "title_ar": "وظائف يونيسف المفتوحة",
                "url": "https://jobs.unicef.org/en-us/listing/",
                "org": "UNICEF",
            },
        ],
    },
    "data": {
        "courses": [
            {
                "title_en": "Google Data Analytics Professional Certificate",
                "title_ar": "شهادة جوجل لتحليل البيانات",
                "url": "https://www.coursera.org/professional-certificates/google-data-analytics",
                "org": "Google / Coursera",
            },
            {
                "title_en": "IBM Data Science Professional Certificate",
                "title_ar": "شهادة IBM لعلوم البيانات",
                "url": "https://www.coursera.org/professional-certificates/ibm-data-science",
                "org": "IBM / Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "UN Careers Job Openings",
                "title_ar": "وظائف الأمم المتحدة",
                "url": "https://careers.un.org/",
                "org": "United Nations",
            },
        ],
    },
    "teacher": {
        "courses": [
            {
                "title_en": "Foundations of Teaching for Learning",
                "title_ar": "أساسيات التعليم والتعلّم",
                "url": "https://www.coursera.org/learn/teach-learn",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "UNESCO Internships & Volunteers",
                "title_ar": "تدريب وتطوع اليونسكو",
                "url": "https://careers.unesco.org/go/Internships-and-volunteers/783902/",
                "org": "UNESCO",
            },
        ],
    },
    "accountant": {
        "courses": [
            {
                "title_en": "Introduction to Financial Accounting",
                "title_ar": "مقدمة في المحاسبة المالية",
                "url": "https://www.coursera.org/learn/wharton-accounting",
                "org": "Coursera / Wharton",
            },
        ],
        "jobs": [
            {
                "title_en": "UNDP Current Vacancies",
                "title_ar": "الوظائف الحالية في UNDP",
                "url": "https://jobs.undp.org/cj_view_jobs.cfm",
                "org": "UNDP",
            },
        ],
    },
    "hr": {
        "courses": [
            {
                "title_en": "Human Resources Management",
                "title_ar": "إدارة الموارد البشرية",
                "url": "https://www.coursera.org/learn/human-resources",
                "org": "Coursera",
            },
            {
                "title_en": "Google Project Management Certificate",
                "title_ar": "شهادة جوجل لإدارة المشاريع",
                "url": "https://www.coursera.org/professional-certificates/google-project-management",
                "org": "Google / Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "UNICEF Open Vacancies",
                "title_ar": "وظائف يونيسف المفتوحة",
                "url": "https://jobs.unicef.org/en-us/listing/",
                "org": "UNICEF",
            },
        ],
    },
    "engineer": {
        "courses": [
            {
                "title_en": "Construction Project Management",
                "title_ar": "إدارة مشاريع الإنشاء",
                "url": "https://www.coursera.org/specializations/construction-project-management",
                "org": "Coursera / Columbia",
            },
        ],
        "jobs": [
            {
                "title_en": "WFP Careers Portal",
                "title_ar": "بوابة وظائف WFP",
                "url": "https://careers.wfp.org/careersection/ex/jobsearch.ftl",
                "org": "WFP",
            },
        ],
    },
    "nurse": {
        "courses": [
            {
                "title_en": "Vital Signs: Understanding What the Body Is Telling Us",
                "title_ar": "العلامات الحيوية",
                "url": "https://www.coursera.org/learn/vital-signs",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "WHO Careers — Current Vacancies",
                "title_ar": "وظائف منظمة الصحة العالمية",
                "url": "https://careers.who.int/careersection/ex/jobsearch.ftl",
                "org": "WHO",
            },
        ],
    },
    "customer_support": {
        "courses": [
            {
                "title_en": "Customer Service Fundamentals",
                "title_ar": "أساسيات خدمة العملاء",
                "url": "https://www.coursera.org/specializations/customer-service",
                "org": "Coursera",
            },
        ],
        "jobs": [
            {
                "title_en": "UNV Unified Volunteering Platform",
                "title_ar": "منصة التطوع UNV",
                "url": "https://app.unv.org/",
                "org": "UN Volunteers",
            },
        ],
    },
}

_DEFAULT = {
    "courses": [
        {
            "title_en": "Google Career Certificates on Coursera",
            "title_ar": "شهادات جوجل المهنية على Coursera",
            "url": "https://www.coursera.org/professional-certificates/google-data-analytics",
            "org": "Google / Coursera",
        },
        {
            "title_en": "CS50x — Introduction to Computer Science",
            "title_ar": "CS50x — مقدمة في علوم الحاسوب",
            "url": "https://cs50.harvard.edu/x/",
            "org": "Harvard",
        },
    ],
    "jobs": [
        {
            "title_en": "UNICEF Open Vacancies",
            "title_ar": "وظائف يونيسف المفتوحة",
            "url": "https://jobs.unicef.org/en-us/listing/",
            "org": "UNICEF",
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
