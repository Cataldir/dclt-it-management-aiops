"""Local fraud model training for Lesson 05."""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.model_selection import train_test_split


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a synthetic fraud model")
    parser.add_argument("--input", type=str, required=True, help="Training CSV dataset.")
    parser.add_argument("--model-output", type=str, required=True, help="Output .pkl file.")
    parser.add_argument("--metrics-output", type=str, required=True, help="Metrics JSON file.")
    parser.add_argument("--fairness-output", type=str, required=True, help="Fairness JSON file.")
    parser.add_argument("--env", type=str, default="dev", help="Logical training environment.")
    args = parser.parse_args()

    dataframe = pd.read_csv(args.input)
    feature_columns = [
        "amount",
        "velocity_1h",
        "device_risk",
        "historical_chargeback_ratio",
        "is_high_amount",
        "night_transaction",
        "cross_border",
    ]
    X = dataframe[feature_columns]
    y = dataframe["is_fraud"]
    groups = dataframe["customer_segment"]

    X_train, X_test, y_train, y_test, _, group_test = train_test_split(
        X, y, groups, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=160, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "environment": args.env,
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "f1_score": round(float(f1_score(y_test, predictions)), 4),
        "rows_train": int(len(X_train)),
        "rows_test": int(len(X_test)),
    }

    recall_by_group: dict[str, float] = {}
    for group in sorted(group_test.unique()):
        mask = group_test == group
        recall_by_group[group] = round(
            float(recall_score(y_test[mask], predictions[mask], zero_division=0)), 4
        )

    fairness = {
        "recall_by_group": recall_by_group,
        "recall_gap": round(max(recall_by_group.values()) - min(recall_by_group.values()), 4),
    }

    model_path = Path(args.model_output)
    metrics_path = Path(args.metrics_output)
    fairness_path = Path(args.fairness_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    with model_path.open("wb") as file_handle:
        pickle.dump(model, file_handle)

    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    fairness_path.write_text(json.dumps(fairness, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()