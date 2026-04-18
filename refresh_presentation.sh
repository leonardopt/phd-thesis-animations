#!/usr/bin/env bash
# Refresh the full presentation pipeline for one selected render quality.
#
# Usage:
#   ./refresh_presentation.sh
#   ./refresh_presentation.sh -qh
#   QUALITY=-qm ./refresh_presentation.sh

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./refresh_presentation.sh [QUALITY]"
    echo
    echo "Run the full presentation refresh pipeline:"
    echo "  1. sync Python dependencies"
    echo "  2. sync small external assets"
    echo "  3. rerender all top-level presentation sections"
    echo "  4. regenerate timing and backup PDFs"
    echo "  5. build the Keynote deck"
    echo "  6. run preflight on the generated deck"
    echo "  7. package the emergency bundle"
    echo
    echo "QUALITY defaults to the QUALITY environment variable or -qh."
    echo "Examples:"
    echo "  ./refresh_presentation.sh"
    echo "  ./refresh_presentation.sh -qm"
    echo "  QUALITY=-ql ./refresh_presentation.sh"
    exit 0
fi

QUALITY="${1:-${QUALITY:--qh}}"
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

echo "Refreshing presentation pipeline with quality $QUALITY ($QUALITY_DIR)"

echo
echo "[1/8] Syncing Python environment"
uv sync

echo
echo "[2/8] Syncing small external assets"
uv run python scripts/sync_external_assets.py --groups small

echo
echo "[3/8] Rendering all presentation sections"
./render_all.sh "$QUALITY"

echo
echo "[4/8] Writing duration report"
uv run python scripts/report_video_durations.py --quality "$QUALITY_DIR"

echo
echo "[5/8] Regenerating backup PDFs"
uv run python scripts/export_last_frames_pdf.py
uv run python scripts/export_frame_screener_pdf.py
uv run python scripts/build_static_rescue_deck.py

echo
echo "[6/8] Building Keynote deck"
DECK_PATH="$(osascript scripts/create_keynote_presentation.applescript "$QUALITY")"
echo "Deck created at: $DECK_PATH"

echo
echo "[7/8] Running presentation preflight"
uv run python scripts/presentation_preflight.py --presentation-file "$DECK_PATH"

echo
echo "[8/8] Packaging emergency bundle"
uv run python scripts/package_emergency_bundle.py --presentation-file "$DECK_PATH"

echo
echo "Refresh complete."
echo "Quality: $QUALITY ($QUALITY_DIR)"
echo "Deck: $DECK_PATH"
