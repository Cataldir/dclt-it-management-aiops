from __future__ import annotations

import pickle
import sys
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import FEATURE_COLUMNS, TARGET_COLUMN, generate_credit_data, load_or_create_dataset
from foundry_release_gate import build_release_context, run_local_release_policy


def test_generate_credit_data_has_expected_columns() -> None:
    dataframe = generate_credit_data(samples=64, seed=7)
    expected = set(FEATURE_COLUMNS + [TARGET_COLUMN, "segment"])
    assert expected.issubset(dataframe.columns)
    assert dataframe[TARGET_COLUMN].nunique() == 2


def test_load_or_create_dataset_creates_file(tmp_path: Path) -> None:
    dataset_path = tmp_path / "latest.csv"
    dataframe = load_or_create_dataset(str(dataset_path), seed=13)
    assert dataset_path.exists()
    assert len(dataframe) == 800


def test_local_release_gate_generates_approval_report(tmp_path: Path) -> None:
    dataset_path = tmp_path / "latest.csv"
    dataframe = load_or_create_dataset(str(dataset_path), seed=19)

    model = RandomForestClassifier(n_estimators=48, max_depth=6, random_state=19)
    model.fit(dataframe[FEATURE_COLUMNS], dataframe[TARGET_COLUMN])

    model_path = tmp_path / "credit_risk.pkl"
    with model_path.open("wb") as file_handle:
        pickle.dump(model, file_handle)

    context = build_release_context(
        model_path=str(model_path),
        data_path=str(dataset_path),
        accuracy_threshold=0.6,
        max_fairness_gap=0.5,
        deployment_strategy="canary",
        traffic_weight=10,
        seed=19,
    )
    assessment = run_local_release_policy(context)

    assert assessment["engine"] == "local-policy"
    assert assessment["decision"] == "approve"
    assert assessment["requires_human_approval"] is False