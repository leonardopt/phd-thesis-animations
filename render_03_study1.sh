#!/usr/bin/env bash
# Render all numbered Study 1 scenes in narrative order with numbered output filenames.
# Usage:
#   ./render_03_study1.sh        # low quality (480p15, fast preview)
#   ./render_03_study1.sh -qh    # high quality (1080p60)
#   ./render_03_study1.sh -qm    # medium quality

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./render_03_study1.sh [QUALITY]"
    echo
    echo "Render all Study 1 scenes in numbered narrative order."
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
from pathlib import Path


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


scene_order = load_mapping("scenes/study1.py", "_STUDY1_SCENE_ORDER")
output_name_overrides = load_mapping("scenes/study1.py", "_STUDY1_OUTPUT_NAME_OVERRIDES")

for class_name, scene_number in sorted(scene_order.items(), key=lambda item: int(item[1])):
    output_name = output_name_overrides.get(class_name, f"{scene_number}_{class_name}")
    print(f"{output_name}:{class_name}")
' 
)

total=${#scenes[@]}
idx=0

for entry in "${scenes[@]}"; do
    outname="${entry%%:*}"
    classname="${entry##*:}"
    idx=$((idx + 1))
    echo "[$idx/$total] $classname -> $outname"
    uv run manim scenes/study1.py "$classname" "$QUALITY" -o "$outname"
done

echo "Done. Videos saved to media/videos/03_study1/"
