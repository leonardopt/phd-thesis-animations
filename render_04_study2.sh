#!/usr/bin/env bash
# Render all Study 2 scenes in narrative order with numbered output filenames.
# Usage:
#   ./render_04_study2.sh        # low quality (480p15, fast preview)
#   ./render_04_study2.sh -qh    # high quality (1080p60)
#   ./render_04_study2.sh -qm    # medium quality

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_04_study2.sh [QUALITY]"
    echo
    echo "Render all Study 2 scenes in numbered narrative order."
    echo "Defaults to -ql when no quality is provided."
    exit 0
fi

QUALITY="${1:--ql}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$SCRIPT_DIR/.uv-cache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$UV_CACHE_DIR" "$MPLCONFIGDIR"

scenes=()
while IFS= read -r line; do
    scenes+=("$line")
done < <(
    uv run python -c '
import ast
import re
from pathlib import Path


def load_scene_order(path_str: str, variable_name: str) -> dict[str, str]:
    tree = ast.parse(Path(path_str).read_text())
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == variable_name:
            return ast.literal_eval(node.value)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    return ast.literal_eval(node.value)
    raise SystemExit(f"Could not find {variable_name} in {path_str}")


def sort_key(scene_number: str) -> tuple[int, str]:
    match = re.fullmatch(r"(\d+)([A-Za-z]*)", scene_number)
    if match is None:
        raise SystemExit(f"Unsupported scene number: {scene_number}")
    return int(match.group(1)), match.group(2)


for class_name, scene_number in sorted(load_scene_order("scenes/study2.py", "_STUDY2_SCENE_ORDER").items(), key=lambda item: sort_key(item[1])):
    print(f"{scene_number}_{class_name}:{class_name}")
' 
)

total=${#scenes[@]}
idx=0

for entry in "${scenes[@]}"; do
    outname="${entry%%:*}"
    classname="${entry##*:}"
    idx=$((idx + 1))
    echo "[$idx/$total] $classname -> $outname"
    uv run manim scenes/study2.py "$classname" "$QUALITY" -o "$outname"
done

echo "Done. Videos saved to media/videos/04_study2/"
