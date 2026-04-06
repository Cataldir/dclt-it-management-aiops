"""
Aula 02 – Ciclo de Desenvolvimento de IA: Pipeline ML com MLflow
=================================================================
Pipeline simplificado de Machine Learning para previsão de readmissão
hospitalar, com rastreamento de experimentos via MLflow.

Etapas cobertas:
  1. Preparação de dados
  2. Treinamento com rastreamento MLflow
  3. Validação (acurácia e F1-score)
  4. Registro do modelo (pronto para deploy)
"""

import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report


def gerar_dados_sinteticos(n_amostras: int = 500) -> pd.DataFrame:
    """Gera um dataset sintético de pacientes para demonstração."""
    import numpy as np

    rng = np.random.default_rng(42)
    dados = {
        "idade": rng.integers(18, 90, size=n_amostras),
        "tempo_internacao": rng.integers(1, 30, size=n_amostras),
        "num_comorbidades": rng.integers(0, 6, size=n_amostras),
        "num_medicamentos": rng.integers(1, 15, size=n_amostras),
    }
    df = pd.DataFrame(dados)
    # Probabilidade de readmissão cresce com idade, comorbidades e internação
    prob = (
        0.1
        + 0.005 * df["idade"]
        + 0.05 * df["num_comorbidades"]
        + 0.01 * df["tempo_internacao"]
    )
    prob = prob.clip(0, 1)
    df["readmitido"] = rng.binomial(1, prob)
    return df


def executar_pipeline(csv_path: str | None = None) -> None:
    """Executa o pipeline completo de ML com rastreamento MLflow."""

    # ── Etapa 1: Preparação de Dados ──
    if csv_path:
        df = pd.read_csv(csv_path)
    else:
        print("Usando dados sintéticos (arquivo CSV não fornecido).")
        df = gerar_dados_sinteticos()

    df = df.dropna(subset=["idade", "tempo_internacao", "num_comorbidades"])

    features = ["idade", "tempo_internacao", "num_comorbidades", "num_medicamentos"]
    X = df[features]
    y = df["readmitido"]  # 1 = readmitido em 30 dias, 0 = não

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── Etapa 2: Treinamento com rastreamento MLflow ──
    mlflow.set_experiment("readmissao_hospitalar")

    with mlflow.start_run(run_name="rf_baseline_v1"):
        params = {"n_estimators": 200, "max_depth": 10, "random_state": 42}
        mlflow.log_params(params)

        modelo = RandomForestClassifier(**params)
        modelo.fit(X_train, y_train)

        # ── Etapa 3: Validação ──
        y_pred = modelo.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        mlflow.log_metrics({"accuracy": acc, "f1_score": f1})
        print(classification_report(y_test, y_pred))

        # ── Etapa 4: Registro do modelo (pronto para deploy) ──
        mlflow.sklearn.log_model(modelo, artifact_path="modelo_readmissao")
        print(f"Modelo registrado | Accuracy: {acc:.3f} | F1: {f1:.3f}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Pipeline ML – Previsão de Readmissão Hospitalar"
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Caminho para o CSV de pacientes (opcional; gera dados sintéticos se omitido).",
    )
    args = parser.parse_args()
    executar_pipeline(csv_path=args.data)


if __name__ == "__main__":
    main()
