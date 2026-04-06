"""Preprocessing for the Lesson 05 fraud pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def run(input_path: str, output_path: str) -> dict[str, object]:
    """Convert raw transactions into a tabular training dataset."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    records = [json.loads(line) for line in input_file.read_text(encoding="utf-8").splitlines() if line]
    dataframe = pd.DataFrame(records)
    dataframe["is_high_amount"] = (dataframe["amount"] > 2500).astype(int)
    dataframe["night_transaction"] = dataframe["hour"].isin([0, 1, 2, 3, 4, 23]).astype(int)
    dataframe["cross_border"] = (dataframe["country"] != dataframe["home_country"]).astype(int)

    dataframe.to_csv(output_file, index=False)
    return {
        "rows": int(len(dataframe)),
        "output_path": str(output_file),
        "feature_columns": [
            "amount",
            "velocity_1h",
            "device_risk",
            "historical_chargeback_ratio",
            "is_high_amount",
            "night_transaction",
            "cross_border",
        ],
    }