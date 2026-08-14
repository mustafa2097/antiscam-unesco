# Anti-Scam Job Detector — Kaggle Training Notebook
#
# How to use on Kaggle:
# 1. Create a new Notebook.
# 2. Add dataset: "Real or Fake Job Posting Prediction" (or any CSV with
#    description/title text + fraudulent/label column).
# 3. Paste this file into a cell OR upload it and run:
#      %run train_scam_detector_kaggle.py
# 4. Download scam_tfidf_logreg.joblib and place it in:
#      backend/app/ml/artifacts/scam_tfidf_logreg.joblib
#
# Then redeploy the API so inference uses the Kaggle-trained weights.

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

# ---- configure paths for Kaggle ----
INPUT_CANDIDATES = [
    Path("/kaggle/input"),
    Path("."),
]
OUTPUT_DIR = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path(".")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_csv() -> Path:
    for root in INPUT_CANDIDATES:
        if not root.exists():
            continue
        for path in root.rglob("*.csv"):
            name = path.name.lower()
            if "fake" in name or "job" in name or "scam" in name or "fraud" in name:
                return path
        csvs = list(root.rglob("*.csv"))
        if csvs:
            return csvs[0]
    raise FileNotFoundError("No CSV found. Attach a Kaggle job-posting dataset.")


def build_text(row: pd.Series) -> str:
    parts = []
    for col in (
        "title",
        "company_profile",
        "description",
        "requirements",
        "benefits",
        "text",
        "job_description",
    ):
        if col in row and pd.notna(row[col]):
            parts.append(str(row[col]))
    return " ".join(parts).lower()


def label_of(row: pd.Series) -> int:
    for col in ("fraudulent", "label", "is_scam", "scam"):
        if col in row and pd.notna(row[col]):
            val = row[col]
            if isinstance(val, str):
                return 1 if val.strip().lower() in {"1", "true", "yes", "scam", "fraud"} else 0
            return int(float(val))
    return 0


def main() -> None:
    csv_path = find_csv()
    print(f"Using dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    df["text_blob"] = df.apply(build_text, axis=1)
    df["y"] = df.apply(label_of, axis=1)
    df = df[df["text_blob"].str.len() > 20].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        df["text_blob"],
        df["y"],
        test_size=0.2,
        random_state=42,
        stratify=df["y"],
    )

    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=40000, sublinear_tf=True)),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear")),
        ]
    )
    pipe.fit(X_train, y_train)

    proba = pipe.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    auc = float(roc_auc_score(y_test, proba))
    report = classification_report(y_test, pred, output_dict=True)

    model_path = OUTPUT_DIR / "scam_tfidf_logreg.joblib"
    metrics_path = OUTPUT_DIR / "metrics.json"
    joblib.dump(pipe, model_path)
    metrics_path.write_text(json.dumps({"roc_auc": auc, "report": report, "rows": len(df)}, indent=2))
    print(f"ROC-AUC: {auc:.4f}")
    print(f"Saved model → {model_path}")
    print(f"Saved metrics → {metrics_path}")


if __name__ == "__main__":
    main()
