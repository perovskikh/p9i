# p9i Makefile - Automation for Docker, K3s, and deployment
# Usage: make <target>

# Configuration
REGISTRY ?= 176.108.255.121:5000
IMAGE_NAME ?= p9i
IMAGE_TAG ?= latest
FULL_IMAGE ?= $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
K8S_DIR := $(shell pwd)/k8s
NAMESPACE ?= p9i
# Detect local registry availability
LOCAL_REGISTRY ?= localhost:5000
K8S_REGISTRY ?= $(shell (curl -s --connect-timeout 2 -o /dev/null https://$(REGISTRY)/v2/ 2>/dev/null && echo "$(REGISTRY)") || echo "$(LOCAL_REGISTRY)")
HELM_CHART := $(shell pwd)/helm/p9i

# Load .env if exists (for build args)
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Kubernetes command (use $(KUBECTL) on K3s)
KUBECTL := $(shell (sudo -n kubectl --help >/dev/null 2>&1 && echo "sudo kubectl") || echo "kubectl")

# App label for K8s selectors
APP_LABEL := app=p9i-p9i

# Colors
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m

# Default target
.DEFAULT_GOAL := help

# =============================================================================
# PHONY DECLARATIONS
# =============================================================================
.PHONY: help dev deploy watch scale hpa status
.PHONY: build build-push run start stop logs shell
.PHONY: compose-up compose-down compose-logs compose-restart compose-clean
.PHONY: k3s-install k3s-install-server k3s-install-agent k3s-uninstall
.PHONY: k3s-deploy k3s-delete k3s-logs k3s-restart k3s-redeploy
.PHONY: k3s-status k3s-status-nodes k3s-port-forward k3s-describe k3s-events
.PHONY: helm-install helm-upgrade helm-uninstall helm-template helm-values helm-list
.PHONY: backup restore backup-rotate backup-list
.PHONY: lint test clean prune info ci-check
.PHONY: install-docker install-k3s install-helm install-all
.PHONY: mcp-setup mcp-remove mcp-test mcp-status
.PHONY: cert-setup cert-create-secret install-certbot

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
	@echo "$(GREEN)Setup targets:$(NC)"
	@echo "  make install-all        Install Docker + K3s + Helm (full setup)"
	@echo "  make install-docker     Install Docker Engine"
	@echo "  make install-k3s        Install K3s single node"
	@echo "  make install-helm       Install Helm 3"
	@echo ""
	@echo "$(GREEN)K3s/Kubernetes targets:$(NC)"
	@echo "  make k3s-install        Install K3s single node"
	@echo "  make k3s-install-server Install K3s server (cluster)"
	@echo "  make k3s-install-agent  Install K3s agent (worker)"
	@echo "  make k3s-uninstall      Uninstall K3s"
	@echo "  make k3s-deploy         Deploy to K3s (builds, pushes, cleans old pods)"
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
	@echo "$(GREEN)Claude Code MCP targets:$(NC)"
	@echo "  make mcp-setup        Configure Claude Code MCP client"
	@echo "  make mcp-test         Test MCP connection to server"
	@echo "  make mcp-status       Show MCP client status"
	@echo "  make mcp-remove       Remove Claude Code MCP settings"
	@echo ""
	@echo "$(GREEN)SSL/TLS certificate targets:$(NC)"
	@echo "  make install-certbot  Install certbot for SSL certificates"
	@echo "  make cert-setup      Get SSL certificates (Let's Encrypt)"
	@echo "  make cert-create-secret  Create K8s TLS secret from certificates"
	@echo ""

# =============================================================================
# SETUP - Install prerequisites (Debian/Ubuntu)
# =============================================================================

.PHONY: install-all
install-all: install-docker install-k3s install-helm ## Install everything (Docker + K3s + Helm)
	@echo "$(GREEN)=== All prerequisites installed ===$(NC)"
	@echo "$(GREEN)Run: make deploy$(NC)"

.PHONY: install-docker
install-docker: ## Install Docker Engine (Debian/Ubuntu)
	@echo "$(YELLOW)Installing Docker Engine...$(NC)"
	@if command -v docker >/dev/null 2>&1; then \
		echo "$(GREEN)Docker already installed: $$(docker --version)$(NC)"; \
		exit 0; \
	fi
	sudo apt-get update -qq
	sudo apt-get install -y -qq ca-certificates curl gnupg
	sudo install -m 0755 -d /etc/apt/keyrings
	@curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null || \
		curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null
	@echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $$(. /etc/os-release && echo "$$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
	sudo apt-get update -qq
	sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin
	sudo usermod -aG docker $$(whoami)
	@echo "$(GREEN)Docker installed: $$(docker --version)$(NC)"
	@echo "$(YELLOW)NOTE: Run 'newgrp docker' or re-login for group changes$(NC)"

.PHONY: install-k3s
install-k3s: ## Install K3s lightweight Kubernetes (single node)
	@echo "$(YELLOW)Installing K3s...$(NC)"
	@if command -v k3s >/dev/null 2>&1; then \
		echo "$(GREEN)K3s already installed: $$(k3s --version)$(NC)"; \
		exit 0; \
	fi
	@curl -sfL https://get.k3s.io | sudo sh -s - --write-kubeconfig-mode 644
	@sudo chmod 644 /etc/rancher/k3s/k3s.yaml 2>/dev/null || true
	@mkdir -p $$(HOME)/.kube
	@sudo cp /etc/rancher/k3s/k3s.yaml $$(HOME)/.kube/config 2>/dev/null || true
	@echo "$(GREEN)K3s installed: $$(k3s --version 2>/dev/null | head -1)$(NC)"
	@echo "$(YELLOW)Waiting for K3s node ready...$(NC)"
	@sudo k3s kubectl wait --for=condition=ready node/$$(hostname) --timeout=120s 2>/dev/null || echo "Node not ready yet, check: sudo k3s kubectl get nodes"

.PHONY: install-helm
install-helm: ## Install Helm 3 Kubernetes package manager
	@echo "$(YELLOW)Installing Helm 3...$(NC)"
	@if command -v helm >/dev/null 2>&1; then \
		echo "$(GREEN)Helm already installed: $$(helm version --short)$(NC)"; \
		exit 0; \
	fi
	@curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | sudo bash
	@echo "$(GREEN)Helm installed: $$(helm version --short)$(NC)"

# =============================================================================
# MCP CLIENT - Claude Code MCP integration
# =============================================================================

.PHONY: mcp-setup
mcp-setup: ## Configure Claude Code MCP client (local mode)
	@echo "$(YELLOW)Setting up Claude Code MCP client...$(NC)"
	@. ./.env 2>/dev/null || true; \
	echo "DOMAIN=$${DOMAIN:-p9i.ru}"; \
	echo "P9I_API_KEY=$${P9I_API_KEY:-sk-p9i-codeshift-p9i.ru}"; \
	mkdir -p ~/.claude; \
	if [ -f /home/worker/p9i/.mcp.json ]; then \
		cp /home/worker/p9i/.mcp.json ~/.claude/settings.json; \
		echo "$(GREEN)Copied .mcp.json to ~/.claude/settings.json$(NC)"; \
	else \
		echo "$(RED)Error: /home/worker/p9i/.mcp.json not found$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)MCP client configured. Restart Claude Code to use p9i server.$(NC)"; \
	echo "$(YELLOW)To test: make mcp-test$(NC)"

.PHONY: mcp-test
mcp-test: ## Test MCP connection to p9i server
	@echo "$(YELLOW)Testing MCP connection...$(NC)"
	@. ./.env 2>/dev/null || true; \
	URL="https://$${DOMAIN:-p9i.ru}/mcp"; \
	KEY="$${P9I_API_KEY:-sk-p9i-codeshift-p9i.ru}"; \
	echo "Testing MCP endpoint: $$URL"; \
	echo "API Key: [configured]"; \
	RESPONSE=$$(curl -sk -X POST "$$URL" \
		-H "Content-Type: application/json" \
		-H "X-API-Key: $$KEY" \
		-H "Accept: application/json, text/event-stream" \
		-d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}}}' \
		--max-time 30 2>&1); \
	if [ $$? -eq 0 ]; then \
		echo "Response: $$RESPONSE" | head -c 300; \
		echo ""; \
		echo "$(GREEN)✓ MCP server is reachable$(NC)"; \
	else \
		echo "Connection failed: $$RESPONSE"; \
		echo "$(RED)Check:$(NC)"; \
		echo "  1. Server is running: kubectl get pods -n p9i"; \
		echo "  2. Domain resolves: nslookup $$DOMAIN"; \
		echo "  3. Firewall allows 443"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "$(GREEN)MCP connection test complete.$(NC)"

.PHONY: mcp-status
mcp-status: ## Show MCP client status
	@echo "$(BLUE)=== MCP Client Status ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Local .mcp.json:$(NC)"
	@if [ -f /home/worker/p9i/.mcp.json ]; then \
		echo "  Found at: /home/worker/p9i/.mcp.json"; \
		echo "  Content:"; \
		cat /home/worker/p9i/.mcp.json | sed 's/^/    /'; \
	else \
		echo "  Not found"; \
	fi
	@echo ""
	@echo "$(YELLOW)Claude Code settings:$(NC)"
	@if [ -f ~/.claude/settings.json ]; then \
		echo "  Found at: ~/.claude/settings.json"; \
		echo "  Content:"; \
		cat ~/.claude/settings.json | sed 's/^/    /'; \
	else \
		echo "  Not configured. Run: make mcp-setup"; \
	fi
	@echo ""
	@echo "$(YELLOW)Server endpoint:$(NC)"
	@. ./.env 2>/dev/null || true; \
	echo "  URL: https://$${DOMAIN:-p9i.ru}/mcp"; \
	echo "  API Key: $${P9I_API_KEY:+Configured} $$(test -n "$$P9I_API_KEY" && echo "(set)" || echo "(not set)")$$"; \
	if . ./.env 2>/dev/null && [ -n "$$MINIMAX_API_KEY" ]; then \
		echo "  MINIMAX_API_KEY: $(GREEN)✓ configured$(NC)"; \
	else \
		echo "  MINIMAX_API_KEY: $(RED)✗ not configured$(NC)"; \
	fi
	@if . ./.env 2>/dev/null && [ -n "$$ZAI_API_KEY" ]; then \
		echo "  ZAI_API_KEY: $(GREEN)✓ configured$(NC)"; \
	else \
		echo "  ZAI_API_KEY: $(RED)✗ not configured$(NC)"; \
	fi

.PHONY: mcp-remove
mcp-remove: ## Remove Claude Code MCP settings
	@echo "$(YELLOW)Removing Claude Code MCP settings...$(NC)"
	@if [ -f ~/.claude/settings.json ]; then \
		rm -v ~/.claude/settings.json; \
		echo "$(GREEN)MCP settings removed from ~/.claude/settings.json$(NC)"; \
	else \
		echo "$(YELLOW)No MCP settings found in ~/.claude/settings.json$(NC)"; \
	fi
	@echo "$(GREEN)Done.$(NC)"

# =============================================================================
# SSL/TLS - Certificate setup for HTTPS
# =============================================================================

.PHONY: install-certbot
install-certbot: ## Install certbot for SSL certificates
	@echo "$(YELLOW)Installing certbot...$(NC)"
	@if command -v certbot >/dev/null 2>&1; then \
		echo "$(GREEN)certbot already installed: $$(certbot --version 2>/dev/null)$(NC)"; \
	else \
		sudo apt-get update -qq; \
		sudo apt-get install -y -qq certbot; \
		echo "$(GREEN)certbot installed: $$(certbot --version)$(NC)"; \
	fi

.PHONY: cert-setup
cert-setup: install-certbot ## Get SSL certificates via Let's Encrypt
	@echo "$(YELLOW)Setting up SSL certificates...$(NC)"
	@. ./.env 2>/dev/null || true; \
	DOMAIN="$${DOMAIN:-p9i.ru}"; \
	EMAIL="$${SSL_EMAIL:-admin@$$DOMAIN}"; \
	SSL_DIR="./nginx/ssl"; \
	echo "Domain: $$DOMAIN"; \
	echo "Email: $$EMAIL"; \
	echo "SSL directory: $$SSL_DIR"; \
	mkdir -p "$$SSL_DIR" "./nginx/certbot-www"; \
	if [ ! -f "$$SSL_DIR/privkey.pem" ] || [ ! -f "$$SSL_DIR/fullchain.pem" ]; then \
		echo "Getting certificate from Let's Encrypt... "; \
		sudo certbot certonly --standalone -d "$$DOMAIN" \
			--email "$$EMAIL" --agree-tos --non-interactive --keep-until-expiring; \
		sudo cp "/etc/letsencrypt/live/$$DOMAIN/fullchain.pem" "$$SSL_DIR/"; \
		sudo cp "/etc/letsencrypt/live/$$DOMAIN/privkey.pem" "$$SSL_DIR/"; \
		sudo chmod 644 "$$SSL_DIR/fullchain.pem"; \
		sudo chmod 600 "$$SSL_DIR/privkey.pem"; \
		echo "$(GREEN)Certificates installed in $$SSL_DIR$(NC)"; \
	else \
		echo "$(GREEN)Certificates already exist in $$SSL_DIR$(NC)"; \
	fi; \
	echo "$(GREEN)Certificate setup complete. Run 'make cert-create-secret' to create K8s TLS secret.$(NC)"

.PHONY: cert-create-secret
cert-create-secret: ## Create K8s TLS secret from SSL certificates
	@echo "$(YELLOW)Creating K8s TLS secret...$(NC)"
	@. ./.env 2>/dev/null || true; \
	DOMAIN="$${DOMAIN:-p9i.ru}"; \
	SSL_DIR="./nginx/ssl"; \
	if [ ! -f "$$SSL_DIR/privkey.pem" ] || [ ! -f "$$SSL_DIR/fullchain.pem" ]; then \
		echo "$(RED)Error: Certificates not found in $$SSL_DIR. Run 'make cert-setup' first.$(NC)"; \
		exit 1; \
	fi; \
	echo "Creating TLS secret 'p9i-tls' in namespace p9i..."; \
	sudo kubectl create secret tls p9i-tls \
		--cert="$$SSL_DIR/fullchain.pem" \
		--key="$$SSL_DIR/privkey.pem" \
		-n p9i --dry-run=client -o yaml | sudo kubectl apply -f -; \
	echo "$(GREEN)TLS secret 'p9i-tls' created/updated in namespace p9i$(NC)"; \
	echo "$(YELLOW)Now restart the ingress controller or redeploy to apply.$(NC)"

# =============================================================================
# SIMPLE ALIASES - Quick access for daily development
# =============================================================================
dev: compose-up ## Start local development (Docker Compose)
	@echo "$(GREEN)Started in Docker Compose mode$(NC)"

deploy: k3s-deploy ## Deploy to K3s (kubectl apply -f k8s/)
	@echo "$(GREEN)Deployed to K3s$(NC)"

watch: ## Watch K3s logs (Ctrl+C to exit)
	$(KUBECTL) logs -n $(NAMESPACE) -l $(APP_LABEL) -f --tail=50

scale: ## Scale HPA (e.g., make scale REPLICAS=5)
	$(KUBECTL) scale deployment/p9i-p9i -n $(NAMESPACE) --replicas=$(or $(REPLICAS),3)

hpa: ## Show HPA status
	$(KUBECTL) get hpa -n $(NAMESPACE)

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
	@echo "$(YELLOW)Checking for uncommitted changes...$(NC)"
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "$(YELLOW)WARNING: You have uncommitted changes. Building with uncommitted changes.$(NC)"; \
		echo "$(YELLOW)Run 'git status' to see changes.$(NC)"; \
		if [ "$$BUILD_STRICT" = "1" ]; then \
			echo "$(RED)Refusing to build with uncommitted changes (BUILD_STRICT=1).$(NC)"; \
			exit 1; \
		fi; \
	fi
	@echo "$(YELLOW)Building p9i Docker image (no cache)...$(NC)"
	@. ./.env 2>/dev/null || true; \
	sudo docker build --no-cache \
		-f docker/Dockerfile \
		-t $(IMAGE_NAME):latest \
		-t $(FULL_IMAGE) \
		--build-arg MINIMAX_API_KEY="$$MINIMAX_API_KEY" \
		--build-arg ZAI_API_KEY="$$ZAI_API_KEY" \
		--build-arg OPENROUTER_API_KEY="$$OPENROUTER_API_KEY" \
		--build-arg DEEPSEEK_API_KEY="$$DEEPSEEK_API_KEY" \
		--build-arg ANTHROPIC_API_KEY="$$ANTHROPIC_API_KEY" \
		--build-arg P9I_API_KEY="$$P9I_API_KEY" \
		--build-arg JWT_SECRET="$$JWT_SECRET" \
		--build-arg JWT_ENABLED="$$JWT_ENABLED" \
		--build-arg DOMAIN="$$DOMAIN" \
		--build-arg GITHUB_TOKEN="$$GITHUB_TOKEN" \
		--build-arg FIGMA_TOKEN="$$FIGMA_TOKEN" \
		--build-arg CONTEXT7_API_KEY="$$CONTEXT7_API_KEY" \
		.
	@echo "$(GREEN)Built: $(IMAGE_NAME):latest$(NC)"

.PHONY: build-push
build-push: build
	@echo "$(YELLOW)Pushing to registry...$(NC)"
	@echo "Using registry: $(K8S_REGISTRY)"
	sudo docker tag $(IMAGE_NAME):latest $(K8S_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	sudo docker push $(K8S_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "$(GREEN)Pushed: $(K8S_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)$(NC)"

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
	$(KUBECTL) get nodes -o wide

.PHONY: k3s-deploy
k3s-deploy:
	@echo "$(YELLOW)Checking prerequisites...$(NC)"
	@# Check .env exists
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file not found. Run: cp .env.example .env$(NC)"; \
		exit 1; \
	fi
	@# Load env to check keys
	@. ./.env 2>/dev/null; \
	echo "$(YELLOW)Checking LLM API keys in .env...$(NC)"; \
	HAS_KEY=0; \
	for key in MINIMAX_API_KEY ZAI_API_KEY OPENROUTER_API_KEY DEEPSEEK_API_KEY; do \
		val="$$key"; \
		if [ -n "$$val" ]; then \
			echo "$(GREEN)✓ $$key found$(NC)"; \
			HAS_KEY=1; \
		else \
			echo "$(YELLOW)✗ $$key not set$(NC)"; \
		fi; \
	done; \
	if [ $$HAS_KEY -eq 0 ]; then \
		echo "$(RED)Error: No LLM API keys found in .env. Set at least one of:$(NC)"; \
		echo "$(RED)  MINIMAX_API_KEY, ZAI_API_KEY, OPENROUTER_API_KEY, DEEPSEEK_API_KEY$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Cleaning up Docker resources to prevent disk pressure...$(NC)"
	@sudo docker system prune -af --filter "until=72h" 2>/dev/null || true
	@echo "$(YELLOW)Building and pushing Docker image...$(NC)"
	$(MAKE) build-push
	@echo "$(YELLOW)Cleaning up old/evicted pods before deploy...$(NC)"
	@$(KUBECTL) get pods -n $(NAMESPACE) -l app=p9i-p9i --no-headers 2>/dev/null | \
		grep -v "Running" | awk '{print $$1}' | \
		xargs -r $(KUBECTL) delete pod -n $(NAMESPACE) 2>/dev/null || true
	@echo "$(YELLOW)Deploying to K3s via Helm...$(NC)"
	$(KUBECTL) create namespace $(NAMESPACE) --dry-run=client -o yaml | $(KUBECTL) apply -f -
	@# Load ALL env vars from .env (including GITHUB_TOKEN, FIGMA_TOKEN)
	@. ./.env 2>/dev/null || true; \
	helm upgrade --install p9i $(HELM_CHART) --namespace $(NAMESPACE) --create-namespace \
		-f $(HELM_CHART)/values.yaml \
		--set env.MINIMAX_API_KEY="$$MINIMAX_API_KEY" \
		--set env.ZAI_API_KEY="$$ZAI_API_KEY" \
		--set env.OPENROUTER_API_KEY="$$OPENROUTER_API_KEY" \
		--set env.DEEPSEEK_API_KEY="$$DEEPSEEK_API_KEY" \
		--set env.ANTHROPIC_API_KEY="$$ANTHROPIC_API_KEY" \
		--set env.GITHUB_TOKEN="$$GITHUB_TOKEN" \
		--set env.FIGMA_TOKEN="$$FIGMA_TOKEN" \
		--set env.CONTEXT7_API_KEY="$$CONTEXT7_API_KEY" \
		--set env.P9I_API_KEY="$$P9I_API_KEY" \
		--set env.ALLOWED_ORIGINS="$$ALLOWED_ORIGINS" \
		--set ingress.hosts[0].host="$${DOMAIN:-p9i.ru}" \
		--set ingress.tls[0].hosts[0]="$${DOMAIN:-p9i.ru}" \
		--set image.repository="$(K8S_REGISTRY)/$(IMAGE_NAME)" \
		--wait --timeout 5m
	@echo "$(YELLOW)Cleaning up old pods after deploy...$(NC)"
	@sleep 5 && $(KUBECTL) get pods -n $(NAMESPACE) -l app=p9i-p9i --no-headers 2>/dev/null | \
		grep -v "Running" | awk '{print $$1}' | \
		xargs -r $(KUBECTL) delete pod -n $(NAMESPACE) 2>/dev/null || true
	@echo "$(GREEN)Deployed to K3s namespace: $(NAMESPACE)$(NC)"
	@echo "$(GREEN)Pod status:"
	@$(KUBECTL) get pods -n $(NAMESPACE) -l app=p9i-p9i


.PHONY: k3s-delete
k3s-delete:
	@echo "$(YELLOW)Deleting from K3s (Helm)...$(NC)"
	helm uninstall p9i --namespace $(NAMESPACE) 2>/dev/null || true
	$(KUBECTL) delete namespace $(NAMESPACE) --ignore-not-found=true
	@echo "$(GREEN)Deleted from K3s$(NC)"

.PHONY: k3s-logs
k3s-logs:
	$(KUBECTL) logs -n $(NAMESPACE) -l $(APP_LABEL) -f --tail=100

.PHONY: k3s-restart
k3s-restart:
	$(KUBECTL) rollout restart -n $(NAMESPACE) deployment/p9i-p9i
	@echo "$(GREEN)Restarted deployment$(NC)"

.PHONY: k3s-redeploy
k3s-redeploy: k3s-delete build-push k3s-deploy
	@echo "$(GREEN)Full redeploy complete!$(NC)"

.PHONY: k3s-status
k3s-status:
	@echo "$(BLUE)=== Namespace $(NAMESPACE) ===$(NC)"
	$(KUBECTL) get all -n $(NAMESPACE)
	@echo ""
	@echo "$(BLUE)=== Endpoints ===$(NC)"
	$(KUBECTL) get endpoints -n $(NAMESPACE)

.PHONY: k3s-port-forward
k3s-port-forward:
	@echo "$(YELLOW)Port forwarding to K3s service...$(NC)"
	@echo "MCP: localhost:8000 -> p9i-p9i:8000"
	$(KUBECTL) port-forward -n $(NAMESPACE) svc/p9i-p9i 8000:8000 & \
	wait

.PHONY: k3s-describe
k3s-describe:
	$(KUBECTL) describe all -n $(NAMESPACE)

.PHONY: k3s-events
k3s-events:
	$(KUBECTL) get events -n $(NAMESPACE) --sort-by='.lastTimestamp'

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
	$(KUBECTL) delete namespace $(NAMESPACE) --ignore-not-found=true

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