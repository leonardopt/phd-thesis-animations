#!/usr/bin/env bash
# Render all Study 2 scenes in narrative order with numbered output filenames.
# Usage:
#   ./render_study2.sh        # low quality (480p15, fast preview)
#   ./render_study2.sh -qh    # high quality (1080p60)
#   ./render_study2.sh -qm    # medium quality

set -euo pipefail

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


for class_name, scene_number in load_scene_order("scenes/study2.py", "_STUDY2_SCENE_ORDER").items():
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

echo "Done. Videos saved to media/videos/study2/"
