# Lesson 03 - AI Infrastructure with Terraform

## Overview

This module shows how to move from an improvised environment to a repeatable infrastructure baseline for AI workloads. The stack uses Terraform to declare networking, cluster resources, and specialized capacity in a reproducible way that is ready to integrate with pipelines.

## What You Will Practice

- Declarative provisioning of AI infrastructure.
- Separation of responsibilities between network, cluster, and GPU capacity.
- Use of variables to adapt the same code to multiple environments.
- Exposure of outputs for integration with later workflows.

## Technologies

- Terraform 1.5+
- AzureRM Provider
- Azure AKS

## Prerequisites

- Terraform 1.5+
- Optional Azure account to apply the real stack

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation and practical applications.
- `main.tf`: main stack.
- `terraform.tfvars.example`: example values.

## Quick Start

```bash
terraform init
copy terraform.tfvars.example terraform.tfvars
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Provisioned Resources

- Resource Group with governance tags.
- Virtual Network and private subnet.
- AKS cluster.
- Dedicated GPU node pool.

## Supporting Files

- See `LESSON_SCRIPT.md` for lesson delivery.
- See `docs/README.md` for architecture, use cases, and troubleshooting.

## Where To Apply This Knowledge

- Cloud training and inference platforms.
- Standardized environments for data squads.
- IaC baselines integrated with MLOps and CI/CD.

## Connection To The Track

- Lesson 07 reuses the same declarative infrastructure concept in governed deployment.
- Later lessons build on this foundation for workflows and remediation.
