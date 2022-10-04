data "mcs_kubernetes_clustertemplate" "cluster_template" {
  version = var.cluster_version
}
data "openstack_compute_flavor_v2" "master_flavor_id" {
    name = var.master_flavor
}
data "openstack_compute_flavor_v2" "node_flavor_id" {
    name = var.node_flavor
}


resource "mcs_kubernetes_cluster" "cluster" {
    name                = var.cluster_name
    cluster_template_id = data.mcs_kubernetes_clustertemplate.cluster_template.id
    master_flavor       = data.openstack_compute_flavor_v2.master_flavor_id.id
    master_count        = var.master_count
    network_id          = openstack_networking_network_v2.network.id
    subnet_id           = openstack_networking_subnet_v2.subnet.id
    availability_zone   = var.az
    floating_ip_enabled = var.floating_ip_enabled
    keypair             = openstack_compute_keypair_v2.terraform.name # Не изменять
    labels = {
      ingress_controller="nginx"
      prometheus_monitoring=false
    }
}
resource "mcs_kubernetes_node_group" "nodegroup" {
    node_count          = var.node_count
    cluster_id          = mcs_kubernetes_cluster.cluster.id
    name                = var.nodegroup_name
    flavor_id           = data.openstack_compute_flavor_v2.node_flavor_id.id
    volume_size         = var.node_volume_size
    volume_type         = var.node_volume_type
}
data "mcs_kubernetes_cluster" "cluster" {
    cluster_id                = mcs_kubernetes_cluster.cluster.id
}
# output "k8s_config" {
#     value = data.mcs_kubernetes_cluster.cluster.k8s_config
# }
