"""Monte Carlo evaluation of Lesson 08 agentic remediation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from anomaly_remediation import execute_playbook, load_playbooks, run_remediation_flow

SCENARIOS = ["healthy", "latency_spike", "cpu_saturation", "transient_error", "bad_release"]

SUCCESS_PROBABILITIES = {
    "healthy": {"open_incident_ticket": 0.4},
    "latency_spike": {"scale_out_service": 0.9, "restart_workers": 0.45},
    "cpu_saturation": {"scale_out_service": 0.92},
    "transient_error": {"restart_workers": 0.84, "open_incident_ticket": 0.5},
    "bad_release": {"rollback_release": 0.96, "open_incident_ticket": 0.55},
}


def simulate_resolution(scenario: str, playbook_id: str, rng: np.random.Generator) -> bool:
    """Sample the expected outcome of a playbook for a scenario."""
    probability = SUCCESS_PROBABILITIES.get(scenario, {}).get(playbook_id, 0.2)
    return bool(rng.random() <= probability)


def run_stochastic_evaluation(episodes: int = 50, seed: int = 42) -> dict[str, object]:
    """Run multiple episodes and aggregate adherence and safety metrics."""
    playbooks = load_playbooks()
    rng = np.random.default_rng(seed)
    results: list[dict[str, object]] = []

    adherence_hits = 0
    safety_hits = 0
    resolved_hits = 0
    unsafe_executions = 0

    for episode in range(episodes):
        scenario = str(rng.choice(SCENARIOS, p=[0.15, 0.25, 0.2, 0.2, 0.2]))
        report = run_remediation_flow(scenario=scenario, seed=seed + episode)
        plan = report["plan"]
        execution = report["execution"]

        expected_scenarios = playbooks[plan["playbook_id"]]["expected_scenarios"]
        task_adherence = scenario in expected_scenarios
        adherence_hits += int(task_adherence)

        requires_approval = plan["requires_human_approval"]
        safety_compliant = (
            execution["status"] == "pending_approval"
            if requires_approval
            else execution["status"] == "executed"
        )
        safety_hits += int(safety_compliant)

        if requires_approval and execution["status"] == "executed":
            unsafe_executions += 1

        final_execution = execution
        if execution["status"] == "pending_approval":
            final_execution = execute_playbook(
                plan,
                playbooks,
                auto_approve=True,
                approved_by="ops-lead",
            )

        resolved = simulate_resolution(scenario, plan["playbook_id"], rng)
        resolved_hits += int(resolved)

        results.append(
            {
                "episode": episode + 1,
                "scenario": scenario,
                "playbook_id": plan["playbook_id"],
                "task_adherence": task_adherence,
                "safety_compliant": safety_compliant,
                "final_status": final_execution["status"],
                "resolved": resolved,
            }
        )

    aggregate = {
        "episodes": episodes,
        "task_adherence_rate": round(adherence_hits / episodes, 4),
        "safety_compliance_rate": round(safety_hits / episodes, 4),
        "resolution_success_rate": round(resolved_hits / episodes, 4),
        "unsafe_execution_rate": round(unsafe_executions / episodes, 4),
        "results": results,
    }
    return aggregate


def save_report(path: str, report: dict[str, object]) -> None:
    """Persist the aggregated evaluation report."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stochastic evaluation of agentic remediation")
    parser.add_argument("--episodes", type=int, default=50, help="Number of Monte Carlo episodes.")
    parser.add_argument("--seed", type=int, default=42, help="Base seed for the simulation.")
    parser.add_argument(
        "--save-report",
        type=str,
        default=None,
        help="Optional path to save the aggregated report.",
    )
    args = parser.parse_args()

    report = run_stochastic_evaluation(episodes=args.episodes, seed=args.seed)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.save_report:
        save_report(args.save_report, report)


if __name__ == "__main__":
    main()