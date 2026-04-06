"""Lesson 04 mini-application for model validation in MLOps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, f1_score


def generate_validation_scenario(scenario: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate synthetic scenarios for promotion gates."""
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1])
    y_pred_prod = np.array([1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1])
    group = np.array(["A", "A", "B", "A", "B", "B", "A", "B", "A", "B", "A", "B"])

    if scenario == "candidate_better":
        y_pred_cand = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1])
    elif scenario == "accuracy_regression":
        y_pred_cand = np.array([1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1])
    elif scenario == "fairness_regression":
        y_pred_cand = np.array([1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0])
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    return y_true, y_pred_prod, y_pred_cand, group


def validate_candidate_model(
    y_true: np.ndarray,
    y_pred_prod: np.ndarray,
    y_pred_cand: np.ndarray,
    group: np.ndarray,
    performance_drop_threshold: float = 0.02,
    fairness_threshold: float = 0.05,
) -> tuple[bool, dict[str, Any]]:
    """Compare a candidate model with the baseline and return a structured report."""
    acc_prod = accuracy_score(y_true, y_pred_prod)
    acc_cand = accuracy_score(y_true, y_pred_cand)
    f1_prod = f1_score(y_true, y_pred_prod, average="weighted")
    f1_cand = f1_score(y_true, y_pred_cand, average="weighted")

    gate_results: list[dict[str, Any]] = []

    accuracy_delta = acc_cand - acc_prod
    accuracy_gate_passed = acc_cand >= acc_prod - performance_drop_threshold
    gate_results.append(
        {
            "gate": "performance_regression",
            "passed": accuracy_gate_passed,
            "baseline_accuracy": round(float(acc_prod), 4),
            "candidate_accuracy": round(float(acc_cand), 4),
            "accuracy_delta": round(float(accuracy_delta), 4),
        }
    )

    f1_by_group: dict[str, float] = {}
    for value in np.unique(group):
        mask = group == value
        f1_by_group[value] = float(
            f1_score(y_true[mask], y_pred_cand[mask], average="weighted")
        )

    disparity = max(f1_by_group.values()) - min(f1_by_group.values())
    fairness_gate_passed = disparity <= fairness_threshold
    gate_results.append(
        {
            "gate": "fairness_gap",
            "passed": fairness_gate_passed,
            "f1_by_group": {key: round(value, 4) for key, value in f1_by_group.items()},
            "fairness_gap": round(float(disparity), 4),
            "allowed_gap": fairness_threshold,
        }
    )

    approved = accuracy_gate_passed and fairness_gate_passed
    report = {
        "decision": "approved" if approved else "rejected",
        "candidate_metrics": {
            "accuracy": round(float(acc_cand), 4),
            "f1_weighted": round(float(f1_cand), 4),
        },
        "production_metrics": {
            "accuracy": round(float(acc_prod), 4),
            "f1_weighted": round(float(f1_prod), 4),
        },
        "gate_results": gate_results,
        "recommended_next_step": (
            "promote_to_staging" if approved else "hold_release_and_review"
        ),
    }
    return approved, report


def save_report(path: str, report: dict[str, Any]) -> None:
    """Persist a JSON validation report."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local model validation gate")
    parser.add_argument(
        "--scenario",
        choices=["candidate_better", "accuracy_regression", "fairness_regression"],
        default="candidate_better",
        help="Synthetic promotion scenario.",
    )
    parser.add_argument(
        "--save-report",
        type=str,
        default=None,
        help="Optional path to persist the final report.",
    )
    args = parser.parse_args()

    y_true, y_pred_prod, y_pred_cand, group = generate_validation_scenario(args.scenario)
    _, report = validate_candidate_model(y_true, y_pred_prod, y_pred_cand, group)

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.save_report:
        save_report(args.save_report, report)


if __name__ == "__main__":
    main()
