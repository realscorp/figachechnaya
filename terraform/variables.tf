# Настройки сети
variable "subnet_cidr" {
    type = string
}
###########################
# Настройки инстанса DBaaS
variable "postgresql_flavor" {
    type = string
}
variable "postgresql_disk_size" {
    type = number
}
variable "postgresql_disk_type" {
    type = string
}
##########################
# Эти значения будут браться из переменных окружения вида TF_VAR_varname
variable "postgresql_db_name" {
    type = string
}
variable "postgresql_db_user" {
    type = string
}
variable "postgresql_db_pass" {
    type = string
}
##########################
# Настройки кластера Кубернетес
variable "cluster_name" {
    type = string
}
variable "cluster_version" {
    type = string
}
variable "master_flavor" {
    type = string
}
variable "master_count" {
    type = number
}
variable "nodegroup_name" {
    type = string
}
variable "node_flavor" {
    type = string
}
variable "node_count" {
    type = number
}
variable "node_volume_size" {
    type = number
}
variable "node_volume_type" {
    type = string
}
variable "az" {
    type = string
}
variable "floating_ip_enabled" {
    type = bool
}