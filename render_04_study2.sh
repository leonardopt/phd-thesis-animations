#!/usr/bin/env bash
# Render the unified Study 2 production scene and keep the section clips.
# Usage:
#   ./render_04_study2.sh        # low quality (480p15, fast preview)
#   ./render_04_study2.sh -qh    # high quality (1080p60)
#   ./render_04_study2.sh -qm    # medium quality

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_04_study2.sh [QUALITY]"
    echo
    echo "Render the unified Study 2 production scene and keep section clips."
    echo "Defaults to -ql when no quality is provided."
    exit 0
fi

QUALITY="${1:--ql}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$SCRIPT_DIR/.uv-cache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$UV_CACHE_DIR" "$MPLCONFIGDIR"

# Clear stale section clips from previous Study 2 layouts before rendering.
find media/videos/04_study2 -path "*/sections/*" -type f -delete 2>/dev/null || true

echo "[1/1] Study2 -> study2 (sectioned, no cache)"
uv run manim scenes/study2.py Study2 "$QUALITY" --save_sections --disable_caching

# Remove the combined scene render and keep only per-section files.
find media/videos/04_study2 -maxdepth 2 -name "*.mp4" -not -path "*/sections/*" -delete 2>/dev/null || true

echo "Done. Section videos saved to media/videos/04_study2/*/sections/"
