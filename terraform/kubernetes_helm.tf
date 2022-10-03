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
    
    depends_on = [mcs_kubernetes_node_group.nodegroup]
}

resource "helm_release" "kube-prometheus-stack" {
    name       = "kube-prometheus-stack"
    repository = "https://prometheus-community.github.io/helm-charts"
    chart      = "kube-prometheus-stack"
    version    = "40.3.1"
    values = file("helm/kube-prometheus-stack.yml")

    depends_on = [mcs_kubernetes_node_group.nodegroup]
}