"""Simple fairness gate for the Lesson 07 workflow."""

from __future__ import annotations

import argparse

from common import load_model, load_or_create_dataset, measure_fairness_gap, write_json_artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the fairness gap across segments")
    parser.add_argument("--model", type=str, required=True, help="Serialized model.")
    parser.add_argument("--data", type=str, default="data/features/latest.csv", help="Evaluation dataset.")
    parser.add_argument("--max-gap", type=float, default=0.18, help="Maximum accepted gap.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for the reproducible split.")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to persist the fairness report.",
    )
    args = parser.parse_args()

    dataset = load_or_create_dataset(args.data, seed=args.seed)
    model = load_model(args.model)
    fairness = measure_fairness_gap(model, dataset, seed=args.seed)
    gap = float(fairness["fairness_gap"])

    report = {
        "model_path": args.model,
        "data_path": args.data,
        "seed": args.seed,
        "max_gap": args.max_gap,
        "fairness_gap": round(gap, 4),
        "recall_by_group": fairness["recall_by_group"],
        "status": "passed" if gap <= args.max_gap else "failed",
    }

    if args.output:
        write_json_artifact(args.output, report)

    if gap > args.max_gap:
        raise SystemExit(
            f"Fairness gap {gap:.4f} is above the limit {args.max_gap:.2f}."
        )

    print(f"fairness_gap={gap:.4f}")


if __name__ == "__main__":
    main()