# Деплоим из yaml-файлов
##########################
resource "kubernetes_manifest" "manifest" {
    for_each   = fileset(path.module, "../kubernetes/manifests/**/*.yml")
    manifest   = yamldecode(file(each.value))
    depends_on = [mcs_kubernetes_node_group.nodegroup]
}

# Создаём секрет для передачи в под History кредсов от БД
##########################
resource "kubernetes_manifest" "secrets" {
    manifest              = {
        "apiVersion"      = "v1"
        "kind"            = "Secret"
        "metadata"        = {
            "name"        = "history"
            "namespace"   = "default"
        }
        "type"            = "Opaque"
        "data"            = {
            # Эти значения мы получим из переменных окружения раннера
            "db_login"    = base64encode(var.postgresql_db_user,)
            "db_password" = base64encode(var.postgresql_db_pass)
        }
    }
}

resource "kubernetes_manifest" "secrets-imagizer" {
    manifest              = {
        "apiVersion"      = "v1"
        "kind"            = "Secret"
        "metadata"        = {
            "name"        = "imagizer"
            "namespace"   = "default"
        }
        "type"            = "Opaque"
        "data"            = {
            # Эти значения мы получим из переменных окружения раннера
            "s3_access_key"    = base64encode(var.s3_access_key,)
            "s3_secret_key" = base64encode(var.s3_secret_key)
        }
    }
}

# Создаём секрет для настройки Gitlab image registry
##########################
resource "kubernetes_manifest" "registry-secret" {
    manifest            = {
        "apiVersion"    = "v1"
        "kind"          = "Secret"
        "metadata"      = {
            "name"      = "registry-secret"
            "namespace" = "default"
        }
        "type" = "kubernetes.io/dockerconfigjson"
        "data" = {
            # Эти значения мы получим из переменных окружения раннера
            ".dockerconfigjson" = base64encode(
                templatefile(
                    "templates/registryconfig.tftpl",
                    {
                        registry_username=var.registry_username,
                        registry_password=var.registry_password,
                        registry_auth=base64encode("${var.registry_username}:${var.registry_password}")
                    }
                )
            )
        }
    }
}
