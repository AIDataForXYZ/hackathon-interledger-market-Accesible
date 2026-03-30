.PHONY: help init plan apply destroy ssh tmux tunnel logs status output fmt validate clean claude codex update-tools update-claude update-codex revert-claude revert-codex update-log push-makefile push-compose push-update-script push-all start stop

# Read from tfvars for gcloud commands
ZONE    := $(shell grep '^zone ' terraform.tfvars 2>/dev/null | sed 's/.*= *"\(.*\)"/\1/')
PROJECT := $(shell grep '^project_id ' terraform.tfvars 2>/dev/null | sed 's/.*= *"\(.*\)"/\1/')
ZONE    := $(or $(ZONE),southamerica-east1-a)
PROJECT := $(or $(PROJECT),voxvox-dev)
VM_NAME := voxvox-server
export CLOUDSDK_PYTHON_SITEPACKAGES := 1

_SSH_CMD = gcloud compute ssh $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap
_UPDATE_SCRIPT = /home/dev/vm-files/update-tools.sh

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# --- Terraform lifecycle ---

init: ## Initialize Terraform with GCS backend
	terraform init -backend-config="bucket=$(PROJECT)-terraform-state" -backend-config="prefix=terraform/state"

plan: ## Preview infrastructure changes
	terraform plan

apply: ## Create or update the dev VM
	terraform apply

destroy: ## Tear down all dev infrastructure
	terraform destroy

output: ## Show Terraform outputs
	terraform output

# --- Terraform utilities ---

fmt: ## Format .tf files
	terraform fmt -recursive

validate: ## Validate Terraform configuration
	terraform validate

# --- Remote VM access ---

ssh: ## SSH into the dev VM (as dev user)
	-gcloud compute ssh $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap \
		-- -tt "exec sudo -iu dev bash"

tmux: ## Attach to tmux session chooser on the VM
	-gcloud compute ssh $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap \
		-- -tt "exec sudo -iu dev bash -c 'tmux attach \\; choose-tree || tmux new-session \\; choose-tree'"

tunnel: ## Forward Django dev server to localhost:8000
	@echo "Forwarding localhost:8000 -> Django dev server"
	@echo "Press Ctrl+C to stop"
	-gcloud compute ssh $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap \
		-- -NL 8000:localhost:8000

logs: ## Tail the startup script log on the VM
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap \
		--command='sudo tail -f /var/log/voxvox-startup.log'

status: ## Check VM status and running containers
	@echo "--- VM instance ---"
	gcloud compute instances describe $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) \
		--format='table(name, status, networkInterfaces[0].accessConfigs[0].natIP, machineType.basename())' 2>/dev/null || echo "  VM not found (run 'make apply' first)"
	@echo ""
	@echo "--- Docker containers ---"
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap \
		--command='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"' 2>/dev/null || echo "  Could not reach VM"

# --- AI coding tools (use N=1, N=2, etc. for multiple sessions) ---

N :=
_CLAUDE_SESSION = claude$(if $(N),-$(N))
_CODEX_SESSION  = codex$(if $(N),-$(N))

claude: ## Launch Claude Code (N=1 for extra session)
	-gcloud compute ssh $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap \
		-- -tt "exec sudo -iu dev bash -c 'tmux new-session -As $(_CLAUDE_SESSION) -c ~/marketplace \"claude --dangerously-skip-permissions\"'"

codex: ## Launch Codex CLI (N=1 for extra session)
	-gcloud compute ssh $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap \
		-- -tt "exec sudo -iu dev bash -c 'tmux new-session -As $(_CODEX_SESSION) -c ~/marketplace \"codex --dangerously-bypass-approvals-and-sandbox\"'"

# --- Tool updates (Claude Code + Codex CLI) ---

VER :=

update-tools: ## Update both Claude Code and Codex CLI on the VM
	$(_SSH_CMD) --command='sudo $(_UPDATE_SCRIPT) all'

update-claude: ## Update only Claude Code on the VM
	$(_SSH_CMD) --command='sudo $(_UPDATE_SCRIPT) claude'

update-codex: ## Update only Codex CLI on the VM
	$(_SSH_CMD) --command='sudo $(_UPDATE_SCRIPT) codex'

revert-claude: ## Revert Claude to a specific version (VER=x.y.z)
	@[ -n "$(VER)" ] || { echo "Usage: make revert-claude VER=x.y.z"; exit 1; }
	$(_SSH_CMD) --command='sudo $(_UPDATE_SCRIPT) claude --revert $(VER)'

revert-codex: ## Revert Codex to a specific version (VER=x.y.z)
	@[ -n "$(VER)" ] || { echo "Usage: make revert-codex VER=x.y.z"; exit 1; }
	$(_SSH_CMD) --command='sudo $(_UPDATE_SCRIPT) codex --revert $(VER)'

update-log: ## Show tool update history from the VM
	$(_SSH_CMD) --command='sudo $(_UPDATE_SCRIPT) all --log'

# --- Push files to VM ---

push-makefile: ## Push templates/vm-Makefile to the VM
	gcloud compute scp templates/vm-Makefile $(VM_NAME):/tmp/vm-Makefile --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap
	$(_SSH_CMD) --command='sudo mv /tmp/vm-Makefile /home/dev/Makefile && sudo chown dev:dev /home/dev/Makefile'

push-compose: ## Push docker-compose.yml to the VM and recreate
	gcloud compute scp templates/docker-compose.yml $(VM_NAME):/tmp/docker-compose.yml --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap
	$(_SSH_CMD) --command='sudo mv /tmp/docker-compose.yml /home/dev/marketplace-deploy/docker-compose.yml && sudo chown dev:dev /home/dev/marketplace-deploy/docker-compose.yml && sudo -u dev bash -c "cd /home/dev/marketplace-deploy && docker compose up -d --force-recreate web"'

push-update-script: ## Push update-tools.sh to the VM
	gcloud compute scp vm-files/update-tools.sh $(VM_NAME):/tmp/update-tools.sh --zone=$(ZONE) --project=$(PROJECT) --tunnel-through-iap
	$(_SSH_CMD) --command='sudo mkdir -p /home/dev/vm-files && sudo mv /tmp/update-tools.sh /home/dev/vm-files/update-tools.sh && sudo chmod +x /home/dev/vm-files/update-tools.sh && sudo chown -R dev:dev /home/dev/vm-files'

push-all: push-makefile push-compose push-update-script ## Push all files to VM

# --- Lifecycle helpers ---

start: ## Start a stopped VM
	gcloud compute instances start $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT)

stop: ## Stop the VM (saves cost, keeps disk)
	gcloud compute instances stop $(VM_NAME) --zone=$(ZONE) --project=$(PROJECT)

# --- Cleanup ---

clean: ## Remove local Terraform state and cache
	rm -rf .terraform .terraform.lock.hcl
	@echo "Run 'make init' to re-initialize"
