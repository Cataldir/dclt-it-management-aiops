"""Lesson 02 experiment review agent.

Reviews ML pipeline artifacts and produces a structured assessment
using local policy rules or an Azure AI Foundry agent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from foundry_helper import (
    CLI_MODE_CHOICES,
    foundry_is_configured,
    normalize_mode,
    run_foundry_json_agent,
)


DEFAULT_ARTIFACTS_DIR = "artifacts"
MIN_ACCURACY = 0.80
MIN_F1 = 0.70


def load_metrics(artifacts_dir: str) -> dict[str, Any]:
    path = Path(artifacts_dir) / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_model_card(artifacts_dir: str) -> str | None:
    path = Path(artifacts_dir) / "model_card.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def run_local_review(
    metrics: dict[str, Any],
    min_accuracy: float = MIN_ACCURACY,
    min_f1: float = MIN_F1,
) -> dict[str, Any]:
    accuracy = float(metrics["accuracy"])
    f1 = float(metrics["f1_score"])
    suggestions: list[str] = []
    decision = "promote"

    if accuracy < min_accuracy:
        decision = "iterate"
        suggestions.append(
            f"Accuracy {accuracy:.4f} is below the minimum {min_accuracy:.2f}. "
            "Consider tuning hyperparameters or adding features."
        )

    if f1 < min_f1:
        decision = "iterate"
        suggestions.append(
            f"F1 score {f1:.4f} is below the minimum {min_f1:.2f}. "
            "Check class imbalance handling."
        )

    if accuracy >= 0.95 and f1 >= 0.95:
        suggestions.append(
            "Metrics are unusually high — verify there is no data leakage."
        )

    if decision == "promote":
        suggestions.append(
            "Metrics are within acceptable bounds. The model is ready for the validation gate."
        )

    return {
        "engine": "local-policy",
        "decision": decision,
        "accuracy": accuracy,
        "f1_score": f1,
        "suggestions": suggestions,
        "summary": f"Local review: {decision}",
    }


def build_foundry_prompt(metrics: dict[str, Any], model_card: str | None) -> str:
    context: dict[str, Any] = {"metrics": metrics}
    if model_card:
        context["model_card"] = model_card
    return (
        "You are an ML experiment review agent. "
        "Analyze the training metrics and model card below and respond ONLY in JSON with the keys: "
        "decision (one of: promote, iterate, discard), suggestions (list of strings), summary (string). "
        "Context:\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def run_foundry_review(metrics: dict[str, Any], model_card: str | None) -> dict[str, Any]:
    response = run_foundry_json_agent(
        build_foundry_prompt(metrics, model_card),
        instructions=(
            "You are an ML experiment review agent. "
            "Evaluate the training run and return a structured review in JSON only."
        ),
        agent_name_env_var="FOUNDRY_EXPERIMENT_AGENT_NAME",
        default_agent_name="ml-experiment-reviewer",
    )
    response.setdefault("decision", "iterate")
    response.setdefault("suggestions", [])
    response.setdefault("summary", "Foundry review completed")
    return response


def review_experiment(
    artifacts_dir: str = DEFAULT_ARTIFACTS_DIR,
    mode: str = "auto",
    min_accuracy: float = MIN_ACCURACY,
    min_f1: float = MIN_F1,
) -> dict[str, Any]:
    normalized_mode = normalize_mode(mode)
    metrics = load_metrics(artifacts_dir)
    model_card = load_model_card(artifacts_dir)
    fallback_reason: str | None = None

    if normalized_mode == "local-policy":
        assessment = run_local_review(metrics, min_accuracy, min_f1)
    elif normalized_mode == "foundry-agent":
        assessment = run_foundry_review(metrics, model_card)
    else:
        if foundry_is_configured():
            try:
                assessment = run_foundry_review(metrics, model_card)
            except (ImportError, OSError, RuntimeError, ValueError) as error:
                fallback_reason = str(error)
                assessment = run_local_review(metrics, min_accuracy, min_f1)
        else:
            fallback_reason = "Foundry environment variables are missing; using local policy."
            assessment = run_local_review(metrics, min_accuracy, min_f1)

    report: dict[str, Any] = {
        "requested_mode": normalized_mode,
        "metrics": metrics,
        "assessment": assessment,
    }
    if fallback_reason:
        report["fallback_reason"] = fallback_reason
    return report


def save_report(path: str, report: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Experiment review agent for Lesson 02")
    parser.add_argument("--artifacts-dir", default=DEFAULT_ARTIFACTS_DIR, help="Directory with pipeline artifacts.")
    parser.add_argument("--mode", choices=CLI_MODE_CHOICES, default="auto", help="Review mode.")
    parser.add_argument("--min-accuracy", type=float, default=MIN_ACCURACY)
    parser.add_argument("--min-f1", type=float, default=MIN_F1)
    parser.add_argument("--output", type=str, default=None, help="Optional path to persist the review report.")
    args = parser.parse_args()

    report = review_experiment(
        artifacts_dir=args.artifacts_dir,
        mode=args.mode,
        min_accuracy=args.min_accuracy,
        min_f1=args.min_f1,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.output:
        save_report(args.output, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
