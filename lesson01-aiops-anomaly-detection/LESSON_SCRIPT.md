# Lesson 01 - Presentation Script

## Lesson Title

AIOps vs DevOps: how to move from static alerts to proactive incident detection.

## Learning Objective

By the end of this lesson, the class should understand three points:

1. Why DevOps alone does not solve the scale and speed of modern operational signals.
2. How a simple statistical detector already creates real value in AIOps.
3. How to turn telemetry into reusable operational decisions for later lessons.

## Business Problem

A fintech or digital platform does not want to discover an incident only after a customer complains. The value of this lesson is showing that latency, CPU, and error rate can be treated as early signs of service degradation.

## Lesson Application

Application demonstrated: local anomaly monitor with severity classification and operational recommendation.

Main file: `anomaly_detection.py`

## Application Build Sequence

### Build 1 - Generate synthetic telemetry

Goal: simulate the signals that would normally come from Prometheus, OpenTelemetry, or Azure Monitor.

### Build 2 - Detect anomalies with a statistical rule

Goal: compare the latest value against the historical baseline and classify deviations.

### Build 3 - Classify severity and recommend an action

Goal: turn the anomaly into operational context useful for an SRE, NOC, or support team.

### Build 4 - Prepare handoff for automation and agents

Goal: generate a JSON report that can be consumed by pipelines, workflows, or agents.

## Demo Commands

```bash
python anomaly_detection.py --scenario healthy
python anomaly_detection.py --scenario latency_spike --save-report artifacts/lesson01-latency.json
python anomaly_detection.py --scenario error_burst --save-report artifacts/lesson01-error.json
```

## Where To Apply This Knowledge

- IT operations with high alert volume.
- Critical APIs and services that need fast response.
- Automated triage and downstream remediation workflows.
