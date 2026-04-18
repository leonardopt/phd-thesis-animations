"""
Study 1, Step 1 — Prompt Design.

Study1Step1a — 6 category boxes (text word labels, 2 × 3 grid).
Study1Step1b — Boxes collapse to vertical stack; word "fish" highlighted;
               annotated prompt (centre-left) + fish image (right).

Render:
    uv run manim scenes/study1_step1.py Study1Step1a -qh
    uv run manim scenes/study1_step1.py Study1Step1b -qh
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from PIL import Image as PILImage

from manim import *
from utils import REPO_ROOT, env_path

# ── Palette ────────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
GREY  = "#6B7280"
LGREY = "#D1D5DB"
BLUE  = "#2563EB"   # central subject — "colorful fish", "centered in the scene"
ORNG  = "#EA580C"   # coherent scene  — "coral reef"
NAT_C = "#4C7A6D"
ART_C = "#A06A4B"

ANCHOR_DIR = env_path(
    "ANCHOR_IMAGES_DIR",
    REPO_ROOT / "assets" / "images" / "study1" / "anchor_images",
)

# ── Category definitions ───────────────────────────────────────────────────────
# (cat_key, display_name, [word_a, word_b, word_c])
CAT_INFO = [
    ("animal",            "Animals",
        ["dog",             "fish",           "owl"             ]),
    ("plant",             "Plants",
        ["oak",             "palm",           "sequoia"         ]),
    ("landscape_element", "Landscape elements",
        ["mountain ridge",  "polar iceberg",  "sea stack"       ]),
    ("building",          "Buildings",
        ["lighthouse",      "observatory",    "windmill"        ]),
    ("vehicle",           "Vehicles",
        ["campervan", "sailboat",       "scooter"]),
    ("item",              "Items",
        ["teapot",          "vase",           "bottle"      ]),
]

# ── Box geometry ───────────────────────────────────────────────────────────────
BOX_W = 2.70
BOX_H = 1.60
SZ    = 512


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_pix(path: Path) -> np.ndarray:
    return np.asarray(
        PILImage.open(path).convert("RGBA").resize((SZ, SZ), PILImage.LANCZOS)
    )


def _wrap_tex_label(text: str, max_chars: int) -> str:
    words = text.split()
    if len(text) <= max_chars or len(words) < 2:
        return text

    best_split = None
    best_score = None
    for split_idx in range(1, len(words)):
        left = " ".join(words[:split_idx])
        right = " ".join(words[split_idx:])
        score = abs(len(left) - len(right))
        if best_score is None or score < best_score:
            best_score = score
            best_split = (left, right)

    if best_split is None:
        return text
    return best_split[0] + r"\\" + best_split[1]


def _build_stimulus_tree():
    root = Tex(r"\textbf{Categories}", color=INK, font_size=30)
    root.move_to(UP * 2.15)

    nat_hdr = Tex(r"\textit{Natural}", color=NAT_C, font_size=27)
    nat_hdr.move_to(np.array([-3.55, 1.08, 0.0]))
    art_hdr = Tex(r"\textit{Artificial}", color=ART_C, font_size=27)
    art_hdr.move_to(np.array([3.55, 1.08, 0.0]))

    branch_nat = Line(
        root.get_bottom() + DOWN * 0.12 + LEFT * 0.16,
        nat_hdr.get_top() + UP * 0.18,
        color=NAT_C,
        stroke_width=2.0,
    )
    branch_art = Line(
        root.get_bottom() + DOWN * 0.12 + RIGHT * 0.16,
        art_hdr.get_top() + UP * 0.18,
        color=ART_C,
        stroke_width=2.0,
    )

    NODE_Y = -0.10
    NAT_XS = [-5.55, -3.55, -1.55]
    ART_XS = [1.55, 3.55, 5.55]
    CAT_FONT = 24
    SAMPLE_FONT = 20

    def sample_line(text: str) -> Tex:
        return Tex(
            _wrap_tex_label(text, max_chars=16),
            color=GREY,
            font_size=SAMPLE_FONT,
        )

    def make_category_node(
        display_name: str,
        sample_names: list[str],
        side_color: str,
    ) -> tuple[VGroup, Tex, VGroup, list[Tex]]:
        cat_label = Tex(
            _wrap_tex_label(display_name, max_chars=15),
            color=side_color,
            font_size=CAT_FONT,
        )
        label_top_y = 0.56
        cat_label.shift(UP * (label_top_y - cat_label.get_top()[1]))
        divider = Line(
            LEFT * max(0.82, cat_label.width / 2 + 0.02),
            RIGHT * max(0.82, cat_label.width / 2 + 0.02),
            stroke_color=side_color,
            stroke_width=1.2,
        ).move_to(UP * 0.00)

        stem = Line(
            divider.get_bottom() + DOWN * 0.02,
            divider.get_bottom() + DOWN * 0.22,
            color=side_color,
            stroke_width=1.0,
        )
        sample_texts = [
            sample_line(sample_names[0] + ","),
            sample_line(sample_names[1] + ","),
            sample_line(sample_names[2] + ","),
            Tex(r"\dots", color=GREY, font_size=SAMPLE_FONT),
        ]
        samples = VGroup(*sample_texts).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        samples.next_to(stem, DOWN, buff=0.06)

        node = VGroup(cat_label, divider, stem, samples)
        return node, cat_label, samples, sample_texts

    nat_nodes, nat_labels, nat_sample_lists = [], [], []
    art_nodes, art_labels, art_sample_lists = [], [], []
    fish_word = None
    animals_label = None

    for idx, (x, (cat_key, display_name, sample_names)) in enumerate(zip(NAT_XS, CAT_INFO[:3])):
        node, label, samples, sample_texts = make_category_node(display_name, sample_names, NAT_C)
        node.shift(np.array([x, NODE_Y, 0.0]))
        nat_nodes.append(node)
        nat_labels.append(label)
        nat_sample_lists.append(samples)
        if cat_key == "animal":
            animals_label = label
            fish_word = sample_texts[1]

    for x, (_, display_name, sample_names) in zip(ART_XS, CAT_INFO[3:]):
        node, label, samples, _ = make_category_node(display_name, sample_names, ART_C)
        node.shift(np.array([x, NODE_Y, 0.0]))
        art_nodes.append(node)
        art_labels.append(label)
        art_sample_lists.append(samples)

    nat_connectors = VGroup(*[
        Line(
            nat_hdr.get_bottom() + DOWN * 0.12,
            label.get_top() + UP * 0.12,
            color=NAT_C,
            stroke_width=1.4,
        )
        for label in nat_labels
    ])
    art_connectors = VGroup(*[
        Line(
            art_hdr.get_bottom() + DOWN * 0.12,
            label.get_top() + UP * 0.12,
            color=ART_C,
            stroke_width=1.4,
        )
        for label in art_labels
    ])

    all_sample_lists = VGroup(*nat_sample_lists, *art_sample_lists)
    object_rect = SurroundingRectangle(
        all_sample_lists,
        color=BLUE,
        stroke_width=2.4,
        buff=0.12,
    ).set_fill(BLUE, opacity=0.03)
    object_rect.set_z_index(3)
    object_rect_lbl = Tex(
        r"\textit{Object-scenes}",
        color=BLUE,
        font_size=24,
    ).next_to(object_rect, DOWN, buff=0.15)
    object_rect_lbl.set_z_index(4)

    total_lbl = Tex(
        r"$6$ categories $\times$ $18$ object-scenes $= 108$",
        color=GREY, font_size=26,
    ).to_edge(DOWN, buff=0.36)

    tree_group = VGroup(
        root,
        nat_hdr,
        art_hdr,
        branch_nat,
        branch_art,
        *nat_connectors,
        *art_connectors,
        *nat_nodes,
        *art_nodes,
        object_rect,
        object_rect_lbl,
        total_lbl,
    )

    return {
        "root": root,
        "nat_hdr": nat_hdr,
        "art_hdr": art_hdr,
        "branch_nat": branch_nat,
        "branch_art": branch_art,
        "nat_nodes": nat_nodes,
        "art_nodes": art_nodes,
        "nat_connectors": nat_connectors,
        "art_connectors": art_connectors,
        "object_rect": object_rect,
        "object_rect_lbl": object_rect_lbl,
        "total_lbl": total_lbl,
        "tree_group": tree_group,
        "animals_label": animals_label,
        "fish_word": fish_word,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Scene A — 6 category boxes with word labels
# ══════════════════════════════════════════════════════════════════════════════

class Study1Step1a(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        title = Tex(r"\textbf{Stimulus set design}", color=INK, font_size=40)
        title.to_edge(UP, buff=0.36)
        tree = _build_stimulus_tree()
        root = tree["root"]
        nat_hdr = tree["nat_hdr"]
        art_hdr = tree["art_hdr"]
        branch_nat = tree["branch_nat"]
        branch_art = tree["branch_art"]
        nat_nodes = tree["nat_nodes"]
        art_nodes = tree["art_nodes"]
        nat_connectors = tree["nat_connectors"]
        art_connectors = tree["art_connectors"]
        object_rect = tree["object_rect"]
        object_rect_lbl = tree["object_rect_lbl"]
        total_lbl = tree["total_lbl"]

        self.play(Write(title), run_time=0.50)
        self.play(FadeIn(root, shift=DOWN * 0.05), run_time=0.40)
        self.play(
            Create(branch_nat),
            Create(branch_art),
            FadeIn(nat_hdr, art_hdr, shift=DOWN * 0.04),
            run_time=0.65,
        )
        self.play(
            LaggedStart(
                *[AnimationGroup(Create(conn), FadeIn(node, shift=UP * 0.04), lag_ratio=0.0)
                  for conn, node in zip(nat_connectors, nat_nodes)],
                lag_ratio=0.16,
            ),
            run_time=0.95,
        )
        self.play(
            LaggedStart(
                *[AnimationGroup(Create(conn), FadeIn(node, shift=UP * 0.04), lag_ratio=0.0)
                  for conn, node in zip(art_connectors, art_nodes)],
                lag_ratio=0.16,
            ),
            run_time=0.95,
        )
        self.play(
            FadeIn(object_rect, shift=UP * 0.03),
            FadeIn(object_rect_lbl, shift=UP * 0.03),
            run_time=0.40,
        )
        self.play(FadeIn(total_lbl, shift=DOWN * 0.05), run_time=0.40)
        self.wait(1.80)


# ══════════════════════════════════════════════════════════════════════════════
# Scene B — collapse → fish highlight → prompt (left) + image (right)
# ══════════════════════════════════════════════════════════════════════════════

class Study1Step1b(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        fish_pix = load_pix(ANCHOR_DIR / "anchor-animal-fish.png")
        tree = _build_stimulus_tree()
        tree_group = tree["tree_group"]
        nat_hdr = tree["nat_hdr"]
        animals_label = tree["animals_label"]
        fish_word = tree["fish_word"]
        object_rect = tree["object_rect"]
        object_rect_lbl = tree["object_rect_lbl"]
        total_lbl = tree["total_lbl"]
        self.add(tree_group)

        title = Tex(r"\textbf{Prompt design}", color=INK, font_size=30)
        subtitle = Tex(
            r"each object-scene is defined with a single text prompt",
            color=GREY, font_size=22,
        )
        title_block = VGroup(title, subtitle).arrange(DOWN, buff=0.16)
        title_block.to_edge(UP, buff=0.28)
        self.play(FadeIn(title_block, shift=DOWN * 0.04), run_time=0.45)

        nat_hl = SurroundingRectangle(nat_hdr, color=BLUE, stroke_width=2.2, buff=0.06)
        animal_hl = SurroundingRectangle(animals_label, color=BLUE, stroke_width=2.2, buff=0.06)
        fish_hl = SurroundingRectangle(fish_word, color=BLUE, stroke_width=2.0, buff=0.04)
        self.play(Create(nat_hl), run_time=0.30)
        self.play(Create(animal_hl), run_time=0.30)
        self.play(
            fish_word.animate.set_color(BLUE),
            Create(fish_hl),
            run_time=0.30,
        )
        self.wait(0.20)

        keep_group = VGroup(nat_hdr, animals_label, fish_word, nat_hl, animal_hl, fish_hl)
        fade_group = VGroup(*[
            m for m in tree_group
            if m not in keep_group
            and m is not nat_hdr
            and m is not animals_label
            and m is not fish_word
            and m is not object_rect
            and m is not object_rect_lbl
            and m is not total_lbl
        ])

        LEFT_COL_X  = -4.0
        MID_COL_X   = 0.00
        RIGHT_COL_X = 4.60
        COL_CENTER_Y = -0.06

        path_nat = nat_hdr.copy().set_color(INK)
        path_animal = animals_label.copy().set_color(INK)
        path_fish = Tex(r"fish", color=INK, font_size=28)
        path_nat.move_to(np.array([LEFT_COL_X, COL_CENTER_Y + 0.98, 0.0]))
        path_animal.move_to(np.array([LEFT_COL_X, COL_CENTER_Y + 0.12, 0.0]))
        path_fish.move_to(np.array([LEFT_COL_X, COL_CENTER_Y - 0.88, 0.0]))

        path_arrow_1 = Arrow(
            path_nat.get_bottom() + DOWN * 0.04,
            path_animal.get_top() + UP * 0.04,
            buff=0.02, color=INK, stroke_width=2.8, tip_length=0.18,
        )
        path_arrow_2 = Arrow(
            path_animal.get_bottom() + DOWN * 0.04,
            path_fish.get_top() + UP * 0.04,
            buff=0.02, color=INK, stroke_width=2.8, tip_length=0.18,
        )
        path_col = VGroup(path_nat, path_animal, path_fish, path_arrow_1, path_arrow_2)
        path_col.shift(np.array([LEFT_COL_X, COL_CENTER_Y, 0.0]) - path_col.get_center())

        self.play(
            FadeOut(object_rect),
            FadeOut(object_rect_lbl),
            FadeOut(total_lbl),
            fade_group.animate.set_opacity(0.10),
            FadeOut(nat_hdr, nat_hl, animal_hl, fish_hl),
            TransformFromCopy(nat_hdr, path_nat),
            TransformFromCopy(animals_label, path_animal),
            FadeIn(path_fish, shift=UP * 0.08),
            Create(path_arrow_1),
            Create(path_arrow_2),
            run_time=1.0,
        )
        self.wait(0.20)
        self.play(
            FadeOut(fade_group),
            run_time=0.25,
        )
        self.wait(0.45)

        # ── Step C: prompt appears centre-left; fish image appears to its right
        IMG_H    = 3.20
        fish_img = (ImageMobject(fish_pix)
                    .set_height(IMG_H)
                    .move_to(np.array([RIGHT_COL_X, COL_CENTER_Y, 0.0])))

        FS = 21

        def prow(*parts):
            return VGroup(
                *[Tex(t, color=c, font_size=FS) for t, c in parts]
            ).arrange(RIGHT, buff=0.04)

        p_r0  = Tex(r"``award-winning marine photo", color=INK, font_size=FS)
        p_r1  = prow(("of a ", INK), ("colorful fish", INK))
        p_r2  = prow(("in a ", INK), ("coral reef", INK), (",", INK))
        p_r3  = Tex(r"centered in the scene,", color=INK, font_size=FS)
        p_r4  = Tex(r"vibrant underwater scene,", color=INK, font_size=FS)
        p_r5  = Tex(r"high detail''", color=INK, font_size=FS)
        p_lbl_prefix = Tex(r"Fixed prompt", color=INK, font_size=FS + 2)
        p_lbl_func = MathTex(r"p(\mathrm{fish})", color=GREY, font_size=FS + 1)
        p_lbl_colon = Tex(r":", color=GREY, font_size=FS)
        p_lbl = VGroup(p_lbl_prefix, p_lbl_func, p_lbl_colon).arrange(RIGHT, buff=0.08, aligned_edge=DOWN)
        p_body = VGroup(p_r0, p_r1, p_r2, p_r3, p_r4, p_r5).arrange(
                     DOWN, aligned_edge=ORIGIN, buff=0.09)
        p_block = VGroup(p_lbl, p_body).arrange(DOWN, aligned_edge=ORIGIN, buff=0.12)
        p_block.move_to(np.array([MID_COL_X, COL_CENTER_Y, 0.0]))

        self.play(
            FadeIn(p_lbl_prefix, shift=RIGHT * 0.06),
            TransformFromCopy(path_fish, p_lbl_func),
            FadeIn(p_lbl_colon, shift=RIGHT * 0.06),
            LaggedStart(*[FadeIn(r, shift=RIGHT * 0.06) for r in p_body], lag_ratio=0.15),
            run_time=1.10,
        )
        self.play(FadeIn(fish_img, scale=0.93), run_time=0.55)
        self.wait(0.30)

        # ── Step D: highlight prompt phrases + image overlays ──────────────────

        # D1 — subject emphasis: prompt phrases + foreground callout together
        cs_ring = Circle(radius=1.00, color=BLUE, stroke_width=3.5,
                         fill_color=BLUE, fill_opacity=0.15)
        cs_ring.move_to(fish_img.get_center())
        subject_tip = cs_ring.get_top() + UP * 0.02
        subject_lbl = Tex(r"clear subject in the foreground", color=BLUE, font_size=22)
        subject_lbl.next_to(fish_img, UP, buff=0.42)
        subject_arrow = Arrow(
            subject_lbl.get_bottom() + DOWN * 0.02,
            subject_tip,
            buff=0.08, color=BLUE, stroke_width=2.8, tip_length=0.16,
        )

        self.play(
            p_r1[1].animate.set_color(BLUE),
            p_r3[0].animate.set_color(BLUE),
            FadeIn(cs_ring, scale=0.88),
            FadeIn(subject_lbl, shift=LEFT * 0.08),
            GrowArrow(subject_arrow),
            run_time=0.55,
        )
        self.play(Indicate(cs_ring, color=BLUE, scale_factor=1.06), run_time=0.45)
        self.wait(0.20)

        # D2 — "coral reef" → ORNG  +  background-scene callout
        coh_rect = SurroundingRectangle(fish_img, color=ORNG, stroke_width=3.5, buff=0.04)
        bg_tip = coh_rect.get_bottom() + DOWN * 0.02
        bg_lbl = Tex(r"coherent scene in the background", color=ORNG, font_size=22)
        bg_lbl.next_to(fish_img, DOWN, buff=0.42)
        bg_arrow = Arrow(
            bg_lbl.get_top() + UP * 0.02,
            bg_tip,
            buff=0.08, color=ORNG, stroke_width=2.8, tip_length=0.16,
        )

        self.play(
            p_r2[1].animate.set_color(ORNG),
            Create(coh_rect),
            FadeIn(bg_lbl, shift=LEFT * 0.08),
            GrowArrow(bg_arrow),
            run_time=0.55,
        )
        self.play(Indicate(coh_rect, color=ORNG, scale_factor=1.03), run_time=0.45)
        self.wait(0.20)

        self.wait(1.60)
