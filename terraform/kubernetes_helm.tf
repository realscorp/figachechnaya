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