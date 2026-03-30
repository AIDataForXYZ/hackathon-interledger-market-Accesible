# --------------------------------------------------------------------------
# VoxVos Dev Environment — Outputs
# --------------------------------------------------------------------------

output "ssh_command" {
  description = "SSH into the dev VM via IAP tunnel"
  value       = "gcloud compute ssh voxvox-server --zone=${var.zone} --project=${var.project_id} --tunnel-through-iap"
}

output "tunnel_command" {
  description = "Forward Django dev server to localhost:8000"
  value       = "gcloud compute ssh voxvox-server --zone=${var.zone} --project=${var.project_id} --tunnel-through-iap -- -NL 8000:localhost:8000"
}

output "startup_log_command" {
  description = "Command to check startup script progress"
  value       = "gcloud compute ssh voxvox-server --zone=${var.zone} --project=${var.project_id} --tunnel-through-iap -- sudo tail -f /var/log/voxvox-startup.log"
}

output "tfstate_bucket" {
  description = "GCS bucket for Terraform remote state"
  value       = google_storage_bucket.tfstate.name
}

output "dev_info" {
  description = "Development environment paths and useful info"
  value       = <<-EOT
    After SSH:     sudo su - ${var.dev_username}   (switch to dev user with full env)
    Project repo:  ~/marketplace
    Django:        make dev-run  (runserver on :8000)
    Docker:        make up       (docker compose up)
    Claude:        make claude   (Claude Code in tmux)
    Codex:         make codex    (Codex CLI in tmux)
    Web UI:        make tunnel   (then open http://localhost:8000)
  EOT
}
