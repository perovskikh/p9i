#!/bin/bash
# ADR Checklist Progress Script for p9i
# Reports status of ADR implementations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ADR_DIR="$PROJECT_ROOT/docs/explanation/adr"

echo "=== ADR Checklist Progress ==="
echo "Project: p9i"
echo ""

if [ ! -d "$ADR_DIR" ]; then
    echo "{\"status\": \"no_adr_dir\", \"message\": \"ADR directory not found\"}"
    exit 0
fi

# Count total ADRs
TOTAL=$(find "$ADR_DIR" -name "ADR-*.md" 2>/dev/null | wc -l)
echo "Total ADRs: $TOTAL"

# List ADRs with their status
echo ""
echo "ADRs:"
find "$ADR_DIR" -name "ADR-*.md" -type f | sort | while read f; do
    name=$(basename "$f" .md)
    # Check for status markers
    if grep -q "Status: Proposed\|Status: Accepted" "$f" 2>/dev/null; then
        status="in_progress"
    elif grep -q "Status: Deprecated\|Status: Rejected" "$f" 2>/dev/null; then
        status="deprecated"
    else
        status="active"
    fi
    echo "  - $name: $status"
done

echo ""
echo "✅ Checklist complete"
exit 0
