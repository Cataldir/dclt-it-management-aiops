"""Lesson 04 model promotion review agent.

Takes the validation report produced by model_validation.py and generates
a human-readable promotion decision using local policy or a Foundry agent.
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
from model_validation import generate_validation_scenario, save_report, validate_candidate_model


def load_report(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_local_review(report: dict[str, Any]) -> dict[str, Any]:
    decision = report["decision"]
    gates = report["gate_results"]
    candidate = report["candidate_metrics"]
    production = report["production_metrics"]
    rationale: list[str] = []
    recommended_actions: list[str] = []

    for gate in gates:
        if gate["passed"]:
            rationale.append(f"Gate '{gate['gate']}' passed.")
        else:
            rationale.append(f"Gate '{gate['gate']}' failed.")

    acc_delta = candidate["accuracy"] - production["accuracy"]
    f1_delta = candidate["f1_weighted"] - production["f1_weighted"]

    if decision == "approved":
        rationale.append(
            f"Candidate improves accuracy by {acc_delta:+.4f} and F1 by {f1_delta:+.4f}."
        )
        recommended_actions.append("promote candidate to staging")
        recommended_actions.append("schedule integration tests before production rollout")
    else:
        rationale.append(
            f"Accuracy delta {acc_delta:+.4f}, F1 delta {f1_delta:+.4f} — review before re-submitting."
        )
        recommended_actions.append("investigate failing gates before next iteration")
        recommended_actions.append("check training data quality and feature engineering")

    return {
        "engine": "local-policy",
        "decision": decision,
        "rationale": rationale,
        "recommended_actions": recommended_actions,
        "summary": f"Local promotion review: {decision}",
    }


def build_foundry_prompt(report: dict[str, Any]) -> str:
    return (
        "You are a model promotion review agent. "
        "Analyze the validation report below and respond ONLY in JSON with the keys: "
        "decision (approved or rejected), rationale (list of strings), "
        "recommended_actions (list of strings), summary (string). "
        "Context:\n"
        f"{json.dumps(report, ensure_ascii=False, indent=2)}"
    )


def run_foundry_review(report: dict[str, Any]) -> dict[str, Any]:
    response = run_foundry_json_agent(
        build_foundry_prompt(report),
        instructions=(
            "You are a model promotion review agent. "
            "Evaluate the candidate model against production metrics and fairness gates. "
            "Return a structured promotion review in JSON only."
        ),
        agent_name_env_var="FOUNDRY_PROMOTION_AGENT_NAME",
        default_agent_name="model-promotion-reviewer",
    )
    response.setdefault("decision", "rejected")
    response.setdefault("rationale", [])
    response.setdefault("recommended_actions", [])
    response.setdefault("summary", "Foundry promotion review completed")
    return response


def review_promotion(
    report_path: str | None = None,
    scenario: str = "candidate_better",
    mode: str = "auto",
) -> dict[str, Any]:
    normalized_mode = normalize_mode(mode)

    if report_path:
        validation_report = load_report(report_path)
    else:
        y_true, y_pred_prod, y_pred_cand, group = generate_validation_scenario(scenario)
        _, validation_report = validate_candidate_model(y_true, y_pred_prod, y_pred_cand, group)

    fallback_reason: str | None = None

    if normalized_mode == "local-policy":
        assessment = run_local_review(validation_report)
    elif normalized_mode == "foundry-agent":
        assessment = run_foundry_review(validation_report)
    else:
        if foundry_is_configured():
            try:
                assessment = run_foundry_review(validation_report)
            except (ImportError, OSError, RuntimeError, ValueError) as error:
                fallback_reason = str(error)
                assessment = run_local_review(validation_report)
        else:
            fallback_reason = "Foundry environment variables are missing; using local policy."
            assessment = run_local_review(validation_report)

    result: dict[str, Any] = {
        "requested_mode": normalized_mode,
        "validation_report": validation_report,
        "assessment": assessment,
    }
    if fallback_reason:
        result["fallback_reason"] = fallback_reason
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Model promotion review agent for Lesson 04")
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="Path to an existing validation report. When omitted, a scenario is generated.",
    )
    parser.add_argument(
        "--scenario",
        choices=["candidate_better", "accuracy_regression", "fairness_regression"],
        default="candidate_better",
        help="Scenario to generate when no report is provided.",
    )
    parser.add_argument("--mode", choices=CLI_MODE_CHOICES, default="auto", help="Review mode.")
    parser.add_argument("--output", type=str, default=None, help="Optional path to persist the review report.")
    args = parser.parse_args()

    report = review_promotion(report_path=args.report, scenario=args.scenario, mode=args.mode)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.output:
        save_report(args.output, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
