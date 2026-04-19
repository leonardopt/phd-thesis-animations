#!/usr/bin/env bash
# Reserve the numbered Methods slot in the render workflow.
# Usage:
#   ./render_02_methods.sh
#   ./render_02_methods.sh -qh

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_02_methods.sh [QUALITY]"
    echo
    echo "Reserve the numbered Methods slot. No standalone Methods scene entrypoint exists yet."
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p "media/videos/02_methods" "media/images/02_methods"
echo "Reserved media/videos/02_methods and media/images/02_methods."
echo "No standalone Methods render script exists yet."
