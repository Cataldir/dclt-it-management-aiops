"""Local credit-risk model training for Lesson 07."""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from common import FEATURE_COLUMNS, TARGET_COLUMN, load_or_create_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a synthetic credit-risk model")
    parser.add_argument("--data", type=str, required=True, help="Feature CSV file.")
    parser.add_argument("--output", type=str, required=True, help="Model .pkl output file.")
    parser.add_argument("--seed", type=int, default=42, help="Training seed.")
    args = parser.parse_args()

    dataset = load_or_create_dataset(args.data, seed=args.seed)
    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=args.seed, stratify=y
    )

    model = RandomForestClassifier(n_estimators=120, max_depth=8, random_state=args.seed)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    model_path = Path(args.output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as file_handle:
        pickle.dump(model, file_handle)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "f1_score": round(float(f1_score(y_test, predictions)), 4),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }
    metrics_path = model_path.with_suffix(".metrics.json")
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()