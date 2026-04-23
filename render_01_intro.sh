#!/usr/bin/env bash
# Render the unified introduction production scene and keep the section clips.
# Usage:
#   ./render_01_intro.sh        # low quality (480p15, fast preview)
#   ./render_01_intro.sh -qh    # high quality (1080p60)
#   ./render_01_intro.sh -qm    # medium quality

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_01_intro.sh [QUALITY]"
    echo
    echo "Render the unified introduction production scene and keep section clips."
    echo "Defaults to -ql when no quality is provided."
    exit 0
fi

QUALITY="${1:--ql}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$SCRIPT_DIR/.uv-cache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$UV_CACHE_DIR" "$MPLCONFIGDIR"

# Clear stale section clips from previous introduction layouts before rendering.
find media/videos/01_intro -path "*/sections/*" -type f -delete 2>/dev/null || true

echo "[1/1] Introduction -> intro (sectioned)"
uv run manim scenes/intro.py Introduction "$QUALITY" --save_sections

# Remove the combined scene render and keep only per-section files.
find media/videos/01_intro -maxdepth 2 -name "*.mp4" -not -path "*/sections/*" -delete 2>/dev/null || true

echo "Done. Section videos saved to media/videos/01_intro/*/sections/"
