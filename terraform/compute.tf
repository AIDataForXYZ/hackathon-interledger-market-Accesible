# --------------------------------------------------------------------------
# VoxVos Dev Environment — Compute (GCE Instance)
# --------------------------------------------------------------------------

resource "google_compute_instance" "server" {
  name         = "voxvox-server"
  machine_type = var.machine_type
  zone         = var.zone
  project      = google_project.voxvox.project_id

  tags = ["voxvox-server"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = var.boot_disk_size_gb
      type  = "pd-balanced"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnet.id
    # No external IP — access via IAP tunnel only
  }

  service_account {
    email  = google_service_account.vm.email
    scopes = ["cloud-platform"]
  }

  metadata = {
    "vm-makefile"     = file("${path.module}/templates/vm-Makefile")
    "update-tools-sh" = file("${path.module}/vm-files/update-tools.sh")
    "docker-compose"  = file("${path.module}/templates/docker-compose.yml")
  }

  metadata_startup_script = templatefile("${path.module}/templates/startup.sh.tpl", {
    dev_username      = var.dev_username
    repo_url          = var.repo_url
    git_branch        = var.git_branch
    anthropic_api_key       = var.anthropic_api_key
    openai_api_key          = var.openai_api_key
    cloudflare_tunnel_token = var.cloudflare_tunnel_token
  })

  allow_stopping_for_update = true

  lifecycle {
    ignore_changes = [metadata, metadata_startup_script]
  }

  depends_on = [
    google_project_iam_member.vm_roles,
  ]
}
