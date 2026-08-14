"""
Train a lightweight TF-IDF + LogisticRegression scam detector.

Usage (from backend/):
  python -m app.ml.train

Optional Kaggle CSV (fake-job-postings or similar with text + fraudulent label):
  python -m app.ml.train --kaggle-csv path/to/fake_job_postings.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from app.ml.predictor import MODEL_DIR, MODEL_PATH, normalize_text

# Seed corpus: realistic scam vs legit posts (EN + AR) across common roles.
SEED_ROWS: list[tuple[str, int]] = [
    # ---- scam (1) ----
    ("Urgent hiring work from home earn $5000 per week no experience send gift cards for equipment fee", 1),
    ("Congratulations you are hired! Pay $200 registration fee via Western Union to start today", 1),
    ("Telegram only recruiter: send passport copy and bank account details before interview", 1),
    ("Cash this company check deposit and return the excess amount immediately", 1),
    ("Limited spots act now! Crypto payment job, whatsapp only, no interview required", 1),
    ("توظيف فوري بدون مقابلة راتب 3000 دولار اسبوعيا ادفع رسوم تسجيل عبر ويسترن يونيون", 1),
    ("أرسل صورة جواز السفر ورقم حسابك البنكي قبل المقابلة التقديم عبر واتساب فقط", 1),
    ("عمل من المنزل أرباح سهلة بدون خبرة اصرف الشيك وارجع الباقي", 1),
    ("الفرصة تنتهي اليوم رسوم تدريب مطلوبة عبر بطاقة هدايا", 1),
    ("مطلوب فوراً مطور ادفع رسوم معدات وابدأ اليوم عبر تيليجرام فقط", 1),
    ("Easy money data entry $4000 weekly processing fee required start immediately", 1),
    ("Package reshipping job: receive packages then forward, keep commission, no contract", 1),
    ("HR manager gmail.com: wire transfer required for background check clearance", 1),
    ("Nurse remote job high salary pay licensing fee first then we hire you", 1),
    ("محاسب عن بعد راتب خيالي دفع مقدم لبطاقة المعدات مطلوب", 1),
    ("مصمم جرافيك راتب عالي بدون خبرة أرسل بياناتك البنكية الآن", 1),
    ("Teacher online $80/hour pay platform access fee with bitcoin", 1),
    ("Delivery driver earn big send money for uniform first via western union", 1),
    ("Customer support agent: gift card payment for software license then start", 1),
    ("Marketing specialist work from home easy money telegram apply only", 1),
    # ---- legit (0) ----
    ("We are hiring a Junior Frontend Developer in Baghdad. Requirements: HTML, CSS, React. Apply via company careers page. Competitive salary based on experience.", 0),
    ("Full-time accountant needed at a licensed firm. Bachelor degree preferred. Interviews held on-site. No fees ever.", 0),
    ("Looking for a certified nurse for a private clinic in Erbil. Valid license required. Official contract and benefits provided.", 0),
    ("Digital marketing assistant: SEO and content. Hybrid schedule. Submit CV through LinkedIn Easy Apply.", 0),
    ("Software engineer role with mentorship program. Salary range disclosed in interview. Equal opportunity employer.", 0),
    ("مطلوب معلم لغة إنجليزية دوام جزئي في مدرسة أهلية. شهادة جامعية مطلوبة. المقابلة في المدرسة. لا رسوم تقديم.", 0),
    ("نبحث عن مطور ويب مبتدئ للعمل في شركة تقنية موثقة. الراتب حسب الخبرة. التقديم عبر موقع الشركة الرسمي.", 0),
    ("فرصة عمل محاسب في مكتب تدقيق مرخص. عقد رسمي وتأمين. لا يطلب أي دفع مسبق.", 0),
    ("وظيفة ممرض/ة في مستشفى خاص. يشترط ترخيص مزاولة. دوام حضوري ومقابلة رسمية.", 0),
    ("مصمم واجهات بدوام هجين. محفظة أعمال مطلوبة. الراتب تنافسي ويحدد بعد المقابلة.", 0),
    ("HR coordinator for a telecom company. Experience with recruitment ATS preferred. Apply on official portal.", 0),
    ("Data analyst internship with stipend. Python and SQL basics. Mentored by senior analysts.", 0),
    ("Civil engineer junior position. Site visits in Baghdad. Engineering degree required. Verified employer.", 0),
    ("Customer support agent for e-commerce. Training provided. Hourly wage + benefits. No upfront costs.", 0),
    ("Translator Arabic-English freelance gigs with published rates. NDA and invoice process.", 0),
    ("Online tutor for math grades 7-12. Platform provides students. Weekly payouts to bank account after work.", 0),
    ("Graphic designer for NGO volunteer project (unpaid). Portfolio review. Certificate of participation.", 0),
    ("Sales representative for retail chain. Commission structure explained in writing. Onboarding in store.", 0),
    ("Photographer for events company. Equipment provided. Contract per event. Portfolio required.", 0),
    ("Lawyer associate at registered law firm. Bar membership required. Partner interview process.", 0),
]


def _load_kaggle_csv(path: Path) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    with path.open(encoding="utf-8", errors="ignore") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # fake_job_postings.csv style
            parts = [
                row.get("title") or "",
                row.get("company_profile") or "",
                row.get("description") or "",
                row.get("requirements") or "",
                row.get("benefits") or "",
                row.get("text") or "",
                row.get("job_description") or "",
            ]
            text = normalize_text(" ".join(parts))
            if not text:
                continue
            label_raw = row.get("fraudulent") or row.get("label") or row.get("is_scam") or "0"
            try:
                label = int(float(str(label_raw).strip()))
            except ValueError:
                label = 1 if str(label_raw).strip().lower() in {"true", "scam", "yes"} else 0
            rows.append((text, 1 if label else 0))
    return rows


def train(kaggle_csv: Path | None = None) -> dict:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, roc_auc_score
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    import joblib

    data = [(normalize_text(t), y) for t, y in SEED_ROWS]
    if kaggle_csv and kaggle_csv.exists():
        data.extend(_load_kaggle_csv(kaggle_csv))

    texts = [t for t, _ in data if t]
    labels = [y for t, y in data if t]

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels if len(set(labels)) > 1 else None,
    )

    pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=25000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    solver="liblinear",
                ),
            ),
        ]
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    try:
        auc = float(roc_auc_score(y_test, y_proba))
    except ValueError:
        auc = 0.0

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    metrics = {
        "samples": len(texts),
        "train": len(X_train),
        "test": len(X_test),
        "roc_auc": round(auc, 4),
        "report": report,
        "model_path": str(MODEL_PATH),
    }
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train scam job detector")
    parser.add_argument("--kaggle-csv", type=Path, default=None)
    args = parser.parse_args()
    metrics = train(args.kaggle_csv)
    print(json.dumps({k: metrics[k] for k in ("samples", "train", "test", "roc_auc", "model_path")}, indent=2))


if __name__ == "__main__":
    main()
