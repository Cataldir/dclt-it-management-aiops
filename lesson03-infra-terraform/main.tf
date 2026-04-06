# ──────────────────────────────────────────────────────────────
# Lesson 03 - AI Infrastructure: Architectural Patterns and Terraform
# ──────────────────────────────────────────────────────────────
# Provisions a basic AI infrastructure stack on Azure:
#   - Resource Group with tags
#   - Virtual Network (VNet) with a private subnet for GPU workloads
#   - AKS cluster with a system node pool plus a GPU node pool
# ──────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}

# ── Variables ────────────────────────────────────────────────

variable "environment" {
  description = "Environment: dev, test, or prod"
  type        = string
  default     = "dev"
}

variable "gpu_node_count" {
  description = "Number of GPU nodes in the cluster"
  type        = number
  default     = 2
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus2"
}

# ── Resource Group ───────────────────────────────────────────

resource "azurerm_resource_group" "ai_rg" {
  name     = "rg-ai-platform-${var.environment}"
  location = var.location

  tags = {
    project     = "ai-platform"
    environment = var.environment
    managed_by  = "terraform"
  }
}

# ── Virtual Network (VNet) with private subnet for GPU ───────

resource "azurerm_virtual_network" "ai_vnet" {
  name                = "vnet-ai-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.ai_rg.location
  resource_group_name = azurerm_resource_group.ai_rg.name
}

resource "azurerm_subnet" "gpu_subnet" {
  name                 = "snet-gpu-training"
  resource_group_name  = azurerm_resource_group.ai_rg.name
  virtual_network_name = azurerm_virtual_network.ai_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# ── AKS cluster with GPU node pool for training ──────────────

resource "azurerm_kubernetes_cluster" "ai_cluster" {
  name                = "aks-ai-${var.environment}"
  location            = azurerm_resource_group.ai_rg.location
  resource_group_name = azurerm_resource_group.ai_rg.name
  dns_prefix          = "ai-${var.environment}"

  default_node_pool {
    name           = "system"
    node_count     = 2
    vm_size        = "Standard_D4s_v3"
    vnet_subnet_id = azurerm_subnet.gpu_subnet.id
  }

  identity {
    type = "SystemAssigned"
  }

  tags = azurerm_resource_group.ai_rg.tags
}

# ── Dedicated GPU node pool for model training ───────────────

resource "azurerm_kubernetes_cluster_node_pool" "gpu_pool" {
  name                  = "gpupool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.ai_cluster.id
  vm_size               = "Standard_NC6s_v3" # NVIDIA V100 GPU
  node_count            = var.gpu_node_count
  vnet_subnet_id        = azurerm_subnet.gpu_subnet.id

  node_labels = {
    "workload" = "gpu-training"
  }

  node_taints = [
    "nvidia.com/gpu=true:NoSchedule"
  ]
}

# ── Outputs ──────────────────────────────────────────────────

output "resource_group_name" {
  value = azurerm_resource_group.ai_rg.name
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.ai_cluster.name
}

output "vnet_name" {
  value = azurerm_virtual_network.ai_vnet.name
}
