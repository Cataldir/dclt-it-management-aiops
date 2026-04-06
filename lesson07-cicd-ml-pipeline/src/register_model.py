"""Local registry for models promoted by the Lesson 07 pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Register a promoted model")
    parser.add_argument("--path", type=str, required=True, help="Path of the promoted model.")
    parser.add_argument("--accuracy", type=float, required=True, help="Final accuracy.")
    parser.add_argument("--run-id", type=str, required=True, help="Workflow identifier.")
    parser.add_argument("--registry", type=str, required=True, help="Local registry JSONL file.")
    args = parser.parse_args()

    entry = {
        "model_path": args.path,
        "accuracy": round(args.accuracy, 4),
        "run_id": args.run_id,
        "status": "production_candidate",
    }

    registry_path = Path(args.registry)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with registry_path.open("a", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()