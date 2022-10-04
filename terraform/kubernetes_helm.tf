resource "helm_release" "certmanager" {
    name       = "certmanager"
    repository = "https://charts.jetstack.io"
    chart      = "cert-manager"
    version    = "v1.9.1"
    namespace = "cert-manager"
    create_namespace    = true

    set {
        name  = "installCRDs"
        value = "true"
    }
    
    # Я пока не нашёл способа сделать implicit dependency на состояние кластера, поэтому более грязный способ
    depends_on = [mcs_kubernetes_node_group.nodegroup]
}

resource "helm_release" "kube-prometheus-stack" {
    name       = "kube-prometheus-stack"
    repository = "https://prometheus-community.github.io/helm-charts"
    chart      = "kube-prometheus-stack"
    version    = "40.3.1"
    values     = [file("helm/prometheus-stack.yml")]

    # Забираем настоящие пароли из CI/CD-переменных
    set {
        name  = "alertmanager.extraSecret.data.auth"
        # в переменных пароль закодирован в base64, иначе Gitlab отказывается его маскировать, т.к. после bcrypt полно спецсимволов
        value = "admin:${base64decode(var.alertmanager_admin_password)}"
    }
    set {
        name  = "prometheus.extraSecret.data.auth"
        value = "admin:${base64decode(var.prometheus_admin_password)}"
    }
    set {
        name  = "grafana.adminPassword"
        value = var.grafana_admin_password
    }
    # Я пока не нашёл способа сделать implicit dependency на состояние кластера, поэтому более грязный способ
    depends_on = [mcs_kubernetes_node_group.nodegroup]
}