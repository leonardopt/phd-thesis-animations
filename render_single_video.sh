#!/usr/bin/env bash
# Render the full presentation section sequence, then concatenate the numbered
# section clips into one MP4.
#
# Usage:
#   ./render_single_video.sh
#   ./render_single_video.sh -qh
#   ./render_single_video.sh -qm output/presentation.mp4

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_single_video.sh [QUALITY] [OUTPUT_MP4]"
    echo
    echo "Render all top-level presentation sections with the requested quality."
    echo "After rendering, concatenate the numbered section clips into one MP4."
    echo
    echo "Examples:"
    echo "  ./render_single_video.sh"
    echo "  ./render_single_video.sh -qh"
    echo "  ./render_single_video.sh -qm media/videos/presentation_full_720p30.mp4"
    exit 0
fi

QUALITY="${1:--ql}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$SCRIPT_DIR/.uv-cache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$UV_CACHE_DIR" "$MPLCONFIGDIR"

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg is required but was not found in PATH." >&2
    exit 1
fi

quality_dir_from_arg() {
    case "${1:-}" in
        ""|-ql|ql|480p15)
            printf '%s\n' "480p15"
            ;;
        -qm|qm|720p30)
            printf '%s\n' "720p30"
            ;;
        -qh|qh|1080p60)
            printf '%s\n' "1080p60"
            ;;
        -qk|qk|2160p60)
            printf '%s\n' "2160p60"
            ;;
        *)
            return 1
            ;;
    esac
}

QUALITY_DIR=""
if QUALITY_DIR="$(quality_dir_from_arg "$QUALITY")"; then
    :
else
    echo "Unsupported quality: $QUALITY" >&2
    echo "Use -ql, -qm, -qh, -qk or 480p15/720p30/1080p60/2160p60." >&2
    exit 1
fi

OUTPUT_MP4="${2:-media/videos/presentation_full_${QUALITY_DIR}.mp4}"

section_dirs=(
    "01_intro"
    "02_methods"
    "03_study1"
    "04_study2"
    "05_conclusion"
    "06_supplementary"
)

concat_list="$(mktemp)"
trap 'rm -f "$concat_list"' EXIT

echo "[1/2] Rendering all presentation sections"
./render_all.sh "$QUALITY"

echo "[2/2] Collecting section clips for concatenation"
for section_dir in "${section_dirs[@]}"; do
    sections_dir="media/videos/$section_dir/$QUALITY_DIR/sections"
    if [[ ! -d "$sections_dir" ]]; then
        echo "Missing section directory: $sections_dir" >&2
        exit 1
    fi

    mapfile -t clip_paths < <(
        find "$sections_dir" -maxdepth 1 -type f -name "*.mp4" ! -name "*_autocreated.mp4" | sort
    )
    if [[ ${#clip_paths[@]} -eq 0 ]]; then
        echo "No section clips found under $sections_dir" >&2
        exit 1
    fi

    for rendered_path in "${clip_paths[@]}"; do
        abs_rendered_path="$(cd "$(dirname "$rendered_path")" && pwd)/$(basename "$rendered_path")"
        printf "file '%s'\n" "$abs_rendered_path" >> "$concat_list"
    done
done

mkdir -p "$(dirname "$OUTPUT_MP4")"
OUTPUT_ABS="$(cd "$(dirname "$OUTPUT_MP4")" && pwd)/$(basename "$OUTPUT_MP4")"

echo "Concatenating all rendered clips into $OUTPUT_ABS"
ffmpeg -y -f concat -safe 0 -i "$concat_list" -c copy "$OUTPUT_ABS"

echo "Done. Single video saved to $OUTPUT_ABS"
