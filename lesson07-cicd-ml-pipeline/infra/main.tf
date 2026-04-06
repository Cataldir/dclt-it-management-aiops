terraform {
  required_version = ">= 1.5.0"
}

variable "model_version" {
  description = "Version of the model promoted by the pipeline."
  type        = string
}

resource "terraform_data" "model_release" {
  input = {
    model_version = var.model_version
  }
}

output "model_version" {
  value = terraform_data.model_release.input.model_version
}