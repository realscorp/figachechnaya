# Деплоим из yaml-файлов
##########################
resource "kubernetes_manifest" "manifest" {
    for_each = fileset(path.module, "../kubernetes/manifests/**/*.yml")
    manifest = yamldecode(file(each.value))
    wait {
        condition {
            type   = "ContainersReady"
            status = "True"
        }
    }
    depends_on = [mcs_kubernetes_node_group.nodegroup]
}

# Создаём секрет для передачи в под History кредсов от БД
##########################
resource "kubernetes_manifest" "secrets" {
    manifest = {
        "apiVersion" = "v1"
        "kind"       = "Secret"
        "metadata" = {
            "name"      = "history"
            "namespace" = "default"
        }
        "type" = "Opaque"
        "data" = {
            # Эти значения мы получим из переменных окружения раннера
            "db_login" = base64encode(var.postgresql_db_user,)
            "db_password" = base64encode(var.postgresql_db_pass)
        }
    }
}