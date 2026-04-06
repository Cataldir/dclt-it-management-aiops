"""Simulate canary deployment for Lesson 07."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate model canary deployment")
    parser.add_argument("--strategy", type=str, required=True, help="Deployment strategy.")
    parser.add_argument("--weight", type=int, required=True, help="Canary traffic percentage.")
    parser.add_argument("--model", type=str, required=True, help="Deployed model.")
    parser.add_argument("--output", type=str, required=True, help="Deployment report.")
    args = parser.parse_args()

    report = {
        "strategy": args.strategy,
        "traffic_weight": args.weight,
        "model_path": args.model,
        "status": "deployed",
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()