# file for the setup of the provider and the cluster
terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "2.23.0"
    }
  }
}

provider "kubernetes" {
  config_context  = "terraform-cluster"
  config_paths = ["~/.kube/config"]
}

