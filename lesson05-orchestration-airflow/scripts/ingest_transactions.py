"""Generate a synthetic batch of transactions for fraud training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def generate_transactions(samples: int = 600, seed: int = 42) -> list[dict[str, object]]:
    """Create synthetic transactions with simple fraud signals."""
    rng = np.random.default_rng(seed)
    countries = ["BR", "US", "AR", "CL"]
    segments = ["retail", "premium"]
    transactions: list[dict[str, object]] = []

    for _ in range(samples):
        amount = float(rng.normal(900, 700))
        velocity_1h = int(rng.integers(1, 12))
        device_risk = float(rng.uniform(0.05, 0.98))
        country = str(rng.choice(countries))
        home_country = "BR"
        hour = int(rng.integers(0, 24))
        historical_chargeback_ratio = float(rng.uniform(0.0, 0.4))
        customer_segment = str(rng.choice(segments, p=[0.75, 0.25]))

        fraud_score = (
            (amount > 2500) * 0.25
            + (velocity_1h > 6) * 0.2
            + device_risk * 0.35
            + (country != home_country) * 0.15
            + historical_chargeback_ratio * 0.3
        )
        is_fraud = int(fraud_score > 0.65)

        transactions.append(
            {
                "amount": round(max(amount, 5.0), 2),
                "velocity_1h": velocity_1h,
                "device_risk": round(device_risk, 4),
                "country": country,
                "home_country": home_country,
                "hour": hour,
                "historical_chargeback_ratio": round(historical_chargeback_ratio, 4),
                "customer_segment": customer_segment,
                "is_fraud": is_fraud,
            }
        )

    return transactions


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic transactions for training")
    parser.add_argument("--output", type=str, required=True, help="Output JSONL file.")
    parser.add_argument("--samples", type=int, default=600, help="Number of transactions.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for reproducibility.")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    transactions = generate_transactions(samples=args.samples, seed=args.seed)
    lines = [json.dumps(record, ensure_ascii=False) for record in transactions]
    output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()