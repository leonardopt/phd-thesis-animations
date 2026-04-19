#!/usr/bin/env bash
# Render all Study 1 and Study 2 scenes sequentially, then concatenate them
# into a single MP4.
#
# Usage:
#   ./render_single_video.sh
#   ./render_single_video.sh -qh
#   ./render_single_video.sh -qm output/presentation.mp4

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_single_video.sh [QUALITY] [OUTPUT_MP4]"
    echo
    echo "Render all Study 1 scenes, then all Study 2 scenes, sequentially."
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

scene_entries=()
while IFS= read -r line; do
    scene_entries+=("$line")
done < <(
    uv run python - <<'PY'
import ast
import re
import sys
from pathlib import Path

SCENES_DIR = Path("scenes").resolve()
if str(SCENES_DIR) not in sys.path:
    sys.path.insert(0, str(SCENES_DIR))

from utils import section_output_dir


def load_mapping(path_str: str, variable_name: str):
    tree = ast.parse(Path(path_str).read_text())
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == variable_name:
            return ast.literal_eval(node.value)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    return ast.literal_eval(node.value)
    raise SystemExit(f"Could not find {variable_name} in {path_str}")


def scene_sort_key(scene_number: str) -> tuple[int, str]:
    match = re.fullmatch(r"(\d+)([A-Za-z]*)", scene_number)
    if match is None:
        raise SystemExit(f"Unsupported scene number: {scene_number}")
    return int(match.group(1)), match.group(2)


def emit_entries(study_slug: str, scene_file: str, order_var: str, overrides_var: str | None = None):
    scene_order = load_mapping(scene_file, order_var)
    output_overrides = load_mapping(scene_file, overrides_var) if overrides_var else {}
    study_dir = section_output_dir(study_slug)
    for class_name, scene_number in sorted(scene_order.items(), key=lambda item: scene_sort_key(item[1])):
        output_name = output_overrides.get(class_name, f"{scene_number}_{class_name}")
        print(f"{study_slug}:{study_dir}:{scene_file}:{output_name}:{class_name}")


emit_entries("study1", "scenes/study1.py", "_STUDY1_SCENE_ORDER", "_STUDY1_OUTPUT_NAME_OVERRIDES")
emit_entries("study2", "scenes/study2.py", "_STUDY2_SCENE_ORDER")
PY
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
    class_name="${rest#*:}"

    idx=$((idx + 1))
    echo "[$idx/$total] $class_name -> $output_name"
    uv run manim "$scene_file" "$class_name" "$QUALITY" -o "$output_name"

    rendered_path="$(find "media/videos/$study_dir" -type f -name "${output_name}.mp4" | sort | tail -n 1)"
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
