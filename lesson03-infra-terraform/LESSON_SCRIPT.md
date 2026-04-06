# Lesson 03 - Presentation Script

## Lesson Title

AI infrastructure as code: how to move from an improvised environment to a repeatable baseline for ML workloads.

## Learning Objective

By the end of this lesson, the class should understand:

1. Why AI projects need intentionally designed infrastructure, not just provisioned infrastructure.
2. How Terraform helps repeat environments predictably.
3. How to separate responsibilities across network, cluster, and specialized capacity.

## Lesson Application

Application demonstrated: Terraform stack for a basic AI platform on Azure with Resource Group, VNet, private subnet, AKS, and a GPU node pool.

Main file: `main.tf`

## Application Build Sequence

### Build 1 - Create the Resource Group with tags

### Build 2 - Define network and isolation

### Build 3 - Create the AKS cluster

### Build 4 - Add the GPU node pool

### Build 5 - Outputs and pipeline integration

## Demo Commands

```bash
terraform init
copy terraform.tfvars.example terraform.tfvars
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Where To Apply This Knowledge

- Cloud AI platforms.
- Governed environments for training and inference.
- IaC baselines for CI/CD and continuous operations.
