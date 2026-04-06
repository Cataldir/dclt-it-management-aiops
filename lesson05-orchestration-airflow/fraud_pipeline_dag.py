"""Lesson 05 mini-application for fraud orchestration with Airflow."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

PROJECT_ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
K8S_MANIFEST = PROJECT_ROOT / "k8s" / "canary-deploy.yaml"


def _preprocess() -> dict[str, object]:
    import preprocess

    return preprocess.run(
        input_path=str(ARTIFACTS_DIR / "raw_transactions.jsonl"),
        output_path=str(ARTIFACTS_DIR / "training_dataset.csv"),
    )


def _evaluate() -> dict[str, object]:
    import evaluate

    return evaluate.check_metrics(
        metrics_path=str(ARTIFACTS_DIR / "metrics.json"),
        fairness_path=str(ARTIFACTS_DIR / "fairness.json"),
    )


def _monitor() -> dict[str, object]:
    import monitor

    return monitor.watch(
        report_path=str(ARTIFACTS_DIR / "canary_report.json"),
        output_path=str(ARTIFACTS_DIR / "monitoring_decision.json"),
        minutes=60,
    )


default_args = {
    "owner": "mlops-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="fraud_model_pipeline",
    default_args=default_args,
    schedule="@weekly",
    start_date=days_ago(1),
    catchup=False,
    tags=["ml", "fraud", "betabank"],
) as dag:
    ingest = BashOperator(
        task_id="ingest_data",
        bash_command=(
            f'python "{(SCRIPTS_DIR / "ingest_transactions.py").as_posix()}" '
            f'--output "{(ARTIFACTS_DIR / "raw_transactions.jsonl").as_posix()}"'
        ),
    )

    preprocess = PythonOperator(
        task_id="preprocess_data",
        python_callable=_preprocess,
    )

    train = BashOperator(
        task_id="train_model",
        bash_command=(
            f'python "{(SCRIPTS_DIR / "train_fraud_model.py").as_posix()}" '
            f'--input "{(ARTIFACTS_DIR / "training_dataset.csv").as_posix()}" '
            f'--model-output "{(ARTIFACTS_DIR / "fraud_model.pkl").as_posix()}" '
            f'--metrics-output "{(ARTIFACTS_DIR / "metrics.json").as_posix()}" '
            f'--fairness-output "{(ARTIFACTS_DIR / "fairness.json").as_posix()}" '
            '--env dev'
        ),
    )

    evaluate = PythonOperator(
        task_id="evaluate_model",
        python_callable=_evaluate,
    )

    deploy_canary = BashOperator(
        task_id="deploy_canary",
        bash_command=(
            f'python "{(SCRIPTS_DIR / "deploy_canary.py").as_posix()}" '
            f'--model "{(ARTIFACTS_DIR / "fraud_model.pkl").as_posix()}" '
            f'--metrics "{(ARTIFACTS_DIR / "metrics.json").as_posix()}" '
            f'--manifest "{K8S_MANIFEST.as_posix()}" '
            f'--output "{(ARTIFACTS_DIR / "canary_report.json").as_posix()}"'
        ),
    )

    monitor = PythonOperator(
        task_id="monitor_canary",
        python_callable=_monitor,
    )

    rollout = BashOperator(
        task_id="full_rollout",
        bash_command=(
            f'python "{(SCRIPTS_DIR / "full_rollout.py").as_posix()}" '
            f'--monitor-report "{(ARTIFACTS_DIR / "monitoring_decision.json").as_posix()}" '
            f'--output "{(ARTIFACTS_DIR / "rollout_result.json").as_posix()}"'
        ),
    )

    ingest >> preprocess >> train >> evaluate >> deploy_canary >> monitor >> rollout
