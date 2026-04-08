# IT Service Management and AI Ops - FIAP Pos Tech

This repository contains the hands-on course material for **IT Service Management and AI Ops** in **FIAP Pos Tech**. Each module is structured as an independent learning unit, with its own README, lesson script, supporting documentation, and enough artifacts to demonstrate real AIOps, MLOps, IaC, orchestration, MCP, CI/CD, and AgentOps scenarios.

The structure was aligned with the course notes in `D:\Documentos\FIAP\AI Ops\Materiais Escritos` and standardized into a format closer to the `Cataldir/k8savancado` repository: independent modules, predictable navigation, and repeatable documentation structure.

[Sneak Peak on Shadow](https://youtu.be/qPFsmAWf2nc?si=vpOHqq4vewq5eNLL)

---

## About The Course

The course covers the evolution from traditional IT operations to AI pipelines and agent-assisted operations. The practical track goes from observability and anomaly detection to agentic remediation with guardrails and stochastic evaluation.

---

## Module Structure

### [Lesson 01 - AIOps Anomaly Detection](./lesson01-aiops-anomaly-detection/)
**Telemetry monitor with anomaly detection**

Hands-on observability and proactive detection demo with:
- synthetic operational signals
- incident and severity classification
- initial action recommendation

**Technologies**: Python, NumPy

### [Lesson 02 - ML Pipeline MLflow](./lesson02-ml-pipeline-mlflow/)
**ML pipeline with artifacts and tracking**

Machine learning pipeline lab with:
- data preparation
- reproducible training
- persisted metrics
- model card and optional tracking
- agent-backed experiment review

**Technologies**: Python, pandas, scikit-learn, MLflow, Azure AI Foundry

### [Lesson 03 - Terraform Infrastructure](./lesson03-infra-terraform/)
**AI infrastructure as code**

Infrastructure baseline for AI workloads with:
- Resource Group and governance
- private network
- AKS
- GPU node pool
- agent-backed Terraform plan review

**Technologies**: Terraform, Azure, Python, Azure AI Foundry

### [Lesson 04 - Model Validation](./lesson04-model-validation/)
**Model promotion gate**

Candidate validation with:
- performance regression checks
- fairness by group
- structured pipeline decision
- agent-backed promotion review

**Technologies**: Python, NumPy, scikit-learn, Azure AI Foundry

### [Lesson 05 - Orchestration Airflow](./lesson05-orchestration-airflow/)
**Fraud workflow with canary deployment and rollout**

ML pipeline orchestration with:
- Airflow DAG
- ingestion and preprocessing
- validation
- canary deployment and monitoring
- agent-backed canary observation

**Technologies**: Python, Apache Airflow, Azure AI Foundry

### [Lesson 06 - MCP Tools](./lesson06-mcp-tools/)
**Operational tools for agents**

MCP server demonstrating:
- tool discovery
- structured execution
- remediation planning
- local auditing
- agent client orchestration loop

**Technologies**: Python, JSON-RPC, JSON Schema, MCP, Azure AI Foundry

### [Lesson 07 - CI/CD ML Pipeline](./lesson07-cicd-ml-pipeline/)
**Governed train, validate, and deploy pipeline**

CI/CD pipeline with:
- GitHub Actions workflow
- tests and fairness checks
- agentic gate with Azure AI Foundry
- Terraform during deployment
- artifact registration

**Technologies**: GitHub Actions, Python, Terraform, pytest, Azure AI Foundry

### [Lesson 08 - AIOps Practice](./lesson08-aiops-practice/)
**Agentic remediation with stochastic evaluation**

Operational capstone with:
- incident detection
- playbook selection
- human approval
- execution and Monte Carlo evaluation

**Technologies**: Python, NumPy, JSON, Azure AI Foundry

---

## Required Tools

### Minimum baseline

- Python 3.13
- `uv`
- Git

### Module-specific tools

- Terraform 1.5+ for Lessons 03 and 07
- Apache Airflow 2.8+ for Lesson 05
- Optional Azure account for real infrastructure deployment
- Optional Azure AI Foundry project to enable the real agentic gate in Lesson 07

---

## How To Use This Repository

Each module is **independent** and can be executed on its own. The standard structure of each module is:

```text
lessonXX-module/
├── README.md           # Quick guide for the module
├── LESSON_SCRIPT.md    # Lesson script / presentation guide
├── docs/README.md      # Supporting documentation
├── src/ or script.py   # Main source code
├── scripts/            # Helper scripts (when applicable)
├── k8s/ or infra/      # Manifests or IaC (when applicable)
└── tests/              # Automated tests (when applicable)
```

### General Execution Flow

1. Enter the lesson directory.
2. Read the module `README.md`.
3. Open `LESSON_SCRIPT.md` if you are using the material in class or in a presentation.
4. Read `docs/README.md` for architecture, usage, and troubleshooting details.
5. Run the quick-start flow for that module.

Each Python-based lesson now ships with its own `pyproject.toml` and can be prepared either with the root bootstrap script or by running `uv sync` inside the lesson directory.

Example:

```bash
uv python install 3.13
python bootstrap.py lesson01-aiops-anomaly-detection
cd lesson01-aiops-anomaly-detection
uv run python anomaly_detection.py --scenario latency_spike --save-report artifacts/report.json
```

To bootstrap every Python lesson from the repository root:

```bash
python bootstrap.py
```

---

## Recommended Study Order

1. Lesson 01 - observability and proactive detection foundations
2. Lesson 02 - ML pipeline and artifacts
3. Lesson 03 - infrastructure as code
4. Lesson 04 - promotion gates and fairness
5. Lesson 05 - workflow orchestration
6. Lesson 06 - agent tooling through MCP
7. Lesson 07 - governed CI/CD for models
8. Lesson 08 - agentic remediation and evaluation

---

## Common Troubleshooting

### Missing or outdated Python dependencies

```bash
cd lesson01-aiops-anomaly-detection
uv sync --python 3.13
```

### Terraform not initialized

```bash
terraform init
```

### Airflow not configured

If Airflow is not ready locally yet, run the Lesson 05 scripts individually before trying the full DAG.

### Model or gate does not run locally

Check whether `scikit-learn`, `pandas`, and `pytest` are installed in the active environment.

---

## License

This project is distributed under the MIT license.

## Contributions

This is an educational repository. Suggestions and improvements can be proposed through issues or pull requests.
