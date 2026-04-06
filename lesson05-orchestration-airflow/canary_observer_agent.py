"""Lesson 05 canary observer agent.

Reads canary metrics (from a report file or a simulated observation) and
decides whether to continue, pause, or rollback using local policy or a
Foundry agent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from foundry_helper import (
    CLI_MODE_CHOICES,
    foundry_is_configured,
    normalize_mode,
    run_foundry_json_agent,
)


DEFAULT_MAX_ERROR_RATE = 0.05
DEFAULT_MAX_LATENCY_MS = 450
DEFAULT_MIN_ACCURACY_DROP = 0.03


def simulate_canary_report(scenario: str = "healthy", seed: int = 42) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    base = {
        "service_name": "fraud-api",
        "canary_weight_pct": 10,
        "observation_window_minutes": 60,
        "offline_accuracy": 0.91,
    }

    if scenario == "healthy":
        base["canary_error_rate"] = round(float(rng.normal(0.012, 0.003)), 4)
        base["observed_accuracy"] = round(float(rng.normal(0.90, 0.005)), 4)
        base["p95_latency_ms"] = round(float(rng.normal(280, 20)), 1)
    elif scenario == "error_spike":
        base["canary_error_rate"] = round(float(rng.normal(0.09, 0.01)), 4)
        base["observed_accuracy"] = round(float(rng.normal(0.88, 0.01)), 4)
        base["p95_latency_ms"] = round(float(rng.normal(310, 30)), 1)
    elif scenario == "latency_breach":
        base["canary_error_rate"] = round(float(rng.normal(0.02, 0.005)), 4)
        base["observed_accuracy"] = round(float(rng.normal(0.89, 0.005)), 4)
        base["p95_latency_ms"] = round(float(rng.normal(520, 40)), 1)
    elif scenario == "accuracy_drop":
        base["canary_error_rate"] = round(float(rng.normal(0.015, 0.003)), 4)
        base["observed_accuracy"] = round(float(rng.normal(0.84, 0.01)), 4)
        base["p95_latency_ms"] = round(float(rng.normal(290, 20)), 1)
    else:
        raise ValueError(f"Unknown canary scenario: {scenario}")

    return base


def load_canary_report(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_local_observation(
    report: dict[str, Any],
    max_error_rate: float = DEFAULT_MAX_ERROR_RATE,
    max_latency_ms: float = DEFAULT_MAX_LATENCY_MS,
    min_accuracy_drop: float = DEFAULT_MIN_ACCURACY_DROP,
) -> dict[str, Any]:
    error_rate = float(report["canary_error_rate"])
    latency = float(report["p95_latency_ms"])
    offline_acc = float(report["offline_accuracy"])
    observed_acc = float(report["observed_accuracy"])
    accuracy_delta = offline_acc - observed_acc

    reasons: list[str] = []
    recommended_actions: list[str] = []
    decision = "continue"
    risk_level = "low"

    if error_rate > max_error_rate:
        decision = "rollback"
        risk_level = "high"
        reasons.append(f"Canary error rate {error_rate:.4f} exceeds limit {max_error_rate:.2f}.")
        recommended_actions.append("initiate rollback to the previous stable version")

    if latency > max_latency_ms:
        if decision != "rollback":
            decision = "rollback"
            risk_level = "high"
        reasons.append(f"P95 latency {latency:.1f}ms exceeds SLA limit {max_latency_ms:.0f}ms.")
        recommended_actions.append("investigate latency regression before retry")

    if accuracy_delta > min_accuracy_drop:
        if decision != "rollback":
            decision = "pause"
            risk_level = "medium"
        reasons.append(
            f"Accuracy dropped by {accuracy_delta:.4f} (offline {offline_acc:.4f} vs observed {observed_acc:.4f})."
        )
        recommended_actions.append("extend observation window or review feature drift")

    if decision == "continue":
        reasons.append("All canary metrics are within acceptable bounds.")
        recommended_actions.append("proceed to full rollout")

    return {
        "engine": "local-policy",
        "decision": decision,
        "risk_level": risk_level,
        "rationale": reasons,
        "recommended_actions": recommended_actions,
        "summary": f"Local canary observation: {decision} (risk: {risk_level})",
    }


def build_foundry_prompt(report: dict[str, Any]) -> str:
    return (
        "You are a canary deployment observer agent. "
        "Analyze the canary monitoring metrics below and respond ONLY in JSON with the keys: "
        "decision (continue, pause, rollback), risk_level (low, medium, high), "
        "rationale (list of strings), recommended_actions (list of strings), summary (string). "
        "Context:\n"
        f"{json.dumps(report, ensure_ascii=False, indent=2)}"
    )


def run_foundry_observation(report: dict[str, Any]) -> dict[str, Any]:
    response = run_foundry_json_agent(
        build_foundry_prompt(report),
        instructions=(
            "You are a canary deployment observer agent. "
            "Evaluate real-time canary metrics and return a deployment decision in JSON only."
        ),
        agent_name_env_var="FOUNDRY_CANARY_AGENT_NAME",
        default_agent_name="canary-observer",
    )
    response.setdefault("decision", "pause")
    response.setdefault("risk_level", "medium")
    response.setdefault("rationale", [])
    response.setdefault("recommended_actions", [])
    response.setdefault("summary", "Foundry canary observation completed")
    return response


def observe_canary(
    report_path: str | None = None,
    scenario: str = "healthy",
    seed: int = 42,
    mode: str = "auto",
    max_error_rate: float = DEFAULT_MAX_ERROR_RATE,
    max_latency_ms: float = DEFAULT_MAX_LATENCY_MS,
    min_accuracy_drop: float = DEFAULT_MIN_ACCURACY_DROP,
) -> dict[str, Any]:
    normalized_mode = normalize_mode(mode)
    canary_report = (
        load_canary_report(report_path) if report_path else simulate_canary_report(scenario, seed)
    )
    fallback_reason: str | None = None

    if normalized_mode == "local-policy":
        assessment = run_local_observation(canary_report, max_error_rate, max_latency_ms, min_accuracy_drop)
    elif normalized_mode == "foundry-agent":
        assessment = run_foundry_observation(canary_report)
    else:
        if foundry_is_configured():
            try:
                assessment = run_foundry_observation(canary_report)
            except (ImportError, OSError, RuntimeError, ValueError) as error:
                fallback_reason = str(error)
                assessment = run_local_observation(canary_report, max_error_rate, max_latency_ms, min_accuracy_drop)
        else:
            fallback_reason = "Foundry environment variables are missing; using local policy."
            assessment = run_local_observation(canary_report, max_error_rate, max_latency_ms, min_accuracy_drop)

    result: dict[str, Any] = {
        "requested_mode": normalized_mode,
        "canary_report": canary_report,
        "assessment": assessment,
    }
    if fallback_reason:
        result["fallback_reason"] = fallback_reason
    return result


def save_report(path: str, report: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Canary observer agent for Lesson 05")
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="Path to an existing canary report. When omitted, a scenario is simulated.",
    )
    parser.add_argument(
        "--scenario",
        choices=["healthy", "error_spike", "latency_breach", "accuracy_drop"],
        default="healthy",
        help="Canary simulation scenario.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for reproducibility.")
    parser.add_argument("--mode", choices=CLI_MODE_CHOICES, default="auto", help="Observation mode.")
    parser.add_argument("--output", type=str, default=None, help="Optional path to persist the report.")
    args = parser.parse_args()

    report = observe_canary(
        report_path=args.report,
        scenario=args.scenario,
        seed=args.seed,
        mode=args.mode,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.output:
        save_report(args.output, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
