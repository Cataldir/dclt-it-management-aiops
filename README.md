# dclt-it-management-aiops

Código de suporte para a turma de DCLT na disciplina **IT Service Management and AI Ops** (FIAP POSTECH).

## Estrutura do Repositório

| Pasta | Aula | Tema | Tecnologias |
|-------|------|------|-------------|
| [`aula01-aiops-anomaly-detection`](aula01-aiops-anomaly-detection/) | 01 | AI Ops vs DevOps – Detecção de anomalias | Python, NumPy |
| [`aula02-ml-pipeline-mlflow`](aula02-ml-pipeline-mlflow/) | 02 | Ciclo de Desenvolvimento de IA – Pipeline ML | Python, MLflow, scikit-learn |
| [`aula03-infra-terraform`](aula03-infra-terraform/) | 03 | Infraestrutura de IA – Padrões Arquiteturais | Terraform, Azure (AKS + GPU) |
| [`aula04-model-validation`](aula04-model-validation/) | 04 | Versionamento e Validação em MLOps | Python, scikit-learn |
| [`aula05-orchestration-airflow`](aula05-orchestration-airflow/) | 05 | Orquestração de Modelos e Agentes | Python, Apache Airflow |
| [`aula06-mcp-tools`](aula06-mcp-tools/) | 06 | Ferramentas e Protocolos para Agentes (MCP) | Python, JSON Schema |
| [`aula07-cicd-ml-pipeline`](aula07-cicd-ml-pipeline/) | 07 | Integração e Governança de Pipelines | GitHub Actions, Terraform |
| [`aula08-aiops-practice`](aula08-aiops-practice/) | 08 | AI Ops na Prática – Projetos e Tendências | Python, NumPy |

## Como Usar

Cada pasta contém o código da respectiva aula com um `requirements.txt` (quando aplicável). Para executar:

```bash
cd aula01-aiops-anomaly-detection
pip install -r requirements.txt
python anomaly_detection.py
```

## Pré-requisitos

- Python 3.11+
- Terraform 1.5+ (para a Aula 03)
- Conta Azure (para provisionar infraestrutura da Aula 03)
- Apache Airflow 2.8+ (para a Aula 05)
