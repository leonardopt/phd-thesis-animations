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

normalize_quality_dir() {
    case "$1" in
        -ql|ql|low|480p15)
            echo "480p15"
            ;;
        -qm|qm|medium|720p30)
            echo "720p30"
            ;;
        -qh|qh|high|1080p60)
            echo "1080p60"
            ;;
        -qk|qk|4k|2160p60)
            echo "2160p60"
            ;;
        *)
            echo "Unsupported quality: $1" >&2
            echo "Use -ql, -qm, -qh, -qk or 480p15/720p30/1080p60/2160p60." >&2
            exit 1
            ;;
    esac
}

QUALITY_DIR="$(normalize_quality_dir "$QUALITY")"

# Clear stale section clips only for the selected quality before rendering.
find "media/videos/03_study1/$QUALITY_DIR/sections" -type f -delete 2>/dev/null || true

echo "[1/1] Study1 -> study1 (sectioned, cache disabled)"
uv run manim scenes/study1.py Study1 "$QUALITY" --save_sections --disable_caching

# Remove combined videos — keep only per-section files.
find "media/videos/03_study1/$QUALITY_DIR" -maxdepth 1 -name "*.mp4" -delete 2>/dev/null || true

echo "Done. Section videos saved to media/videos/03_study1/$QUALITY_DIR/sections/"
