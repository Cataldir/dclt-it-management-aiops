"""Local metrics and fairness gate for Lesson 05."""

from __future__ import annotations

import json
from pathlib import Path


def check_metrics(
    metrics_path: str,
    fairness_path: str,
    min_accuracy: float = 0.85,
    max_fairness_gap: float = 0.2,
) -> dict[str, object]:
    """Validate training artifacts before canary deployment."""
    metrics = json.loads(Path(metrics_path).read_text(encoding="utf-8"))
    fairness = json.loads(Path(fairness_path).read_text(encoding="utf-8"))

    accuracy_ok = metrics["accuracy"] >= min_accuracy
    fairness_ok = fairness["recall_gap"] <= max_fairness_gap

    if not accuracy_ok:
        raise ValueError(
            f"Accuracy {metrics['accuracy']:.4f} is below the threshold {min_accuracy:.2f}"
        )

    if not fairness_ok:
        raise ValueError(
            f"Fairness gap {fairness['recall_gap']:.4f} is above the threshold {max_fairness_gap:.2f}"
        )

    return {
        "decision": "approved",
        "accuracy": metrics["accuracy"],
        "f1_score": metrics["f1_score"],
        "fairness_gap": fairness["recall_gap"],
    }