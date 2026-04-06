"""Accuracy evaluation used by the Lesson 07 workflow."""

from __future__ import annotations

import argparse

from common import (
    evaluate_model_accuracy,
    load_model,
    load_or_create_dataset,
    write_json_artifact,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute the trained model accuracy")
    parser.add_argument("--model", type=str, required=True, help="Serialized model.")
    parser.add_argument("--data", type=str, default="data/features/latest.csv", help="Evaluation dataset.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for the reproducible split.")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to persist the accuracy report.",
    )
    args = parser.parse_args()

    dataset = load_or_create_dataset(args.data, seed=args.seed)
    model = load_model(args.model)
    accuracy = evaluate_model_accuracy(model, dataset, seed=args.seed)

    if args.output:
        write_json_artifact(
            args.output,
            {
                "model_path": args.model,
                "data_path": args.data,
                "accuracy": round(accuracy, 4),
                "seed": args.seed,
            },
        )

    print(f"{accuracy:.4f}")


if __name__ == "__main__":
    main()