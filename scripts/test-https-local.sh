#!/bin/bash
# test-https-local.sh - Test HTTPS setup for p9i MCP server (localhost)

set -e

COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_BLUE}=================================="
echo "HTTPS Setup Test (Localhost)"
echo "==================================${COLOR_RESET}"
echo ""

# Function to print test results
print_result() {
    local test_name="$1"
    local result="$2"
    if [ "$result" -eq 0 ]; then
        echo -e "${COLOR_GREEN}✓${COLOR_RESET} $test_name"
    else
        echo -e "${COLOR_RED}✗${COLOR_RESET} $test_name"
    fi
}

# Function to run test
run_test() {
    local test_name="$1"
    local command="$2"

    echo -n "Testing: $test_name... "
    if eval "$command" > /dev/null 2>&1; then
        print_result "$test_name" 0
        return 0
    else
        print_result "$test_name" 1
        return 1
    fi
}

echo "1. Container Status Tests"
echo "------------------------"

run_test "Nginx Container Running" "docker ps | grep -q p9i-ssl-nginx"
run_test "MCP Server Running" "docker ps | grep -q p9i-ssl-mcp-server"
run_test "PostgreSQL Running" "docker ps | grep -q p9i-ssl-db"
run_test "Redis Running" "docker ps | grep -q p9i-ssl-redis"

echo ""
echo "2. HTTP/HTTPS Port Tests"
echo "------------------------"

run_test "HTTP Port (80) Available" "nc -zv localhost 80"
run_test "HTTPS Port (443) Available" "nc -zv localhost 443"

echo ""
echo "3. Nginx Configuration Tests"
echo "---------------------------"

run_test "HTTP to HTTPS Redirect" "curl -s -o /dev/null -w '%{redirect_url}' http://localhost/ | grep -q 'https://'"
run_test "Nginx Health Check" "curl -s -o /dev/null -w '%{http_code}' http://localhost/nginx-health | grep -q '200'"

echo ""
echo "4. SSL/TLS Tests"
echo "----------------"

run_test "SSL Handshake" "openssl s_client -connect localhost:443 -servername localhost </dev/null 2>&1 | grep -q 'Verify return code'"
run_test "SSE Endpoint HTTPS" "curl -k -s -I https://localhost/sse | grep -q 'text/event-stream'"

echo ""
echo "5. MCP Server Tests"
echo "--------------------"

run_test "MCP to SSE Redirect" "curl -k -s -o /dev/null -w '%{http_code}' https://localhost/mcp | grep -q '301'"

echo ""
echo "6. Security Headers Tests"
echo "------------------------"

run_test "HSTS Header" "curl -k -s -I https://localhost/ | grep -q 'strict-transport-security'"
run_test "X-Frame-Options" "curl -k -s -I https://localhost/ | grep -q 'x-frame-options'"
run_test "X-Content-Type-Options" "curl -k -s -I https://localhost/ | grep -q 'x-content-type-options'"

echo ""
echo "7. Response Time Tests"
echo "---------------------"

echo -e "${COLOR_YELLOW}Testing HTTPS response time...${COLOR_RESET}"
time curl -k -s -o /dev/null https://localhost/sse

echo ""
echo -e "${COLOR_BLUE}=================================="
echo "Test Summary"
echo "==================================${COLOR_RESET}"
echo ""
echo "📊 Service URLs:"
echo -e "${COLOR_GREEN}• MCP SSE (HTTPS):${COLOR_RESET} https://localhost/sse"
echo -e "${COLOR_GREEN}• MCP SSE (HTTP):${COLOR_RESET} http://localhost:8000/sse"
echo -e "${COLOR_GREEN}• Nginx Health:${COLOR_RESET} http://localhost/nginx-health"
echo -e "${COLOR_GREEN}• Web UI:${COLOR_RESET} http://localhost:8501"
echo ""
echo "📝 MCP Client Config:"
echo -e "${COLOR_YELLOW}SSE (Recommended):${COLOR_RESET}"
echo '{'
echo '  "hosted-service": {'
echo '    "type": "sse",'
echo '    "url": "https://localhost/sse"'
echo '  }'
echo '}'
echo ""
echo "🔍 View Logs:"
echo "docker compose -f docker-compose.ssl.yml logs -f"
echo ""
