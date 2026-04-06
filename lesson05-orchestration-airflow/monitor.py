"""Canary monitoring for Lesson 05."""

from __future__ import annotations

import json
from pathlib import Path


def watch(report_path: str, output_path: str, minutes: int = 60) -> dict[str, object]:
    """Evaluate the canary outcome and decide on rollout."""
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    decision = "approved"
    reasons: list[str] = []

    if report["canary_error_rate"] > 0.05:
        decision = "rollback"
        reasons.append("Canary error rate is above 5%.")

    if report["observed_accuracy"] < report["offline_accuracy"] - 0.03:
        decision = "rollback"
        reasons.append("Accuracy drop is above the tolerated limit in real traffic.")

    if report["p95_latency_ms"] > 450:
        decision = "rollback"
        reasons.append("P95 latency is above the operational SLA.")

    result = {
        "observation_window_minutes": minutes,
        "decision": decision,
        "reasons": reasons or ["Canary stayed within the defined limits."],
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result