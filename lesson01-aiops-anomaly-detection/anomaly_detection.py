"""
Aula 01 – AI Ops vs DevOps: Detecção de Anomalia de Latência
=============================================================
Demonstra o conceito central do AIOps: monitoramento proativo com
detecção estatística de anomalias usando a regra dos 3 sigmas.

Quando a latência mais recente excede o limite dinâmico
(média + 3×desvio-padrão), o sistema aciona automaticamente
o escalonamento de recursos.
"""

import numpy as np


def detectar_anomalia(latencias: np.ndarray, sigma: int = 3) -> dict:
    """Detecta anomalias de latência usando a regra dos N-sigmas.

    Args:
        latencias: Array com tempos de resposta recentes (em segundos).
        sigma: Multiplicador do desvio-padrão para definir o limite.

    Returns:
        Dicionário com estatísticas e indicação de anomalia.
    """
    media = latencias.mean()
    desvio = latencias.std()
    limite = media + sigma * desvio
    valor_atual = latencias[-1]
    anomalia = bool(valor_atual > limite)

    return {
        "valor_atual": round(float(valor_atual), 4),
        "media": round(float(media), 4),
        "desvio_padrao": round(float(desvio), 4),
        "limite_superior": round(float(limite), 4),
        "anomalia_detectada": anomalia,
    }


def acionar_escala_recursos(instancias_extra: int = 2) -> None:
    """Simula o escalonamento automático de recursos."""
    print(
        f"[REMEDIAÇÃO] Escalonando {instancias_extra} instâncias adicionais..."
    )


def main() -> None:
    # Tempos de resposta recentes (em segundos) – o último valor é anômalo
    rng = np.random.default_rng(42)
    baseline = rng.normal(loc=0.32, scale=0.02, size=59)  # 59 pontos normais
    latencias = np.append(baseline, 0.89)  # ponto anômalo no final

    resultado = detectar_anomalia(latencias)

    print("=== Diagnóstico de Latência ===")
    for chave, valor in resultado.items():
        print(f"  {chave}: {valor}")

    if resultado["anomalia_detectada"]:
        print("\n⚠  ALERTA: Latência anômala detectada!")
        acionar_escala_recursos(instancias_extra=2)
    else:
        print("\n✔  Métricas dentro do padrão esperado.")


if __name__ == "__main__":
    main()
