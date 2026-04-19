#!/usr/bin/env bash
# Render the full Study 1 and Study 2 production scenes, then concatenate
# them into a single MP4.
#
# Usage:
#   ./render_single_video.sh
#   ./render_single_video.sh -qh
#   ./render_single_video.sh -qm output/presentation.mp4

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_single_video.sh [QUALITY] [OUTPUT_MP4]"
    echo
    echo "Render the full Study 1 scene, then the full Study 2 scene."
    echo "After rendering, concatenate them into one MP4 with ffmpeg."
    echo
    echo "Examples:"
    echo "  ./render_single_video.sh"
    echo "  ./render_single_video.sh -qh"
    echo "  ./render_single_video.sh -qm media/videos/presentation_studies_1_2.mp4"
    exit 0
fi

QUALITY="${1:--ql}"
OUTPUT_MP4="${2:-media/videos/studies_1_2_full.mp4}"

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
        -qp|qp|1440p60)
            printf '%s\n' "1440p60"
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
    QUALITY_DIR=""
fi

scene_entries=(
    "study1:03_study1:scenes/study1.py:study1:Study1:--save_sections"
    "study2:04_study2:scenes/study2.py:study2:Study2:--save_sections"
)

if [[ ${#scene_entries[@]} -eq 0 ]]; then
    echo "No scenes found to render." >&2
    exit 1
fi

concat_list="$(mktemp)"
trap 'rm -f "$concat_list"' EXIT

total=${#scene_entries[@]}
idx=0

for entry in "${scene_entries[@]}"; do
    study_slug="${entry%%:*}"
    rest="${entry#*:}"
    study_dir="${rest%%:*}"
    rest="${rest#*:}"
    scene_file="${rest%%:*}"
    rest="${rest#*:}"
    output_name="${rest%%:*}"
    rest="${rest#*:}"
    class_name="${rest%%:*}"
    sections_flag="${rest#*:}"

    idx=$((idx + 1))
    echo "[$idx/$total] $class_name -> $output_name${sections_flag:+ (sectioned)}"
    uv run manim "$scene_file" "$class_name" "$QUALITY" ${sections_flag:+$sections_flag}

    rendered_path=""
    if [[ -n "$QUALITY_DIR" && -f "media/videos/$study_dir/$QUALITY_DIR/${output_name}.mp4" ]]; then
        rendered_path="media/videos/$study_dir/$QUALITY_DIR/${output_name}.mp4"
    else
        rendered_path="$(find "media/videos/$study_dir" -type f -name "${output_name}.mp4" | sort | tail -n 1)"
    fi
    if [[ -z "$rendered_path" ]]; then
        echo "Could not locate rendered output for $output_name in media/videos/$study_dir" >&2
        exit 1
    fi

    abs_rendered_path="$(cd "$(dirname "$rendered_path")" && pwd)/$(basename "$rendered_path")"
    printf "file '%s'\n" "$abs_rendered_path" >> "$concat_list"
done

mkdir -p "$(dirname "$OUTPUT_MP4")"
OUTPUT_ABS="$(cd "$(dirname "$OUTPUT_MP4")" && pwd)/$(basename "$OUTPUT_MP4")"

echo "Concatenating all rendered clips into $OUTPUT_ABS"
ffmpeg -y -f concat -safe 0 -i "$concat_list" -c copy "$OUTPUT_ABS"

echo "Done. Single video saved to $OUTPUT_ABS"
