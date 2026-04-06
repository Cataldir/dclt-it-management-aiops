"""
Aula 04 – Versionamento e Validação em MLOps
=============================================
Validação automatizada de modelo candidato versus modelo em produção,
com verificações de acurácia (regressão) e fairness (disparidade entre grupos).

Esse tipo de gate é integrado a pipelines CI/CD para bloquear
automaticamente modelos que não atingem os limiares de qualidade.
"""

import numpy as np
from sklearn.metrics import accuracy_score, f1_score


def validar_modelo_candidato(
    y_true: np.ndarray,
    y_pred_prod: np.ndarray,
    y_pred_cand: np.ndarray,
    grupo: np.ndarray,
    limiar_queda: float = 0.02,
    limiar_fairness: float = 0.05,
) -> tuple[bool, str]:
    """Compara modelo candidato com o modelo em produção e verifica fairness.

    Args:
        y_true: Rótulos reais.
        y_pred_prod: Predições do modelo em produção.
        y_pred_cand: Predições do modelo candidato.
        grupo: Vetor indicando o grupo demográfico de cada amostra.
        limiar_queda: Queda máxima permitida em acurácia.
        limiar_fairness: Disparidade máxima de F1 entre grupos.

    Returns:
        Tupla (aprovado, mensagem).
    """
    acc_prod = accuracy_score(y_true, y_pred_prod)
    acc_cand = accuracy_score(y_true, y_pred_cand)
    f1_prod = f1_score(y_true, y_pred_prod, average="weighted")
    f1_cand = f1_score(y_true, y_pred_cand, average="weighted")

    # Gate 1 – Regressão de desempenho
    if acc_cand < acc_prod - limiar_queda:
        return False, f"REPROVADO: acurácia caiu de {acc_prod:.4f} para {acc_cand:.4f}"

    # Gate 2 – Fairness (diferença de F1 entre grupos)
    grupos_unicos = np.unique(grupo)
    f1_por_grupo: dict[str, float] = {}
    for g in grupos_unicos:
        mask = grupo == g
        f1_por_grupo[g] = f1_score(y_true[mask], y_pred_cand[mask], average="weighted")

    disparidade = max(f1_por_grupo.values()) - min(f1_por_grupo.values())
    if disparidade > limiar_fairness:
        return (
            False,
            f"REPROVADO: disparidade de F1 entre grupos = {disparidade:.4f}",
        )

    return (
        True,
        f"APROVADO: acc={acc_cand:.4f}, f1={f1_cand:.4f}, disparidade={disparidade:.4f}",
    )


def main() -> None:
    # Simulação de uso na pipeline CI/CD
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
    y_pred_prod = np.array([1, 0, 1, 0, 0, 1, 0, 0, 1, 1])
    y_pred_cand = np.array([1, 0, 1, 1, 0, 1, 1, 0, 1, 1])
    grupo = np.array(["A", "A", "B", "A", "B", "B", "A", "B", "A", "B"])

    aprovado, msg = validar_modelo_candidato(y_true, y_pred_prod, y_pred_cand, grupo)

    print("=== Validação de Modelo Candidato ===")
    print(f"  Resultado: {msg}")
    print(f"  Deploy autorizado: {aprovado}")


if __name__ == "__main__":
    main()
