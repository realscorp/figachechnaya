# Настройки для доступа к API Openstack в облаке провайдера VK задаются через переменные окружения, см. env-setup-example.sh

terraform {
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
    }
}
