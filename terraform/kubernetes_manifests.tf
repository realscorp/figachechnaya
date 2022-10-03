# Деплоим из yaml-файлов
##########################
resource "kubernetes_manifest" "ingress" {
    manifest = yamldecode(file("../kubernetes/manifests/ingress.yml"))
    depends_on = [mcs_kubernetes_node_group.nodegroup]
}
resource "kubernetes_manifest" "front" {
    manifest = yamldecode(file("../kubernetes/manifests/front.yml"))
    wait {
        condition {
            type   = "ContainersReady"
            status = "True"
        }
    }
    depends_on = [mcs_kubernetes_node_group.nodegroup]
}
resource "kubernetes_manifest" "figalize" {
    manifest = yamldecode(file("../kubernetes/manifests/figalize.yml"))
    wait {
        condition {
            type   = "ContainersReady"
            status = "True"
        }
    }
    depends_on = [mcs_kubernetes_node_group.nodegroup]
}
resource "kubernetes_manifest" "history" {
    manifest = yamldecode(file("../kubernetes/manifests/history.yml"))
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
            "db_login" = var.postgresql_db_login,
            "db_password" = var.postgresql_db_password
        }
    }
}