"""Simulate a canary deployment for the fraud model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate a canary deployment")
    parser.add_argument("--model", type=str, required=True, help="Serialized model.")
    parser.add_argument("--metrics", type=str, required=True, help="Offline model metrics.")
    parser.add_argument("--manifest", type=str, required=True, help="Illustrative Kubernetes manifest.")
    parser.add_argument("--output", type=str, required=True, help="Output report.")
    parser.add_argument("--seed", type=int, default=42, help="Simulation seed.")
    args = parser.parse_args()

    offline_metrics = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    rng = np.random.default_rng(args.seed)

    report = {
        "model_path": args.model,
        "manifest_path": args.manifest,
        "traffic_weight": 0.1,
        "offline_accuracy": offline_metrics["accuracy"],
        "observed_accuracy": round(float(offline_metrics["accuracy"] - rng.uniform(0.0, 0.02)), 4),
        "canary_error_rate": round(float(rng.uniform(0.01, 0.04)), 4),
        "p95_latency_ms": int(rng.integers(180, 360)),
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()