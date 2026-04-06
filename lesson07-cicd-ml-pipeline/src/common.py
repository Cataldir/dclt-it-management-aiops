"""Shared utilities for the Lesson 07 pipeline."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = [
    "income",
    "debt_ratio",
    "credit_utilization",
    "recent_inquiries",
    "late_payments",
    "has_mortgage",
]
TARGET_COLUMN = "defaulted"
GROUP_COLUMN = "segment"


def generate_credit_data(samples: int = 800, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic credit-risk dataset."""
    rng = np.random.default_rng(seed)
    dataframe = pd.DataFrame(
        {
            "income": rng.integers(2500, 22000, size=samples),
            "debt_ratio": rng.uniform(0.05, 0.95, size=samples),
            "credit_utilization": rng.uniform(0.05, 0.99, size=samples),
            "recent_inquiries": rng.integers(0, 8, size=samples),
            "late_payments": rng.integers(0, 6, size=samples),
            "has_mortgage": rng.integers(0, 2, size=samples),
            "segment": rng.choice(["core", "growth"], size=samples, p=[0.7, 0.3]),
        }
    )

    risk_score = (
        0.55 * dataframe["debt_ratio"]
        + 0.45 * dataframe["credit_utilization"]
        + 0.08 * dataframe["recent_inquiries"]
        + 0.1 * dataframe["late_payments"]
        - 0.00002 * dataframe["income"]
        - 0.04 * dataframe["has_mortgage"]
    )
    dataframe[TARGET_COLUMN] = (risk_score > 0.68).astype(int)
    return dataframe


def load_or_create_dataset(path: str, seed: int = 42) -> pd.DataFrame:
    """Load the dataset or generate it automatically for the local pipeline."""
    dataset_path = Path(path)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)

    if dataset_path.exists():
        return pd.read_csv(dataset_path)

    dataframe = generate_credit_data(seed=seed)
    dataframe.to_csv(dataset_path, index=False)
    return dataframe


def load_model(path: str):
    """Load a pickle-serialized model."""
    with Path(path).open("rb") as file_handle:
        return pickle.load(file_handle)


def evaluate_model_accuracy(model, dataframe: pd.DataFrame, seed: int = 42) -> float:
    """Calculate accuracy on a reproducible dataset split."""
    X = dataframe[FEATURE_COLUMNS]
    y = dataframe[TARGET_COLUMN]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )
    predictions = model.predict(X_test)
    return float(accuracy_score(y_test, predictions))


def measure_fairness_gap(model, dataframe: pd.DataFrame, seed: int = 42) -> dict[str, object]:
    """Calculate recall by group and the maximum gap across segments."""
    X = dataframe[FEATURE_COLUMNS]
    y = dataframe[TARGET_COLUMN]
    groups = dataframe[GROUP_COLUMN]
    _, X_test, _, y_test, _, group_test = train_test_split(
        X, y, groups, test_size=0.2, random_state=seed, stratify=y
    )

    predictions = model.predict(X_test)
    recall_by_group: dict[str, float] = {}
    for group in sorted(group_test.unique()):
        mask = group_test == group
        recall_by_group[group] = float(
            recall_score(y_test[mask], predictions[mask], zero_division=0)
        )

    gap = max(recall_by_group.values()) - min(recall_by_group.values())
    return {
        "fairness_gap": float(gap),
        "recall_by_group": recall_by_group,
    }


def write_json_artifact(path: str, payload: dict[str, object]) -> None:
    """Persist JSON artifacts used by the pipeline and agents."""
    artifact_path = Path(path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )