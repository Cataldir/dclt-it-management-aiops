"""Lesson 01 mini-application for telemetry anomaly detection."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

DEFAULT_WINDOW = 60


@dataclass(slots=True)
class MetricAnomaly:
    metric: str
    latest_value: float
    baseline_mean: float
    baseline_std: float
    upper_limit: float
    z_score: float
    severity: str


def generate_service_metrics(
    scenario: str, window: int = DEFAULT_WINDOW, seed: int = 42
) -> dict[str, np.ndarray]:
    """Generate a simple set of operational signals for the service."""
    rng = np.random.default_rng(seed)

    latency = rng.normal(loc=0.32, scale=0.02, size=window)
    error_rate = rng.normal(loc=0.012, scale=0.003, size=window)
    cpu_usage = rng.normal(loc=0.54, scale=0.07, size=window)

    if scenario == "latency_spike":
        latency[-1] = 0.91
        cpu_usage[-1] = 0.86
    elif scenario == "error_burst":
        latency[-1] = 0.66
        error_rate[-1] = 0.18
        cpu_usage[-1] = 0.73
    elif scenario == "cpu_saturation":
        latency[-1] = 0.72
        error_rate[-1] = 0.05
        cpu_usage[-1] = 0.97
    elif scenario != "healthy":
        raise ValueError(f"Unknown scenario: {scenario}")

    return {
        "latency_seconds": np.clip(latency, 0.05, None),
        "error_rate": np.clip(error_rate, 0.0, 1.0),
        "cpu_usage": np.clip(cpu_usage, 0.0, 1.0),
    }


def detect_signal(metric: str, series: np.ndarray, sigma: float = 3.0) -> MetricAnomaly | None:
    """Evaluate whether the latest point in a series is anomalous."""
    baseline = series[:-1]
    latest_value = float(series[-1])
    baseline_mean = float(baseline.mean())
    baseline_std = float(baseline.std())
    effective_std = baseline_std if baseline_std > 1e-8 else 1e-8
    upper_limit = baseline_mean + sigma * effective_std
    z_score = (latest_value - baseline_mean) / effective_std

    if latest_value <= upper_limit:
        return None

    if z_score >= 6:
        severity = "critical"
    elif z_score >= 4:
        severity = "high"
    else:
        severity = "medium"

    return MetricAnomaly(
        metric=metric,
        latest_value=round(latest_value, 4),
        baseline_mean=round(baseline_mean, 4),
        baseline_std=round(baseline_std, 4),
        upper_limit=round(upper_limit, 4),
        z_score=round(float(z_score), 4),
        severity=severity,
    )


def recommend_action(anomalies: list[MetricAnomaly]) -> tuple[str, bool]:
    """Return the recommended initial action for the current incident."""
    metrics = {anomaly.metric for anomaly in anomalies}

    if "error_rate" in metrics:
        return "investigate_recent_change_or_rollback", True
    if "cpu_usage" in metrics or "latency_seconds" in metrics:
        return "scale_out_service", False
    return "open_incident_for_manual_triage", True


def create_report(
    scenario: str, metric_series: dict[str, np.ndarray], sigma: float
) -> dict[str, object]:
    """Generate an operational report for the observed incident."""
    anomalies = [
        anomaly
        for metric, series in metric_series.items()
        if (anomaly := detect_signal(metric, series, sigma=sigma)) is not None
    ]

    action, requires_approval = recommend_action(anomalies)
    severity_rank = {"healthy": 0, "medium": 1, "high": 2, "critical": 3}
    incident_severity = "healthy"
    if anomalies:
        incident_severity = max(anomalies, key=lambda item: severity_rank[item.severity]).severity

    return {
        "scenario": scenario,
        "sigma_threshold": sigma,
        "signals": {
            metric: {
                "current": round(float(series[-1]), 4),
                "baseline_mean": round(float(series[:-1].mean()), 4),
            }
            for metric, series in metric_series.items()
        },
        "incident_detected": bool(anomalies),
        "incident_severity": incident_severity,
        "recommended_action": action,
        "requires_human_approval": requires_approval,
        "anomalies": [asdict(anomaly) for anomaly in anomalies],
    }


def save_report(path: str, report: dict[str, object]) -> None:
    """Persist a JSON report for use in later lessons."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local anomaly monitor for AIOps")
    parser.add_argument(
        "--scenario",
        choices=["healthy", "latency_spike", "error_burst", "cpu_saturation"],
        default="latency_spike",
        help="Synthetic scenario used to generate telemetry.",
    )
    parser.add_argument("--sigma", type=float, default=3.0, help="Sensitivity threshold.")
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW, help="Metric window size.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for reproducibility.")
    parser.add_argument("--save-report", type=str, default=None, help="Optional path to save the report.")
    args = parser.parse_args()

    metrics = generate_service_metrics(args.scenario, window=args.window, seed=args.seed)
    report = create_report(args.scenario, metrics, sigma=args.sigma)

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.save_report:
        save_report(args.save_report, report)


if __name__ == "__main__":
    main()
