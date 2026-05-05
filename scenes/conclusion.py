"""
Conclusion - sectioned production render.

Render from this file to keep all conclusion outputs in the same
`media/videos/05_conclusion/...` folder.

Production render:
    uv run manim scenes/conclusion.py Conclusion -ql --save_sections

Legacy standalone renders:
    uv run manim scenes/conclusion.py ConclusionApproach -ql
    uv run manim scenes/conclusion.py ConclusionTheoreticalImplications -ql
    uv run manim scenes/conclusion.py ConclusionLimitations -ql
    uv run manim scenes/conclusion.py ConclusionFutureDirections -ql
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from PIL import Image as PILImage
import shutil
import subprocess
import sys
import tempfile

from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from utils import REPO_ROOT, env_path, section_output_dir, simplify_manim_section_video_names


_SECTION_OUTPUT_DIR = section_output_dir("conclusion")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"
config.output_file = "conclusion"
simplify_manim_section_video_names(
    lambda _output_name, index, name, ext: f"{index:03}_{name}{ext}"
)

_CONCLUSION_SCENE_ORDER: dict[str, str] = {
    "ConclusionApproach": "00",
    "ConclusionTheoreticalImplications": "01",
    "ConclusionLimitations": "02",
    "ConclusionFutureDirections": "03",
}


class _ConclusionNumberedScene:
    """Mixin that prefixes standalone renders with their chapter order."""

    def __init__(self, *args, **kwargs):
        scene_name = self.__class__.__name__
        number = _CONCLUSION_SCENE_ORDER.get(scene_name, "")
        if number and config.output_file == "conclusion":
            config.output_file = f"{number}_{scene_name}"
        super().__init__(*args, **kwargs)


BG = WHITE
INK = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
BLUE = "#2563EB"
AMBER = "#D97706"
GREEN = "#16A34A"
RED = "#DC2626"
DARK_PURPLE = "#4C1D95"
RQ_BLUE = "#4E647F"
RQ_RED = "#7A2E3A"
RQ_GREEN = "#2F5D50"
SOFT_GREY = "#6B7280"
_ANATOMY_IMAGE_DIR = REPO_ROOT / "assets" / "images" / "anatomy"
_FISH_VIDEO_PATH = REPO_ROOT / "assets" / "videos" / "fish_video.mp4"
_FUTURE_DIRECTIONS_ANCHOR_VIDEO_DIR = env_path(
    "FUTURE_DIRECTIONS_ANCHOR_VIDEO_DIR",
    "assets/videos/future_directions_anchor",
)
_CONCLUSION_PROJECT_SUMMARY_MODEL_ICON_PATH = (
    _SCENES_DIR.parent / "assets" / "images" / "references" / "neural_network_schematic.svg"
)
_CONCLUSION_PROJECT_SUMMARY_VALIDATION_ICON_PATH = (
    REPO_ROOT / "assets" / "images" / "study1" / "stage2" / "computer.png"
)
_CONCLUSION_PROJECT_SUMMARY_NEURO_ICON_PATH = (
    _ANATOMY_IMAGE_DIR / "visual_cortex.png"
)
_CONCLUSION_PROJECT_SUMMARY_STIM_DIR = (
    _SCENES_DIR.parent / "assets" / "images" / "stimuli_reordered"
)
_CONCLUSION_PROJECT_SUMMARY_VALIDATION_HEATMAP_PDF = (
    REPO_ROOT
    / "assets"
    / "images"
    / "study1"
    / "stage2"
    / "lpips_vs_embedding_orders_heatmap.pdf"
)
_CONCLUSION_PROJECT_SUMMARY_BEHAVIOUR_BLOCK = (
    REPO_ROOT / "assets" / "images" / "study1" / "stage3" / "behaviour_block.png"
)
_CONCLUSION_PROJECT_SUMMARY_NEURO_TIMERES = (
    _SCENES_DIR.parent
    / "assets"
    / "images"
    / "study2"
    / "study2_results_ses02ses01timeres.svg"
)
_CONCLUSION_PROJECT_SUMMARY_NEURO_TIMERES_PNG = (
    _SCENES_DIR.parent
    / "assets"
    / "images"
    / "study2"
    / "study2_results_ses02ses01timeres.png"
)
_CONCLUSION_PROJECT_SUMMARY_NEURO_TEMPGEN = (
    _SCENES_DIR.parent / "assets" / "images" / "study2" / "temp_gen_mat_significance.svg"
)
_CONCLUSION_PROJECT_SUMMARY_RESULT_WIDTH = 3.35
_CONCLUSION_PROJECT_SUMMARY_RESULT_HEIGHT = 1.58
_CONCLUSION_PROJECT_SUMMARY_RESULT_GAP = 0.12
_CONCLUSION_PROJECT_SUMMARY_RESULT_FRAME_BUFF = 0.03
_CONCLUSION_PROJECT_SUMMARY_RESULT_PAIR_MAX_WIDTH = 3.42
_VIDEO_FRAME_CACHE: dict[tuple[str, int, int, int, int], list[np.ndarray]] = {}

# Shared research-question panel headings used by the implication slide.
_CONCLUSION_000_QUESTION_PANELS: tuple[dict[str, str], ...] = (
    {
        "label": "Research question 1",
        "title": "Representational format",
        "question": r"Are working memory\\representations sensory-like?",
        "accent": RQ_BLUE,
    },
    {
        "label": "Research question 2",
        "title": "Ecological validity",
        "question": r"Does the sensory recruitment model\\generalize to naturalistic cognition?",
        "accent": RQ_RED,
    },
    {
        "label": "Research question 3",
        "title": "Long-term memory interaction",
        "question": (
            r"Do pre-existing long-term memory\\representations affect how the early\\visual cortex represents\\working memory content?"
        ),
        "accent": RQ_GREEN,
    },
)

# 001_conclusion_theoretical_implications copy. Each RQ keeps a short bullet list.
_CONCLUSION_001_THEORETICAL_IMPLICATION_BULLETS: tuple[
    tuple[tuple[str, ...], ...],
    ...,
] = (
    (
        (
            "early visual cortex maintained",
            "stimulus-specific information across short delays",
        ),
        (
            "it did so using",
            "a memory-specific format",
        ),
    ),
    (
        (
            "sensory recruitment was observed for naturalistic stimuli",
            "in our task with perceptual demands",
        ),
        (
            "more information was found in early visual cortex",
            "than in higher-order areas",
        ),
    ),
    (
        ("repetition improved working-memory performance",),
        (
            "it did not make the representational format",
            "more sensory-like",
        ),
    ),
)

# Edit slide wording here. Each entry records the zero-based master section index
# and the corresponding section-file stem (for example `000_conclusion_summary`).
_CONCLUSION_SLIDES: dict[str, dict[str, object]] = {
    "questions": {
        "scene_name": "ConclusionQuestions",
        "section_index": -1,
        "section_file_stem": "legacy_conclusion_questions",
        "standalone_file_stem": "legacy_ConclusionQuestions",
        "title": r"\textbf{Research questions}",
        "subtitle": None,
        "panels": _CONCLUSION_000_QUESTION_PANELS,
    },
    "summary": {
        "scene_name": "ConclusionApproach",
        "section_index": 0,
        "section_file_stem": "000_conclusion_summary",
        "standalone_file_stem": "00_ConclusionApproach",
        "title": r"\textbf{Project summary}",
        "subtitle": None,
        "steps": (
            {
                "icon_path": _CONCLUSION_PROJECT_SUMMARY_MODEL_ICON_PATH,
                "heading": "Generate stimulus set",
                "rows": (
                    (
                        "diffusion-model-generated stimuli",
                        "produced controlled",
                        "perceptual continua",
                    ),
                ),
                "width": 3.35,
            },
            {
                "icon_path": _CONCLUSION_PROJECT_SUMMARY_VALIDATION_ICON_PATH,
                "heading": "Behavioural validation",
                "rows": (
                    (
                        "stimulus set was suitable",
                        "for cognitive tasks",
                    ),
                ),
                "width": 3.05,
            },
            {
                "icon_path": _CONCLUSION_PROJECT_SUMMARY_NEURO_ICON_PATH,
                "heading": "Neuroimaging study",
                "rows": (
                    (
                        "early visual cortex robustly",
                        "represents stimulus-specific",
                        "information during working",
                        "memory maintenance but not",
                        "in a sensory-like format",
                    ),
                ),
                "width": 3.15,
            },
        ),
        "brackets": (
            {
                "start": 0,
                "end": 1,
                "label": "Study 1",
            },
            {
                "start": 2,
                "end": 2,
                "label": "Study 2",
            },
        ),
        "stimulus_codes": (
            "animal_fish",
            "item_sofa",
            "plant_pine_med",
            "building_observatory",
            "landscape_element_mountain_ridge",
            "vehicle_passenger_train",
        ),
        "content_shift_up": 1.50,
        "bracket_shift_down": 1.75,
    },
    "theoretical_implications": {
        "scene_name": "ConclusionTheoreticalImplications",
        "section_index": 1,
        "section_file_stem": "001_conclusion_theoretical_implications",
        "standalone_file_stem": "01_ConclusionTheoreticalImplications",
        "title": r"\textbf{Theoretical implications}",
        "subtitle": None,
        "take_home_bullets": (
            (
                "deep generative modelling helped tackle the trade-off",
                "between ecological validity and experimental control",
            ),
            (
                "naturalistic working memory with perceptual demands",
                "supports sensory recruitment in early visual cortex,",
                "but in a memory-specific format",
            ),
        ),
    },
    "limitations": {
        "scene_name": "ConclusionLimitations",
        "section_index": 2,
        "section_file_stem": "002_conclusion_limitations",
        "standalone_file_stem": "02_ConclusionLimitations",
        "title": r"\textbf{Main limitations}",
        "subtitle": None,
        "callout": None,
        "left_blocks": (
            {
                "heading": "Selection and coverage",
                "rows": (
                    "selection was partly subjective",
                ),
                "accent": RED,
            },
            {
                "heading": "Controlled dimensions",
                "rows": (
                    "continua mixed multiple features",
                ),
                "accent": AMBER,
            },
        ),
        "right_blocks": (
            {
                "heading": "Stimulus realism",
                "rows": (
                    "images were synthetic and object-centred",
                ),
                "accent": BLUE,
            },
            {
                "heading": "Memory manipulation",
                "rows": (
                    "long-term memory manipulation was brief",
                ),
                "accent": GREEN,
            },
        ),
    },
    "future_directions": {
        "scene_name": "ConclusionFutureDirections",
        "section_index": 3,
        "section_file_stem": "003_conclusion_future_directions",
        "standalone_file_stem": "03_ConclusionFutureDirections",
        "title": r"\textbf{Future directions}",
        "subtitle": None,
        "callout": None,
        "left_blocks": (
            {
                "heading": "Next methodological steps",
                "rows": (
                    "extend synthesis beyond static exemplars to dynamic and interactive stimuli",
                    "increase control over scene clutter, viewpoint, motion, and task relevance",
                    "pair generation with stronger validation loops across behaviour and neuroimaging",
                ),
                "accent": BLUE,
            },
            {
                "heading": "A new standard?",
                "rows": (
                    "shared generative pipelines could make naturalistic stimulus control reproducible across labs",
                    "this would reduce the trade-off between ecological realism and experimental precision",
                ),
                "accent": GREEN,
            },
        ),
        "video_title": r"\textbf{Dynamic synthetic stimuli}",
        "video_frame_color": BLUE,
        "video_loop_count": 5,
    },
}

def _bold_tex(text: str) -> str:
    """Wrap plain text in `\\textbf{}` unless it is already bolded."""
    return text if r"\textbf{" in text else rf"\textbf{{{text}}}"


def title_block(title_text: str, subtitle_text: str | None = None) -> VGroup:
    """Build a chapter-style title and subtitle block."""
    title = Tex(_bold_tex(title_text), color=INK, font_size=34).to_edge(UP, buff=0.34)
    parts = [title]
    if subtitle_text is not None:
        subtitle = Tex(subtitle_text, color=INK, font_size=21)
        subtitle.next_to(title, DOWN, buff=0.14)
        parts.append(subtitle)
    return VGroup(*parts)


def make_callout(text: str, color: str, *, font_size: float = 22) -> VGroup:
    """Build a short concluding takeaway with an underline."""
    line = Tex(text, color=INK, font_size=font_size)
    if line.width > 10.6:
        line.scale_to_fit_width(10.6)
    underline_y = line.get_bottom()[1] - 0.12
    underline = Line(
        np.array([line.get_left()[0], underline_y, 0.0]),
        np.array([line.get_right()[0], underline_y, 0.0]),
        color=color,
        stroke_width=2.0,
    )
    return VGroup(line, underline)


def caption_line(
    text: str,
    *,
    color: str = MGREY,
    font_size: float = 18,
    max_width: float | None = None,
) -> Tex:
    """Build one caption line with optional width capping."""
    line = Tex(text, color=color, font_size=font_size)
    if max_width is not None and line.width > max_width:
        line.scale_to_fit_width(max_width)
    return line


def panel_text(
    text: str,
    *,
    color: str = INK,
    font_size: float = 18,
    max_width: float | None = None,
) -> Tex:
    """Build one wrapped paragraph using the same left-aligned text treatment as the intro."""
    line = Tex(text, color=color, font_size=font_size, tex_environment="flushleft")
    if max_width is not None and line.width > max_width:
        line.scale_to_fit_width(max_width)
    return line


def text_lines(
    rows: tuple[str, ...] | list[str],
    *,
    font_size: float = 18,
    color: str = INK,
    buff: float = 0.06,
    max_width: float | None = None,
) -> VGroup:
    """Build a left-aligned text stack."""
    block = VGroup(
        *[Tex(row, color=color, font_size=font_size) for row in rows]
    ).arrange(DOWN, buff=buff, aligned_edge=LEFT)
    if max_width is not None and block.width > max_width:
        block.scale_to_fit_width(max_width)
    return block


def make_bullet_list(
    bullets: tuple[str | tuple[str, ...], ...] | list[str | tuple[str, ...]],
    *,
    font_size: float = 18,
    color: str = INK,
    bullet_color: str = BLACK,
    width: float = 2.85,
    bullet_radius: float = 0.026,
    line_buff: float = 0.05,
    item_buff: float = 0.19,
) -> VGroup:
    """Build a compact bullet stack."""
    items = VGroup()
    for entry in bullets:
        lines = (entry,) if isinstance(entry, str) else entry
        marker = Dot(radius=bullet_radius, color=bullet_color, stroke_width=0)
        text_block = VGroup(
            *[
                panel_text(
                    line,
                    font_size=font_size,
                    color=color,
                    max_width=width - 0.24,
                )
                for line in lines
            ]
        ).arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
        items.add(VGroup(marker, text_block).arrange(RIGHT, buff=0.10, aligned_edge=UP))
    return items.arrange(DOWN, buff=item_buff, aligned_edge=LEFT)


def simple_divider(width: float, *, color: str = LGREY, stroke_width: float = 1.2) -> Line:
    """Build a centered divider."""
    return Line(LEFT * width / 2, RIGHT * width / 2, color=color, stroke_width=stroke_width)


def load_video_frames(
    video_path: Path,
    *,
    fps: int = 12,
    frame_width_px: int = 420,
) -> list[np.ndarray]:
    """Decode a short mp4 into cached RGBA frames for lightweight playback."""
    stat = video_path.stat()
    cache_key = (
        str(video_path.resolve()),
        int(stat.st_mtime_ns),
        int(stat.st_size),
        fps,
        frame_width_px,
    )
    cached = _VIDEO_FRAME_CACHE.get(cache_key)
    if cached is not None:
        return cached

    digest = hashlib.sha1(
        f"{video_path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}:{fps}:{frame_width_px}".encode()
    ).hexdigest()[:12]
    frame_dir = Path(tempfile.gettempdir()) / "phd_thesis_conclusion_video_frames" / digest
    frame_pattern = frame_dir / "frame_%04d.png"

    if not any(frame_dir.glob("frame_*.png")):
        frame_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-vf",
                f"fps={fps},scale={frame_width_px}:{frame_width_px}:force_original_aspect_ratio=decrease",
                str(frame_pattern),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    frame_paths = sorted(frame_dir.glob("frame_*.png"))
    if not frame_paths:
        raise RuntimeError(f"No frames extracted from {video_path}")

    frames = [np.asarray(PILImage.open(fp).convert("RGBA")) for fp in frame_paths]
    _VIDEO_FRAME_CACHE[cache_key] = frames
    return frames


def video_mobject(
    video_path: Path,
    *,
    width: float,
    fps: int = 12,
    frame_width_px: int = 420,
    loop_count: int | None = None,
) -> ImageMobject:
    """Create a looping video mobject from cached frame arrays."""
    frames = load_video_frames(video_path, fps=fps, frame_width_px=frame_width_px)
    mob = ImageMobject(frames[0]).scale_to_fit_width(width)
    elapsed = {"t": 0.0}
    total_frames = len(frames) * loop_count if loop_count is not None else None

    def _update_frame(m: ImageMobject, dt: float) -> None:
        elapsed["t"] += dt
        frame_idx = int(elapsed["t"] * fps)
        if total_frames is None:
            idx = frame_idx % len(frames)
        else:
            idx = min(frame_idx, total_frames - 1) % len(frames)
        center = m.get_center()
        next_frame = ImageMobject(frames[idx]).scale_to_fit_width(width).move_to(center)
        m.become(next_frame)

    mob.add_updater(_update_frame)
    return mob


def make_video_card(
    video_path: Path,
    *,
    side: float,
    accent: str,
    fps: int = 12,
    frame_width_px: int = 220,
    loop_count: int | None = None,
    stroke_width: float = 1.3,
    corner_radius: float = 0.10,
) -> Group:
    """Build one lightly framed looping-video tile."""
    frame = RoundedRectangle(
        corner_radius=corner_radius,
        width=side,
        height=side,
        stroke_color=accent,
        stroke_width=stroke_width,
    )
    frame.set_fill(WHITE, opacity=0.03)
    clip = video_mobject(
        video_path,
        width=side - 0.10,
        fps=fps,
        frame_width_px=frame_width_px,
        loop_count=loop_count,
    )
    clip.move_to(frame.get_center())
    return Group(frame, clip)


def video_duration_seconds(
    video_path: Path,
    *,
    fps: int,
    frame_width_px: int,
) -> float:
    """Return the decoded clip duration at the target playback fps."""
    return len(load_video_frames(video_path, fps=fps, frame_width_px=frame_width_px)) / fps


def split_columns(
    left: Mobject,
    right: Mobject,
    *,
    buff: float = 0.48,
    divider_color: str = LGREY,
) -> Group:
    """Arrange two columns with a central divider."""
    divider = Line(UP * 0.5, DOWN * 0.5, color=divider_color, stroke_width=1.2)
    divider.set(height=max(left.height, right.height) - 0.06)
    return Group(left, divider, right).arrange(RIGHT, buff=buff, aligned_edge=UP)


def make_section_block(
    heading: str,
    rows: tuple[str, ...] | list[str],
    *,
    accent: str,
    width: float = 4.4,
    heading_size: float = 22,
    line_size: float = 18,
    show_divider: bool = True,
    text_align: str = "left",
    dot_side: str = "left",
) -> VGroup:
    """Build one unframed section block with the intro's lighter divider style."""
    heading_text = Tex(rf"\textbf{{{heading}}}", color=INK, font_size=heading_size)
    heading_dot = Dot(radius=0.045, color=accent)
    heading_items = (
        (heading_dot, heading_text)
        if dot_side == "left"
        else (heading_text, heading_dot)
    )
    heading_row = VGroup(*heading_items).arrange(RIGHT, buff=0.12)
    if heading_row.width > width:
        heading_row.scale_to_fit_width(width)
    body = text_lines(rows, font_size=line_size, color=INK, buff=0.08, max_width=width)
    align_edge = LEFT if text_align == "left" else RIGHT
    if text_align == "right":
        for line in body:
            line.align_to(body, RIGHT)
    parts: list[Mobject] = [heading_row, body]
    if show_divider:
        divider = simple_divider(
            max(heading_row.width, body.width, width * 0.68),
            stroke_width=1.0,
        )
        divider.align_to(body, align_edge)
        divider.set_stroke(opacity=0.72)
        parts.append(divider)
    return VGroup(*parts).arrange(DOWN, buff=0.10, aligned_edge=align_edge)


def make_question_panel(
    label: str,
    heading: str,
    question_text: str,
    *,
    accent: str,
    width: float = 3.08,
) -> VGroup:
    """Build one unframed research-question panel using the intro's labels and accents."""
    header = VGroup(
        Dot(radius=0.038, color=accent, stroke_width=0),
        Tex(label, color=accent, font_size=14),
    ).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)
    if header.width > width:
        header.scale_to_fit_width(width)
    title = Tex(rf"\textbf{{{heading}}}", color=INK, font_size=20)
    if title.width > width:
        title.scale_to_fit_width(width)
    divider = Line(ORIGIN, RIGHT * max(width * 0.86, title.width), color=LGREY, stroke_width=1.0)
    divider.set_stroke(opacity=0.72)
    divider.align_to(title, LEFT)
    body = panel_text(question_text, font_size=16.8, max_width=width)
    return VGroup(header, title, divider, body).arrange(DOWN, buff=0.10, aligned_edge=LEFT)


def make_result_panel(
    label: str,
    heading: str,
    answer_text: str,
    *,
    accent: str,
    label_text: str = r"\textbf{Answer}",
    width: float = 3.08,
) -> VGroup:
    """Build one concise unframed answer block for a research question."""
    header = VGroup(
        Dot(radius=0.038, color=accent, stroke_width=0),
        Tex(label, color=accent, font_size=14),
    ).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)
    if header.width > width:
        header.scale_to_fit_width(width)
    title = Tex(rf"\textbf{{{heading}}}", color=INK, font_size=20)
    if title.width > width:
        title.scale_to_fit_width(width)
    divider = Line(ORIGIN, RIGHT * max(width * 0.86, title.width), color=LGREY, stroke_width=1.0)
    divider.set_stroke(opacity=0.72)
    divider.align_to(title, LEFT)
    answer = caption_line(label_text, color=accent, font_size=15)
    body = panel_text(answer_text, font_size=16.2, max_width=width)
    return VGroup(header, title, divider, answer, body).arrange(
        DOWN,
        buff=0.10,
        aligned_edge=LEFT,
    )


def three_panel_row(left: Mobject, middle: Mobject, right: Mobject, *, buff: float = 0.34) -> Group:
    """Arrange three panels with vertical dividers."""
    divider_height = max(left.height, middle.height, right.height) - 0.06
    dividers = VGroup(
        Line(UP * divider_height / 2, DOWN * divider_height / 2, color=LGREY, stroke_width=1.2),
        Line(UP * divider_height / 2, DOWN * divider_height / 2, color=LGREY, stroke_width=1.2),
    )
    row = Group(left, dividers[0], middle, dividers[1], right).arrange(
        RIGHT,
        buff=buff,
        aligned_edge=UP,
    )
    max_width = config.frame_width - 1.0
    if row.width > max_width:
        row.scale_to_fit_width(max_width)
    return row


def make_takeaway(
    text: str,
    color: str,
    *,
    anchor: Mobject,
    font_size: float,
    buff: float = 0.34,
) -> VGroup:
    """Build and place a concluding takeaway relative to the main content block."""
    takeaway = make_callout(text, color, font_size=font_size)
    takeaway.scale_to_fit_width(min(takeaway.width, anchor.width + 0.15))
    takeaway.next_to(anchor, DOWN, buff=buff)
    takeaway.set_x(anchor.get_center()[0])
    return takeaway


def make_section_column(
    blocks: tuple[dict[str, object], ...],
    *,
    width: float,
    buff: float = 0.24,
) -> VGroup:
    """Stack preconfigured section blocks into one aligned conclusion column."""
    return VGroup(
        *[
            make_section_block(
                block["heading"],
                block["rows"],
                accent=block["accent"],
                width=width,
            )
            for block in blocks
        ]
    ).arrange(DOWN, buff=buff, aligned_edge=LEFT)


def _conclusion_project_summary_model_icon(*, height: float = 0.58) -> SVGMobject:
    """Return the project-summary neural-network icon in soft grey."""
    svg = SVGMobject(str(_CONCLUSION_PROJECT_SUMMARY_MODEL_ICON_PATH), use_svg_cache=False)
    svg.scale_to_fit_height(height)

    if len(svg.submobjects) >= 19:
        left_edges = VGroup(*svg.submobjects[:6])
        right_edges = VGroup(*svg.submobjects[6:12])
        input_nodes = VGroup(*svg.submobjects[12:14])
        output_nodes = VGroup(*svg.submobjects[14:16])
        hidden_nodes = VGroup(*svg.submobjects[16:19])

        for edge_group in (left_edges, right_edges):
            edge_group.set_stroke(SOFT_GREY, width=1.8, opacity=0.42)
            edge_group.set_fill(opacity=0.0)

        for node_group in (input_nodes, hidden_nodes, output_nodes):
            node_group.set_fill(SOFT_GREY, opacity=0.58)
            node_group.set_stroke(SOFT_GREY, width=1.1, opacity=0.18)
    else:
        svg.set_stroke(SOFT_GREY, opacity=0.50, width=1.8)
        svg.set_fill(SOFT_GREY, opacity=0.58)

    return svg


def _make_conclusion_project_summary_step(
    icon_path: Path,
    heading: str,
    rows: tuple[str | tuple[str, ...], ...],
    *,
    width: float,
) -> Group:
    """Build one step in the project-summary flow."""
    if icon_path == _CONCLUSION_PROJECT_SUMMARY_MODEL_ICON_PATH:
        icon = _conclusion_project_summary_model_icon()
    elif icon_path.suffix.lower() == ".svg":
        icon = SVGMobject(str(icon_path))
        icon.scale_to_fit_height(0.58)
    else:
        icon = ImageMobject(str(icon_path))
        icon.scale_to_fit_height(0.58)

    heading_tex = Tex(rf"\textbf{{{heading}}}", color=INK, font_size=22)
    body = make_bullet_list(
        rows,
        font_size=16,
        color=INK,
        width=width - 0.08,
        bullet_radius=0.020,
        line_buff=0.06,
        item_buff=0.12,
    )
    body.next_to(heading_tex, DOWN, buff=0.10, aligned_edge=LEFT)
    body.set_x(heading_tex.get_center()[0])
    text_block = Group(heading_tex, body)
    icon.next_to(text_block, UP, buff=0.18)
    icon.set_x(heading_tex.get_center()[0])
    return Group(icon, text_block)


def _make_conclusion_project_summary_bracket(
    left: Mobject,
    label: str,
    *,
    y: float,
    right: Mobject | None = None,
    color: str = SOFT_GREY,
) -> VGroup:
    """Build the Study 1 / Study 2 bracket used in the summary flow."""
    if right is None:
        right = left
    pad = 0.10
    tick = 0.16
    x0 = left.get_left()[0] - pad
    x1 = right.get_right()[0] + pad
    bracket = VGroup(
        Line(
            np.array([x0, y + tick, 0.0]),
            np.array([x0, y, 0.0]),
            color=color,
            stroke_width=1.05,
        ),
        Line(
            np.array([x0, y, 0.0]),
            np.array([x1, y, 0.0]),
            color=color,
            stroke_width=1.05,
        ),
        Line(
            np.array([x1, y, 0.0]),
            np.array([x1, y + tick, 0.0]),
            color=color,
            stroke_width=1.05,
        ),
    )
    label_tex = Tex(rf"\textbf{{{label}}}", color=INK, font_size=18)
    label_tex.next_to(bracket, DOWN, buff=0.08)
    return VGroup(bracket, label_tex)


def _make_conclusion_project_summary_stimulus_grid(
    stimulus_codes: tuple[str, ...],
    *,
    image_height: float = 0.24,
    image_buff: float = 0.014,
    row_buff: float = 0.030,
) -> Group:
    """Build the stimulus-result grid shown under the first summary step."""
    rows = Group()
    for code in stimulus_codes:
        images = Group(
            *[
                ImageMobject(str(_CONCLUSION_PROJECT_SUMMARY_STIM_DIR / f"{code}-{idx:02d}.png"))
                for idx in range(10)
            ]
        )
        for image in images:
            image.scale_to_fit_height(image_height)
        images.arrange(RIGHT, buff=image_buff)

        frame = SurroundingRectangle(
            images,
            color=LGREY,
            buff=0.025,
            stroke_width=0.9,
            corner_radius=0.05,
        )
        frame.set_stroke(opacity=0.72)
        frame.set_fill(WHITE, opacity=0.06)
        rows.add(Group(frame, images))

    rows.arrange(DOWN, buff=row_buff, aligned_edge=LEFT)
    return rows


def _pdf_first_page_to_png(pdf_path: Path) -> str:
    """Convert the first page of a PDF into a PNG snapshot."""
    out_name = f"{pdf_path.stem}_{hashlib.md5(str(pdf_path).encode()).hexdigest()[:10]}.png"
    out_path = str(Path(tempfile.gettempdir()) / out_name)
    if Path(out_path).exists():
        return out_path
    if shutil.which("sips") is not None:
        subprocess.run(
            ["sips", "-s", "format", "png", str(pdf_path), "--out", out_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if Path(out_path).exists():
            return out_path
    if shutil.which("pdftoppm") is not None:
        prefix = str(Path(tempfile.gettempdir()) / f"{Path(out_name).stem}")
        subprocess.run(
            ["pdftoppm", "-png", "-f", "1", "-singlefile", str(pdf_path), prefix],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        alt_path = prefix + ".png"
        if Path(alt_path).exists():
            return alt_path
    if shutil.which("magick") is not None:
        subprocess.run(
            ["magick", "-density", "220", f"{pdf_path}[0]", out_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if Path(out_path).exists():
            return out_path
    raise FileNotFoundError(
        "Could not convert PDF to PNG. Install sips, pdftoppm, or ImageMagick."
    )


def _vector_asset_to_png(vector_path: Path) -> str:
    """Convert an SVG-like vector asset into a cached PNG snapshot."""
    out_name = f"{vector_path.stem}_{hashlib.md5(vector_path.read_bytes()).hexdigest()[:10]}.png"
    out_path = str(Path(tempfile.gettempdir()) / out_name)
    if Path(out_path).exists():
        return out_path
    if shutil.which("magick") is not None:
        subprocess.run(
            ["magick", "-density", "220", str(vector_path), out_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if Path(out_path).exists():
            return out_path
    if shutil.which("qlmanage") is not None:
        tmp_dir = Path(tempfile.gettempdir()) / "phd_thesis_vector_previews"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["qlmanage", "-t", "-s", "2048", "-o", str(tmp_dir), str(vector_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        preview_path = tmp_dir / f"{vector_path.name}.png"
        if preview_path.exists():
            preview_path.replace(out_path)
            return out_path
    raise FileNotFoundError("Could not convert vector asset to PNG. Install ImageMagick or qlmanage.")


def _make_conclusion_project_summary_validation_results() -> Group:
    """Build the behavioural-validation result pair shown under the middle step."""
    heatmap = ImageMobject(_pdf_first_page_to_png(_CONCLUSION_PROJECT_SUMMARY_VALIDATION_HEATMAP_PDF))
    behaviour = ImageMobject(str(_CONCLUSION_PROJECT_SUMMARY_BEHAVIOUR_BLOCK))
    return _make_conclusion_project_summary_results_pair(heatmap, behaviour)


def _make_conclusion_project_summary_results_pair(left: Mobject, right: Mobject) -> Group:
    """Build a lightly framed two-row result pair."""
    def _normalize_result_visual(visual: Mobject) -> Group:
        box = Rectangle(
            width=_CONCLUSION_PROJECT_SUMMARY_RESULT_WIDTH,
            height=_CONCLUSION_PROJECT_SUMMARY_RESULT_HEIGHT,
            stroke_opacity=0.0,
            fill_opacity=0.0,
        )
        if visual.width > 0 and visual.height > 0:
            visual.scale(
                min(
                    _CONCLUSION_PROJECT_SUMMARY_RESULT_WIDTH / visual.width,
                    _CONCLUSION_PROJECT_SUMMARY_RESULT_HEIGHT / visual.height,
                )
            )
        visual.move_to(box.get_center())
        frame = SurroundingRectangle(
            box,
            color=LGREY,
            buff=_CONCLUSION_PROJECT_SUMMARY_RESULT_FRAME_BUFF,
            stroke_width=0.9,
            corner_radius=0.05,
        )
        frame.set_stroke(opacity=0.72)
        frame.set_fill(WHITE, opacity=0.06)
        return Group(frame, visual)

    pair = Group(
        _normalize_result_visual(left),
        _normalize_result_visual(right),
    ).arrange(DOWN, buff=_CONCLUSION_PROJECT_SUMMARY_RESULT_GAP)
    return pair


def _make_conclusion_project_summary_neuro_results() -> Group:
    """Build the neuroimaging-result pair shown under the third step."""
    timeres = ImageMobject(str(_CONCLUSION_PROJECT_SUMMARY_NEURO_TIMERES_PNG))
    tempgen = ImageMobject(_vector_asset_to_png(_CONCLUSION_PROJECT_SUMMARY_NEURO_TEMPGEN))
    return _make_conclusion_project_summary_results_pair(timeres, tempgen)


# ── Layout builders ───────────────────────────────────────────────────────────

def _build_conclusion_three_panel_layout(
    title_text: str,
    subtitle_text: str,
    left_panel: Mobject,
    middle_panel: Mobject,
    right_panel: Mobject,
    *,
    row_buff: float,
    title_buff: float,
    callout_text: str | None,
    callout_color: str,
    callout_font_size: float,
) -> dict[str, Mobject]:
    """Build a standard three-panel conclusion slide layout."""
    title = title_block(title_text, subtitle_text)
    content = three_panel_row(left_panel, middle_panel, right_panel, buff=row_buff)
    content.next_to(title, DOWN, buff=title_buff)
    state: dict[str, Mobject | None] = {
        "title": title,
        "left_panel": left_panel,
        "middle_panel": middle_panel,
        "right_panel": right_panel,
        "content": content,
    }
    if callout_text is None:
        state["callout"] = None
        state["final_group"] = Group(title, content)
        return state

    callout = make_takeaway(
        callout_text,
        callout_color,
        anchor=content,
        font_size=callout_font_size,
    )
    state["callout"] = callout
    state["final_group"] = Group(title, content, callout)
    return state


def _build_conclusion_two_column_layout(
    title_text: str,
    subtitle_text: str,
    left_column: Mobject,
    right_column: Mobject,
    *,
    column_buff: float,
    title_buff: float,
    callout_text: str | None,
    callout_color: str,
    callout_font_size: float,
) -> dict[str, Mobject]:
    """Build a standard two-column conclusion slide layout."""
    title = title_block(title_text, subtitle_text)
    content = split_columns(left_column, right_column, buff=column_buff)
    content.next_to(title, DOWN, buff=title_buff)
    state: dict[str, Mobject | None] = {
        "title": title,
        "left_column": left_column,
        "divider": content[1],
        "right_column": right_column,
        "content": content,
    }
    if callout_text is None:
        state["callout"] = None
        state["final_group"] = Group(title, content)
        return state

    callout = make_takeaway(
        callout_text,
        callout_color,
        anchor=content,
        font_size=callout_font_size,
    )
    state["callout"] = callout
    state["final_group"] = Group(title, content, callout)
    return state


def _build_conclusion_questions_layout() -> dict[str, Mobject]:
    """Build the opening conclusion slide that restates the three questions."""
    slide = _CONCLUSION_SLIDES["questions"]
    question_panels = [
        make_question_panel(
            panel["label"],
            panel["title"],
            panel["question"],
            accent=panel["accent"],
        )
        for panel in slide["panels"]
    ]
    return _build_conclusion_three_panel_layout(
        slide["title"],
        slide["subtitle"],
        question_panels[0],
        question_panels[1],
        question_panels[2],
        row_buff=0.28,
        title_buff=0.72,
        callout_text=slide.get("callout"),
        callout_color=RQ_BLUE,
        callout_font_size=20,
    )


def _build_conclusion_approach_layout() -> dict[str, Mobject]:
    """Build the project-summary slide with the three-step study flow."""
    slide = _CONCLUSION_SLIDES["summary"]
    title = title_block(slide["title"], slide["subtitle"])

    steps = Group(
        *[
            _make_conclusion_project_summary_step(
                step["icon_path"],
                step["heading"],
                step["rows"],
                width=step["width"],
            )
            for step in slide["steps"]
        ]
    )
    steps.arrange(RIGHT, buff=1.35, aligned_edge=UP)
    if steps.width > config.frame_width - 1.90:
        steps.scale_to_fit_width(config.frame_width - 1.90)
        steps.arrange(RIGHT, buff=1.10, aligned_edge=UP)

    arrow_y = float(np.mean([step[1][0].get_center()[1] for step in steps]))
    arrows = VGroup(
        *[
            Arrow(
                np.array([steps[idx].get_right()[0] + 0.18, arrow_y, 0.0]),
                np.array([steps[idx + 1].get_left()[0] - 0.18, arrow_y, 0.0]),
                color=SOFT_GREY,
                stroke_width=1.5,
                buff=0.0,
                tip_length=0.14,
                tip_shape=StealthTip,
            )
            for idx in range(len(steps) - 1)
        ]
    )

    bracket_y = min(step.get_bottom()[1] for step in steps) - 0.52
    placement_study_groups = VGroup(
        *[
            _make_conclusion_project_summary_bracket(
                steps[bracket["start"]],
                bracket["label"],
                y=bracket_y,
                right=steps[bracket["end"]],
            )
            for bracket in slide["brackets"]
        ]
    )
    content = Group(steps, arrows, placement_study_groups)
    content.move_to(ORIGIN)

    content_shift = UP * float(slide["content_shift_up"])
    bracket_shift = DOWN * float(slide["bracket_shift_down"])
    placement_bracket_top = (
        placement_study_groups[0][0].copy().shift(bracket_shift).get_top()[1]
    )

    def _place_summary_insert(
        mob: Mobject,
        step_index: int,
        *,
        max_width: float | None = None,
    ) -> Mobject:
        target_step = steps[step_index].copy().shift(content_shift)
        available_top = target_step.get_bottom()[1] - 0.08
        available_bottom = placement_bracket_top + 0.08
        available_height = available_top - available_bottom
        max_width = (
            steps[step_index].width + 0.02 if max_width is None else max_width
        )
        if mob.width > max_width:
            mob.scale_to_fit_width(max_width)
        if available_height > 0.0 and mob.height > available_height:
            mob.scale_to_fit_height(available_height)
        if mob.width > max_width:
            mob.scale_to_fit_width(max_width)
        mob.move_to(
            np.array(
                [
                    steps[step_index].get_center()[0],
                    (available_top + available_bottom) / 2,
                    0.0,
                ]
            )
        )
        return mob

    stimulus_grid = _place_summary_insert(
        _make_conclusion_project_summary_stimulus_grid(slide["stimulus_codes"]),
        0,
    )
    validation_results = _place_summary_insert(
        _make_conclusion_project_summary_validation_results(),
        1,
        max_width=_CONCLUSION_PROJECT_SUMMARY_RESULT_PAIR_MAX_WIDTH,
    )
    neuro_results = _place_summary_insert(
        _make_conclusion_project_summary_neuro_results(),
        2,
        max_width=_CONCLUSION_PROJECT_SUMMARY_RESULT_PAIR_MAX_WIDTH,
    )
    summary_inserts_by_step = {
        0: stimulus_grid,
        1: validation_results,
        2: neuro_results,
    }
    study_groups = VGroup(
        *[
            _make_conclusion_project_summary_bracket(
                Group(
                    *[
                        steps[idx]
                        for idx in range(bracket["start"], bracket["end"] + 1)
                    ],
                    *[
                        summary_inserts_by_step[idx]
                        for idx in range(bracket["start"], bracket["end"] + 1)
                        if idx in summary_inserts_by_step
                    ],
                ),
                label=bracket["label"],
                y=bracket_y,
            )
            for bracket in slide["brackets"]
        ]
    )
    content = Group(steps, arrows, study_groups)

    return {
        "title": title,
        "steps": steps,
        "arrows": arrows,
        "study_groups": study_groups,
        "content": content,
        "stimulus_grid": stimulus_grid,
        "validation_results": validation_results,
        "neuro_results": neuro_results,
        "content_shift": content_shift,
        "bracket_shift": bracket_shift,
    }


def _build_conclusion_theoretical_implications_layout() -> dict[str, Mobject]:
    """Build the slide summarizing the project's theoretical implications."""
    slide = _CONCLUSION_SLIDES["theoretical_implications"]
    title = title_block(slide["title"], slide["subtitle"])
    left_width = 3.55
    middle_width = 0.90
    right_width = 4.95
    row_buff = 0.32

    left_cells = VGroup()
    middle_cells = VGroup()
    right_cells = VGroup()
    for panel, bullets in zip(
        _CONCLUSION_000_QUESTION_PANELS,
        _CONCLUSION_001_THEORETICAL_IMPLICATION_BULLETS,
    ):
        left_block = VGroup(
            VGroup(
                Dot(radius=0.038, color=panel["accent"], stroke_width=0),
                Tex(panel["label"], color=panel["accent"], font_size=16),
            ).arrange(RIGHT, buff=0.10, aligned_edge=DOWN),
            Tex(rf"\textbf{{{panel['title']}}}", color=INK, font_size=24),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        if left_block.width > left_width - 0.12:
            left_block.scale_to_fit_width(left_width - 0.12)

        arrow = Arrow(
            LEFT * 0.22,
            RIGHT * 0.22,
            color=panel["accent"],
            stroke_width=1.8,
            buff=0.0,
            tip_length=0.12,
            tip_shape=StealthTip,
        )

        bullet_list = make_bullet_list(
            bullets,
            font_size=16.8,
            width=right_width,
            bullet_radius=0.025,
            line_buff=0.04,
            item_buff=0.14,
        )
        row_height = max(left_block.height, bullet_list.height, 0.48)

        left_cell_frame = Rectangle(
            width=left_width,
            height=row_height,
            stroke_opacity=0.0,
            fill_opacity=0.0,
        )
        left_block.move_to(left_cell_frame.get_center())
        left_block.align_to(left_cell_frame, LEFT)
        left_block.shift(RIGHT * 0.02)
        left_cells.add(VGroup(left_cell_frame, left_block))

        middle_cell_frame = Rectangle(
            width=middle_width,
            height=row_height,
            stroke_opacity=0.0,
            fill_opacity=0.0,
        )
        arrow.move_to(middle_cell_frame.get_center())
        middle_cells.add(VGroup(middle_cell_frame, arrow))

        right_cell_frame = Rectangle(
            width=right_width,
            height=row_height,
            stroke_opacity=0.0,
            fill_opacity=0.0,
        )
        bullet_list.move_to(right_cell_frame.get_center())
        bullet_list.align_to(right_cell_frame, LEFT)
        bullet_list.shift(RIGHT * 0.02)
        right_cells.add(VGroup(right_cell_frame, bullet_list))

    question_rows = VGroup(
        *[
            VGroup(left_cells[idx], middle_cells[idx], right_cells[idx]).arrange(
                RIGHT,
                buff=0.18,
                aligned_edge=UP,
            )
            for idx in range(len(left_cells))
        ]
    )
    row_dividers = VGroup(
        *[
            simple_divider(question_rows[0].width, stroke_width=1.0)
            for _ in range(len(question_rows) - 1)
        ]
    )
    for divider in row_dividers:
        divider.set_stroke(opacity=0.72)

    stacked_items: list[Mobject] = []
    for idx, row in enumerate(question_rows):
        stacked_items.append(row)
        if idx < len(row_dividers):
            stacked_items.append(row_dividers[idx])

    content = VGroup(*stacked_items).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
    content.next_to(title, DOWN, buff=0.28)
    content.set_x(0.0)

    take_home_label = caption_line(r"\textbf{Take-home messages}", color=DARK_PURPLE, font_size=16)
    take_home_text = make_bullet_list(
        slide["take_home_bullets"],
        font_size=16.0,
        color=INK,
        bullet_color=DARK_PURPLE,
        width=7.65,
        bullet_radius=0.024,
        line_buff=0.04,
        item_buff=0.10,
    )
    take_home = VGroup(take_home_label, take_home_text).arrange(
        DOWN,
        buff=0.07,
        aligned_edge=LEFT,
    )
    take_home_frame = RoundedRectangle(
        corner_radius=0.12,
        width=take_home.width + 0.44,
        height=take_home.height + 0.30,
        stroke_color=DARK_PURPLE,
        stroke_width=1.45,
    )
    take_home_frame.set_fill(WHITE, opacity=0.0)
    take_home.move_to(take_home_frame.get_center())
    take_home.align_to(take_home_frame, LEFT)
    take_home.shift(RIGHT * 0.10)
    take_home_group = VGroup(take_home_frame, take_home)
    take_home_group.next_to(content, DOWN, buff=0.16)
    take_home_group.set_x(content.get_center()[0])

    callout = VGroup(take_home_group)
    body = Group(content, callout)
    body.shift(DOWN * 0.41)

    return {
        "title": title,
        "content": content,
        "callout": callout,
        "final_group": Group(title, content, callout),
    }


def _build_conclusion_limitations_layout() -> dict[str, Mobject]:
    """Build the slide summarizing the project's main limitations."""
    slide = _CONCLUSION_SLIDES["limitations"]
    block_width = 4.80
    row_buff = 0.34
    column_buff = 0.52
    center_inset = 0.12
    divider_color = LGREY
    divider_stroke_width = 1.2
    divider_opacity = 0.72

    left_blocks = [
        make_section_block(
            block["heading"],
            block["rows"],
            accent=block["accent"],
            width=block_width,
            show_divider=False,
            text_align="right",
            dot_side="right",
        )
        for block in slide["left_blocks"]
    ]
    right_blocks = [
        make_section_block(
            block["heading"],
            block["rows"],
            accent=block["accent"],
            width=block_width,
            show_divider=False,
            text_align="left",
            dot_side="left",
        )
        for block in slide["right_blocks"]
    ]
    row_heights = [
        max(left_block.height, right_block.height)
        for left_block, right_block in zip(left_blocks, right_blocks)
    ]

    def _place_block_in_cell(
        block: Mobject,
        *,
        cell_height: float,
        side: str,
    ) -> VGroup:
        cell = Rectangle(
            width=block_width,
            height=cell_height,
            stroke_opacity=0.0,
            fill_opacity=0.0,
        )
        if side == "left":
            block.align_to(cell, RIGHT)
            block.shift(LEFT * center_inset)
        else:
            block.align_to(cell, LEFT)
            block.shift(RIGHT * center_inset)
        block.set_y(cell.get_center()[1])
        return VGroup(cell, block)

    left_column = VGroup(
        *[
            _place_block_in_cell(block, cell_height=cell_height, side="left")
            for block, cell_height in zip(left_blocks, row_heights)
        ]
    ).arrange(DOWN, buff=row_buff)
    right_column = VGroup(
        *[
            _place_block_in_cell(block, cell_height=cell_height, side="right")
            for block, cell_height in zip(right_blocks, row_heights)
        ]
    ).arrange(DOWN, buff=row_buff)

    title = title_block(slide["title"], slide["subtitle"])
    columns = Group(left_column, right_column).arrange(RIGHT, buff=column_buff)
    columns.move_to(ORIGIN)
    junction_x = 0.0
    junction_y = (left_column[0].get_bottom()[1] + left_column[1].get_top()[1]) / 2
    vertical_line = Line(
        np.array([junction_x, columns.get_top()[1], 0.0]),
        np.array([junction_x, columns.get_bottom()[1], 0.0]),
        color=divider_color,
        stroke_width=divider_stroke_width,
    )
    horizontal_line = Line(
        np.array([left_column.get_left()[0], junction_y, 0.0]),
        np.array([right_column.get_right()[0], junction_y, 0.0]),
        color=divider_color,
        stroke_width=divider_stroke_width,
    )
    junction_dot = Dot(
        point=np.array([junction_x, junction_y, 0.0]),
        radius=0.040,
        color=divider_color,
        stroke_width=0.0,
    )
    divider = VGroup(vertical_line, horizontal_line, junction_dot)
    divider.set_stroke(opacity=divider_opacity)
    junction_dot.set_fill(divider_color, opacity=1.0)
    content = Group(left_column, divider, right_column)
    state: dict[str, Mobject | None] = {
        "title": title,
        "left_column": left_column,
        "divider": divider,
        "right_column": right_column,
        "content": content,
        "callout": None,
        "final_group": Group(title, content),
    }
    return state


def _build_conclusion_future_directions_layout() -> dict[str, Mobject]:
    """Build the future-directions slide with open questions and looping exemplar videos."""
    slide = _CONCLUSION_SLIDES["future_directions"]
    left_column = make_section_column(slide["left_blocks"], width=4.55, buff=0.28)
    video_loop_count = int(slide["video_loop_count"])

    def _anchor_video(filename: str) -> Path:
        path = _FUTURE_DIRECTIONS_ANCHOR_VIDEO_DIR / filename
        return path if path.exists() else _FISH_VIDEO_PATH

    video_specs = {
        "fish": {
            "path": _FISH_VIDEO_PATH,
            "width": 1.54,
            "frame_width_px": 320,
        },
        "cat": {
            "path": _anchor_video("anchor-animal-cat.mp4"),
            "width": 0.82,
            "frame_width_px": 180,
        },
        "coffee_mug": {
            "path": _anchor_video("anchor-item-coffee_mug.mp4"),
            "width": 0.80,
            "frame_width_px": 180,
        },
        "sofa": {
            "path": _anchor_video("anchor-item-sofa.mp4"),
            "width": 0.84,
            "frame_width_px": 180,
        },
        "sailboat": {
            "path": _anchor_video("anchor-vehicle-sailboat.mp4"),
            "width": 0.88,
            "frame_width_px": 180,
        },
        "palm": {
            "path": _anchor_video("anchor-plant-palm.mp4"),
            "width": 0.84,
            "frame_width_px": 180,
        },
        "polar_iceberg": {
            "path": _anchor_video("anchor-landscape_element-polar_iceberg.mp4"),
            "width": 0.92,
            "frame_width_px": 180,
        },
        "bristlecone": {
            "path": _anchor_video("anchor-plant-bristlecone.mp4"),
            "width": 0.88,
            "frame_width_px": 180,
        },
        "campervan": {
            "path": _anchor_video("anchor-vehicle-campervan.mp4"),
            "width": 0.88,
            "frame_width_px": 180,
        },
        "modern_building": {
            "path": _anchor_video("anchor-building-modern_building.mp4"),
            "width": 0.92,
            "frame_width_px": 180,
        },
        "parrot": {
            "path": _anchor_video("anchor-animal-parrot.mp4"),
            "width": 0.78,
            "frame_width_px": 180,
        },
    }

    video_stage = Rectangle(
        width=4.48,
        height=4.28,
        stroke_width=0,
        fill_opacity=0.0,
    )

    video_cards = {
        key: video_mobject(
            spec["path"],
            width=spec["width"],
            fps=12,
            frame_width_px=spec["frame_width_px"],
            loop_count=video_loop_count,
        )
        for key, spec in video_specs.items()
    }
    max_video_play_time = max(
        video_duration_seconds(
            spec["path"],
            fps=12,
            frame_width_px=spec["frame_width_px"],
        )
        for spec in video_specs.values()
    ) * video_loop_count
    cloud_transforms = {
        "fish": {
            "shift": ORIGIN,
            "rotation": -2 * DEGREES,
            "z_index": 4,
        },
        "cat": {
            "shift": LEFT * 1.32 + UP * 1.30,
            "rotation": -5 * DEGREES,
            "z_index": 3,
        },
        "bristlecone": {
            "shift": LEFT * 0.36 + UP * 1.58,
            "rotation": 3 * DEGREES,
            "z_index": 3,
        },
        "parrot": {
            "shift": RIGHT * 0.70 + UP * 1.54,
            "rotation": -7 * DEGREES,
            "z_index": 3,
        },
        "coffee_mug": {
            "shift": RIGHT * 1.56 + UP * 1.18,
            "rotation": 4 * DEGREES,
            "z_index": 3,
        },
        "polar_iceberg": {
            "shift": LEFT * 1.74 + UP * 0.16,
            "rotation": -4 * DEGREES,
            "z_index": 3,
        },
        "modern_building": {
            "shift": RIGHT * 1.78 + UP * 0.22,
            "rotation": 2 * DEGREES,
            "z_index": 3,
        },
        "sailboat": {
            "shift": LEFT * 1.62 + DOWN * 1.04,
            "rotation": 4 * DEGREES,
            "z_index": 3,
        },
        "sofa": {
            "shift": LEFT * 0.56 + DOWN * 1.54,
            "rotation": 5 * DEGREES,
            "z_index": 3,
        },
        "campervan": {
            "shift": RIGHT * 0.54 + DOWN * 1.56,
            "rotation": -3 * DEGREES,
            "z_index": 3,
        },
        "palm": {
            "shift": RIGHT * 1.56 + DOWN * 1.20,
            "rotation": -6 * DEGREES,
            "z_index": 3,
        },
    }
    for key, card in video_cards.items():
        card.move_to(video_stage.get_center() + cloud_transforms[key]["shift"])
        card.rotate(cloud_transforms[key]["rotation"])
        card.set_z_index(cloud_transforms[key]["z_index"])

    title = title_block(slide["title"], slide["subtitle"])
    video_title = Tex(slide["video_title"], color=INK, font_size=22)
    video_stack = Group(video_stage, *video_cards.values())

    title_gap = 0.42
    bottom_margin = 0.56
    divider_gap = 0.58
    left_padding = 0.18
    content_top_y = title.get_bottom()[1] - title_gap
    content_bottom_y = -config.frame_height / 2 + bottom_margin
    content_height = content_top_y - content_bottom_y
    content_center_y = (content_top_y + content_bottom_y) / 2
    section_width = (config.frame_width - 1.80 - divider_gap) / 2

    left_section = Rectangle(
        width=section_width,
        height=content_height,
        stroke_opacity=0.0,
        fill_opacity=0.0,
    )
    right_section = Rectangle(
        width=section_width,
        height=content_height,
        stroke_opacity=0.0,
        fill_opacity=0.0,
    )
    left_section.move_to(
        np.array([-(divider_gap / 2 + section_width / 2), content_center_y, 0.0])
    )
    right_section.move_to(
        np.array([divider_gap / 2 + section_width / 2, content_center_y, 0.0])
    )

    left_column.move_to(left_section.get_center())
    left_column.align_to(left_section, LEFT)
    left_column.shift(RIGHT * left_padding)

    video_stack.move_to(right_section.get_center())
    video_title.next_to(video_stack, UP, buff=0.18)
    video_title.set_x(video_stack.get_center()[0])
    right_column = Group(video_title, video_stack)

    divider_height = max(left_column.height, video_stack.height) + 0.14
    divider = Line(
        np.array([0.0, content_center_y + divider_height / 2, 0.0]),
        np.array([0.0, content_center_y - divider_height / 2, 0.0]),
        color=LGREY,
        stroke_width=1.2,
    )
    divider.set_stroke(opacity=0.72)

    content = Group(left_section, right_section, left_column, divider, right_column)
    state: dict[str, Mobject | None] = {
        "title": title,
        "left_column": left_column,
        "divider": divider,
        "right_column": right_column,
        "content": content,
        "callout": None,
        "final_group": Group(title, content),
    }
    state.update(
        {
            "video_title": video_title,
            "video_frame": video_stage,
            "video_cards": Group(*video_cards.values()),
            "video_stack": video_stack,
            "target_video_play_time": max_video_play_time,
        }
    )
    return state


class ConclusionQuestions(_ConclusionNumberedScene, Scene):
    """Legacy slide that restates the thesis questions."""

    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_conclusion_questions_layout()
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(state["content"], shift=UP * 0.05), run_time=0.95)
        if state["callout"] is not None:
            self.play(FadeIn(state["callout"], shift=UP * 0.04), run_time=0.55)
        self.wait(3.00)


class ConclusionApproach(_ConclusionNumberedScene, Scene):
    """Chapter 5.1 - summarise the project."""

    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_conclusion_approach_layout()
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(state["steps"][0], shift=UP * 0.04), run_time=0.45)
        self.play(
            Create(state["arrows"][0]),
            FadeIn(state["steps"][1], shift=UP * 0.04),
            run_time=0.48,
        )
        self.play(
            Create(state["arrows"][1]),
            FadeIn(state["steps"][2], shift=UP * 0.04),
            run_time=0.48,
        )
        self.play(
            Create(state["study_groups"][0][0]),
            FadeIn(state["study_groups"][0][1], shift=UP * 0.02),
            Create(state["study_groups"][1][0]),
            FadeIn(state["study_groups"][1][1], shift=UP * 0.02),
            run_time=0.40,
        )
        self.play(
            state["steps"].animate.shift(state["content_shift"]),
            state["arrows"].animate.shift(state["content_shift"]),
            state["study_groups"].animate.shift(state["bracket_shift"]),
            run_time=0.55,
        )
        self.play(
            FadeIn(state["stimulus_grid"], shift=UP * 0.04),
            FadeIn(state["validation_results"], shift=UP * 0.04),
            FadeIn(state["neuro_results"], shift=UP * 0.04),
            run_time=0.65,
        )
        self.wait(3.00)


class ConclusionTheoreticalImplications(_ConclusionNumberedScene, Scene):
    """Chapter 5.2 - state the main theoretical implications."""

    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_conclusion_theoretical_implications_layout()
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(state["content"], shift=UP * 0.05), run_time=1.00)
        self.play(FadeIn(state["callout"], shift=UP * 0.04), run_time=0.55)
        self.wait(3.10)


class ConclusionLimitations(_ConclusionNumberedScene, Scene):
    """Chapter 5.3 - state the main limitations."""

    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_conclusion_limitations_layout()
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(state["left_column"], shift=UP * 0.05), run_time=0.90)
        self.play(
            FadeIn(state["divider"]),
            FadeIn(state["right_column"], shift=UP * 0.05),
            run_time=0.90,
        )
        if state["callout"] is not None:
            self.play(FadeIn(state["callout"], shift=UP * 0.04), run_time=0.55)
        self.wait(3.00)


class ConclusionFutureDirections(_ConclusionNumberedScene, Scene):
    """Chapter 5.4 - argue for generative stimulus synthesis as a general platform."""

    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_conclusion_future_directions_layout()
        right_column_reveal_time = 0.95
        callout_reveal_time = 0.55
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(state["left_column"], shift=UP * 0.05), run_time=0.90)
        self.play(
            FadeIn(state["divider"]),
            FadeIn(state["right_column"], shift=UP * 0.05),
            run_time=right_column_reveal_time,
        )
        if state["callout"] is not None:
            self.play(FadeIn(state["callout"], shift=UP * 0.04), run_time=callout_reveal_time)
        self.wait(
            max(
                0.0,
                float(state["target_video_play_time"]) - right_column_reveal_time
                - (callout_reveal_time if state["callout"] is not None else 0.0),
            )
        )


_CONCLUSION_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    ConclusionApproach,
    ConclusionTheoreticalImplications,
    ConclusionLimitations,
    ConclusionFutureDirections,
)
_CONCLUSION_SECTION_NAMES: tuple[str, ...] = (
    "conclusion_summary",
    "conclusion_theoretical_implications",
    "conclusion_limitations",
    "conclusion_future_directions",
)


class Conclusion(Scene):
    """Unified production render for the conclusion chapter."""

    _SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = tuple(
        zip(_CONCLUSION_SECTION_NAMES, _CONCLUSION_MASTER_SECTION_ORDER)
    )

    def __init__(self, *args, **kwargs):
        config.output_file = "conclusion"
        super().__init__(*args, **kwargs)

    def _reset_master_scene_state(self) -> None:
        """Reset mobjects and camera placement before replaying one section."""
        self.clear()
        self.camera.background_color = BG
        if hasattr(self.camera, "frame_center"):
            self.camera.frame_center = ORIGIN.copy()

    def _hold_previous_section_frame(self) -> None:
        """Pin the previous section's last frame into the next section."""
        self.wait(1 / config.frame_rate)

    def _render_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        """Replay one existing conclusion scene inside the master render."""
        self.next_section(section_name)
        if carry_previous_frame:
            self._hold_previous_section_frame()
        self._reset_master_scene_state()
        scene_cls.construct(self)

    def construct(self) -> None:
        """Render the full conclusion as one sectioned scene."""
        self._reset_master_scene_state()
        for idx, (section_name, scene_cls) in enumerate(self._SECTION_SCENES):
            self._render_section(
                section_name,
                scene_cls,
                carry_previous_frame=idx > 0,
            )


__all__ = ["Conclusion", *list(_CONCLUSION_SCENE_ORDER)]


for _scene_cls in _CONCLUSION_MASTER_SECTION_ORDER:
    _scene_cls.__module__ = "_conclusion_internal"
del _scene_cls
Conclusion.__module__ = __name__
__all__ = ["Conclusion"]
