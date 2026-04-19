#!/usr/bin/env bash
# Render the unified Study 1 production scene and keep the section clips.
# Usage:
#   ./render_03_study1.sh        # low quality (480p15, fast preview)
#   ./render_03_study1.sh -qh    # high quality (1080p60)
#   ./render_03_study1.sh -qm    # medium quality

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_03_study1.sh [QUALITY]"
    echo
    echo "Render the unified Study 1 production scene and keep section clips."
    echo "Defaults to -ql when no quality is provided."
    exit 0
fi

QUALITY="${1:--ql}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$SCRIPT_DIR/.uv-cache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$UV_CACHE_DIR" "$MPLCONFIGDIR"

echo "[1/1] Study1 -> study1 (sectioned)"
uv run manim scenes/study1.py Study1 "$QUALITY" --save_sections

# Remove combined videos — keep only per-section files.
find media/videos/03_study1 -maxdepth 2 -name "*.mp4" -not -path "*/sections/*" -delete 2>/dev/null || true

echo "Done. Section videos saved to media/videos/03_study1/*/sections/"
