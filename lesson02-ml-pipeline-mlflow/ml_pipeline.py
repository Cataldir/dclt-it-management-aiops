"""Lesson 02 mini-application for an ML pipeline with tracking and artifacts."""

from __future__ import annotations

import argparse
import json
import pickle
from contextlib import nullcontext
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

try:
    import mlflow
    import mlflow.sklearn
except ImportError:
    mlflow = None


def generate_synthetic_data(sample_count: int = 500, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic patient dataset for demonstration purposes."""
    import numpy as np

    rng = np.random.default_rng(seed)
    data = {
        "age": rng.integers(18, 90, size=sample_count),
        "length_of_stay": rng.integers(1, 30, size=sample_count),
        "num_comorbidities": rng.integers(0, 6, size=sample_count),
        "num_medications": rng.integers(1, 15, size=sample_count),
    }
    dataframe = pd.DataFrame(data)
    prob = (
        0.08
        + 0.005 * dataframe["age"]
        + 0.055 * dataframe["num_comorbidities"]
        + 0.012 * dataframe["length_of_stay"]
    ).clip(0, 1)
    dataframe["readmitted"] = rng.binomial(1, prob)
    return dataframe


def prepare_data(csv_path: str | None = None, seed: int = 42) -> pd.DataFrame:
    """Load or generate data and apply minimal validation."""
    if csv_path:
        dataframe = pd.read_csv(csv_path)
    else:
        dataframe = generate_synthetic_data(seed=seed)

    return dataframe.dropna(subset=["age", "length_of_stay", "num_comorbidities"])


def save_artifacts(
    artifacts_dir: Path,
    model: RandomForestClassifier,
    metrics: dict[str, Any],
    features: list[str],
) -> None:
    """Save the local artifacts produced by the pipeline."""
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    model_path = artifacts_dir / "model.pkl"
    metrics_path = artifacts_dir / "metrics.json"
    model_card_path = artifacts_dir / "model_card.md"

    with model_path.open("wb") as file_handle:
        pickle.dump(model, file_handle)

    metrics_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    model_card = f"""# Model Card - Hospital Readmission

## Objective

Predict the probability of readmission within 30 days.

## Features

- {features[0]}
- {features[1]}
- {features[2]}
- {features[3]}

## Primary Metrics

- Accuracy: {metrics['accuracy']:.4f}
- F1-score: {metrics['f1_score']:.4f}
- Training size: {metrics['train_size']}
- Test size: {metrics['test_size']}

## Limitations

- Synthetic data; does not replace validation with real data.
- MLflow tracking is optional and depends on the local environment.
"""
    model_card_path.write_text(model_card, encoding="utf-8")


def run_pipeline(
    csv_path: str | None = None,
    artifacts_dir: str = "artifacts",
    seed: int = 42,
) -> dict[str, Any]:
    """Run the full ML pipeline with optional MLflow tracking."""
    dataframe = prepare_data(csv_path=csv_path, seed=seed)

    features = ["age", "length_of_stay", "num_comorbidities", "num_medications"]
    target_column = "readmitted"
    X = dataframe[features]
    y = dataframe[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )

    if mlflow is not None:
        mlflow.set_experiment("hospital_readmission")
        run_context = mlflow.start_run(run_name="rf_baseline_v1")
    else:
        run_context = nullcontext()

    with run_context:
        params = {"n_estimators": 200, "max_depth": 10, "random_state": seed}
        model = RandomForestClassifier(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            random_state=params["random_state"],
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        metrics = {
            "accuracy": round(float(accuracy), 4),
            "f1_score": round(float(f1), 4),
            "train_size": int(len(X_train)),
            "test_size": int(len(X_test)),
            "classification_report": report,
            "tracking_enabled": mlflow is not None,
        }

        if mlflow is not None:
            mlflow.log_params(params)
            mlflow.log_metrics({"accuracy": accuracy, "f1_score": f1})
            mlflow.sklearn.log_model(model, artifact_path="hospital_readmission_model")

        save_artifacts(Path(artifacts_dir), model, metrics, features)
        return metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ML Pipeline - Hospital Readmission Prediction"
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Optional CSV path. If omitted, synthetic data is generated.",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=str,
        default="artifacts",
        help="Directory where training artifacts will be written.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for reproducibility.")
    args = parser.parse_args()

    result = run_pipeline(
        csv_path=args.data, artifacts_dir=args.artifacts_dir, seed=args.seed
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
