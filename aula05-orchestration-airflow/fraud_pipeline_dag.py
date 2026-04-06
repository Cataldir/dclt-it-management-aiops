"""
Aula 05 – Orquestração de Modelos: DAG no Apache Airflow
=========================================================
Define uma DAG que automatiza o ciclo completo de retreinamento
e implantação de um modelo de detecção de fraude:

  ingestão → pré-processamento → treino → avaliação →
  deploy canário → monitoramento → rollout completo

Cada task corresponde a uma etapa do pipeline MLOps.
"""

from datetime import timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    "owner": "mlops-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="fraud_model_pipeline",
    default_args=default_args,
    schedule_interval="@weekly",
    start_date=days_ago(1),
    catchup=False,
    tags=["ml", "fraud", "betabank"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_data",
        bash_command="python scripts/ingest_transactions.py",
    )

    preprocess = PythonOperator(
        task_id="preprocess_data",
        python_callable=lambda: __import__("preprocess").run(),
    )

    train = BashOperator(
        task_id="train_model",
        bash_command="python scripts/train_fraud_model.py --env={{ var.value.ENV }}",
    )

    evaluate = PythonOperator(
        task_id="evaluate_model",
        python_callable=lambda: __import__("evaluate").check_metrics(),
    )

    deploy_canary = BashOperator(
        task_id="deploy_canary",
        bash_command="kubectl apply -f k8s/canary-deploy.yaml",
    )

    monitor = PythonOperator(
        task_id="monitor_canary",
        python_callable=lambda: __import__("monitor").watch(minutes=60),
    )

    rollout = BashOperator(
        task_id="full_rollout",
        bash_command="kubectl set image deploy/fraud-api fraud=fraud:v2",
    )

    # DAG: ingestão → pré-processamento → treino → avaliação → canário → monitoramento → rollout
    ingest >> preprocess >> train >> evaluate >> deploy_canary >> monitor >> rollout
