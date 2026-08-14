"""Built-in EN/AR scam indicators used when the DB has no ingested dataset yet."""

from __future__ import annotations

BUILTIN_INDICATORS: list[dict[str, object]] = [
    # Payment / money upfront
    {"pattern": "pay registration fee", "category": "payment", "severity": 0.92, "language": "en"},
    {"pattern": "pay training fee", "category": "payment", "severity": 0.9, "language": "en"},
    {"pattern": "send money via western union", "category": "payment", "severity": 0.95, "language": "en"},
    {"pattern": "gift card payment", "category": "payment", "severity": 0.93, "language": "en"},
    {"pattern": "wire transfer required", "category": "payment", "severity": 0.9, "language": "en"},
    {"pattern": "processing fee", "category": "payment", "severity": 0.78, "language": "en"},
    {"pattern": "ادفع رسوم", "category": "payment", "severity": 0.92, "language": "ar"},
    {"pattern": "رسوم تسجيل", "category": "payment", "severity": 0.9, "language": "ar"},
    {"pattern": "تحويل عبر ويسترن يونيون", "category": "payment", "severity": 0.95, "language": "ar"},
    {"pattern": "بطاقة هدايا", "category": "payment", "severity": 0.9, "language": "ar"},
    {"pattern": "دفع مقدم", "category": "payment", "severity": 0.85, "language": "ar"},
    # Urgency
    {"pattern": "urgent hiring today", "category": "urgency", "severity": 0.72, "language": "en"},
    {"pattern": "start immediately no interview", "category": "urgency", "severity": 0.88, "language": "en"},
    {"pattern": "limited spots act now", "category": "urgency", "severity": 0.7, "language": "en"},
    {"pattern": "توظيف فوري بدون مقابلة", "category": "urgency", "severity": 0.88, "language": "ar"},
    {"pattern": "الفرصة تنتهي اليوم", "category": "urgency", "severity": 0.75, "language": "ar"},
    {"pattern": "مطلوب فوراً", "category": "urgency", "severity": 0.65, "language": "ar"},
    # Identity / personal data
    {"pattern": "send passport copy first", "category": "identity", "severity": 0.9, "language": "en"},
    {"pattern": "bank account details before interview", "category": "identity", "severity": 0.94, "language": "en"},
    {"pattern": "whatsapp only hiring", "category": "identity", "severity": 0.7, "language": "en"},
    {"pattern": "أرسل صورة جواز السفر", "category": "identity", "severity": 0.9, "language": "ar"},
    {"pattern": "رقم حسابك البنكي قبل المقابلة", "category": "identity", "severity": 0.94, "language": "ar"},
    {"pattern": "التوظيف عبر واتساب فقط", "category": "identity", "severity": 0.72, "language": "ar"},
    # Too-good-to-be-true pay
    {"pattern": "earn $5000 per week from home", "category": "income", "severity": 0.9, "language": "en"},
    {"pattern": "no experience high salary", "category": "income", "severity": 0.8, "language": "en"},
    {"pattern": "work from home easy money", "category": "income", "severity": 0.82, "language": "en"},
    {"pattern": "راتب 3000 دولار اسبوعيا", "category": "income", "severity": 0.9, "language": "ar"},
    {"pattern": "بدون خبرة وراتب عالي", "category": "income", "severity": 0.82, "language": "ar"},
    {"pattern": "عمل من المنزل أرباح سهلة", "category": "income", "severity": 0.85, "language": "ar"},
    # Crypto / check scams
    {"pattern": "crypto payment job", "category": "payment", "severity": 0.75, "language": "en"},
    {"pattern": "cash the check and return excess", "category": "payment", "severity": 0.96, "language": "en"},
    {"pattern": "اصرف الشيك وارجع الباقي", "category": "payment", "severity": 0.96, "language": "ar"},
    # Contact red flags
    {"pattern": "gmail.com recruiter", "category": "contact", "severity": 0.55, "language": "en"},
    {"pattern": "telegram only apply", "category": "contact", "severity": 0.7, "language": "en"},
    {"pattern": "تقديم عبر تيليجرام فقط", "category": "contact", "severity": 0.72, "language": "ar"},
]
