# Настройки для доступа к API Openstack в облаке провайдера VK задаются через переменные окружения, напр.
# export OS_AUTH_URL="https://infra.mail.ru:35357/v3/"
# export OS_PROJECT_ID="*****************"
# export OS_REGION_NAME="RegionOne"
# export OS_USER_DOMAIN_NAME="users"
# export OS_USERNAME=**************
# export OS_PASSWORD=**************

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
    }
}