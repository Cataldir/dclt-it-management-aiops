"""Lesson 08 mini-application for agentic remediation with guardrails."""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
from typing import Any

import numpy as np

PLAYBOOKS_FILE = Path(__file__).with_name("playbooks.json")


def load_playbooks() -> dict[str, dict[str, Any]]:
    """Load the versioned catalog of operational playbooks."""
    return json.loads(PLAYBOOKS_FILE.read_text(encoding="utf-8"))


def simulate_signals(scenario: str, seed: int = 42) -> dict[str, Any]:
    """Generate synthetic telemetry for common operational scenarios."""
    rng = np.random.default_rng(seed)
    signals = {
        "scenario": scenario,
        "service_name": "fraud-api",
        "latency_seconds": round(float(rng.normal(0.32, 0.02)), 4),
        "error_rate": round(float(rng.normal(0.012, 0.004)), 4),
        "cpu_usage": round(float(rng.normal(0.56, 0.05)), 4),
        "recent_deployment": False,
    }

    if scenario == "latency_spike":
        signals["latency_seconds"] = 0.88
        signals["cpu_usage"] = 0.84
    elif scenario == "cpu_saturation":
        signals["latency_seconds"] = 0.71
        signals["cpu_usage"] = 0.97
    elif scenario == "transient_error":
        signals["error_rate"] = 0.082
    elif scenario == "bad_release":
        signals["latency_seconds"] = 0.76
        signals["error_rate"] = 0.11
        signals["recent_deployment"] = True
    elif scenario != "healthy":
        raise ValueError(f"Unknown scenario: {scenario}")

    return signals


def detect_incident(signals: dict[str, Any]) -> dict[str, Any]:
    """Translate operational signals into a structured diagnosis."""
    if signals["recent_deployment"] and signals["error_rate"] > 0.08:
        incident_type = "bad_release"
        severity = "critical"
    elif signals["cpu_usage"] > 0.9:
        incident_type = "cpu_saturation"
        severity = "high"
    elif signals["latency_seconds"] > 0.75:
        incident_type = "latency_spike"
        severity = "high"
    elif signals["error_rate"] > 0.05:
        incident_type = "transient_error"
        severity = "medium"
    else:
        incident_type = "healthy"
        severity = "healthy"

    return {
        "incident_detected": incident_type != "healthy",
        "incident_type": incident_type,
        "severity": severity,
        "summary": (
            f"{signals['service_name']} showing signs of {incident_type}"
            if incident_type != "healthy"
            else "No relevant incident detected"
        ),
    }


def plan_remediation(
    incident: dict[str, Any],
    signals: dict[str, Any],
    playbooks: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Choose the right playbook while respecting explicit policies."""
    incident_type = incident["incident_type"]

    if incident_type == "bad_release":
        playbook_id = "rollback_release"
    elif incident_type in {"latency_spike", "cpu_saturation"}:
        playbook_id = "scale_out_service"
    elif incident_type == "transient_error":
        playbook_id = "restart_workers"
    else:
        playbook_id = "open_incident_ticket"

    playbook = playbooks[playbook_id]
    return {
        "service_name": signals["service_name"],
        "incident_type": incident_type,
        "severity": incident["severity"],
        "playbook_id": playbook_id,
        "requires_human_approval": playbook["requires_human_approval"],
        "reasoning": playbook["description"],
        "steps": [
            "collect operational context",
            f"execute {playbook_id}",
            "record the result and evaluate effectiveness",
        ],
    }


def execute_playbook(
    plan: dict[str, Any],
    playbooks: dict[str, dict[str, Any]],
    auto_approve: bool = False,
    approved_by: str | None = None,
) -> dict[str, Any]:
    """Execute the playbook or signal that human approval is required."""
    playbook = playbooks[plan["playbook_id"]]
    approval_identity = approved_by or ("auto-approval-bot" if auto_approve else None)

    if playbook["requires_human_approval"] and approval_identity is None:
        return {
            "status": "pending_approval",
            "playbook_id": plan["playbook_id"],
            "service_name": plan["service_name"],
            "message": "High-impact action blocked until human approval is granted.",
        }

    return {
        "status": "executed",
        "playbook_id": plan["playbook_id"],
        "service_name": plan["service_name"],
        "approved_by": approval_identity,
        "message": playbook["description"],
        "executed_at": datetime.datetime.now(datetime.UTC).isoformat(),
    }


def run_remediation_flow(
    scenario: str,
    seed: int = 42,
    auto_approve: bool = False,
    approved_by: str | None = None,
) -> dict[str, Any]:
    """Run the full cycle: detect, plan, approve, and act."""
    playbooks = load_playbooks()
    signals = simulate_signals(scenario=scenario, seed=seed)
    incident = detect_incident(signals)
    plan = plan_remediation(incident, signals, playbooks)
    execution = execute_playbook(
        plan, playbooks, auto_approve=auto_approve, approved_by=approved_by
    )

    return {
        "signals": signals,
        "incident": incident,
        "plan": plan,
        "execution": execution,
    }


def save_report(path: str, report: dict[str, Any]) -> None:
    """Persist the result of the agentic execution."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic remediation for AI Ops")
    parser.add_argument(
        "--scenario",
        choices=["healthy", "latency_spike", "cpu_saturation", "transient_error", "bad_release"],
        default="bad_release",
        help="Synthetic operational scenario.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for reproducibility.")
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve actions that require human intervention.",
    )
    parser.add_argument(
        "--approved-by",
        type=str,
        default=None,
        help="Human identity responsible for approval.",
    )
    parser.add_argument(
        "--save-report",
        type=str,
        default=None,
        help="Optional path to persist the final result.",
    )
    args = parser.parse_args()

    report = run_remediation_flow(
        scenario=args.scenario,
        seed=args.seed,
        auto_approve=args.auto_approve,
        approved_by=args.approved_by,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.save_report:
        save_report(args.save_report, report)


if __name__ == "__main__":
    main()
