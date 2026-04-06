"""
Aula 08 – AI Ops na Prática: Detecção de Anomalias com Auto-Remediação
======================================================================
Script completo de detecção de anomalias inspirado em cenários reais
de AI Ops. Implementa o ciclo: monitorar → detectar → agir → registrar.

Simula coleta de métricas de infraestrutura e aplica detecção estatística
(regra dos 3 sigmas) para identificar valores anômalos, acionando
escalonamento horizontal automático quando necessário.
"""

from __future__ import annotations

import datetime
import json

import numpy as np

# ── Configuração ─────────────────────────────────────────────

SIGMA_THRESHOLD = 3          # limiar para regra dos 3 sigmas
SCALE_OUT_INSTANCES = 2      # instâncias adicionais em caso de anomalia
METRIC_WINDOW = 60           # janela de métricas (últimos N pontos)


# ── Simulação de métricas coletadas via Prometheus ───────────

def gerar_metricas_latencia(seed: int = 42) -> np.ndarray:
    """Gera série temporal de latências com baseline estável e anomalia."""
    rng = np.random.default_rng(seed)
    baseline = rng.normal(loc=0.32, scale=0.02, size=METRIC_WINDOW - 1)
    anomalia = np.array([0.89])
    return np.concatenate([baseline, anomalia])


# ── Detecção de anomalias ────────────────────────────────────

def detectar_anomalia(
    metricas: np.ndarray, sigma: int = SIGMA_THRESHOLD
) -> dict:
    """Detecta anomalias usando a regra estatística dos N-sigmas."""
    media = metricas.mean()
    desvio = metricas.std()
    limite_superior = media + sigma * desvio
    valor_atual = metricas[-1]
    anomalia = bool(valor_atual > limite_superior)

    return {
        "valor_atual": round(float(valor_atual), 4),
        "media": round(float(media), 4),
        "desvio_padrao": round(float(desvio), 4),
        "limite_superior": round(float(limite_superior), 4),
        "anomalia_detectada": anomalia,
    }


# ── Auto-remediação ─────────────────────────────────────────

def acionar_auto_remediacao(diagnostico: dict) -> dict:
    """Aciona escalonamento automático quando anomalia é confirmada."""
    acao = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "tipo_acao": "scale_out",
        "instancias_adicionais": SCALE_OUT_INSTANCES,
        "motivo": (
            f"Latência {diagnostico['valor_atual']}s excede limite "
            f"{diagnostico['limite_superior']}s"
        ),
        "status": "executado",
    }
    print(f"[REMEDIAÇÃO] Escalonando {SCALE_OUT_INSTANCES} instâncias...")
    return acao


# ── Pipeline principal ───────────────────────────────────────

def main() -> None:
    latencias = gerar_metricas_latencia()

    resultado = detectar_anomalia(latencias)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    if resultado["anomalia_detectada"]:
        print("\n⚠  ALERTA: Latência anômala detectada!")
        registro = acionar_auto_remediacao(resultado)
        print(json.dumps(registro, indent=2, ensure_ascii=False))
    else:
        print("\n✔  Métricas dentro do padrão esperado.")


if __name__ == "__main__":
    main()
