#!/bin/bash
# start-https.sh - Start p9i MCP server with HTTPS support

set -e

DOMAIN="${DOMAIN:-mcp.coderweb.ru}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Color codes
COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_YELLOW='\033[1;33m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_BLUE}=================================="
echo "Starting p9i MCP Server with HTTPS"
echo "Domain: $DOMAIN"
echo "==================================${COLOR_RESET}"
echo ""

# Check if SSL certificates exist
if [ ! -f "nginx/ssl/fullchain.pem" ] || [ ! -f "nginx/ssl/privkey.pem" ]; then
    echo -e "${COLOR_YELLOW}SSL certificates not found. Generating self-signed certificates...${COLOR_RESET}"
    bash scripts/setup-ssl.sh self-signed
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${COLOR_YELLOW}.env file not found. Creating from example...${COLOR_RESET}"
    cp .env.example .env
    echo "Please configure your .env file with API keys and settings"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${COLOR_YELLOW}Docker Compose not found. Please install Docker Compose.${COLOR_RESET}"
    exit 1
fi

# Function to get docker compose command
get_docker_compose() {
    if docker compose version &> /dev/null; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

DOCKER_COMPOSE=$(get_docker_compose)

# Stop existing containers
echo -e "${COLOR_BLUE}Stopping existing containers...${COLOR_RESET}"
$DOCKER_COMPOSE -f docker-compose.ssl.yml down 2>/dev/null || true

# Pull latest images
echo -e "${COLOR_BLUE}Pulling latest images...${COLOR_RESET}"
$DOCKER_COMPOSE -f docker-compose.ssl.yml pull

# Build and start services
echo -e "${COLOR_BLUE}Building and starting services...${COLOR_RESET}"
$DOCKER_COMPOSE -f docker-compose.ssl.yml up -d --build

# Wait for services to be healthy
echo -e "${COLOR_BLUE}Waiting for services to be ready...${COLOR_RESET}"
sleep 5

# Check service status
echo ""
echo -e "${COLOR_BLUE}Service Status:${COLOR_RESET}"
$DOCKER_COMPOSE -f docker-compose.ssl.yml ps

echo ""
echo -e "${COLOR_GREEN}=================================="
echo "Services started successfully!"
echo "==================================${COLOR_RESET}"
echo ""
echo "Available endpoints:"
echo -e "${COLOR_GREEN}• MCP Server (HTTPS):${COLOR_RESET} https://$DOMAIN/mcp"
echo -e "${COLOR_GREEN}• MCP Server (HTTP):${COLOR_RESET} http://localhost:8000/mcp"
echo -e "${COLOR_GREEN}• Web UI:${COLOR_RESET} http://localhost:8501"
echo -e "${COLOR_GREEN}• Health Check:${COLOR_RESET} https://$DOMAIN/health"
echo ""
echo "Useful commands:"
echo "• View logs: $DOCKER_COMPOSE -f docker-compose.ssl.yml logs -f"
echo "• Stop services: $DOCKER_COMPOSE -f docker-compose.ssl.yml down"
echo "• Restart services: $DOCKER_COMPOSE -f docker-compose.ssl.yml restart"
echo "• Test HTTPS: bash scripts/test-https.sh"
echo ""
echo -e "${COLOR_YELLOW}Note: For production, use Let's Encrypt certificates:${COLOR_RESET}"
echo "bash scripts/setup-ssl.sh letsencrypt"
echo ""
