#!/bin/bash
# scripts/sync-uiux.sh
# Sync UI/UX data from ui-ux-pro-mcp using curl

set -e

BASE_URL="https://raw.githubusercontent.com/redf0x1/ui-ux-pro-mcp/main/data"
OUTPUT_DIR="/home/worker/p9i/src/infrastructure/uiux/data"

echo "Syncing UI/UX data from ui-ux-pro-mcp..."

# Colors - download and convert to JSON
echo "Fetching colors.csv..."
curl -s "${BASE_URL}/colors.csv" > /tmp/colors.csv
echo "  Downloaded $(wc -l < /tmp/colors.csv) rows"

# Styles - download
echo "Fetching styles.csv..."
curl -s "${BASE_URL}/styles.csv" > /tmp/styles.csv
echo "  Downloaded $(wc -l < /tmp/styles.csv) rows"

# Check what's available
ls -la /tmp/*.csv

echo "Sync complete. Use Python sync.py to parse and update embedded.py"
echo "To parse data, run: python3 -m src.infrastructure.uiux.sync --all"