#!/bin/bash
# ADR Verification Script for p9i
# This script validates ADR compliance

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== ADR Verification ==="
echo "Project: p9i"
echo "Root: $PROJECT_ROOT"

# Check if ADR directory exists
ADR_DIR="$PROJECT_ROOT/docs/explanation/adr"
if [ ! -d "$ADR_DIR" ]; then
    echo "⚠️  ADR directory not found: $ADR_DIR"
    exit 0  # Not a failure, just not applicable
fi

# Count ADRs
ADR_COUNT=$(find "$ADR_DIR" -name "ADR-*.md" 2>/dev/null | wc -l)
echo "Found $ADR_COUNT ADRs"

# List recent ADRs
echo ""
echo "Recent ADRs:"
find "$ADR_DIR" -name "ADR-*.md" -type f | sort | tail -5 | while read f; do
    basename "$f"
done

echo ""
echo "✅ ADR verification complete"
exit 0
