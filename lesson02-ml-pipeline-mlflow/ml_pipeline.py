"""Lesson 02 mini-application for an ML pipeline with tracking and artifacts."""

from __future__ import annotations

import argparse
import json
import pickle
from contextlib import nullcontext
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

try:
    import mlflow
    import mlflow.sklearn
except ImportError:
    mlflow = None


def generate_synthetic_data(sample_count: int = 500, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic patient dataset for demonstration purposes."""
    import numpy as np

    rng = np.random.default_rng(seed)
    data = {
        "age": rng.integers(18, 90, size=sample_count),
        "length_of_stay": rng.integers(1, 30, size=sample_count),
        "num_comorbidities": rng.integers(0, 6, size=sample_count),
        "num_medications": rng.integers(1, 15, size=sample_count),
    }
    dataframe = pd.DataFrame(data)
    prob = (
        0.08
        + 0.005 * dataframe["age"]
        + 0.055 * dataframe["num_comorbidities"]
        + 0.012 * dataframe["length_of_stay"]
    ).clip(0, 1)
    dataframe["readmitted"] = rng.binomial(1, prob)
    return dataframe


def prepare_data(csv_path: str | None = None, seed: int = 42) -> pd.DataFrame:
    """Load or generate data and apply minimal validation."""
    if csv_path:
        dataframe = pd.read_csv(csv_path)
    else:
        dataframe = generate_synthetic_data(seed=seed)

    return dataframe.dropna(subset=["age", "length_of_stay", "num_comorbidities"])


def save_artifacts(
    artifacts_dir: Path,
    model: Any,
    metrics: dict[str, Any],
    features: list[str],
) -> None:
    """Save the local artifacts produced by the pipeline."""
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    model_path = artifacts_dir / "model.pkl"
    metrics_path = artifacts_dir / "metrics.json"
    model_card_path = artifacts_dir / "model_card.md"

    with model_path.open("wb") as file_handle:
        pickle.dump(model, file_handle)

    metrics_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    model_card = f"""
# Model Card - Hospital Readmission

## Objective

Predict the probability of readmission within 30 days.

## Features

- {features[0]}
- {features[1]}
- {features[2]}
- {features[3]}

## Primary Metrics

- Accuracy: {metrics['accuracy']:.4f}
- F1-score: {metrics['f1_score']:.4f}
- Training size: {metrics['train_size']}
- Test size: {metrics['test_size']}

## Limitations

- Synthetic data; does not replace validation with real data.
- MLflow tracking is optional and depends on the local environment.
"""
    model_card_path.write_text(model_card, encoding="utf-8")


def load_model(model_path: str) -> RandomForestClassifier:
    """Load a previously trained model from a pickle file."""
    with Path(model_path).open("rb") as fh:
        model = pickle.load(fh)  # noqa: S301
    if not isinstance(model, RandomForestClassifier):
        raise TypeError(
            f"Expected RandomForestClassifier, got {type(model).__name__}"
        )
    return model


def parse_agent_review(review_path: str) -> dict[str, Any]:
    """Extract actionable hyperparameter overrides from an agent review JSON.

    Reads the assessment suggestions and maps known recommendation patterns
    to concrete sklearn parameter changes.
    """
    review = json.loads(Path(review_path).read_text(encoding="utf-8"))
    assessment = review.get("assessment", {})
    suggestions: list[str] = assessment.get("suggestions", [])
    joined = " ".join(s.lower() for s in suggestions)

    overrides: dict[str, Any] = {}

    if any(kw in joined for kw in ("class imbalance", "class weighting", "resampling")):
        overrides["class_weight"] = "balanced"

    if any(kw in joined for kw in ("gradient boosting", "stronger baseline")):
        overrides["algorithm"] = "gradient_boosting"

    if any(kw in joined for kw in ("tune hyperparameters", "hyperparameter")):
        overrides.setdefault("n_estimators", 400)
        overrides.setdefault("max_depth", 15)

    if "cross-validation" in joined or "k-fold" in joined:
        overrides["cv_folds"] = 5

    overrides["_review_decision"] = assessment.get("decision", "unknown")
    overrides["_review_summary"] = assessment.get("summary", "")
    return overrides


def run_pipeline(
    csv_path: str | None = None,
    artifacts_dir: str = "artifacts",
    seed: int = 42,
    model_path: str | None = None,
    agent_review_path: str | None = None,
) -> dict[str, Any]:
    """Run the full ML pipeline with optional MLflow tracking.

    Parameters
    ----------
    csv_path:
        Optional CSV with patient data.  Synthetic data is generated when omitted.
    artifacts_dir:
        Directory where training artifacts will be written.
    seed:
        Seed for reproducibility.
    model_path:
        Path to a previously trained model pickle.  When provided the model is
        loaded and fine-tuned (warm-start) instead of training from scratch.
    agent_review_path:
        Path to an agent review JSON (e.g. ``review-foundry.json``).  When
        provided the suggestions are parsed into hyperparameter overrides so
        the pipeline can be re-run incorporating agent feedback.
    """
    dataframe = prepare_data(csv_path=csv_path, seed=seed)

    features = ["age", "length_of_stay", "num_comorbidities", "num_medications"]
    target_column = "readmitted"
    feature_values = dataframe[features]
    y = dataframe[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        feature_values, y, test_size=0.2, random_state=seed, stratify=y
    )

    # --- resolve hyperparameter overrides from agent review ----------------
    review_overrides: dict[str, Any] = {}
    if agent_review_path:
        review_overrides = parse_agent_review(agent_review_path)

    use_gradient_boosting = review_overrides.pop("algorithm", None) == "gradient_boosting"
    cv_folds = review_overrides.pop("cv_folds", None)
    review_decision = review_overrides.pop("_review_decision", None)
    review_summary = review_overrides.pop("_review_summary", None)

    is_finetune = model_path is not None
    run_name = "rf_finetune_v1" if is_finetune else "rf_baseline_v1"

    if mlflow is not None:
        mlflow.set_experiment("hospital_readmission")
        run_context = mlflow.start_run(run_name=run_name)
    else:
        run_context = nullcontext()

    with run_context:
        params: dict[str, Any] = {
            "n_estimators": review_overrides.get("n_estimators", 200),
            "max_depth": review_overrides.get("max_depth", 10),
            "random_state": seed,
        }
        if review_overrides.get("class_weight"):
            params["class_weight"] = review_overrides["class_weight"]

        if use_gradient_boosting:
            from sklearn.ensemble import GradientBoostingClassifier

            gb_params = {
                k: v
                for k, v in params.items()
                if k != "class_weight"
            }
            model = GradientBoostingClassifier(**gb_params)
            model.fit(X_train, y_train)
        elif is_finetune:
            model = load_model(model_path)
            model.set_params(warm_start=True, **params)
            model.fit(X_train, y_train)
        else:
            model = RandomForestClassifier(**params)
            model.fit(X_train, y_train)

        # --- optional cross-validation ------------------------------------
        cv_scores: dict[str, Any] | None = None
        if cv_folds:
            from sklearn.model_selection import cross_val_score

            cv_acc = cross_val_score(
                model, feature_values, y, cv=cv_folds, scoring="accuracy"
            )
            cv_f1 = cross_val_score(
                model, feature_values, y, cv=cv_folds, scoring="f1"
            )
            cv_scores = {
                "cv_folds": cv_folds,
                "cv_accuracy_mean": round(float(cv_acc.mean()), 4),
                "cv_accuracy_std": round(float(cv_acc.std()), 4),
                "cv_f1_mean": round(float(cv_f1.mean()), 4),
                "cv_f1_std": round(float(cv_f1.std()), 4),
            }

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        metrics: dict[str, Any] = {
            "accuracy": round(float(accuracy), 4),
            "f1_score": round(float(f1), 4),
            "train_size": int(len(X_train)),
            "test_size": int(len(X_test)),
            "classification_report": report,
            "tracking_enabled": mlflow is not None,
            "is_finetune": is_finetune,
        }
        if cv_scores:
            metrics["cross_validation"] = cv_scores
        if review_decision:
            metrics["agent_review_decision"] = review_decision
            metrics["agent_review_summary"] = review_summary

        if mlflow is not None:
            mlflow.log_params(params)
            mlflow.log_metrics({"accuracy": accuracy, "f1_score": f1})
            if cv_scores:
                mlflow.log_metrics({
                    "cv_accuracy_mean": cv_scores["cv_accuracy_mean"],
                    "cv_f1_mean": cv_scores["cv_f1_mean"],
                })
            mlflow.sklearn.log_model(model, artifact_path="hospital_readmission_model")

        save_artifacts(Path(artifacts_dir), model, metrics, features)
        return metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ML Pipeline - Hospital Readmission Prediction"
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Optional CSV path. If omitted, synthetic data is generated.",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=str,
        default="artifacts",
        help="Directory where training artifacts will be written.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for reproducibility.")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to a trained model pickle to fine-tune instead of training from scratch.",
    )
    parser.add_argument(
        "--agent-review",
        type=str,
        default=None,
        help="Path to an agent review JSON whose suggestions drive hyperparameter overrides.",
    )
    args = parser.parse_args()

    result = run_pipeline(
        csv_path=args.data,
        artifacts_dir=args.artifacts_dir,
        seed=args.seed,
        model_path=args.model,
        agent_review_path=args.agent_review,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
