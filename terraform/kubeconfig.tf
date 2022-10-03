resource "filesystem_file" "writer" {
  path    = file(pathexpand("~/.kube/config"))
  content = data.mcs_kubernetes_cluster.cluster.k8s_config
}