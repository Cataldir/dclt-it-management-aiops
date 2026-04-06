"""Execute full rollout after canary monitoring."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate full rollout")
    parser.add_argument("--monitor-report", type=str, required=True, help="Monitoring result file.")
    parser.add_argument("--output", type=str, required=True, help="Final rollout file.")
    args = parser.parse_args()

    report = json.loads(Path(args.monitor_report).read_text(encoding="utf-8"))
    if report["decision"] != "approved":
        raise SystemExit("Canary not approved. Full rollout blocked.")

    result = {
        "status": "completed",
        "message": "Full rollout approved after canary observation.",
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()