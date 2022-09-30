# Создаём ключ из локального публичного ключа, для удобства разработки без пайплайна
resource "openstack_compute_keypair_v2" "terraform" {
    name       = "terraform-${basename(abspath("../${path.module}"))}"
    public_key = file(pathexpand("~/.ssh/id_rsa.pub"))
}