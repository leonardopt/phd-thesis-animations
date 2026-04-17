#!/usr/bin/env bash
# Render the main Study 1 scenes in narrative order with numbered output filenames.
# Usage:
#   ./render_study1.sh        # low quality (480p15, fast preview)
#   ./render_study1.sh -qh    # high quality (1080p60)
#   ./render_study1.sh -qm    # medium quality

set -euo pipefail

QUALITY="${1:--ql}"

scenes=(
    "00_Study1Pipeline:Study1Pipeline"
    "01_Study1Step1a:Study1Step1a"
    "02_Study1Step1b:Study1Step1b"
    "03_Study1Step2:Study1Step2"
    "04_Study1Step2Showcase:Study1Step2Showcase"
    "05_Study1Step3Part1:Study1Step3Part1"
    "06_Study1Step3Part2:Study1Step3Part2"
    "07_Study1Step4Setup:Study1Step4Setup"
    "08_Study1Step4Interpolation:Study1Step4Interpolation"
    "09_Study1Step5Handoff:Study1Step5Handoff"
    "10_Study1Step5Deck:Study1Step5Deck"
    "11_Study1Step5LPIPS:Study1Step5LPIPS"
    "12_Study1StimulusSetShowcase:Study1StimulusSetShowcase"
    "13_Study1Stage2TripletTask:Study1Stage2TripletTask"
    "14_Study1Stage2TripletTask2:Study1Stage2TripletTask2"
    "15_Study1Stage2SimilarityJudgementsExamples:Study1Stage2SimilarityJudgementsExamples"
    "16_Study1Stage2EmbeddingResult:Study1Stage2EmbeddingResult"
    "17_Study1Stage2ModelOrderToHeatmap:Study1Stage2ModelOrderToHeatmap"
    "18_Study1Stage3MemoryIntro:Study1Stage3MemoryIntro"
    "19_Study1Stage3MemoryExpDesignA:Study1Stage3MemoryExpDesignA"
    "20_Study1Stage3MemoryExpDesignB:Study1Stage3MemoryExpDesignB"
    "21_Study1Stage3MemoryExpResults:Study1Stage3MemoryExpResults"
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

echo "Done. Videos saved to media/videos/study1/"
