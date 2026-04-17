#!/usr/bin/env bash
# Render all Study 2 scenes in narrative order with numbered output filenames.
# Usage:
#   ./render_study2.sh        # low quality (480p15, fast preview)
#   ./render_study2.sh -qh    # high quality (1080p60)
#   ./render_study2.sh -qm    # medium quality

set -euo pipefail

QUALITY="${1:--ql}"

scenes=(
    "01_Study2ExperimentalDesign:Study2ExperimentalDesign"
    "02_Study2DecodingOverview:Study2DecodingOverview"
    "03_Study2WithinSession2Decoding:Study2WithinSession2Decoding"
    "04_Study2WithinSession2DecodingResults:Study2WithinSession2DecodingResults"
    "05_Study2CrossSessionDecoding:Study2CrossSessionDecoding"
    "06_Study2CrossSessionDecodingResultsA:Study2CrossSessionDecodingResultsA"
    "07_Study2CrossSessionDecodingResultsB:Study2CrossSessionDecodingResultsB"
    "08_Study2WithinSession1DecodingA:Study2WithinSession1DecodingA"
    "09_Study2WithinSession1DecodingB:Study2WithinSession1DecodingB"
    "10_Study2WithinSession1DecodingResultsA:Study2WithinSession1DecodingResultsA"
    "11_Study2WithinSession1DecodingResultsB:Study2WithinSession1DecodingResultsB"
    "12_Study2WithinSession1DecodingResultsC:Study2WithinSession1DecodingResultsC"
    "13_Study2WithinSession1DecodingResultsD:Study2WithinSession1DecodingResultsD"
    "14_Study2LTMResultsExplainer:Study2LTMResultsExplainer"
    "15_Study2WithinSession1TrainTestPanel:Study2WithinSession1TrainTestPanel"
    "16_Study2SupplementalRoiTimecoursesA:Study2SupplementalRoiTimecoursesA"
    "17_Study2SupplementalRoiTimecoursesB:Study2SupplementalRoiTimecoursesB"
    "18_Study2SupplementalRoiTempGenMats:Study2SupplementalRoiTempGenMats"
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
