from __future__ import annotations

import argparse
import json

from agent_pipeline_common import CLI_MODE_CHOICES
from anomaly_remediation import run_remediation_flow, save_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agent-backed remediation pipeline for Lesson 08")
    parser.add_argument(
        "--scenario",
        choices=["healthy", "latency_spike", "cpu_saturation", "transient_error", "bad_release"],
        default="bad_release",
        help="Synthetic operational scenario.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for reproducibility.")
    parser.add_argument(
        "--mode",
        choices=CLI_MODE_CHOICES,
        default="auto",
        help="How to produce the remediation plan.",
    )
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
        "--enforce",
        action="store_true",
        help="Fail when the execution remains blocked waiting for approval.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to persist the final report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_remediation_flow(
        scenario=args.scenario,
        seed=args.seed,
        mode=args.mode,
        auto_approve=args.auto_approve,
        approved_by=args.approved_by,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.output:
        save_report(args.output, report)

    if args.enforce and report["execution"]["status"] != "executed":
        raise SystemExit("Remediation pipeline requires human approval before execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())