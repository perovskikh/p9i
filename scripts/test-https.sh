#!/bin/bash
# test-https.sh - Test HTTPS setup for p9i MCP server

set -e

DOMAIN="${DOMAIN:-p9i.ru}"
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_RESET='\033[0m'

echo "=================================="
echo "HTTPS Setup Test for $DOMAIN"
echo "=================================="
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

# Function to run test with output
run_test_output() {
    local test_name="$1"
    local command="$2"

    echo "Testing: $test_name"
    eval "$command"
    echo ""
}

echo "1. Network Connectivity Tests"
echo "----------------------------"

run_test "DNS Resolution" "nslookup $DOMAIN"
run_test "HTTP Port (80)" "nc -zv $DOMAIN 80"
run_test "HTTPS Port (443)" "nc -zv $DOMAIN 443"

echo ""
echo "2. SSL/TLS Tests"
echo "----------------"

run_test "SSL Handshake" "openssl s_client -connect $DOMAIN:443 -servername $DOMAIN </dev/null"

echo ""
echo "3. SSL Certificate Details"
echo "----------------------------"

run_test_output "SSL Certificate Info" "openssl s_client -connect $DOMAIN:443 -servername $DOMAIN </dev/null | openssl x509 -text -noout | grep -E 'Subject:|Issuer:|Not Before|Not After|DNS:|CN='"

echo ""
echo "4. HTTP/HTTPS Tests"
echo "-------------------"

run_test "HTTP to HTTPS Redirect" "curl -s -o /dev/null -w '%{redirect_url}' http://$DOMAIN | grep -q 'https://'"

echo ""
echo "5. MCP Server Tests"
echo "-------------------"

run_test "MCP Health Check (HTTP)" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health | grep -q '200'"
run_test "MCP Health Check (HTTPS)" "curl -s -o /dev/null -w '%{http_code}' https://$DOMAIN/health | grep -q '200'"

echo ""
echo "6. SSL Certificate Validation"
echo "------------------------------"

run_test_output "Certificate Validity" "openssl s_client -connect $DOMAIN:443 -servername $DOMAIN </dev/null | openssl x509 -checkend 86400 -noout && echo 'Certificate is valid for at least 24 hours' || echo 'Certificate will expire within 24 hours or is invalid'"

echo ""
echo "7. Security Headers Tests"
echo "-------------------------"

run_test_output "Security Headers" "curl -s -I https://$DOMAIN/ | grep -i -E 'strict-transport-security|x-frame-options|x-content-type-options|x-xss-protection'"

echo ""
echo "8. Connection Performance"
echo "--------------------------"

run_test_output "HTTPS Connection Time" "time curl -s -o /dev/null https://$DOMAIN/health"

echo ""
echo "=================================="
echo "Test Summary"
echo "=================================="

echo ""
echo "Manual Testing Commands:"
echo "1. Test MCP SSE connection:"
echo "   curl -N https://$DOMAIN/mcp"
echo ""
echo "2. Test MCP tools list:"
echo "   curl -X POST https://$DOMAIN/mcp -H 'Content-Type: application/json' -d '{\"method\": \"tools/list\"}'"
echo ""
echo "3. Test with API key:"
echo "   curl -X POST https://$DOMAIN/mcp -H 'Content-Type: application/json' -H 'Authorization: Bearer YOUR_API_KEY' -d '{\"method\": \"tools/list\"}'"
echo ""
echo "4. Monitor logs:"
echo "   docker compose -f docker-compose.ssl.yml logs -f"
echo ""
