data "vkcs_compute_flavor" "postgresql" {
    name = var.postgresql_flavor
}

resource "vkcs_db_instance" "postgresql" {
  name        = "postgresql"

  datastore {
    type    = "postgresql"
    version = "13"
  }

  keypair     = openstack_compute_keypair_v2.terraform.id
  flavor_id   = data.vkcs_compute_flavor.postgresql.id
  size        = var.postgresql_disk_size
  volume_type = var.postgresql_disk_type
  disk_autoexpand {
    autoexpand    = false
    max_disk_size = 10
  }

  network {
    uuid = openstack_networking_network_v2.network.id
  }

  capabilities {
    name = "node_exporter"
    settings = {
      "listen_port" : "9100"
    }
  }
}

resource "vkcs_db_database" "db" {
  name          = var.postgresql_db_name
  dbms_id       = vkcs_db_instance.postgresql.id
  charset       = "utf8"
}

resource "vkcs_db_user" "user" {
  name        = var.postgresql_db_user
  password    = var.postgresql_db_pass

  dbms_id = vkcs_db_instance.postgresql.id

  databases   = vkcs_db_database.db[*].name
}