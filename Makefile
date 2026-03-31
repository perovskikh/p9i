# p9i Makefile - Automation for Docker, K3s, and deployment
# Usage: make <target>

# Configuration
REGISTRY ?= localhost:5000
IMAGE_NAME ?= p9i
IMAGE_TAG ?= k8s
FULL_IMAGE ?= $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
K8S_DIR := $(shell pwd)/k8s
NAMESPACE ?= p9i
HELM_CHART := $(shell pwd)/helm/p9i

# Kubernetes command (use sudo k3s kubectl on K3s)
Kubectl ?= kubectl
KUBECTL := $(shell (sudo -n kubectl --help >/dev/null 2>&1 && echo "sudo kubectl") || echo "kubectl")

# Colors
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m

# Default target
.DEFAULT_GOAL := help

# =============================================================================
# HELP
# =============================================================================
.PHONY: help
help:
	@echo ""
	@echo "$(BLUE)p9i - AI Prompt System Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Docker targets:$(NC)"
	@echo "  make build              Build Docker image"
	@echo "  make build-push         Build and push to local registry"
	@echo "  make run                Run container locally (stdio mode)"
	@echo "  make start              Build and run"
	@echo "  make stop               Stop running container"
	@echo "  make logs               View container logs"
	@echo "  make shell              Shell into running container"
	@echo ""
	@echo "$(GREEN)Docker Compose targets:$(NC)"
	@echo "  make compose-up         Start all services (db, redis, mcp-server)"
	@echo "  make compose-down       Stop all services"
	@echo "  make compose-logs        View logs from all services"
	@echo "  make compose-restart    Restart all services"
	@echo "  make compose-clean      Remove containers, volumes, networks"
	@echo ""
	@echo "$(GREEN)K3s/Kubernetes targets:$(NC)"
	@echo "  make k3s-install        Install K3s single node"
	@echo "  make k3s-install-server Install K3s server (cluster)"
	@echo "  make k3s-install-agent  Install K3s agent (worker)"
	@echo "  make k3s-uninstall      Uninstall K3s"
	@echo "  make k3s-deploy         Deploy to K3s"
	@echo "  make k3s-delete         Delete from K3s"
	@echo "  make k3s-logs           View K3s pod logs"
	@echo "  make k3s-restart        Restart K3s deployment"
	@echo "  make k3s-status         Check K3s deployment status"
	@echo "  make k3s-status-nodes   Show K3s nodes"
	@echo "  make k3s-port-forward   Port forward to K3s service"
	@echo ""
	@echo "$(GREEN)Helm targets:$(NC)"
	@echo "  make helm-install       Install Helm chart"
	@echo "  make helm-upgrade       Upgrade Helm release"
	@echo "  make helm-uninstall     Uninstall Helm release"
	@echo "  make helm-template      Render Helm template"
	@echo "  make helm-values        Show current Helm values"
	@echo ""
	@echo "$(GREEN)Backup/Restore targets:$(NC)"
	@echo "  make backup             Backup PostgreSQL + Redis"
	@echo "  make restore FILE=      Restore from backup file"
	@echo "  make backup-rotate      Rotate old backups (keep last 5)"
	@echo ""
	@echo "$(GREEN)Maintenance targets:$(NC)"
	@echo "  make lint               Run code linters"
	@echo "  make test               Run tests"
	@echo "  make clean              Clean build artifacts"
	@echo "  make prune             Docker prune (remove unused images)"
	@echo ""

# =============================================================================
# SIMPLE ALIASES - Quick access for daily development
# =============================================================================
dev: compose-up ## Start local development (Docker Compose)
	@echo "$(GREEN)Started in Docker Compose mode$(NC)"

deploy: k3s-deploy ## Deploy to K3s (kubectl apply -f k8s/)
	@echo "$(GREEN)Deployed to K3s$(NC)"

watch: ## Watch K3s logs (Ctrl+C to exit)
	sudo k3s kubectl logs -n $(NAMESPACE) -l app=mcp-server -f --tail=50

scale: ## Scale HPA (e.g., make scale REPLICAS=5)
	sudo k3s kubectl scale deployment/mcp-server -n $(NAMESPACE) --replicas=$(or $(REPLICAS),3)

hpa: ## Show HPA status
	sudo k3s kubectl get hpa -n $(NAMESPACE)

# =============================================================================
# CI/CD
# =============================================================================
.PHONY: ci-check
ci-check: ## Run CI checks locally (test + lint)
	@echo "$(YELLOW)Running tests...$(NC)"
	pytest --cov=src 2>/dev/null || echo "No tests found"
	@echo "$(YELLOW)Running linters...$(NC)"
	black --check src/ 2>/dev/null || echo "black not installed"
	ruff check src/ 2>/dev/null || echo "ruff not installed"
	@echo "$(GREEN)CI checks passed$(NC)"

status: k3s-status ## Check status (K3s)
	@echo "$(BLUE)=== K3s status ===$(NC)"

# =============================================================================
# DOCKER
# =============================================================================
.PHONY: build
build:
	@echo "$(YELLOW)Building p9i Docker image (no cache)...$(NC)"
	docker build --no-cache \
		-f docker/Dockerfile \
		-t $(IMAGE_NAME):latest \
		-t $(FULL_IMAGE) \
		.
	@echo "$(GREEN)Built: $(IMAGE_NAME):latest$(NC)"

.PHONY: build-push
build-push: build
	@echo "$(YELLOW)Pushing to local registry...$(NC)"
	docker tag $(IMAGE_NAME):latest $(FULL_IMAGE)
	docker push $(FULL_IMAGE)
	@echo "$(GREEN)Pushed: $(FULL_IMAGE)$(NC)"

.PHONY: run
run:
	@echo "$(YELLOW)Running p9i in stdio mode...$(NC)"
	MCP_TRANSPORT=stdio python -m src.api.server

.PHONY: start
start: build
	@echo "$(YELLOW)Starting p9i in stdio mode...$(NC)"
	MCP_TRANSPORT=stdio python -m src.api.server

.PHONY: stop
stop:
	@echo "$(YELLOW)Stopping p9i containers...$(NC)"
	docker stop $$(docker ps -q --filter "ancestor=$(IMAGE_NAME)") 2>/dev/null || true

.PHONY: logs
logs:
	docker logs -f $$(docker ps -q --filter "ancestor=$(IMAGE_NAME)" | head -1) 2>/dev/null || echo "No container running"

.PHONY: shell
shell:
	docker exec -it $$(docker ps -q --filter "ancestor=$(IMAGE_NAME)" | head -1) /bin/sh

# =============================================================================
# DOCKER COMPOSE
# =============================================================================
.PHONY: compose-up
compose-up:
	@echo "$(YELLOW)Starting all services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Services started. Check with: docker compose ps$(NC)"

.PHONY: compose-down
compose-down:
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker compose down

.PHONY: compose-logs
compose-logs:
	docker compose logs -f

.PHONY: compose-restart
compose-restart:
	docker compose restart

.PHONY: compose-clean
compose-clean:
	@echo "$(YELLOW)Cleaning up containers, volumes, networks...$(NC)"
	docker compose down -v --remove-orphans
	@echo "$(GREEN)Cleanup complete$(NC)"

# =============================================================================
# K3s/KUBERNETES
# =============================================================================

# K3s configuration
K3S_VERSION ?= v1.29.4+k3s1
K3S_CLUSTER_NAME ?= p9i-cluster

.PHONY: k3s-install
k3s-install: ## Install K3s single node
	@echo "$(YELLOW)Installing K3s $(K3S_VERSION)...$(NC)"
	curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=$(K3S_VERSION) sh -
	sudo chmod 644 /etc/rancher/k3s/k3s.yaml
	@echo "$(GREEN)K3s installed. Kubeconfig: ~/.kube/config$(NC)"

.PHONY: k3s-install-server
k3s-install-server: ## Install K3s server (first node in cluster)
	@echo "$(YELLOW)Installing K3s Server...$(NC)"
	curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=$(K3S_VERSION) \
		K3S_KUBECONFIG_MODE="644" \
		K3S_CLUSTER_SECRET="${CLUSTER_SECRET:-changeme}" \
		sh -s - server --cluster-init
	@echo "$(GREEN)K3s server installed$(NC)"

.PHONY: k3s-install-agent
k3s-install-agent: ## Install K3s agent (worker node)
	@if [ ! -f /var/lib/rancher/k3s/server/node-token ]; then \
		echo "$(RED)Token file not found. Run on server first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Installing K3s Agent...$(NC)"
	@read -p "Enter server IP: " SERVER_IP; \
	curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=$(K3S_VERSION) \
		K3S_URL="https://$$SERVER_IP:6443" \
		K3S_TOKEN="$$(cat /var/lib/rancher/k3s/server/node-token)" \
		sh -
	@echo "$(GREEN)K3s agent installed$(NC)"

.PHONY: k3s-uninstall
k3s-uninstall: ## Uninstall K3s
	@echo "$(YELLOW)Uninstalling K3s...$(NC)"
	@if command -v k3s-uninstall.sh &> /dev/null; then \
		sudo k3s-uninstall.sh; \
	elif command -v k3s-agent-uninstall.sh &> /dev/null; then \
		sudo k3s-agent-uninstall.sh; \
	else \
		echo "K3s uninstall scripts not found"; \
	fi
	@echo "$(GREEN)K3s uninstalled$(NC)"

.PHONY: k3s-status-nodes
k3s-status-nodes: ## Show K3s nodes status
	sudo k3s kubectl get nodes -o wide

.PHONY: k3s-deploy
k3s-deploy: build-push
	@echo "$(YELLOW)Deploying to K3s via Helm...$(NC)"
	sudo k3s kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | sudo k3s kubectl apply -f -
	helm upgrade --install p9i $(HELM_CHART) --namespace $(NAMESPACE) --create-namespace -f $(HELM_CHART)/values.yaml --wait --timeout 5m
	@echo "$(GREEN)Deployed to K3s namespace: $(NAMESPACE)$(NC)"

.PHONY: k3s-delete
k3s-delete:
	@echo "$(YELLOW)Deleting from K3s (Helm)...$(NC)"
	helm uninstall p9i --namespace $(NAMESPACE) 2>/dev/null || true
	sudo k3s kubectl delete namespace $(NAMESPACE) --ignore-not-found=true
	@echo "$(GREEN)Deleted from K3s$(NC)"

.PHONY: k3s-logs
k3s-logs:
	sudo k3s kubectl logs -n $(NAMESPACE) -l app=p9i-p9i -f --tail=100

.PHONY: k3s-restart
k3s-restart:
	sudo k3s kubectl rollout restart -n $(NAMESPACE) deployment/mcp-server
	@echo "$(GREEN)Restarted deployment$(NC)"

.PHONY: k3s-redeploy
k3s-redeploy: k3s-delete build-push k3s-deploy
	@echo "$(GREEN)Full redeploy complete!$(NC)"

.PHONY: k3s-status
k3s-status:
	@echo "$(BLUE)=== Namespace $(NAMESPACE) ===$(NC)"
	sudo k3s kubectl get all -n $(NAMESPACE)
	@echo ""
	@echo "$(BLUE)=== Endpoints ===$(NC)"
	sudo k3s kubectl get endpoints -n $(NAMESPACE)

.PHONY: k3s-port-forward
k3s-port-forward:
	@echo "$(YELLOW)Port forwarding to K3s service...$(NC)"
	@echo "MCP: localhost:8000 -> mcp-server:8000"
	sudo k3s kubectl port-forward -n $(NAMESPACE) svc/mcp-server 8000:8000 & \
	wait

.PHONY: k3s-describe
k3s-describe:
	sudo k3s kubectl describe all -n $(NAMESPACE)

.PHONY: k3s-events
k3s-events:
	sudo k3s kubectl get events -n $(NAMESPACE) --sort-by='.lastTimestamp'

# =============================================================================
# HELM
# =============================================================================
.PHONY: helm-install
helm-install: build-push
	@echo "$(YELLOW)Labeling namespace for Helm...$(NC)"
	@kubectl label namespace $(NAMESPACE) app.kubernetes.io/managed-by=Helm --overwrite 2>/dev/null || true
	@kubectl annotate namespace $(NAMESPACE) meta.helm.sh/release-name=p9i meta.helm.sh/release-namespace=$(NAMESPACE) --overwrite 2>/dev/null || true
	@echo "$(YELLOW)Installing Helm chart...$(NC)"
	helm install p9i $(HELM_CHART) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		--set image.repository=$(REGISTRY)/$(IMAGE_NAME) \
		--set image.tag=$(IMAGE_TAG) \
		--wait \
		--timeout 10m \
		--no-hooks
	@echo "$(GREEN)Helm installed: p9i$(NC)"

.PHONY: helm-upgrade
helm-upgrade: build-push
	@echo "$(YELLOW)Labeling resources for Helm...$(NC)"
	@for resource in $$(kubectl get all,secret,configmap -n $(NAMESPACE) -o name 2>/dev/null); do \
		kubectl label $$resource app.kubernetes.io/managed-by=Helm --overwrite -n $(NAMESPACE) 2>/dev/null || true; \
		kubectl annotate $$resource meta.helm.sh/release-name=p9i meta.helm.sh/release-namespace=$(NAMESPACE) --overwrite -n $(NAMESPACE) 2>/dev/null || true; \
	done
	@echo "$(YELLOW)Upgrading Helm release...$(NC)"
	helm upgrade p9i $(HELM_CHART) \
		--namespace $(NAMESPACE) \
		--set image.repository=$(REGISTRY)/$(IMAGE_NAME) \
		--set image.tag=$(IMAGE_TAG) \
		--wait \
		--timeout 10m \
		--no-hooks
	@echo "$(GREEN)Helm upgraded$(NC)"

.PHONY: helm-uninstall
helm-uninstall:
	@echo "$(YELLOW)Uninstalling Helm release...$(NC)"
	helm uninstall p9i --namespace $(NAMESPACE) || true
	sudo k3s kubectl delete namespace $(NAMESPACE) --ignore-not-found=true

.PHONY: helm-template
helm-template:
	helm template p9i $(HELM_CHART) --debug

.PHONY: helm-values
helm-values:
	@echo "$(BLUE)=== Default values ===$(NC)"
	@cat $(HELM_CHART)/values.yaml 2>/dev/null || echo "No values.yaml found"
	@echo ""
	@echo "$(BLUE)=== Installed values ===$(NC)"
	helm get values p9i -n $(NAMESPACE) 2>/dev/null || echo "Release not installed"

.PHONY: helm-list
helm-list:
	helm list -n $(NAMESPACE)

# =============================================================================
# BACKUP/RESTORE
# =============================================================================
BACKUP_DIR ?= ./backups
BACKUP_NAME := p9i-backup-$(shell date +%Y%m%d-%H%M%S)

.PHONY: backup
backup:
	@mkdir -p $(BACKUP_DIR)
	@echo "$(YELLOW)Creating backup: $(BACKUP_NAME)$(NC)"
	@echo "PostgreSQL..."
	@docker exec p9i-db-1 pg_dump -U postgres ai_prompts > $(BACKUP_DIR)/$(BACKUP_NAME).sql 2>/dev/null || \
		kubectl exec -n $(NAMESPACE) db-0 -- pg_dump -U postgres ai_prompts > $(BACKUP_DIR)/$(BACKUP_NAME).sql
	@echo "Memory..."
	@cp -r memory/p9i $(BACKUP_DIR)/$(BACKUP_NAME)-memory/ 2>/dev/null || true
	@echo "Env..."
	@cp .env $(BACKUP_DIR)/$(BACKUP_NAME).env 2>/dev/null || true
	@tar -czf $(BACKUP_DIR)/$(BACKUP_NAME).tar.gz $(BACKUP_NAME).sql $(BACKUP_NAME)-memory/ 2>/dev/null
	@rm -rf $(BACKUP_DIR)/$(BACKUP_NAME)*.sql $(BACKUP_DIR)/$(BACKUP_NAME)-memory 2>/dev/null
	@echo "$(GREEN)Backup saved: $(BACKUP_DIR)/$(BACKUP_NAME).tar.gz$(NC)"

.PHONY: restore
restore: $(FILE)
	@FILE=$(FILE); \
	echo "$(YELLOW)Restoring from: $$FILE$(NC)"; \
	tar -xzf $$FILE -C /tmp; \
	echo "Restoring PostgreSQL..."; \
	cat /tmp/*.sql | docker exec -i p9i-db-1 psql -U postgres ai_prompts 2>/dev/null || \
		kubectl exec -i -n $(NAMESPACE) db-0 -- psql -U postgres ai_prompts < /tmp/*.sql; \
	echo "$(GREEN)Restore complete$(NC)"

.PHONY: backup-rotate
backup-rotate:
	@echo "$(YELLOW)Rotating backups (keep last 5)...$(NC)"
	@ls -t $(BACKUP_DIR)/*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -f
	@echo "$(GREEN)Rotation complete$(NC)"

.PHONY: backup-list
backup-list:
	@ls -lh $(BACKUP_DIR)/*.tar.gz 2>/dev/null || echo "No backups found"

# =============================================================================
# MAINTENANCE
# =============================================================================
.PHONY: lint
lint:
	@echo "$(YELLOW)Running linters...$(NC)"
	@ruff check src/ 2>/dev/null || echo "Install ruff: pip install ruff"
	@black --check src/ 2>/dev/null || echo "Install black: pip install black"
	@mypy src/ 2>/dev/null || echo "Install mypy: pip install mypy"

.PHONY: test
test:
	@echo "$(YELLOW)Running tests...$(NC)"
	pytest -v

.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

.PHONY: prune
prune:
	@echo "$(YELLOW)Pruning Docker resources...$(NC)"
	docker system prune -af --volumes
	@echo "$(GREEN)Prune complete$(NC)"

.PHONY: info
info:
	@echo "$(BLUE)=== p9i Configuration ===$(NC)"
	@echo "Image:        $(IMAGE_NAME):latest"
	@echo "Full Image:   $(FULL_IMAGE)"
	@echo "Registry:     $(REGISTRY)"
	@echo "Namespace:    $(NAMESPACE)"
	@echo "K8s Dir:      $(K8S_DIR)"
	@echo "Helm Chart:   $(HELM_CHART)"
	@echo ""
	@echo "$(BLUE)=== Docker ===$(NC)"
	@docker ps --filter "name=p9i" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "$(BLUE)=== K3s ===$(NC)"
	@kubectl get nodes 2>/dev/null || echo "K3s not available"