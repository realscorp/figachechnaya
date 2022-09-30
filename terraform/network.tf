data "openstack_networking_network_v2" "ext-net" {
    name = "ext-net"
}
resource "openstack_networking_router_v2" "gateway" {
    name                = "gateway"
    admin_state_up      = true
    external_network_id = data.openstack_networking_network_v2.ext-net.id
}
resource "openstack_networking_network_v2" "network" {
    name = "network"
    admin_state_up = "true"
}
resource "openstack_networking_subnet_v2" "subnet" {
    name = "subnet"
    network_id = "${openstack_networking_network_v2.network.id}"
    cidr       = var.subnet_cidr
    ip_version = 4
    enable_dhcp = true
}
resource "openstack_networking_router_interface_v2" "router-interface" {
    router_id = "${openstack_networking_router_v2.gateway.id}"
    subnet_id = "${openstack_networking_subnet_v2.subnet.id}"
}