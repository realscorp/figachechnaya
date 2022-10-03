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
    
    kubernetes {
        host = yamldecode(data.mcs_kubernetes_cluster.cluster.k8s_config).clusters[0].cluster.server
        cluster_ca_certificate = base64(yamldecode(data.mcs_kubernetes_cluster.cluster.k8s_config).clusters[0].cluster.certificate-authority-data)
        client_certificate = base64(yamldecode(data.mcs_kubernetes_cluster.cluster.k8s_config).users[0].user.client-certificate-data)
        client_key = base64(yamldecode(data.mcs_kubernetes_cluster.cluster.k8s_config).users[0].user.client-key-data)
    }
}