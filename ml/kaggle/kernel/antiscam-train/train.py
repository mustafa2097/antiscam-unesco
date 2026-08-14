"""
Anti-Scam Job Detector — trains FULLY on Kaggle (online GPU/CPU).
Dataset: Real or Fake Job Posting Prediction (or first matching CSV under /kaggle/input).
Outputs: scam_tfidf_logreg.joblib + metrics.json in /kaggle/working
"""

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

INPUT_ROOT = Path("/kaggle/input")
OUTPUT_DIR = Path("/kaggle/working")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_csv() -> Path:
    preferred = []
    others = []
    for path in INPUT_ROOT.rglob("*.csv"):
        name = path.name.lower()
        if any(k in name for k in ("fake", "job", "fraud", "scam")):
            preferred.append(path)
        else:
            others.append(path)
    if preferred:
        return preferred[0]
    if others:
        return others[0]
    raise FileNotFoundError("No CSV under /kaggle/input — add a job-posting dataset.")


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
    raise KeyError("No fraudulent/label column found")


def main() -> None:
    csv_path = find_csv()
    print(f"Dataset CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Rows: {len(df)} cols: {list(df.columns)}")

    df["text_blob"] = df.apply(build_text, axis=1)
    df["y"] = df.apply(label_of, axis=1)
    df = df[df["text_blob"].str.len() > 20].copy()
    print(f"Usable rows: {len(df)} | scam rate: {df['y'].mean():.4f}")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text_blob"],
        df["y"],
        test_size=0.2,
        random_state=42,
        stratify=df["y"],
    )

    pipe = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=50000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    solver="liblinear",
                ),
            ),
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
    metrics = {
        "roc_auc": round(auc, 4),
        "rows": int(len(df)),
        "train": int(len(X_train)),
        "test": int(len(X_test)),
        "scam_rate": float(df["y"].mean()),
        "report": report,
        "source_csv": str(csv_path),
        "trained_on": "kaggle-online",
    }
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"ROC-AUC: {auc:.4f}")
    print(f"Saved {model_path}")
    print(f"Saved {metrics_path}")


if __name__ == "__main__":
    main()
