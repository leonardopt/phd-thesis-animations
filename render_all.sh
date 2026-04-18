#!/usr/bin/env bash
# Run every top-level render_*.sh script with the same Manim quality flag.
# Usage:
#   ./render_all.sh        # low quality (defaults to -ql)
#   ./render_all.sh -qk    # 4K quality
#   ./render_all.sh -qh    # high quality

set -euo pipefail
shopt -s nullglob

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_all.sh [QUALITY]"
    echo
    echo "Run all top-level render_*.sh scripts with the same Manim quality flag."
    echo "Defaults to -ql when no quality is provided."
    exit 0
fi

QUALITY="${1:--ql}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "$0")"

cd "$SCRIPT_DIR"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$SCRIPT_DIR/.uv-cache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$UV_CACHE_DIR" "$MPLCONFIGDIR"

all_scripts=(render_*.sh)
scripts=()

for script in "${all_scripts[@]}"; do
    if [[ "$(basename "$script")" != "$SCRIPT_NAME" ]]; then
        scripts+=("$script")
    fi
done

if [[ ${#scripts[@]} -eq 0 ]]; then
    echo "No render scripts found." >&2
    exit 1
fi

total=${#scripts[@]}
idx=0

for script in "${scripts[@]}"; do
    idx=$((idx + 1))
    echo "[$idx/$total] Running $script $QUALITY"
    "./$script" "$QUALITY"
done

echo "Done. Rendered all presentation sections with quality $QUALITY."
