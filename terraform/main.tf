# Настройки для доступа к API Openstack в облаке провайдера VK задаются через переменные окружения, см. env-setup-example.sh

terraform {
    backend "http" {
    }
    required_providers {
        openstack = {
        source = "terraform-provider-openstack/openstack"
        version = "1.48.0"
        }
        mcs = {
            source = "MailRuCloudSolutions/mcs"
            version = "0.6.14"
        }
        vkcs = {
            source = "vk-cs/vkcs"
            version = "~> 0.1.0"
        }
        helm = {
            source = "hashicorp/helm"
            version = "2.7.0"
        }
        kubernetes = {
            source = "hashicorp/kubernetes"
            version = "2.13.1"
        }
    }
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

provider "kubernetes" {
    config_path = "~/.kube/config"
}