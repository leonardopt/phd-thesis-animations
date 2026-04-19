"""
Study 1 — sectioned production render.

Render from this file to keep all Study 1 outputs in the same
`media/videos/03_study1/...` folder.

Production render:
    uv run manim scenes/study1.py Study1 -ql --save_sections
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.cm as _mcm
from PIL import Image as PILImage

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

import types

from manim import *

from utils import REPO_ROOT, env_path, section_output_dir, simplify_manim_section_video_names


_SECTION_OUTPUT_DIR = section_output_dir("study1")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"
config.output_file = "study1"
simplify_manim_section_video_names(
    lambda _output_name, index, name, ext: f"{index:03}_{name}{ext}"
)


def _ensure_study1_output_dirs(output_name: str | None = None) -> None:
    """Create the Study 1 render directories before Manim writes uncached frames."""
    video_dir = Path(config.get_dir("video_dir"))
    images_dir = Path(config.get_dir("images_dir"))
    video_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    if output_name:
        (video_dir / "partial_movie_files" / output_name).mkdir(parents=True, exist_ok=True)



# --- inlined from study1_step1.py ---

_s1_step1_BG = WHITE
_s1_step1_INK = '#1C1C1E'
_s1_step1_GREY = '#6B7280'
_s1_step1_LGREY = '#D1D5DB'
_s1_step1_BLUE = '#2563EB'
_s1_step1_ORNG = '#EA580C'
_s1_step1_NAT_C = '#4C7A6D'
_s1_step1_ART_C = '#A06A4B'
_s1_step1_ANCHOR_DIR = env_path('ANCHOR_IMAGES_DIR', REPO_ROOT / 'assets' / 'images' / 'study1' / 'anchor_images')
_s1_step1_CAT_INFO = [('animal', 'Animals', ['dog', 'fish', 'owl']), ('plant', 'Plants', ['oak', 'palm', 'sequoia']), ('landscape_element', 'Landscape elements', ['mountain ridge', 'polar iceberg', 'sea stack']), ('building', 'Buildings', ['lighthouse', 'observatory', 'windmill']), ('vehicle', 'Vehicles', ['campervan', 'sailboat', 'scooter']), ('item', 'Items', ['teapot', 'vase', 'bottle'])]
_s1_step1_BOX_W = 2.7
_s1_step1_BOX_H = 1.6
_s1_step1_SZ = 512

def _s1_step1_load_pix(path: Path) -> np.ndarray:
    """Load and resize one anchor image into the shared RGBA tensor size."""
    return np.asarray(PILImage.open(path).convert('RGBA').resize((_s1_step1_SZ, _s1_step1_SZ), PILImage.LANCZOS))

def _s1_step1__wrap_tex_label(text: str, max_chars: int) -> str:
    """Insert a balanced line break into a long TeX label when needed."""
    words = text.split()
    if len(text) <= max_chars or len(words) < 2:
        return text
    best_split = None
    best_score = None
    for split_idx in range(1, len(words)):
        left = ' '.join(words[:split_idx])
        right = ' '.join(words[split_idx:])
        score = abs(len(left) - len(right))
        if best_score is None or score < best_score:
            best_score = score
            best_split = (left, right)
    if best_split is None:
        return text
    return best_split[0] + '\\\\' + best_split[1]

def _s1_step1__build_stimulus_tree():
    """Build the category tree, connectors, and summary annotations for Step 1."""
    root = Tex('\\textbf{Categories}', color=_s1_step1_INK, font_size=30)
    root.move_to(UP * 2.15)
    nat_hdr = Tex('\\textit{Natural}', color=_s1_step1_NAT_C, font_size=27)
    nat_hdr.move_to(np.array([-3.55, 1.08, 0.0]))
    art_hdr = Tex('\\textit{Artificial}', color=_s1_step1_ART_C, font_size=27)
    art_hdr.move_to(np.array([3.55, 1.08, 0.0]))
    branch_nat = Line(root.get_bottom() + DOWN * 0.12 + LEFT * 0.16, nat_hdr.get_top() + UP * 0.18, color=_s1_step1_NAT_C, stroke_width=2.0)
    branch_art = Line(root.get_bottom() + DOWN * 0.12 + RIGHT * 0.16, art_hdr.get_top() + UP * 0.18, color=_s1_step1_ART_C, stroke_width=2.0)
    NODE_Y = -0.1
    NAT_XS = [-5.55, -3.55, -1.55]
    ART_XS = [1.55, 3.55, 5.55]
    CAT_FONT = 24
    SAMPLE_FONT = 20

    def sample_line(text: str) -> Tex:
        """Build one sample-name line for a category node."""
        return Tex(_s1_step1__wrap_tex_label(text, max_chars=16), color=_s1_step1_INK, font_size=SAMPLE_FONT)

    def make_category_node(display_name: str, sample_names: list[str], side_color: str) -> tuple[VGroup, Tex, VGroup, list[Tex]]:
        """Build one category node with its divider, stem, and sample list."""
        cat_label = Tex(_s1_step1__wrap_tex_label(display_name, max_chars=15), color=side_color, font_size=CAT_FONT)
        label_top_y = 0.56
        cat_label.shift(UP * (label_top_y - cat_label.get_top()[1]))
        divider = Line(LEFT * max(0.82, cat_label.width / 2 + 0.02), RIGHT * max(0.82, cat_label.width / 2 + 0.02), stroke_color=side_color, stroke_width=1.2).move_to(UP * 0.0)
        stem = Line(divider.get_bottom() + DOWN * 0.02, divider.get_bottom() + DOWN * 0.22, color=side_color, stroke_width=1.0)
        sample_texts = [sample_line(sample_names[0] + ','), sample_line(sample_names[1] + ','), sample_line(sample_names[2] + ','), Tex('\\dots', color=_s1_step1_GREY, font_size=SAMPLE_FONT)]
        samples = VGroup(*sample_texts).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        samples.next_to(stem, DOWN, buff=0.06)
        node = VGroup(cat_label, divider, stem, samples)
        return (node, cat_label, samples, sample_texts)
    nat_nodes, nat_labels, nat_sample_lists = ([], [], [])
    art_nodes, art_labels, art_sample_lists = ([], [], [])
    fish_word = None
    animals_label = None
    for idx, (x, (cat_key, display_name, sample_names)) in enumerate(zip(NAT_XS, _s1_step1_CAT_INFO[:3])):
        node, label, samples, sample_texts = make_category_node(display_name, sample_names, _s1_step1_NAT_C)
        node.shift(np.array([x, NODE_Y, 0.0]))
        nat_nodes.append(node)
        nat_labels.append(label)
        nat_sample_lists.append(samples)
        if cat_key == 'animal':
            animals_label = label
            fish_word = sample_texts[1]
    for x, (_, display_name, sample_names) in zip(ART_XS, _s1_step1_CAT_INFO[3:]):
        node, label, samples, _ = make_category_node(display_name, sample_names, _s1_step1_ART_C)
        node.shift(np.array([x, NODE_Y, 0.0]))
        art_nodes.append(node)
        art_labels.append(label)
        art_sample_lists.append(samples)
    nat_connectors = VGroup(*[Line(nat_hdr.get_bottom() + DOWN * 0.12, label.get_top() + UP * 0.12, color=_s1_step1_NAT_C, stroke_width=1.4) for label in nat_labels])
    art_connectors = VGroup(*[Line(art_hdr.get_bottom() + DOWN * 0.12, label.get_top() + UP * 0.12, color=_s1_step1_ART_C, stroke_width=1.4) for label in art_labels])
    all_sample_lists = VGroup(*nat_sample_lists, *art_sample_lists)
    object_rect = SurroundingRectangle(all_sample_lists, color=_s1_step1_BLUE, stroke_width=2.4, buff=0.12).set_fill(_s1_step1_BLUE, opacity=0.03)
    object_rect.set_z_index(3)
    object_rect_lbl = Tex('\\textit{Object-scenes}', color=_s1_step1_BLUE, font_size=24).next_to(object_rect, DOWN, buff=0.15)
    object_rect_lbl.set_z_index(4)
    total_lbl = Tex('$6$ categories $\\times$ $18$ object-scenes $= 108$', color=_s1_step1_INK, font_size=26).to_edge(DOWN, buff=0.36)
    tree_group = VGroup(root, nat_hdr, art_hdr, branch_nat, branch_art, *nat_connectors, *art_connectors, *nat_nodes, *art_nodes, object_rect, object_rect_lbl, total_lbl)
    return {'root': root, 'nat_hdr': nat_hdr, 'art_hdr': art_hdr, 'branch_nat': branch_nat, 'branch_art': branch_art, 'nat_nodes': nat_nodes, 'art_nodes': art_nodes, 'nat_connectors': nat_connectors, 'art_connectors': art_connectors, 'object_rect': object_rect, 'object_rect_lbl': object_rect_lbl, 'total_lbl': total_lbl, 'tree_group': tree_group, 'animals_label': animals_label, 'fish_word': fish_word}

class Study1Stage1Step1a(Scene):
    """Introduce the stimulus-set taxonomy and overall object-scene count."""
    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_step1_BG
        title = Tex('\\textbf{Stimulus set design}', color=_s1_step1_INK, font_size=40)
        title.to_edge(UP, buff=0.36)
        tree = _s1_step1__build_stimulus_tree()
        root = tree['root']
        nat_hdr = tree['nat_hdr']
        art_hdr = tree['art_hdr']
        branch_nat = tree['branch_nat']
        branch_art = tree['branch_art']
        nat_nodes = tree['nat_nodes']
        art_nodes = tree['art_nodes']
        nat_connectors = tree['nat_connectors']
        art_connectors = tree['art_connectors']
        object_rect = tree['object_rect']
        object_rect_lbl = tree['object_rect_lbl']
        total_lbl = tree['total_lbl']
        self.play(Write(title), run_time=0.5)
        self.play(FadeIn(root, shift=DOWN * 0.05), run_time=0.4)
        self.play(Create(branch_nat), Create(branch_art), FadeIn(nat_hdr, art_hdr, shift=DOWN * 0.04), run_time=0.65)
        self.play(LaggedStart(*[AnimationGroup(Create(conn), FadeIn(node, shift=UP * 0.04), lag_ratio=0.0) for conn, node in zip(nat_connectors, nat_nodes)], lag_ratio=0.16), run_time=0.95)
        self.play(LaggedStart(*[AnimationGroup(Create(conn), FadeIn(node, shift=UP * 0.04), lag_ratio=0.0) for conn, node in zip(art_connectors, art_nodes)], lag_ratio=0.16), run_time=0.95)
        self.play(FadeIn(object_rect, shift=UP * 0.03), FadeIn(object_rect_lbl, shift=UP * 0.03), run_time=0.4)
        self.play(FadeIn(total_lbl, shift=DOWN * 0.05), run_time=0.4)
        self.wait(1.8)

class Study1Stage1Step1b(Scene):
    """Trace one category path into a fixed prompt and highlighted exemplar image."""
    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_step1_BG
        fish_pix = _s1_step1_load_pix(_s1_step1_ANCHOR_DIR / 'anchor-animal-fish.png')
        tree = _s1_step1__build_stimulus_tree()
        tree_group = tree['tree_group']
        nat_hdr = tree['nat_hdr']
        animals_label = tree['animals_label']
        fish_word = tree['fish_word']
        object_rect = tree['object_rect']
        object_rect_lbl = tree['object_rect_lbl']
        total_lbl = tree['total_lbl']
        self.add(tree_group)
        title = Tex('\\textbf{Prompt design}', color=_s1_step1_INK, font_size=30)
        subtitle = Tex('each object-scene is defined with a single text prompt', color=_s1_step1_INK, font_size=22)
        title_block = VGroup(title, subtitle).arrange(DOWN, buff=0.16)
        title_block.to_edge(UP, buff=0.28)
        self.play(FadeIn(title_block, shift=DOWN * 0.04), run_time=0.45)
        nat_hl = SurroundingRectangle(nat_hdr, color=_s1_step1_BLUE, stroke_width=2.2, buff=0.06)
        animal_hl = SurroundingRectangle(animals_label, color=_s1_step1_BLUE, stroke_width=2.2, buff=0.06)
        fish_hl = SurroundingRectangle(fish_word, color=_s1_step1_BLUE, stroke_width=2.0, buff=0.04)
        self.play(Create(nat_hl), run_time=0.3)
        self.play(Create(animal_hl), run_time=0.3)
        self.play(fish_word.animate.set_color(_s1_step1_BLUE), Create(fish_hl), run_time=0.3)
        self.wait(0.2)
        keep_group = VGroup(nat_hdr, animals_label, fish_word, nat_hl, animal_hl, fish_hl)
        fade_group = VGroup(*[m for m in tree_group if m not in keep_group and m is not nat_hdr and (m is not animals_label) and (m is not fish_word) and (m is not object_rect) and (m is not object_rect_lbl) and (m is not total_lbl)])
        LEFT_COL_X = -4.0
        MID_COL_X = 0.0
        RIGHT_COL_X = 4.6
        COL_CENTER_Y = -0.06
        path_nat = nat_hdr.copy().set_color(_s1_step1_INK)
        path_animal = animals_label.copy().set_color(_s1_step1_INK)
        path_fish = Tex('fish', color=_s1_step1_INK, font_size=28)
        path_nat.move_to(np.array([LEFT_COL_X, COL_CENTER_Y + 0.98, 0.0]))
        path_animal.move_to(np.array([LEFT_COL_X, COL_CENTER_Y + 0.12, 0.0]))
        path_fish.move_to(np.array([LEFT_COL_X, COL_CENTER_Y - 0.88, 0.0]))
        path_arrow_1 = Arrow(path_nat.get_bottom() + DOWN * 0.04, path_animal.get_top() + UP * 0.04, buff=0.02, color=_s1_step1_INK, stroke_width=2.8, tip_length=0.18)
        path_arrow_2 = Arrow(path_animal.get_bottom() + DOWN * 0.04, path_fish.get_top() + UP * 0.04, buff=0.02, color=_s1_step1_INK, stroke_width=2.8, tip_length=0.18)
        path_col = VGroup(path_nat, path_animal, path_fish, path_arrow_1, path_arrow_2)
        path_col.shift(np.array([LEFT_COL_X, COL_CENTER_Y, 0.0]) - path_col.get_center())
        self.play(FadeOut(object_rect), FadeOut(object_rect_lbl), FadeOut(total_lbl), fade_group.animate.set_opacity(0.1), FadeOut(nat_hdr, nat_hl, animal_hl, fish_hl), TransformFromCopy(nat_hdr, path_nat), TransformFromCopy(animals_label, path_animal), FadeIn(path_fish, shift=UP * 0.08), Create(path_arrow_1), Create(path_arrow_2), run_time=1.0)
        self.wait(0.2)
        self.play(FadeOut(fade_group), run_time=0.25)
        self.wait(0.45)
        IMG_H = 3.2
        fish_img = ImageMobject(fish_pix).scale_to_fit_height(IMG_H).move_to(np.array([RIGHT_COL_X, COL_CENTER_Y, 0.0]))
        FS = 21

        def prow(*parts):
            """Build one prompt row with per-span color control."""
            return VGroup(*[Tex(t, color=c, font_size=FS) for t, c in parts]).arrange(RIGHT, buff=0.04)
        p_r0 = Tex('``award-winning marine photo', color=_s1_step1_INK, font_size=FS)
        p_r1 = prow(('of a ', _s1_step1_INK), ('colorful fish', _s1_step1_INK))
        p_r2 = prow(('in a ', _s1_step1_INK), ('coral reef', _s1_step1_INK), (',', _s1_step1_INK))
        p_r3 = Tex('centered in the scene,', color=_s1_step1_INK, font_size=FS)
        p_r4 = Tex('vibrant underwater scene,', color=_s1_step1_INK, font_size=FS)
        p_r5 = Tex("high detail''", color=_s1_step1_INK, font_size=FS)
        p_lbl_prefix = Tex('Fixed prompt', color=_s1_step1_INK, font_size=FS + 2)
        p_lbl_func = MathTex('p(\\mathrm{fish})', color=_s1_step1_INK, font_size=FS + 1)
        p_lbl_colon = Tex(':', color=_s1_step1_INK, font_size=FS)
        p_lbl = VGroup(p_lbl_prefix, p_lbl_func, p_lbl_colon).arrange(RIGHT, buff=0.08, aligned_edge=DOWN)
        p_body = VGroup(p_r0, p_r1, p_r2, p_r3, p_r4, p_r5).arrange(DOWN, aligned_edge=ORIGIN, buff=0.09)
        p_block = VGroup(p_lbl, p_body).arrange(DOWN, aligned_edge=ORIGIN, buff=0.12)
        p_block.move_to(np.array([MID_COL_X, COL_CENTER_Y, 0.0]))
        self.play(FadeIn(p_lbl_prefix, shift=RIGHT * 0.06), TransformFromCopy(path_fish, p_lbl_func), FadeIn(p_lbl_colon, shift=RIGHT * 0.06), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.06) for r in p_body], lag_ratio=0.15), run_time=1.1)
        self.play(FadeIn(fish_img, scale=0.93), run_time=0.55)
        self.wait(0.3)
        cs_ring = Circle(radius=1.0, color=_s1_step1_BLUE, stroke_width=3.5, fill_color=_s1_step1_BLUE, fill_opacity=0.15)
        cs_ring.move_to(fish_img.get_center())
        subject_tip = cs_ring.get_top() + UP * 0.02
        subject_lbl = Tex('clear subject in the foreground', color=_s1_step1_BLUE, font_size=22)
        subject_lbl.next_to(fish_img, UP, buff=0.42)
        subject_arrow = Arrow(subject_lbl.get_bottom() + DOWN * 0.02, subject_tip, buff=0.08, color=_s1_step1_BLUE, stroke_width=2.8, tip_length=0.16)
        self.play(p_r1[1].animate.set_color(_s1_step1_BLUE), p_r3[0].animate.set_color(_s1_step1_BLUE), FadeIn(cs_ring, scale=0.88), FadeIn(subject_lbl, shift=LEFT * 0.08), GrowArrow(subject_arrow), run_time=0.55)
        self.play(Indicate(cs_ring, color=_s1_step1_BLUE, scale_factor=1.06), run_time=0.45)
        self.wait(0.2)
        coh_rect = SurroundingRectangle(fish_img, color=_s1_step1_ORNG, stroke_width=3.5, buff=0.04)
        bg_tip = coh_rect.get_bottom() + DOWN * 0.02
        bg_lbl = Tex('coherent scene in the background', color=_s1_step1_ORNG, font_size=22)
        bg_lbl.next_to(fish_img, DOWN, buff=0.42)
        bg_arrow = Arrow(bg_lbl.get_top() + UP * 0.02, bg_tip, buff=0.08, color=_s1_step1_ORNG, stroke_width=2.8, tip_length=0.16)
        self.play(p_r2[1].animate.set_color(_s1_step1_ORNG), Create(coh_rect), FadeIn(bg_lbl, shift=LEFT * 0.08), GrowArrow(bg_arrow), run_time=0.55)
        self.play(Indicate(coh_rect, color=_s1_step1_ORNG, scale_factor=1.03), run_time=0.45)
        self.wait(0.2)
        self.wait(1.6)


# --- inlined from study1_step2.py ---

_s1_step2_BG = WHITE
_s1_step2_INK = '#1C1C1E'
_s1_step2_GREY = '#6B7280'
_s1_step2_LGREY = '#D1D5DB'
_s1_step2_IMG_DIR = env_path('EXEMPLAR_FISH_DIR', REPO_ROOT / 'assets' / 'images' / 'study1' / 'exemplar_images' / 'animal' / 'fish')
_s1_step2_N_SWAPS = 59
_s1_step2_SWAP_TOTAL_DUR = 10
_s1_step2_PROMPT_LINES = ['``award-winning marine photo', 'of a colorful fish in a coral reef,', 'centered in the scene, vibrant', "underwater scene, high detail''"]

def _s1_step2_noise_magma(seed: int, sz: int=128) -> np.ndarray:
    """Generate a deterministic magma-coloured noise image for one seed."""
    rng = np.random.default_rng(seed)
    gray = rng.random((sz, sz)).astype(np.float32)
    return (_mcm.magma(gray) * 255).astype(np.uint8)

def _s1_step2_cloud_positions(n: int, cx: float, cy: float):
    """
    Ring-based layout centred at (cx, cy) with no random jitter.
    Ring radii and counts are chosen so that both the tangential spacing
    (within a ring) and the radial gap (between rings) are ≥ 0.65,
    comfortably larger than the image height of 0.45.

      ring 0 : r=0.00,  1
      ring 1 : r=0.65,  6  → tangential gap ≈ 0.68
      ring 2 : r=1.30, 12  → tangential gap ≈ 0.68
      ring 3 : r=1.95, 18  → tangential gap ≈ 0.68
      ring 4 : r=2.60, 23  → tangential gap ≈ 0.71   total = 60
    """
    rings = [(0.0, 1, 0.0), (0.65, 6, 0.0), (1.3, 12, 0.26), (1.95, 18, 0.0), (2.6, 23, 0.14)]
    out, total = ([], 0)
    for r, n_def, off in rings:
        cnt = min(n_def, n - total)
        if cnt <= 0:
            break
        for k in range(cnt):
            ang = 2 * np.pi * k / max(cnt, 1) + off
            out.append((cx + r * np.cos(ang), cy + r * np.sin(ang)))
        total += cnt
    return out

class Study1Stage1Step2(Scene):
    """Show how one fixed prompt and varying noise seeds produce a cloud of exemplars."""
    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_step2_BG
        files = sorted(_s1_step2_IMG_DIR.glob('ANI-FIS-*.png'))
        N, SZ = (len(files), 512)
        pixels = [np.asarray(PILImage.open(fp).convert('RGBA').resize((SZ, SZ), PILImage.LANCZOS)) for fp in files]
        p_label = Tex('Fixed prompt $p$\\,:', color=_s1_step2_INK, font_size=26)
        p_body = VGroup(*[Tex(ln, color=_s1_step2_INK, font_size=36) for ln in _s1_step2_PROMPT_LINES]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        p_block = VGroup(p_label, p_body).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        p_block.move_to(ORIGIN)
        self.play(FadeIn(p_label, shift=DOWN * 0.06), run_time=0.35)
        self.play(LaggedStart(*[FadeIn(ln, shift=DOWN * 0.06) for ln in p_body], lag_ratio=0.18), run_time=1.2)
        self.wait(0.55)
        b_label = Tex('Fixed prompt $p$\\,:', color=_s1_step2_INK, font_size=22)
        b_body = VGroup(*[Tex(ln, color=_s1_step2_INK, font_size=25) for ln in _s1_step2_PROMPT_LINES]).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        p_banner = VGroup(b_label, b_body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        p_banner.to_corner(UL, buff=0.32)
        self.play(FadeTransform(p_block, p_banner), run_time=0.65)
        IMG_H = 2.6
        CY = -0.55
        NX, FX = (-3.1, 3.1)
        arrow_mob = Arrow(LEFT * 0.85, RIGHT * 0.85, buff=0, color=_s1_step2_GREY, stroke_width=2.5, tip_length=0.22, max_stroke_width_to_length_ratio=20)
        sdxl_tex = Tex('\\textbf{Stable Diffusion XL}', color=_s1_step2_INK, font_size=22)
        sdxl_tex.next_to(arrow_mob, UP, buff=0.16)
        sdxl_grp = VGroup(arrow_mob, sdxl_tex).move_to(UP * CY)
        noise_mob = ImageMobject(_s1_step2_noise_magma(seed=3)).scale_to_fit_height(IMG_H)
        noise_mob.move_to(RIGHT * NX + UP * CY)
        seed_lab = MathTex('\\mathbf{z}_1', color=_s1_step2_GREY, font_size=28)
        seed_lab.next_to(noise_mob, DOWN, buff=0.12)
        dist_lab = MathTex('\\sim \\mathcal{N}(\\mathbf{0},\\, \\mathbf{I})', color=_s1_step2_GREY, font_size=21)
        dist_lab.next_to(seed_lab, DOWN, buff=0.06)
        seq_idx = [int(round(i * (N - 1) / _s1_step2_N_SWAPS)) for i in range(_s1_step2_N_SWAPS + 1)]
        fish_mob = ImageMobject(pixels[seq_idx[0]]).scale_to_fit_height(IMG_H)
        fish_mob.move_to(RIGHT * FX + UP * CY)
        self.play(FadeIn(noise_mob, shift=RIGHT * 0.12), FadeIn(seed_lab), FadeIn(dist_lab), Create(arrow_mob), Write(sdxl_tex), FadeIn(fish_mob, shift=LEFT * 0.12, scale=0.95), run_time=1.0)
        self.wait(0.65)
        weights = np.geomspace(1.0, 0.2, _s1_step2_N_SWAPS)
        swap_times = list(_s1_step2_SWAP_TOTAL_DUR * weights / weights.sum())
        for i, (rt, idx) in enumerate(zip(swap_times, seq_idx[1:])):
            new_noise = ImageMobject(_s1_step2_noise_magma(seed=(i + 1) * 41 + 7)).scale_to_fit_height(IMG_H)
            new_noise.move_to(RIGHT * NX + UP * CY)
            new_fish = ImageMobject(pixels[idx]).scale_to_fit_height(IMG_H)
            new_fish.move_to(RIGHT * FX + UP * CY)
            new_seed = MathTex(f'\\mathbf{{z}}_{{{i + 2}}}', color=_s1_step2_GREY, font_size=28)
            new_seed.next_to(new_noise, DOWN, buff=0.12)
            self.play(FadeTransform(noise_mob, new_noise), FadeTransform(fish_mob, new_fish), FadeTransform(seed_lab, new_seed), run_time=rt)
            noise_mob = new_noise
            fish_mob = new_fish
            seed_lab = new_seed
        self.wait(0.4)
        IMG_CLOUD_H = 0.45
        CLOUD_CX, CLOUD_CY = (4.3, -0.1)
        cpos = _s1_step2_cloud_positions(N, cx=CLOUD_CX, cy=CLOUD_CY)
        cloud_imgs = [ImageMobject(pixels[i]).scale_to_fit_height(IMG_CLOUD_H).move_to(RIGHT * px + UP * py) for i, (px, py) in enumerate(cpos[:N])]
        c_title = Tex('\\textbf{60 exemplars} — \\textit{fish}', color=_s1_step2_INK, font_size=24).move_to(RIGHT * CLOUD_CX + UP * 3.2)
        c_sub = Tex('Same semantic identity $\\cdot$ Perceptually distinct realisations', color=_s1_step2_INK, font_size=19).to_edge(DOWN, buff=0.3)
        LEFT_CX = -3.8
        fp_label = Tex('Fixed prompt $p$\\,:', color=_s1_step2_INK, font_size=22)
        fp_body = VGroup(*[Tex(ln, color=_s1_step2_INK, font_size=25) for ln in _s1_step2_PROMPT_LINES]).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        fp_block = VGroup(fp_label, fp_body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        fp_block.move_to(RIGHT * LEFT_CX + UP * 1.7)
        comp_sym = MathTex('\\oplus', color=_s1_step2_GREY, font_size=52)
        comp_sym.move_to(RIGHT * LEFT_CX + UP * 0.0)
        THUMB_H = 0.75
        thumb_seeds = [3, 44, 85]
        thumbs = [ImageMobject(_s1_step2_noise_magma(seed=s)).scale_to_fit_height(THUMB_H) for s in thumb_seeds]
        dots_tex = MathTex('\\ldots', color=_s1_step2_GREY, font_size=36)
        thumb_row = Group(*thumbs, dots_tex).arrange(RIGHT, buff=0.18)
        lbrace = MathTex('\\bigl\\{', color=_s1_step2_INK, font_size=52)
        rbrace = MathTex('\\bigr\\}', color=_s1_step2_INK, font_size=52)
        set_row = Group(lbrace, thumb_row, rbrace).arrange(RIGHT, buff=0.14)
        set_row.move_to(RIGHT * LEFT_CX + UP * -1.1)
        set_brace = Brace(set_row, DOWN, color=_s1_step2_GREY, buff=0.08)
        set_brace_lab = MathTex('60 \\text{ noise tensors}', color=_s1_step2_GREY, font_size=20).next_to(set_brace, DOWN, buff=0.08)
        dist_note = MathTex('\\mathbf{z}_i \\sim \\mathcal{N}(\\mathbf{0},\\,\\mathbf{I})', color=_s1_step2_GREY, font_size=20).next_to(set_brace_lab, DOWN, buff=0.14)
        ARR_START = np.array([-0.85, 0.0, 0.0])
        ARR_END = np.array([1.4, 0.0, 0.0])
        new_arrow = Arrow(ARR_START, ARR_END, buff=0, color=_s1_step2_GREY, stroke_width=2.5, tip_length=0.22, max_stroke_width_to_length_ratio=20)
        new_sdxl = Tex('\\textbf{Stable Diffusion XL}', color=_s1_step2_INK, font_size=22)
        new_sdxl.next_to(new_arrow, UP, buff=0.16)
        new_sdxl_grp = VGroup(new_arrow, new_sdxl).move_to(ORIGIN)
        self.play(FadeOut(noise_mob, seed_lab, dist_lab, fish_mob), FadeTransform(p_banner, fp_block), FadeTransform(sdxl_grp, new_sdxl_grp), run_time=0.65)
        self.play(FadeIn(comp_sym, shift=DOWN * 0.06), FadeIn(lbrace), FadeIn(rbrace), LaggedStart(*[FadeIn(t, scale=0.9) for t in thumbs], lag_ratio=0.15), Write(dots_tex), run_time=0.9)
        self.play(FadeIn(set_brace, set_brace_lab, dist_note, shift=DOWN * 0.04), run_time=0.6)
        self.wait(0.3)
        self.play(Write(c_title), LaggedStart(*[FadeIn(m, shift=UP * 0.04) for m in cloud_imgs], lag_ratio=0.02), run_time=2.6)
        self.play(Write(c_sub), run_time=0.55)
        self.wait(1.5)


# --- inlined from study1_step2_showcase.py ---

_s1_step2_showcase_BG = WHITE
_s1_step2_showcase_INK = '#1C1C1E'
_s1_step2_showcase_GREY = '#6B7280'
_s1_step2_showcase_LGREY = '#D1D5DB'
_s1_step2_showcase_BASE = env_path('EXEMPLAR_IMAGES_DIR', REPO_ROOT / 'assets' / 'images' / 'study1' / 'exemplar_images')
_s1_step2_showcase_SHOWCASE = [dict(category='plant', folder='sequoia', glob='PLA-SEQ-*.png', label='sequoia', prompt_lines=['``film shot of a majestic Sequoia tree in the centre,', 'forest and mountains in the background,', 'high resolution photography,', "crisp clear sky''"]), dict(category='landscape_element', folder='lake_island', glob='LAN-LAK-*.png', label='lake island', prompt_lines=['``film shot of a towering rocky lake island in the center,', 'hilly meadows on the horizon,', 'high resolution photography,', "vibrant natural light''"]), dict(category='building', folder='observatory', glob='BUI-OBS-*.png', label='observatory', prompt_lines=['``film shot of an observatory', 'on a remote hilly landscape,', 'high resolution photography,', "exploratory, cinematic''"]), dict(category='vehicle', folder='campervan', glob='VEH-CAM-*.png', label='camper van', prompt_lines=['``photo of a solitary vintage camper van', 'in a countryside camping spot,', 'mountains in the background,', "high resolution photography, cinematic''"]), dict(category='item', folder='sofa', glob='ITE-SOF-*.png', label='sofa', prompt_lines=['``film shot of an art deco sofa,', 'minimalistic background,', "high resolution photography''"])]
_s1_step2_showcase_IMG_CLOUD_H = 0.45
_s1_step2_showcase_CLOUD_CX = 4.3
_s1_step2_showcase_CLOUD_CY = -0.1
_s1_step2_showcase_LEFT_CX = -3.8
_s1_step2_showcase_THUMB_H = 0.75
_s1_step2_showcase_HOLD_TIME = 1.6

def _s1_step2_showcase_noise_magma(seed: int, sz: int=128) -> np.ndarray:
    """Generate a deterministic showcase noise image for one seed."""
    rng = np.random.default_rng(seed)
    gray = rng.random((sz, sz)).astype(np.float32)
    return (_mcm.magma(gray) * 255).astype(np.uint8)

def _s1_step2_showcase_cloud_positions(n: int, cx: float, cy: float):
    """Return the fixed concentric layout used for showcase exemplar clouds."""
    rings = [(0.0, 1, 0.0), (0.65, 6, 0.0), (1.3, 12, 0.26), (1.95, 18, 0.0), (2.6, 23, 0.14)]
    out, total = ([], 0)
    for r, n_def, off in rings:
        cnt = min(n_def, n - total)
        if cnt <= 0:
            break
        for k in range(cnt):
            ang = 2 * np.pi * k / max(cnt, 1) + off
            out.append((cx + r * np.cos(ang), cy + r * np.sin(ang)))
        total += cnt
    return out
_s1_step2_showcase_SZ = 512

def _s1_step2_showcase_load_pixels(img_dir: Path, glob: str) -> list[np.ndarray]:
    """Load and resize all exemplar images for one showcase entry."""
    return [np.asarray(PILImage.open(fp).convert('RGBA').resize((_s1_step2_showcase_SZ, _s1_step2_showcase_SZ), PILImage.LANCZOS)) for fp in sorted(img_dir.glob(glob))]

def _s1_step2_showcase_make_prompt_block(prompt_lines: list[str], label: str) -> VGroup:
    """Prompt block with labelled subscript: Fixed prompt p(label) :"""
    p_label = Tex(f'Fixed prompt $p(\\text{{{label}}})$\\,:', color=_s1_step2_showcase_INK, font_size=22)
    p_body = VGroup(*[Tex(ln, color=_s1_step2_showcase_INK, font_size=25) for ln in prompt_lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
    block = VGroup(p_label, p_body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    block.move_to(RIGHT * _s1_step2_showcase_LEFT_CX + UP * 1.7)
    return block

def _s1_step2_showcase_make_cloud(pixels: list[np.ndarray]) -> Group:
    """Build the exemplar cloud for one showcase entry."""
    N = len(pixels)
    cpos = _s1_step2_showcase_cloud_positions(N, cx=_s1_step2_showcase_CLOUD_CX, cy=_s1_step2_showcase_CLOUD_CY)
    return Group(*[ImageMobject(pixels[i]).scale_to_fit_height(_s1_step2_showcase_IMG_CLOUD_H).move_to(RIGHT * px + UP * py) for i, (px, py) in enumerate(cpos[:N])])

def _s1_step2_showcase_make_title(label: str) -> Tex:
    """Build the exemplar-cloud title for one showcase entry."""
    return Tex(f'\\textbf{{60 exemplars}} — \\textit{{{label}}}', color=_s1_step2_showcase_INK, font_size=24).move_to(RIGHT * _s1_step2_showcase_CLOUD_CX + UP * 3.2)

def _s1_step2_showcase_make_thumbs(entry_idx: int, positions: list) -> list:
    """Three noise ImageMobjects at pre-computed fixed positions."""
    base = entry_idx * 97 + 3
    return [ImageMobject(_s1_step2_showcase_noise_magma(seed=base + k * 41)).scale_to_fit_height(_s1_step2_showcase_THUMB_H).move_to(pos) for k, pos in enumerate(positions)]

def _s1_step2_showcase_build_static_frame(scene: Scene) -> list:
    """
    Add the structural frame that never changes (⊕, braces, SDXL arrow, subtitle)
    directly to the scene with no animation.  Returns the list of fixed thumbnail
    slot positions so callers can place ImageMobjects there.
    """
    comp_sym = MathTex('\\oplus', color=_s1_step2_showcase_GREY, font_size=52)
    comp_sym.move_to(RIGHT * _s1_step2_showcase_LEFT_CX)
    _dummy = [ImageMobject(_s1_step2_showcase_noise_magma(seed=0)).scale_to_fit_height(_s1_step2_showcase_THUMB_H) for _ in range(3)]
    dots_tex = MathTex('\\ldots', color=_s1_step2_showcase_GREY, font_size=36)
    thumb_row = Group(*_dummy, dots_tex).arrange(RIGHT, buff=0.18)
    lbrace = MathTex('\\bigl\\{', color=_s1_step2_showcase_INK, font_size=52)
    rbrace = MathTex('\\bigr\\}', color=_s1_step2_showcase_INK, font_size=52)
    set_row = Group(lbrace, thumb_row, rbrace).arrange(RIGHT, buff=0.14)
    set_row.move_to(RIGHT * _s1_step2_showcase_LEFT_CX + UP * -1.1)
    thumb_positions = [d.get_center().copy() for d in _dummy]
    set_brace = Brace(set_row, DOWN, color=_s1_step2_showcase_GREY, buff=0.08)
    set_brace_lab = MathTex('60 \\text{ noise tensors}', color=_s1_step2_showcase_GREY, font_size=20).next_to(set_brace, DOWN, buff=0.08)
    dist_note = MathTex('\\mathbf{z}_i \\sim \\mathcal{N}(\\mathbf{0},\\,\\mathbf{I})', color=_s1_step2_showcase_GREY, font_size=20).next_to(set_brace_lab, DOWN, buff=0.14)
    sdxl_arrow = Arrow(np.array([-0.85, 0.0, 0.0]), np.array([1.4, 0.0, 0.0]), buff=0, color=_s1_step2_showcase_GREY, stroke_width=2.5, tip_length=0.22, max_stroke_width_to_length_ratio=20)
    sdxl_tex = Tex('\\textbf{Stable Diffusion XL}', color=_s1_step2_showcase_INK, font_size=22)
    sdxl_tex.next_to(sdxl_arrow, UP, buff=0.16)
    sdxl_grp = VGroup(sdxl_arrow, sdxl_tex).move_to(ORIGIN)
    c_sub = Tex('Same semantic identity $\\cdot$ Perceptually distinct realisations', color=_s1_step2_showcase_INK, font_size=19).to_edge(DOWN, buff=0.3)
    scene.add(comp_sym, lbrace, dots_tex, rbrace, set_brace, set_brace_lab, dist_note, sdxl_grp, c_sub)
    return thumb_positions

def _s1_step2_showcase_animate_entry(scene: Scene, entry: dict, pixels: list, thumb_positions: list, entry_idx: int, prev_state: dict | None) -> dict:
    """
    Animate one showcase entry.  If prev_state is None this is the first entry
    (fade in).  Otherwise swap out the previous mobjects.
    Returns the current state dict for the next call.
    """
    fp_block = _s1_step2_showcase_make_prompt_block(entry['prompt_lines'], entry['label'])
    thumbs = _s1_step2_showcase_make_thumbs(entry_idx, thumb_positions)
    cloud_grp = _s1_step2_showcase_make_cloud(pixels)
    c_title = _s1_step2_showcase_make_title(entry['label'])
    if prev_state is None:
        scene.play(FadeIn(fp_block, shift=DOWN * 0.06), *[FadeIn(t, scale=0.9) for t in thumbs], run_time=0.5)
        scene.play(Write(c_title), LaggedStart(*[FadeIn(m, shift=UP * 0.04) for m in cloud_grp], lag_ratio=0.02), run_time=2.0)
    else:
        scene.play(FadeTransform(prev_state['fp_block'], fp_block), FadeTransform(prev_state['c_title'], c_title), *[FadeOut(t) for t in prev_state['thumbs']], FadeOut(prev_state['cloud_grp']), run_time=0.5)
        scene.play(*[FadeIn(t, scale=0.9) for t in thumbs], LaggedStart(*[FadeIn(m, shift=UP * 0.04) for m in cloud_grp], lag_ratio=0.02), run_time=1.8)
    scene.wait(_s1_step2_showcase_HOLD_TIME)
    return dict(fp_block=fp_block, thumbs=thumbs, cloud_grp=cloud_grp, c_title=c_title)

def _s1_step2_showcase__make_single_scene(idx: int) -> type:
    """Create a one-off scene class for a single showcase entry."""
    entry = _s1_step2_showcase_SHOWCASE[idx]

    class _S(Scene):
        """Single-entry showcase scene generated for one exemplar family."""
        def construct(self_):
            """Run the animation sequence for this scene."""
            self_.camera.background_color = _s1_step2_showcase_BG
            pixels = _s1_step2_showcase_load_pixels(_s1_step2_showcase_BASE / entry['category'] / entry['folder'], entry['glob'])
            thumb_pos = _s1_step2_showcase_build_static_frame(self_)
            _s1_step2_showcase_animate_entry(self_, entry, pixels, thumb_pos, idx, None)
    name = f"Showcase_{entry['folder']}"
    _S.__name__ = name
    _S.__qualname__ = name
    return _S
for _i, _e in enumerate(_s1_step2_showcase_SHOWCASE):
    globals()[f"Showcase_{_e['folder']}"] = _s1_step2_showcase__make_single_scene(_i)

class Study1Stage1Step2Showcase(Scene):
    """Cycle through several object-scene prompts and exemplar clouds in a shared frame."""
    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_step2_showcase_BG
        all_pixels = [_s1_step2_showcase_load_pixels(_s1_step2_showcase_BASE / e['category'] / e['folder'], e['glob']) for e in _s1_step2_showcase_SHOWCASE]
        thumb_pos = _s1_step2_showcase_build_static_frame(self)
        state = None
        for i, (entry, pixels) in enumerate(zip(_s1_step2_showcase_SHOWCASE, all_pixels)):
            state = _s1_step2_showcase_animate_entry(self, entry, pixels, thumb_pos, i, state)


# --- inlined from study1_step3.py ---

_s1_step3_BG = WHITE
_s1_step3_INK = '#1C1C1E'
_s1_step3_GREY = '#6B7280'
_s1_step3_LGREY = '#D1D5DB'
_s1_step3_C_ANCHOR = '#2563EB'
_s1_step3_C_GUIDE = '#DC2626'
_s1_step3_C_ACCENT = '#D97706'
_s1_step3_C_MATRIX = '#3F7F7A'
_s1_step3_C_FLOW = '#C58A2A'
_s1_step3_IMG_DIR = env_path('EXEMPLAR_FISH_DIR', REPO_ROOT / 'assets' / 'images' / 'study1' / 'exemplar_images' / 'animal' / 'fish')
_s1_step3_NN_ICON_PATH = REPO_ROOT / 'assets' / 'images' / 'references' / 'neural_network_schematic.svg'
_s1_step3_ANCHOR_NAME = 'ANI-FIS-3873620486.png'
_s1_step3_GUIDE_NAME = 'ANI-FIS-4212442282.png'
_s1_step3_SIMILARITY_CSV_PATH = env_path('SIMILARITY_ANCHORS_FISH_CSV', REPO_ROOT / 'assets' / 'data' / 'study1' / 'lpips-squeeze-mat-animal-fish.csv')

def _s1_step3_cloud_positions(n: int, cx: float, cy: float):
    """
    Same deterministic ring layout used in Study1Step2.
    """
    rings = [(0.0, 1, 0.0), (0.65, 6, 0.0), (1.3, 12, 0.26), (1.95, 18, 0.0), (2.6, 23, 0.14)]
    out, total = ([], 0)
    for r, n_def, off in rings:
        cnt = min(n_def, n - total)
        if cnt <= 0:
            break
        for k in range(cnt):
            ang = 2 * np.pi * k / max(cnt, 1) + off
            out.append((cx + r * np.cos(ang), cy + r * np.sin(ang)))
        total += cnt
    return out

def _s1_step3_choose_demo_pairs(cloud_pts: list[tuple[float, float]], cx: float, cy: float, selected_pair: tuple[int, int], excluded_indices: set[int], count: int=8) -> list[tuple[int, int]]:
    """
    Pick demo pairs from different cloud regions so the LPIPS examples feel
    visually varied, while keeping pair spacing moderate, readable, and away
    from the matrix edges.
    """
    target_offsets = [(-1.1, 0.7), (-0.1, 1.55), (1.75, 1.0), (1.45, -0.9), (0.1, -1.85), (-1.15, -0.75), (-1.0, 0.15), (0.95, 0.45)]
    n = len(cloud_pts)
    edge_margin = max(8, n // 7)
    distance_target = 1.95
    candidates: list[tuple[tuple[int, int], np.ndarray, float]] = []
    for i in range(n):
        if i in excluded_indices:
            continue
        for j in range(i):
            if j in excluded_indices:
                continue
            pair = tuple(sorted((i, j)))
            if pair == selected_pair:
                continue
            if j < edge_margin or i > n - 1 - edge_margin:
                continue
            (x1, y1), (x2, y2) = (cloud_pts[i], cloud_pts[j])
            dist = float(np.hypot(x1 - x2, y1 - y2))
            if not 1.45 <= dist <= 2.2:
                continue
            midpoint = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
            candidates.append((pair, midpoint, dist))
    chosen: list[tuple[int, int]] = []
    used_indices = set(excluded_indices)
    for dx, dy in target_offsets:
        target = np.array([cx + dx, cy + dy])
        best_pair = None
        best_score = None
        for pair, midpoint, dist in candidates:
            i, j = pair
            if pair in chosen or i in used_indices or j in used_indices:
                continue
            score = np.linalg.norm(midpoint - target) + 0.45 * abs(dist - distance_target)
            if best_score is None or score < best_score:
                best_score = score
                best_pair = pair
        if best_pair is not None:
            chosen.append(best_pair)
            used_indices.update(best_pair)
        if len(chosen) == count:
            break
    if len(chosen) < count:
        remaining = sorted(candidates, key=lambda item: abs(item[2] - distance_target))
        for pair, _, _ in remaining:
            i, j = pair
            if pair in chosen or i in used_indices or j in used_indices:
                continue
            chosen.append(pair)
            used_indices.update(pair)
            if len(chosen) == count:
                break
    return chosen

def _s1_step3_load_pixels(sz: int=320) -> tuple[list[np.ndarray], list[Path]]:
    """Load and resize the fish exemplar set for the LPIPS scene."""
    files = sorted(_s1_step3_IMG_DIR.glob('ANI-FIS-*.png'))
    pixels = [np.asarray(PILImage.open(fp).convert('RGBA').resize((sz, sz), PILImage.LANCZOS)) for fp in files]
    return (pixels, files)

def _s1_step3_load_pixel(path: Path, sz: int=320) -> np.ndarray:
    """Load and resize one fish exemplar image."""
    return np.asarray(PILImage.open(path).convert('RGBA').resize((sz, sz), PILImage.LANCZOS))

def _s1_step3_load_similarity_matrix() -> tuple[np.ndarray, list[str]]:
    """Load the LPIPS similarity matrix and validate its row and column order."""
    with _s1_step3_SIMILARITY_CSV_PATH.open(newline='') as f:
        rows = list(csv.reader(f))
    ordered_names = rows[0][1:]
    row_names = [row[0] for row in rows[1:]]
    if row_names != ordered_names:
        raise ValueError('Similarity CSV row/column ordering mismatch')
    scores = np.asarray([[float(value) for value in row[1:]] for row in rows[1:]], dtype=np.float32)
    return (scores, ordered_names)

def _s1_step3_score_heatmap_rgba(scores: np.ndarray, row_start: int=0, row_end: int | None=None) -> np.ndarray:
    """Convert lower-triangular similarity scores into an RGBA heatmap image."""
    n = scores.shape[0]
    if row_end is None:
        row_end = n
    vmax = max(float(scores.max()), 1e-06)
    norm = np.clip(scores / vmax, 0.0, 1.0)
    low = np.array([242, 247, 246, 255], dtype=np.float32)
    mid = np.array([181, 208, 204, 255], dtype=np.float32)
    high = np.array([63, 127, 122, 255], dtype=np.float32)
    colored = (((1 - norm) ** 2)[..., None] * low + (2 * (1 - norm) * norm)[..., None] * mid + (norm ** 2)[..., None] * high).astype(np.uint8)
    rgba = np.zeros((n, n, 4), dtype=np.uint8)
    row_mask = np.zeros(n, dtype=bool)
    row_mask[row_start:row_end] = True
    lower_mask = np.tril(np.ones((n, n), dtype=bool), k=-1)
    keep_mask = lower_mask & row_mask[:, None]
    rgba[keep_mask] = colored[keep_mask]
    diag_idx = np.arange(n)
    diag_mask = row_mask
    rgba[diag_idx[diag_mask], diag_idx[diag_mask]] = np.array([248, 248, 250, 255], dtype=np.uint8)
    return rgba

def _s1_step3_thumb(pixel: np.ndarray, h: float, border_color: str=_s1_step3_LGREY, sw: float=1.8) -> Group:
    """Build a thumbnail card for one exemplar image."""
    img = ImageMobject(pixel).scale_to_fit_height(h)
    border = SurroundingRectangle(img, color=border_color, stroke_width=sw, buff=0.03)
    return Group(img, border)

def _s1_step3_nn_icon(height: float=0.76) -> SVGMobject:
    """Load the neural-network schematic used above the LPIPS matrix."""
    svg = SVGMobject(str(_s1_step3_NN_ICON_PATH), use_svg_cache=False)
    svg.set_stroke(_s1_step3_INK, opacity=1.0)
    svg.set_fill(_s1_step3_INK, opacity=1.0)
    svg.scale_to_fit_height(height)
    return svg

class _Study1Step3Base(Scene):
    """Shared LPIPS similarity-matrix scene with optional segment-level cut points."""
    segment = 'full'

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_step3_BG
        pixels, files = _s1_step3_load_pixels()
        scores_csv, ordered_names = _s1_step3_load_similarity_matrix()
        csv_index_by_name = {name: i for i, name in enumerate(ordered_names)}
        perm = [csv_index_by_name[fp.name] for fp in files]
        scores = scores_csv[np.ix_(perm, perm)]
        n = len(pixels)
        file_index_by_name = {fp.name: i for i, fp in enumerate(files)}
        anchor_idx = file_index_by_name[_s1_step3_ANCHOR_NAME]
        guide_idx = file_index_by_name[_s1_step3_GUIDE_NAME]
        anchor_pixel = pixels[anchor_idx]
        guide_pixel = pixels[guide_idx]
        selected_pair = tuple(sorted((anchor_idx, guide_idx)))
        IMG_CLOUD_H = 0.45
        CLOUD_CX, CLOUD_CY = (-4.15, -0.1)
        MATRIX_SIDE = 4.1
        MATRIX_C = np.array([1.05, -0.28, 0.0])
        cloud_pts = _s1_step3_cloud_positions(n, cx=CLOUD_CX, cy=CLOUD_CY)
        demo_pairs = _s1_step3_choose_demo_pairs(cloud_pts, cx=CLOUD_CX, cy=CLOUD_CY, selected_pair=selected_pair, excluded_indices={anchor_idx, guide_idx}, count=8)
        cloud_imgs = [ImageMobject(pixels[i]).scale_to_fit_height(IMG_CLOUD_H).move_to(RIGHT * x + UP * y) for i, (x, y) in enumerate(cloud_pts)]
        cloud_title = Tex('\\textbf{60 exemplars} — \\textit{fish}', color=_s1_step3_INK, font_size=24).move_to(RIGHT * CLOUD_CX + UP * 3.2)
        matrix_title_text = VGroup(
            Tex('Neural network-based perceptual similarity', color=_s1_step3_INK, font_size=20),
            Tex('\\textbf{LPIPS} (Zhang et al., 2018)', color=_s1_step3_INK, font_size=20),
        ).arrange(DOWN, buff=0.05)
        matrix_icon = _s1_step3_nn_icon()
        matrix_title = VGroup(matrix_title_text, matrix_icon).arrange(DOWN, buff=0.15).move_to(RIGHT * MATRIX_C[0] + UP * 3.05)
        half = MATRIX_SIDE / 2
        mat_ul = MATRIX_C + np.array([-half, half, 0.0])
        mat_dl = MATRIX_C + np.array([-half, -half, 0.0])
        mat_ur = MATRIX_C + np.array([half, half, 0.0])
        mat_dr = MATRIX_C + np.array([half, -half, 0.0])
        tri_bg = Polygon(mat_ul, mat_dl, mat_dr, stroke_width=0).set_fill('#FAFAFB', opacity=1.0)
        tri_frame = Polygon(mat_ul, mat_dl, mat_dr, color=_s1_step3_LGREY, stroke_width=1.5)
        diag_line = Line(mat_ul, mat_dr, color=_s1_step3_LGREY, stroke_width=1.0)
        axis_x = Tex('\\textit{exemplar }j', color=_s1_step3_GREY, font_size=14).next_to(tri_frame, DOWN, buff=0.15)
        axis_y = Tex('\\textit{exemplar }i', color=_s1_step3_GREY, font_size=14).rotate(PI / 2).next_to(tri_frame, LEFT, buff=0.15)
        tri_bg.set_z_index(0)
        tri_frame.set_z_index(2)
        diag_line.set_z_index(2)
        matrix_title.set_z_index(3)
        axis_x.set_z_index(3)
        axis_y.set_z_index(3)
        band_edges = np.linspace(0, n, 7, dtype=int)
        band_imgs = []
        for start, end in zip(band_edges[:-1], band_edges[1:]):
            band = ImageMobject(_s1_step3_score_heatmap_rgba(scores, start, end)).scale_to_fit_height(MATRIX_SIDE).move_to(MATRIX_C)
            band.set_resampling_algorithm(RESAMPLING_ALGORITHMS['nearest'])
            band.set_z_index(1)
            band_imgs.append(band)
        cell = MATRIX_SIDE / n

        def cell_center(i: int, j: int) -> np.ndarray:
            """Return the scene position of one lower-triangular matrix cell."""
            i, j = (max(i, j), min(i, j))
            left = MATRIX_C[0] - MATRIX_SIDE / 2
            top = MATRIX_C[1] + MATRIX_SIDE / 2
            return np.array([left + (j + 0.5) * cell, top - (i + 0.5) * cell, 0.0])

        def pair_cell(i: int, j: int, color: str=_s1_step3_C_ACCENT) -> Square:
            """Build a highlighted square around one similarity-matrix cell."""
            box = Square(side_length=max(cell * 2.2, 0.07), stroke_color=color, stroke_width=2.2).set_fill(color, opacity=0.14)
            box.move_to(cell_center(i, j))
            return box

        def score_label(i: int, j: int) -> Tex:
            """Build the LPIPS score label for one exemplar pair."""
            score = float(scores[i, j])
            return Tex(f'\\textit{{score}} = {score:.3f}', color=_s1_step3_C_MATRIX, font_size=18)
        pair_title = Tex('\\textbf{Example pairwise similarity}', color=_s1_step3_INK, font_size=20)
        pair_l = _s1_step3_thumb(pixels[demo_pairs[0][0]], h=0.9)
        pair_r = _s1_step3_thumb(pixels[demo_pairs[0][1]], h=0.9)
        pair_formula = MathTex('\\mathrm{LPIPS}(x_i,x_j)', color=_s1_step3_C_MATRIX, font_size=24)
        pair_imgs = Group(pair_l, pair_r).arrange(RIGHT, buff=0.24)
        pair_score = score_label(*demo_pairs[0])
        pair_title.set_z_index(6)
        pair_formula.set_z_index(6)
        pair_imgs.set_z_index(6)
        pair_score.set_z_index(6)
        pair_card = Group(pair_title, pair_formula, pair_imgs, pair_score).arrange(DOWN, buff=0.12)
        pair_card.move_to(RIGHT * 5.25 + UP * 2.15)
        pair_card.set_z_index(5)
        repeat_note = Tex('\\textit{repeat for all exemplar pairs}', color=_s1_step3_GREY, font_size=16).next_to(pair_card, DOWN, buff=0.16)
        repeat_note.set_z_index(5)
        pair_arrow = Arrow(pair_card.get_left() + LEFT * 0.04 + DOWN * 0.1, cell_center(*demo_pairs[0]) + RIGHT * 0.1, buff=0.08, color=_s1_step3_C_FLOW, stroke_width=2.0, tip_length=0.18, max_stroke_width_to_length_ratio=20)
        pair_arrow.set_z_index(4)
        current_cell = pair_cell(*demo_pairs[0], color=_s1_step3_C_FLOW)
        current_cell.set_z_index(4)

        def cloud_pair_box(idx: int) -> SurroundingRectangle:
            """Build a highlight box around one exemplar in the cloud layout."""
            return SurroundingRectangle(cloud_imgs[idx], color=_s1_step3_C_FLOW, stroke_width=2.4, buff=0.04).set_fill(_s1_step3_C_FLOW, opacity=0.06)
        current_cloud_left = cloud_pair_box(demo_pairs[0][0])
        current_cloud_right = cloud_pair_box(demo_pairs[0][1])
        current_cloud_left.set_z_index(4)
        current_cloud_right.set_z_index(4)
        algo_title = Tex('\\textbf{Custom selection algorithm}', color=_s1_step3_INK, font_size=18)
        algo_body = VGroup(Tex('Batch-representative', color=_s1_step3_INK, font_size=15), Tex('Similar to each other', color=_s1_step3_INK, font_size=15), Tex('Returns \\textit{anchor} and \\textit{guide}', color=_s1_step3_INK, font_size=15)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        algo_content = VGroup(algo_title, algo_body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        algo_box = RoundedRectangle(width=algo_content.width + 0.42, height=algo_content.height + 0.36, corner_radius=0.12, stroke_color=_s1_step3_LGREY, stroke_width=1.4).set_fill(WHITE, opacity=0.96)
        algo_content.move_to(algo_box.get_center())
        algo_panel = Group(algo_box, algo_content).move_to(RIGHT * 5.25 + UP * 1.15)
        algo_panel.set_z_index(5)
        output_title = Tex('\\textbf{Selected pair}', color=_s1_step3_INK, font_size=20)
        anchor_card = _s1_step3_thumb(anchor_pixel, h=1.02, border_color=_s1_step3_C_ANCHOR, sw=2.4)
        guide_card = _s1_step3_thumb(guide_pixel, h=1.02, border_color=_s1_step3_C_GUIDE, sw=2.4)
        anchor_label = Tex('\\textit{anchor}', color=_s1_step3_C_ANCHOR, font_size=22)
        guide_label = Tex('\\textit{guide}', color=_s1_step3_C_GUIDE, font_size=22)
        anchor_panel = Group(anchor_label, anchor_card).arrange(DOWN, buff=0.12)
        guide_panel = Group(guide_label, guide_card).arrange(DOWN, buff=0.12)
        output_group = Group(anchor_panel, guide_panel).arrange(DOWN, buff=0.42)
        output_block = Group(output_title, output_group).arrange(DOWN, buff=0.18)
        output_block.move_to(RIGHT * 5.1 + DOWN * 1.65)
        output_block.set_z_index(5)
        cloud_anchor_box = SurroundingRectangle(cloud_imgs[anchor_idx], color=_s1_step3_C_ANCHOR, stroke_width=2.5, buff=0.04)
        cloud_guide_box = SurroundingRectangle(cloud_imgs[guide_idx], color=_s1_step3_C_GUIDE, stroke_width=2.5, buff=0.04)
        selected_cell = pair_cell(*selected_pair, color=_s1_step3_C_ACCENT)
        selected_row = max(anchor_idx, guide_idx)
        selected_col = min(anchor_idx, guide_idx)
        row_color = _s1_step3_C_ANCHOR if selected_row == anchor_idx else _s1_step3_C_GUIDE
        col_color = _s1_step3_C_ANCHOR if selected_col == anchor_idx else _s1_step3_C_GUIDE

        def row_band(row_idx: int, color: str) -> Rectangle:
            """Build a translucent band for one matrix row."""
            width = (row_idx + 1) * cell
            left = MATRIX_C[0] - MATRIX_SIDE / 2
            top = MATRIX_C[1] + MATRIX_SIDE / 2
            band = Rectangle(width=width, height=cell * 0.96, stroke_color=color, stroke_width=2.6).set_fill(color, opacity=0.1)
            band.move_to(np.array([left + width / 2, top - (row_idx + 0.5) * cell, 0.0]))
            return band

        def col_band(col_idx: int, color: str) -> Rectangle:
            """Build a translucent band for one matrix column."""
            height = (n - col_idx) * cell
            left = MATRIX_C[0] - MATRIX_SIDE / 2
            top = MATRIX_C[1] + MATRIX_SIDE / 2
            band = Rectangle(width=cell * 0.96, height=height, stroke_color=color, stroke_width=2.6).set_fill(color, opacity=0.1)
            band.move_to(np.array([left + (col_idx + 0.5) * cell, top - col_idx * cell - height / 2, 0.0]))
            return band
        selected_row_band = row_band(selected_row, row_color)
        selected_col_band = col_band(selected_col, col_color)
        anchor_source_band = selected_row_band if selected_row == anchor_idx else selected_col_band
        guide_source_band = selected_row_band if selected_row == guide_idx else selected_col_band
        search_path = [(8, 1), (18, 4), (30, 11), (41, 20), (50, 31), selected_pair]
        search_cell = pair_cell(*search_path[0], color=YELLOW)
        cloud_anchor_box.set_z_index(4)
        cloud_guide_box.set_z_index(4)
        selected_cell.set_z_index(4)
        search_cell.set_z_index(4)
        selected_row_band.set_z_index(3)
        selected_col_band.set_z_index(3)

        def make_algo_scan_arrow() -> CurvedArrow:
            """Build the scan arrow used during the anchor-guide search."""
            arrow = CurvedArrow(algo_panel.get_left() + LEFT * 0.08 + DOWN * 0.04, search_cell.get_center() + RIGHT * (cell * 0.95), angle=32 * DEGREES, color=_s1_step3_C_FLOW, stroke_width=2.4, tip_length=0.18)
            arrow.set_z_index(4)
            return arrow
        algo_scan_arrow = always_redraw(make_algo_scan_arrow)

        def play_intro_and_matrix(keep_example_visible: bool=False) -> None:
            """Animate the LPIPS matrix construction sequence."""
            nonlocal pair_score
            self.play(Write(cloud_title), LaggedStart(*[FadeIn(m, shift=UP * 0.03) for m in cloud_imgs], lag_ratio=0.01), run_time=1.45)
            self.wait(0.45)
            self.play(FadeIn(tri_bg), Create(tri_frame), Create(diag_line), run_time=0.65)
            self.add(matrix_icon)
            self.play(Write(matrix_title_text), run_time=0.6)
            self.wait(1.15)
            self.play(FadeIn(axis_x, axis_y), run_time=0.4)
            first_left = cloud_imgs[demo_pairs[0][0]]
            first_right = cloud_imgs[demo_pairs[0][1]]
            self.play(FadeIn(pair_title, pair_formula, pair_score, shift=DOWN * 0.04), TransformFromCopy(first_left, pair_l[0]), FadeIn(pair_l[1]), TransformFromCopy(first_right, pair_r[0]), FadeIn(pair_r[1]), FadeIn(current_cloud_left, current_cloud_right), Create(pair_arrow), FadeIn(current_cell), run_time=1.05)
            self.wait(0.45)
            for next_pair in demo_pairs[1:]:
                new_left = _s1_step3_thumb(pixels[next_pair[0]], h=0.9)
                new_right = _s1_step3_thumb(pixels[next_pair[1]], h=0.9)
                new_left.move_to(pair_l.get_center())
                new_right.move_to(pair_r.get_center())
                new_score = score_label(*next_pair).move_to(pair_score.get_center())
                new_arrow = Arrow(pair_card.get_left() + LEFT * 0.04 + DOWN * 0.1, cell_center(*next_pair) + RIGHT * 0.1, buff=0.08, color=_s1_step3_C_FLOW, stroke_width=2.0, tip_length=0.18, max_stroke_width_to_length_ratio=20)
                new_cell = pair_cell(*next_pair, color=_s1_step3_C_FLOW)
                new_cloud_left = cloud_pair_box(next_pair[0]).set_z_index(4)
                new_cloud_right = cloud_pair_box(next_pair[1]).set_z_index(4)
                self.play(Transform(pair_l, new_left), Transform(pair_r, new_right), FadeTransform(pair_score, new_score), Transform(pair_arrow, new_arrow), Transform(current_cell, new_cell), Transform(current_cloud_left, new_cloud_left), Transform(current_cloud_right, new_cloud_right), run_time=0.65)
                pair_score = new_score
                self.wait(0.14)
            self.play(Write(repeat_note), run_time=0.45)
            self.wait(0.45)
            fill_anims = [LaggedStart(*[FadeIn(band, shift=UP * 0.02) for band in band_imgs], lag_ratio=0.14)]
            if not keep_example_visible:
                fill_anims.extend([FadeOut(current_cloud_left, current_cloud_right), FadeOut(pair_arrow, current_cell)])
            self.play(*fill_anims, run_time=2.2)
            self.wait(0.45)
            if not keep_example_visible:
                self.play(FadeOut(pair_card, pair_score, repeat_note), run_time=0.45)
                self.wait(0.25)

        def play_selection_sequence() -> None:
            """Animate the anchor-guide selection sequence."""
            self.play(FadeIn(algo_panel, shift=UP * 0.04), run_time=0.95)
            self.wait(0.45)
            self.play(FadeIn(search_cell), FadeIn(algo_scan_arrow), run_time=0.45)
            self.wait(0.2)
            for pair in search_path[1:]:
                self.play(Transform(search_cell, pair_cell(*pair, color=YELLOW).set_z_index(4)), run_time=0.34)
            self.play(Transform(search_cell, selected_cell), FadeOut(algo_scan_arrow), run_time=0.45)
            self.wait(0.35)
            self.play(AnimationGroup(GrowFromCenter(selected_row_band), GrowFromCenter(selected_col_band), lag_ratio=0.18), FadeIn(cloud_anchor_box, cloud_guide_box), run_time=0.9)
            self.wait(0.35)
            self.play(FadeIn(output_title, shift=DOWN * 0.04), GrowFromPoint(anchor_card, anchor_source_band.get_center()), GrowFromPoint(guide_card, guide_source_band.get_center()), FadeIn(anchor_label, target_position=anchor_source_band.get_center()), FadeIn(guide_label, target_position=guide_source_band.get_center()), run_time=1.1)
            self.wait(1.45)

        def build_part1_final_frame() -> dict[str, Mobject]:
            """Build the held end state for the matrix-only segment."""
            final_pair = demo_pairs[-1]
            pair_title_final = pair_title.copy().set_z_index(6)
            pair_formula_final = pair_formula.copy().set_z_index(6)
            pair_l_final = _s1_step3_thumb(pixels[final_pair[0]], h=0.9)
            pair_r_final = _s1_step3_thumb(pixels[final_pair[1]], h=0.9)
            pair_imgs_final = Group(pair_l_final, pair_r_final).arrange(RIGHT, buff=0.24)
            pair_imgs_final.set_z_index(6)
            pair_score_final = score_label(*final_pair).set_z_index(6)
            pair_card_final = Group(pair_title_final, pair_formula_final, pair_imgs_final, pair_score_final).arrange(DOWN, buff=0.12)
            pair_card_final.move_to(pair_card.get_center())
            pair_card_final.set_z_index(5)
            repeat_note_final = repeat_note.copy()
            repeat_note_final.next_to(pair_card_final, DOWN, buff=0.16)
            repeat_note_final.set_z_index(5)
            pair_arrow_final = Arrow(pair_card_final.get_left() + LEFT * 0.04 + DOWN * 0.1, cell_center(*final_pair) + RIGHT * 0.1, buff=0.08, color=_s1_step3_C_FLOW, stroke_width=2.0, tip_length=0.18, max_stroke_width_to_length_ratio=20)
            pair_arrow_final.set_z_index(4)
            current_cell_final = pair_cell(*final_pair, color=_s1_step3_C_FLOW)
            current_cell_final.set_z_index(4)
            current_cloud_left_final = cloud_pair_box(final_pair[0]).set_z_index(4)
            current_cloud_right_final = cloud_pair_box(final_pair[1]).set_z_index(4)
            return {'pair_card': pair_card_final, 'repeat_note': repeat_note_final, 'pair_arrow': pair_arrow_final, 'current_cell': current_cell_final, 'current_cloud_left': current_cloud_left_final, 'current_cloud_right': current_cloud_right_final}
        if self.segment == 'merged':
            self.next_section("05_Step3Part1")
            play_intro_and_matrix(keep_example_visible=True)
            self.wait(0.55)
            self.next_section("06_Step3Part2")
            self.play(
                FadeOut(current_cloud_left, current_cloud_right),
                FadeOut(pair_arrow, current_cell),
                FadeOut(pair_title, pair_formula, pair_l, pair_r, pair_score, repeat_note),
                run_time=0.45,
            )
            self.wait(0.25)
            play_selection_sequence()
            return
        if self.segment == 'selection':
            part1_final_frame = build_part1_final_frame()
            self.add(cloud_title, *cloud_imgs, tri_bg, tri_frame, diag_line, matrix_title, axis_x, axis_y, *band_imgs, part1_final_frame['pair_card'], part1_final_frame['repeat_note'], part1_final_frame['pair_arrow'], part1_final_frame['current_cell'], part1_final_frame['current_cloud_left'], part1_final_frame['current_cloud_right'])
            self.wait(0.55)
            self.play(FadeOut(part1_final_frame['current_cloud_left'], part1_final_frame['current_cloud_right']), FadeOut(part1_final_frame['pair_arrow'], part1_final_frame['current_cell']), FadeOut(part1_final_frame['pair_card'], part1_final_frame['repeat_note']), run_time=0.45)
            self.wait(0.25)
            play_selection_sequence()
            return
        play_intro_and_matrix(keep_example_visible=self.segment == 'matrix')
        if self.segment == 'matrix':
            self.wait(1.35)
            return
        play_selection_sequence()

class Study1Stage1Step3(_Study1Step3Base):
    """LPIPS matrix construction and anchor-guide selection with next_section() continuity."""
    segment = 'merged'

class Study1Stage1Step3Part1(_Study1Step3Base):
    """Render the matrix-building half of the LPIPS selection story."""
    segment = 'matrix'

class Study1Stage1Step3Part2(_Study1Step3Base):
    """Render the anchor-guide selection half of the LPIPS selection story."""
    segment = 'selection'


# --- inlined from study1_step4.py ---

_s1_step4_BG = WHITE
_s1_step4_INK = '#1C1C1E'
_s1_step4_LGREY = '#D1D5DB'
_s1_step4_MGREY = '#9CA3AF'
_s1_step4_C_Z0 = '#2563EB'
_s1_step4_C_Z1 = '#DC2626'
_s1_step4_C_ZA = '#D97706'
_s1_step4_C_ARC = '#93C5FD'
_s1_step4_IMG_DIR = env_path('FISH_INTERPOLATIONS_DIR', env_path('INTERPOLATIONS_DIR', REPO_ROOT / 'assets' / 'images' / 'study1' / 'fish_interpolations'))
_s1_step4_PROMPT = "\\textit{``a fish swimming in the ocean''}"
_s1_step4_PROMPT_BOX_LINES = ('"award-winning marine photo', 'of a colorful fish', 'in a coral reef,', 'centered in the scene,', 'vibrant underwater scene,', 'high detail"')
_s1_step4_COMPACT_PROMPT_LINES = ('``award-winning marine photo', 'of a colorful fish in a coral reef,', 'centered in the scene,', 'vibrant underwater scene,', "high detail''")

def _s1_step4_slerp(u: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
    """Interpolate between two latent directions on the unit sphere."""
    cos_t = float(np.clip(np.dot(u, v), -1.0, 1.0))
    theta = np.arccos(cos_t)
    if abs(np.sin(theta)) < 1e-08:
        return (1 - t) * u + t * v
    return (np.sin((1 - t) * theta) * u + np.sin(t * theta) * v) / np.sin(theta)

def _s1_step4_vec3(start, end, color, sw=3.5, tl=0.18) -> Arrow:
    """Thin VMobject arrow in 3-D space (fast to create, projects correctly)."""
    return Arrow(np.asarray(start, dtype=float), np.asarray(end, dtype=float), color=color, stroke_width=sw, tip_length=tl, buff=0, max_stroke_width_to_length_ratio=100)

def _s1_step4_load_interpolation_pixels() -> tuple[np.ndarray, int]:
    """Load and resize the fish interpolation frames for Step 4."""
    files = sorted(_s1_step4_IMG_DIR.glob('ANI-FIS-interpol-*.png'))
    if not files:
        raise FileNotFoundError(f"No interpolation frames found for Study 1 Step 4. Looked in {_s1_step4_IMG_DIR} for files matching 'ANI-FIS-interpol-*.png'. Set FISH_INTERPOLATIONS_DIR in .env to the directory containing the fish interpolation frames.")
    N, SZ = (len(files), 512)
    pixels = np.empty((N, SZ, SZ, 4), dtype=np.uint8)
    for i, fp in enumerate(files):
        pixels[i] = np.asarray(PILImage.open(fp).convert('RGBA').resize((SZ, SZ), PILImage.LANCZOS))
    return (pixels, N)

class Study1Stage1Step4Detailed(ThreeDScene):
    """Show the full 3-D SLERP interpolation story alongside the generated image preview."""
    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_step4_BG
        LEFT_BLOCK_CENTER = np.array([2.3, 0.0, 0.0])
        MID_BLOCK_SHIFT = UP * 0.55
        RIGHT_BLOCK_CENTER = RIGHT * 6.15 + MID_BLOCK_SHIFT
        MID_ARROW_CENTER_X = 4.15
        MID_ARROW_HALF_LEN = 0.5
        PROGRESS_Y = -3.5
        PANEL_TITLE_CORNER = UL
        PANEL_TITLE_BUFF = 0.45
        AXIS_LABEL_OFFSET = 0.3
        Z0_THUMB_DIST = 0.98
        Z0_LABEL_EXTRA = 0.34
        Z1_THUMB_OFFSET_EXTRA = np.array([0.05, 0.0, 0.16])
        Z1_LABEL_OFFSET_XYZ = np.array([0.0, 0.02, 0.3])
        ZA_LABEL_SCALE = 1.28
        pixels, N = _s1_step4_load_interpolation_pixels()
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, frame_center=LEFT_BLOCK_CENTER)
        GRID_R, STEP = (2.2, 0.5)
        grid_lines = VGroup(*[line for k in np.arange(-GRID_R, GRID_R + STEP * 0.5, STEP) for line in (Line(np.array([k, -GRID_R, 0.0]), np.array([k, GRID_R, 0.0]), color=_s1_step4_LGREY, stroke_width=0.9), Line(np.array([-GRID_R, k, 0.0]), np.array([GRID_R, k, 0.0]), color=_s1_step4_LGREY, stroke_width=0.9))])
        L = 3.0
        ax_x = _s1_step4_vec3(ORIGIN, [L, 0, 0], _s1_step4_MGREY, sw=2.2, tl=0.18)
        ax_y = _s1_step4_vec3(ORIGIN, [0, L, 0], _s1_step4_MGREY, sw=2.2, tl=0.18)
        ax_z = _s1_step4_vec3(ORIGIN, [0, 0, L], _s1_step4_MGREY, sw=2.2, tl=0.18)
        FS = 28
        lab_x = MathTex('x', color=_s1_step4_MGREY, font_size=FS).move_to(np.array([L + AXIS_LABEL_OFFSET, 0.0, 0.0]))
        lab_y = MathTex('y', color=_s1_step4_MGREY, font_size=FS).move_to(np.array([0.0, L + AXIS_LABEL_OFFSET, 0.0]))
        lab_z = MathTex('z', color=_s1_step4_MGREY, font_size=FS).move_to(np.array([0.0, 0.0, L + AXIS_LABEL_OFFSET]))
        R = 1.7
        z0_dir = np.array([0.52, -0.18, 1.0])
        z0_dir /= np.linalg.norm(z0_dir)
        z1_dir = np.array([1.0, 0.5, 0.3])
        z1_dir /= np.linalg.norm(z1_dir)
        tip0, tip1 = (R * z0_dir, R * z1_dir)
        vec_z0 = _s1_step4_vec3(ORIGIN, tip0, _s1_step4_C_Z0, sw=4.0, tl=0.22)
        vec_z1 = _s1_step4_vec3(ORIGIN, tip1, _s1_step4_C_Z1, sw=4.0, tl=0.22)
        arc_3d = ParametricFunction(lambda t: R * _s1_step4_slerp(z0_dir, z1_dir, t), t_range=[0.0, 1.0, 0.005], color=_s1_step4_C_ARC, stroke_width=4)
        THUMB_H = 0.85
        z0_label_dist = Z0_THUMB_DIST + THUMB_H / 2 + Z0_LABEL_EXTRA
        z1_thumb_offset = np.array([THUMB_H / 2, THUMB_H / 2, 0.0]) + Z1_THUMB_OFFSET_EXTRA
        z1_label_offset = np.array([0.0, 0.0, THUMB_H / 2]) + Z1_LABEL_OFFSET_XYZ
        thumb0 = ImageMobject(pixels[0]).scale_to_fit_height(THUMB_H).move_to(tip0 + z0_dir * Z0_THUMB_DIST)
        border0 = SurroundingRectangle(thumb0, color=_s1_step4_C_Z0, stroke_width=2.5, buff=0.03)
        thumb1 = ImageMobject(pixels[-1]).scale_to_fit_height(THUMB_H).move_to(tip1 + z1_thumb_offset)
        border1 = SurroundingRectangle(thumb1, color=_s1_step4_C_Z1, stroke_width=2.5, buff=0.03)
        lab_z0_3d = MathTex('\\mathbf{z}_0', '\\text{(anchor)}', color=_s1_step4_C_Z0, font_size=30).arrange(DOWN, buff=0.06).move_to(tip0 + z0_dir * z0_label_dist)
        lab_z1_3d = MathTex('\\mathbf{z}_1', '\\text{(guide)}', color=_s1_step4_C_Z1, font_size=30).arrange(DOWN, buff=0.06).move_to(thumb1.get_center() + z1_label_offset)
        alpha = ValueTracker(0.0)
        vec_za = always_redraw(lambda: _s1_step4_vec3(ORIGIN, R * _s1_step4_slerp(z0_dir, z1_dir, alpha.get_value()), _s1_step4_C_ZA, sw=4.0, tl=0.22))
        lab_za_3d = MathTex('\\mathbf{z}_\\alpha', color=_s1_step4_C_ZA, font_size=36)
        lab_za_3d.move_to(R * _s1_step4_slerp(z0_dir, z1_dir, 0.0) * ZA_LABEL_SCALE)
        lab_za_3d.add_updater(lambda mob: mob.move_to(R * _s1_step4_slerp(z0_dir, z1_dir, alpha.get_value()) * ZA_LABEL_SCALE))
        IMG_H = 3.0
        img_display = ImageMobject(pixels[0]).scale_to_fit_height(IMG_H).move_to(RIGHT_BLOCK_CENTER)

        def upd_img(mob):
            """Update the generated image to match the current interpolation value."""
            idx = int(round(alpha.get_value() * (N - 1)))
            mob.become(ImageMobject(pixels[np.clip(idx, 0, N - 1)]).scale_to_fit_height(IMG_H).move_to(RIGHT_BLOCK_CENTER))
        img_display.add_updater(upd_img)
        img_frame = SurroundingRectangle(img_display, color=_s1_step4_LGREY, stroke_width=1.5, buff=0.03)
        title_img = Tex('\\textit{Generated image}', color=_s1_step4_INK, font_size=24).next_to(img_frame, UP, buff=0.2)
        arrow_dn = Arrow(RIGHT * (MID_ARROW_CENTER_X - MID_ARROW_HALF_LEN) + MID_BLOCK_SHIFT, RIGHT * (MID_ARROW_CENTER_X + MID_ARROW_HALF_LEN) + MID_BLOCK_SHIFT, buff=0, color=_s1_step4_MGREY, stroke_width=2.5, tip_length=0.22)
        lab_fn = MathTex('f_\\theta(\\mathbf{z}_\\alpha)', color=_s1_step4_INK, font_size=24).next_to(arrow_dn, UP, buff=0.14)
        BW, BY, BAR_CX = (4.6, PROGRESS_Y, MID_ARROW_CENTER_X)
        bl = RIGHT * (BAR_CX - BW / 2) + DOWN * abs(BY)
        bar_bg = Line(bl, bl + RIGHT * BW, color=_s1_step4_LGREY, stroke_width=4)
        lab_al0 = MathTex('\\alpha=0', color=_s1_step4_MGREY, font_size=24).next_to(bar_bg, LEFT, buff=0.1)
        lab_al1 = MathTex('\\alpha=1', color=_s1_step4_MGREY, font_size=24).next_to(bar_bg, RIGHT, buff=0.1)
        bar_fill = always_redraw(lambda: Line(bl, bl + RIGHT * (alpha.get_value() * BW), color=_s1_step4_C_ZA, stroke_width=4))
        slerp_eq = MathTex('\\mathbf{z}_\\alpha= \\dfrac{\\sin((1-\\alpha)\\theta)}{\\sin\\theta}\\;\\mathbf{z}_0+ \\dfrac{\\sin(\\alpha\\theta)}{\\sin\\theta}\\;\\mathbf{z}_1', color=_s1_step4_INK, font_size=24).next_to(bar_bg, UP, buff=0.26)
        panel_title = Tex('\\textit{Noise latent space} ($\\mathbb{R}^n$)', color=_s1_step4_INK, font_size=26).to_corner(PANEL_TITLE_CORNER, buff=PANEL_TITLE_BUFF)
        self.play(Create(grid_lines), run_time=0.7)
        self.add_fixed_orientation_mobjects(lab_x, lab_y, lab_z)
        self.play(Create(ax_x), Create(ax_y), Create(ax_z), Write(lab_x), Write(lab_y), Write(lab_z), run_time=0.9)
        self.add_fixed_orientation_mobjects(thumb0, border0, lab_z0_3d, thumb1, border1, lab_z1_3d)
        self.add_fixed_in_frame_mobjects(slerp_eq)
        self.play(Create(vec_z0), FadeIn(thumb0), FadeIn(border0), Write(lab_z0_3d), Create(vec_z1), FadeIn(thumb1), FadeIn(border1), Write(lab_z1_3d), Write(slerp_eq), run_time=1.2)
        self.add_fixed_in_frame_mobjects(panel_title, arrow_dn, lab_fn)
        self.add_fixed_orientation_mobjects(lab_za_3d)
        self.play(Write(panel_title), Create(arc_3d), FadeIn(vec_za), FadeIn(lab_za_3d), Create(arrow_dn), Write(lab_fn), run_time=1.0)
        self.wait(0.3)
        self.add_fixed_in_frame_mobjects(img_display, img_frame, title_img, bar_bg, lab_al0, lab_al1, bar_fill)
        self.play(FadeIn(img_display), FadeIn(img_frame), Write(title_img), FadeIn(bar_bg), FadeIn(bar_fill), Write(lab_al0), Write(lab_al1), alpha.animate.set_value(1.0), run_time=10.0, rate_func=linear)
        self.wait(0.8)

class _Study1Step4CompactBase(ThreeDScene):
    """Shared compact latent-space interpolation state and split-scene helpers."""
    def build_common_state(self) -> dict[str, object]:
        """Build the shared compact latent-space scene state."""
        self.camera.background_color = _s1_step4_BG
        pixels, N = _s1_step4_load_interpolation_pixels()
        self.set_camera_orientation(phi=62 * DEGREES, theta=-42 * DEGREES, frame_center=np.array([0.35, 0.2, 0.0]))
        STEP = 0.5
        L_XY, L_Z = (4.8, 3.95)
        GRID_R = L_XY * 0.9
        grid_lines = VGroup(*[line for k in np.arange(-GRID_R, GRID_R + STEP * 0.5, STEP) for line in (Line(np.array([k, -GRID_R, 0.0]), np.array([k, GRID_R, 0.0]), color=_s1_step4_LGREY, stroke_width=0.9), Line(np.array([-GRID_R, k, 0.0]), np.array([GRID_R, k, 0.0]), color=_s1_step4_LGREY, stroke_width=0.9))])
        ax_x = _s1_step4_vec3(ORIGIN, [L_XY, 0, 0], _s1_step4_MGREY, sw=2.4, tl=0.24)
        ax_y = _s1_step4_vec3(ORIGIN, [0, L_XY, 0], _s1_step4_MGREY, sw=2.4, tl=0.24)
        ax_z = _s1_step4_vec3(ORIGIN, [0, 0, L_Z], _s1_step4_MGREY, sw=2.4, tl=0.24)
        lab_x = MathTex('x', color=_s1_step4_MGREY, font_size=30).move_to(np.array([L_XY + 0.32, 0.0, 0.0]))
        lab_y = MathTex('y', color=_s1_step4_MGREY, font_size=30).move_to(np.array([0.0, L_XY + 0.32, 0.0]))
        lab_z = MathTex('z', color=_s1_step4_MGREY, font_size=30).move_to(np.array([0.18, 0.18, L_Z - 0.08]))
        R = 2.85
        z0_dir = np.array([0.0, 1.0, 1.0])
        z0_dir /= np.linalg.norm(z0_dir)
        z1_dir = np.array([1.0, 1.0, 0.0])
        z1_dir /= np.linalg.norm(z1_dir)
        tip0, tip1 = (R * z0_dir, R * z1_dir)
        vec_z0 = _s1_step4_vec3(ORIGIN, tip0, _s1_step4_C_Z0, sw=4.2, tl=0.28)
        vec_z1 = _s1_step4_vec3(ORIGIN, tip1, _s1_step4_C_Z1, sw=4.2, tl=0.28)
        arc_3d = ParametricFunction(lambda t: R * _s1_step4_slerp(z0_dir, z1_dir, t), t_range=[0.0, 1.0, 0.005], color=_s1_step4_C_ARC, stroke_width=4)
        thumb_h = 0.95
        thumb0 = ImageMobject(pixels[0]).scale_to_fit_height(thumb_h).move_to(tip0 + z0_dir * 0.92)
        border0 = SurroundingRectangle(thumb0, color=_s1_step4_C_Z0, stroke_width=2.5, buff=0.03)
        thumb1_offset = np.array([thumb_h / 2 + 0.05, thumb_h / 2, 0.16])
        thumb1 = ImageMobject(pixels[-1]).scale_to_fit_height(thumb_h).move_to(tip1 + thumb1_offset)
        border1 = SurroundingRectangle(thumb1, color=_s1_step4_C_Z1, stroke_width=2.5, buff=0.03)
        lab_z0 = Tex('\\text{anchor}', color=_s1_step4_C_Z0, font_size=30)
        lab_z0.move_to(thumb0.get_center() + np.array([0.0, 0.0, thumb_h / 2 + 0.26]))
        lab_z0.set_z_index(10)
        lab_z1 = Tex('\\text{guide}', color=_s1_step4_C_Z1, font_size=30)
        lab_z1.set_z_index(10)
        lab_z1.move_to(thumb1.get_center() + np.array([0.0, 0.0, -(thumb_h / 2 + 0.28)]))
        alpha = ValueTracker(0.0)
        vec_za = always_redraw(lambda: _s1_step4_vec3(ORIGIN, R * _s1_step4_slerp(z0_dir, z1_dir, alpha.get_value()), _s1_step4_C_ZA, sw=4.2, tl=0.28))
        lab_za = MathTex('\\mathbf{z}_\\alpha', color=_s1_step4_C_ZA, font_size=36)
        lab_za.add_updater(lambda mob: mob.move_to(R * _s1_step4_slerp(z0_dir, z1_dir, alpha.get_value()) * 1.3))
        follow_start_offset = thumb0.get_center() - tip0
        follow_end_offset = thumb1.get_center() - tip1

        def follow_center(t: float) -> np.ndarray:
            """Return the moving image centre for the current interpolation value."""
            tip = R * _s1_step4_slerp(z0_dir, z1_dir, t)
            offset = (1 - t) * follow_start_offset + t * follow_end_offset
            return tip + offset
        img_follow = ImageMobject(pixels[0]).scale_to_fit_height(thumb_h)
        img_follow.add_updater(lambda mob: mob.become(ImageMobject(pixels[np.clip(int(round(alpha.get_value() * (N - 1))), 0, N - 1)]).scale_to_fit_height(thumb_h).move_to(follow_center(alpha.get_value()))))
        img_follow.move_to(follow_center(0.0))
        img_follow_border = always_redraw(lambda: SurroundingRectangle(img_follow, color=_s1_step4_C_ZA, stroke_width=2.5, buff=0.03))
        scene_title = Tex('\\textit{Noise latent space} ($\\mathbb{R}^n$)', color=_s1_step4_INK, font_size=24).to_corner(UL, buff=0.45).shift(RIGHT * 1.8)
        prompt_bg = RoundedRectangle(corner_radius=0.12, width=3.1, height=2.55, stroke_color=_s1_step4_LGREY, stroke_width=1.5).set_fill(WHITE, opacity=0.95).to_corner(UR, buff=0.22)
        p_title = Tex('\\textbf{Prompt}', color=_s1_step4_INK, font_size=21)
        p_lines = VGroup(*[Tex(line, color=BLACK, font_size=17) for line in _s1_step4_COMPACT_PROMPT_LINES]).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        VGroup(p_title, p_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(prompt_bg.get_center())
        return {'alpha': alpha, 'grid_lines': grid_lines, 'ax_x': ax_x, 'ax_y': ax_y, 'ax_z': ax_z, 'lab_x': lab_x, 'lab_y': lab_y, 'lab_z': lab_z, 'vec_z0': vec_z0, 'vec_z1': vec_z1, 'thumb0': thumb0, 'border0': border0, 'lab_z0': lab_z0, 'thumb1': thumb1, 'border1': border1, 'lab_z1': lab_z1, 'scene_title': scene_title, 'prompt_bg': prompt_bg, 'p_title': p_title, 'p_lines': p_lines, 'arc_3d': arc_3d, 'vec_za': vec_za, 'lab_za': lab_za, 'img_follow': img_follow, 'img_follow_border': img_follow_border}

    def play_setup_intro(self, state: dict[str, object]) -> None:
        """Animate the compact latent-space setup sequence."""
        self.play(Create(state['grid_lines']), run_time=0.8)
        self.add_fixed_orientation_mobjects(state['lab_x'], state['lab_y'], state['lab_z'])
        self.add_fixed_in_frame_mobjects(state['scene_title'], state['prompt_bg'], state['p_title'], state['p_lines'])
        self.play(Create(state['ax_x']), Create(state['ax_y']), Create(state['ax_z']), Write(state['lab_x']), Write(state['lab_y']), Write(state['lab_z']), Write(state['scene_title']), FadeIn(state['prompt_bg']), Write(state['p_title']), Write(state['p_lines']), run_time=1.0)
        self.add_fixed_orientation_mobjects(state['thumb0'], state['border0'], state['lab_z0'], state['thumb1'], state['border1'], state['lab_z1'])
        self.play(Create(state['vec_z0']), FadeIn(state['thumb0']), FadeIn(state['border0']), Write(state['lab_z0']), Create(state['vec_z1']), FadeIn(state['thumb1']), FadeIn(state['border1']), Write(state['lab_z1']), run_time=1.2)

    def add_setup_static(self, state: dict[str, object]) -> None:
        """Add the compact latent-space setup without animation."""
        self.add(state['grid_lines'], state['ax_x'], state['ax_y'], state['ax_z'], state['vec_z0'], state['vec_z1'])
        self.add_fixed_orientation_mobjects(state['lab_x'], state['lab_y'], state['lab_z'], state['thumb0'], state['border0'], state['lab_z0'], state['thumb1'], state['border1'], state['lab_z1'])
        self.add_fixed_in_frame_mobjects(state['scene_title'], state['prompt_bg'], state['p_title'], state['p_lines'])
        self.add(state['lab_x'], state['lab_y'], state['lab_z'], state['thumb0'], state['border0'], state['lab_z0'], state['thumb1'], state['border1'], state['lab_z1'], state['scene_title'], state['prompt_bg'], state['p_title'], state['p_lines'])

    def play_interpolation(self, state: dict[str, object]) -> None:
        """Animate the compact interpolation sequence."""
        self.add_fixed_orientation_mobjects(state['lab_za'], state['img_follow'], state['img_follow_border'])
        self.play(Create(state['arc_3d']), FadeIn(state['vec_za']), FadeIn(state['lab_za']), FadeIn(state['img_follow']), FadeIn(state['img_follow_border']), run_time=0.9)
        self.wait(0.2)
        self.play(state['alpha'].animate.set_value(1.0), run_time=10.0, rate_func=linear)
        self.wait(0.8)

class Study1Stage1Step4Setup(_Study1Step4CompactBase):
    """Render the compact latent-space setup before interpolation begins."""
    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        state = _Study1Step4CompactBase.build_common_state(self)
        _Study1Step4CompactBase.play_setup_intro(self, state)
        self.wait(0.8)

class Study1Stage1Step4Interpolation(_Study1Step4CompactBase):
    """Animate only the compact latent interpolation on top of the prebuilt setup."""
    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        state = _Study1Step4CompactBase.build_common_state(self)
        _Study1Step4CompactBase.add_setup_static(self, state)
        _Study1Step4CompactBase.play_interpolation(self, state)

class Study1Stage1Step4(_Study1Step4CompactBase):
    """Compact latent-space setup and interpolation with next_section() continuity."""
    def construct(self) -> None:
        state = _Study1Step4CompactBase.build_common_state(self)
        self.next_section("07_Step4Setup")
        _Study1Step4CompactBase.play_setup_intro(self, state)
        self.wait(0.8)
        self.next_section("08_Step4Interpolation")
        _Study1Step4CompactBase.play_interpolation(self, state)


# --- inlined from study1_step5.py ---

_s1_step5_BG = WHITE
_s1_step5_INK = '#1C1C1E'
_s1_step5_LGREY = '#D1D5DB'
_s1_step5_MGREY = '#9CA3AF'
_s1_step5_BLUE = '#2563EB'
_s1_step5_ORNG = '#EA580C'
_s1_step5__INTERP_DIR = env_path('FISH_INTERPOLATIONS_DIR', REPO_ROOT / 'assets' / 'images' / 'study1' / 'fish_interpolations')
_s1_step5__LPIPS_CSV = env_path('SIMILARITY_INTERPOLATIONS_FISH_CSV', REPO_ROOT / 'assets' / 'data' / 'study1' / 'lpips-squeeze-mat-interpols-animal-fish.csv')
_s1_step5_ANCHOR_NAME = 'ANI-FIS-interpol-000.png'
_s1_step5_SELECTED_INDICES: list[int] = [0, 1, 12, 21, 31, 38, 42, 63, 91, 199]
_s1_step5__C_Z1 = '#DC2626'
_s1_step5__C_ZA = '#D97706'
_s1_step5__C_ARC = '#93C5FD'

def _s1_step5__slerp(u: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
    """Interpolate between two latent directions on the unit sphere."""
    cos_t = float(np.clip(np.dot(u, v), -1.0, 1.0))
    theta = np.arccos(cos_t)
    if abs(np.sin(theta)) < 1e-08:
        return (1.0 - t) * u + t * v
    return (np.sin((1.0 - t) * theta) * u + np.sin(t * theta) * v) / np.sin(theta)

def _s1_step5__vec3(start, end, color, sw: float=3.5, tl: float=0.18) -> Arrow:
    """Build a thin 3-D arrow for latent-space annotations."""
    return Arrow(np.asarray(start, dtype=float), np.asarray(end, dtype=float), color=color, stroke_width=sw, tip_length=tl, buff=0, max_stroke_width_to_length_ratio=100)

def _s1_step5_load_lpips_to_anchor(csv_path: Path, anchor_name: str) -> tuple[list[str], np.ndarray]:
    """Load LPIPS scores from the anchor image to every interpolation step."""
    df = pd.read_csv(csv_path, index_col=0)
    df.index.name = None
    names = df.index.tolist()
    scores = df[anchor_name].to_numpy()
    return (names, scores)

def _s1_step5_load_pixels(images_dir: Path, image_names: list[str], sz: int=256) -> np.ndarray:
    """Load and resize the selected interpolation images."""
    N = len(image_names)
    pixels = np.empty((N, sz, sz, 4), dtype=np.uint8)
    for i, name in enumerate(image_names):
        pixels[i] = np.asarray(PILImage.open(str(images_dir / name)).convert('RGBA').resize((sz, sz), PILImage.LANCZOS))
    return pixels

def _s1_step5_build_deck(images_dir: Path, image_names: list[str], n_visible: int, selected_indices: list[int], thumb_h: float=0.55, rotation_deg: float=0.0, step_x: float=0.38, step_y: float=0.02, depth_scale: float=0.998) -> Group:
    """Build the compressed interpolation deck and reserve a placeholder slot near the centre."""
    total = len(image_names)
    sample = np.linspace(0, total - 1, n_visible).round().astype(int).tolist()
    endpoint_indices = {0, total - 1}
    selected_set = set(selected_indices)
    visible = sorted((set(sample) | {i for i in selected_indices if i not in endpoint_indices}) - endpoint_indices)
    n = len(visible)
    placeholder_rank = None
    candidate_ranks = [rank for rank, img_idx in enumerate(visible) if img_idx not in selected_set]
    if candidate_ranks:
        center = (n - 1) / 2
        placeholder_rank = min(candidate_ranks, key=lambda rank: abs(rank - center))
    thumbs = Group()
    for rank, img_idx in enumerate(visible):
        if rank == placeholder_rank:
            continue
        mob = ImageMobject(str(images_dir / image_names[img_idx]))
        mob.height = thumb_h
        mob.is_placeholder = False
        mob.img_idx = img_idx
        mob.move_to([rank * step_x, rank * step_y, 0.0])
        mob.set_opacity(1.0)
        mob.set_z_index(n - rank)
        thumbs.add(mob)
    thumbs.move_to(ORIGIN)
    return (thumbs, placeholder_rank)

def _s1_step5_find_thumb(deck: Group, img_idx: int) -> Group:
    """Return the visible deck card closest to the requested image index."""
    candidates = [t for t in deck if not getattr(t, 'is_placeholder', False)]
    return min(candidates, key=lambda t: abs(t.img_idx - img_idx))

def _s1_step5_row_layout_for_mobs(mobs: list[Mobject], target_h: float, buff: float, max_width: float, y: float=0.0) -> tuple[float, float, list[np.ndarray]]:
    """Compute a centered row layout that fits the supplied mobjects within a maximum width."""
    raw_widths = [mob.width * (target_h / max(mob.height, 1e-06)) for mob in mobs]
    total_w = sum(raw_widths) + buff * max(len(mobs) - 1, 0)
    scale = min(1.0, max_width / max(total_w, 1e-06))
    final_h = target_h * scale
    final_buff = buff * scale
    final_widths = [w * scale for w in raw_widths]
    positions: list[np.ndarray] = []
    cursor = -(sum(final_widths) + final_buff * max(len(mobs) - 1, 0)) / 2
    for width in final_widths:
        positions.append(np.array([cursor + width / 2, y, 0.0]))
        cursor += width + final_buff
    return (final_h, final_buff, positions)

def _s1_step5_build_anchor_panel(images_dir: Path, anchor_name: str, img_h: float=1.55) -> Group:
    """Build the labelled anchor panel used beside the interpolation deck."""
    img = ImageMobject(str(images_dir / anchor_name))
    img.height = img_h
    border = SurroundingRectangle(img, color=_s1_step5_BLUE, stroke_width=2.5, buff=0.04)
    label = Tex('\\textbf{Anchor}', color=_s1_step5_BLUE, font_size=22)
    panel = Group(label, Group(img, border)).arrange(DOWN, buff=0.12)
    panel.anchor_img = img
    return panel

def _s1_step5_build_placeholder_card(card_h: float) -> Mobject:
    """Build the ellipsis placeholder used for omitted interpolation steps."""
    box = Square(side_length=card_h)
    box.set_stroke(opacity=0)
    box.set_fill(opacity=0)
    dots = Text('...', color=_s1_step5_INK, font_size=30)
    dots.move_to(box.get_center())
    mob = Group(box, dots)
    mob.is_placeholder = True
    return mob

class _Study1Step5Base(ThreeDScene):
    """Shared handoff, deck, and LPIPS-preselection helpers for the interpolation-strip scenes."""
    def build_common_state(self) -> dict:
        """Build the shared interpolation-strip scene state."""
        self.camera.background_color = _s1_step5_BG
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        P1_IMG_H = 2.4
        P1_ANCHOR_X = -2.8
        P1_INTERP_X = 2.8
        P1_IMG_Y = 0.2
        ANCHOR_X = -5.5
        STRIP_Y = 1.8
        STRIP_ANCHOR_GAP = 0.5
        THUMB_H = 0.55
        ROT_DEG = 0.0
        STEP_X = 0.03
        STEP_Y = 0.0
        DEPTH_SCALE = 1.0
        N_VISIBLE = 12
        image_names, lpips_scores = _s1_step5_load_lpips_to_anchor(_s1_step5__LPIPS_CSV, _s1_step5_ANCHOR_NAME)
        selected_indices = _s1_step5_SELECTED_INDICES
        pixels = _s1_step5_load_pixels(_s1_step5__INTERP_DIR, image_names, sz=256)
        N = len(pixels)
        title = Tex('Selecting Interpolation Steps', color=_s1_step5_INK, font_size=36).to_edge(UP, buff=0.36)
        anchor_simple = ImageMobject(pixels[0]).scale_to_fit_height(P1_IMG_H).move_to([P1_ANCHOR_X, P1_IMG_Y, 0.0])
        guide_simple = ImageMobject(pixels[-1]).scale_to_fit_height(P1_IMG_H).move_to([P1_INTERP_X, P1_IMG_Y, 0.0])
        anchor_grp = Group(anchor_simple)
        guide_grp = Group(guide_simple)
        anchor_simple.set_z_index(100)
        guide_simple.set_z_index(100)
        anchor_panel = _s1_step5_build_anchor_panel(_s1_step5__INTERP_DIR, _s1_step5_ANCHOR_NAME)
        anchor_panel.move_to([ANCHOR_X, STRIP_Y, 0.0])
        deck, placeholder_rank = _s1_step5_build_deck(_s1_step5__INTERP_DIR, image_names, N_VISIBLE, selected_indices, thumb_h=THUMB_H, rotation_deg=ROT_DEG, step_x=STEP_X, step_y=STEP_Y, depth_scale=DEPTH_SCALE)
        deck_left = anchor_panel.get_right()[0] + STRIP_ANCHOR_GAP
        deck.move_to([deck_left + deck.width / 2, STRIP_Y, 0.0])
        deck_label = Tex('200 interpolation steps', color=_s1_step5_INK, font_size=16).next_to(deck, UP, buff=0.15)
        deck_count_label = Tex('200 interpolated images', color=_s1_step5_INK, font_size=24)
        return {'image_names': image_names, 'lpips_scores': lpips_scores, 'selected_indices': selected_indices, 'pixels': pixels, 'N': N, 'anchor_simple': anchor_simple, 'guide_simple': guide_simple, 'anchor_grp': anchor_grp, 'guide_grp': guide_grp, 'anchor_panel': anchor_panel, 'deck': deck, 'placeholder_rank': placeholder_rank, 'deck_label': deck_label, 'deck_count_label': deck_count_label}

    def _deck_final_layout(self, st: dict) -> dict:
        """Compute the held deck layout for the interpolation-strip scenes."""
        anchor_grp = st['anchor_grp']
        guide_grp = st['guide_grp']
        deck = st['deck']
        placeholder_rank = st['placeholder_rank']
        anchor_target = np.array([-4.9, 2.15, 0.0])
        guide_target = np.array([4.9, 2.15, 0.0])
        deck_target_y = 2.28
        target_h = anchor_grp[0].height * 0.24
        edge_gap = 0.18
        inner_left = anchor_target[0] + target_h / 2 + edge_gap
        inner_right = guide_target[0] - target_h / 2 - edge_gap
        available_w = inner_right - inner_left
        card_w = target_h
        total_slots = len(deck) + (1 if placeholder_rank is not None else 0)
        step_x = max(0.0, (available_w - card_w) / max(total_slots - 1, 1))
        start_x = inner_left + card_w / 2
        slot_centers = []
        slot_scales = []
        slot_opacities = []
        for idx in range(total_slots):
            t = idx / max(total_slots - 1, 1)
            x = start_x + idx * step_x
            y = deck_target_y + 0.58 * np.sin(np.pi * t)
            recede = np.sin(np.pi * t)
            slot_centers.append(np.array([x, y, 0.0]))
            slot_scales.append(1.0 - 0.22 * recede)
            slot_opacities.append(1.0 - 0.2 * recede)
        final_centers = []
        final_scales = []
        final_opacities = []
        placeholder_center = None
        placeholder_scale = None
        for idx in range(total_slots):
            if placeholder_rank is not None and idx == placeholder_rank:
                placeholder_center = slot_centers[idx]
                placeholder_scale = slot_scales[idx]
                continue
            final_centers.append(slot_centers[idx])
            final_scales.append(slot_scales[idx])
            final_opacities.append(slot_opacities[idx])
        return {'anchor_target': anchor_target, 'guide_target': guide_target, 'target_h': target_h, 'edge_gap': edge_gap, 'final_centers': final_centers, 'final_scales': final_scales, 'final_opacities': final_opacities, 'placeholder_center': placeholder_center, 'placeholder_scale': placeholder_scale}

    def _apply_deck_card_layout(self, deck: Group, layout: dict) -> None:
        """Apply a precomputed layout to each visible deck card."""
        center = (len(deck) - 1) / 2
        for idx, card in enumerate(deck):
            card.scale_to_fit_height(layout['target_h'])
            card.move_to(layout['final_centers'][idx])
            card.scale(layout['final_scales'][idx])
            card.set_opacity(layout['final_opacities'][idx])
            card.set_z_index(10 + abs(idx - center))

    def setup_deck_final_state(self, st: dict) -> None:
        """Add the held deck layout without replaying the preceding animation."""
        layout = self._deck_final_layout(st)
        deck = st['deck']
        anchor_grp = st['anchor_grp']
        guide_grp = st['guide_grp']
        placeholder_rank = st['placeholder_rank']
        anchor_grp.scale(0.5)
        anchor_grp.move_to(layout['anchor_target'])
        guide_grp.scale(0.5)
        guide_grp.move_to(layout['guide_target'])
        anchor_grp[0].set_z_index(100)
        guide_grp[0].set_z_index(100)
        self._apply_deck_card_layout(deck, layout)
        placeholder = None
        if placeholder_rank is not None:
            placeholder = _s1_step5_build_placeholder_card(layout['target_h'])
            placeholder.scale_to_fit_height(layout['target_h'])
            placeholder.move_to(layout['placeholder_center'])
            placeholder.scale(layout['placeholder_scale'])
            placeholder.set_opacity(1.0)
            placeholder.set_z_index(20)
        st['_placeholder'] = placeholder
        deck_count_label = st['deck_count_label']
        deck_count_label.to_edge(UP, buff=0.2)
        if placeholder is not None:
            self.add(anchor_grp, guide_grp, deck, placeholder)
        else:
            self.add(anchor_grp, guide_grp, deck)
        self.add_fixed_in_frame_mobjects(deck_count_label)

    def play_step4_handoff(self, st: dict) -> None:
        """
        Replicate step-4's final state (α=1 SLERP), then:
          A — fade out all 3-D decorations and borders;
          B — rotate camera to flat 2-D view;
          C — float anchor and guide (borderless) to P1 positions, labels appear.
        """
        pixels = st['pixels']
        R = 2.85
        z0_dir = np.array([0.0, 1.0, 1.0])
        z0_dir /= np.linalg.norm(z0_dir)
        z1_dir = np.array([1.0, 1.0, 0.0])
        z1_dir /= np.linalg.norm(z1_dir)
        tip0, tip1 = (R * z0_dir, R * z1_dir)
        STEP, L_XY, L_Z = (0.5, 4.8, 3.95)
        GRID_R = L_XY * 0.9
        grid_lines = VGroup(*[seg for k in np.arange(-GRID_R, GRID_R + STEP * 0.5, STEP) for seg in (Line(np.array([k, -GRID_R, 0.0]), np.array([k, GRID_R, 0.0]), color=_s1_step5_LGREY, stroke_width=0.9), Line(np.array([-GRID_R, k, 0.0]), np.array([GRID_R, k, 0.0]), color=_s1_step5_LGREY, stroke_width=0.9))])
        ax_x = _s1_step5__vec3(ORIGIN, [L_XY, 0, 0], _s1_step5_MGREY, sw=2.4, tl=0.24)
        ax_y = _s1_step5__vec3(ORIGIN, [0, L_XY, 0], _s1_step5_MGREY, sw=2.4, tl=0.24)
        ax_z = _s1_step5__vec3(ORIGIN, [0, 0, L_Z], _s1_step5_MGREY, sw=2.4, tl=0.24)
        lab_ax = MathTex('x', color=_s1_step5_MGREY, font_size=30).move_to([L_XY + 0.32, 0.0, 0.0])
        lab_ay = MathTex('y', color=_s1_step5_MGREY, font_size=30).move_to([0.0, L_XY + 0.32, 0.0])
        lab_az = MathTex('z', color=_s1_step5_MGREY, font_size=30).move_to([0.18, 0.18, L_Z - 0.08])
        vec_z0 = _s1_step5__vec3(ORIGIN, tip0, _s1_step5_BLUE, sw=4.2, tl=0.28)
        vec_z1 = _s1_step5__vec3(ORIGIN, tip1, _s1_step5__C_Z1, sw=4.2, tl=0.28)
        arc_3d = ParametricFunction(lambda t: R * _s1_step5__slerp(z0_dir, z1_dir, t), t_range=[0.0, 1.0, 0.005], color=_s1_step5__C_ARC, stroke_width=4)
        tip_a = R * _s1_step5__slerp(z0_dir, z1_dir, 1.0)
        vec_za = _s1_step5__vec3(ORIGIN, tip_a, _s1_step5__C_ZA, sw=4.2, tl=0.28)
        lab_za = MathTex('\\mathbf{z}_\\alpha', color=_s1_step5__C_ZA, font_size=36).move_to(tip_a * 1.3)
        THUMB_H = 0.95
        thumb0 = st['anchor_grp'][0]
        thumb0.scale_to_fit_height(THUMB_H).move_to(tip0 + z0_dir * 0.92)
        border0 = SurroundingRectangle(thumb0, color=_s1_step5_BLUE, stroke_width=2.5, buff=0.03)
        t1_offset = np.array([THUMB_H / 2 + 0.05, THUMB_H / 2, 0.16])
        thumb1 = st['guide_grp'][0]
        thumb1.scale_to_fit_height(THUMB_H).move_to(tip1 + t1_offset)
        border1 = SurroundingRectangle(thumb1, color=_s1_step5__C_Z1, stroke_width=2.5, buff=0.03)
        lab_z0 = Tex('\\text{anchor}', color=_s1_step5_BLUE, font_size=30).set_z_index(10)
        lab_z0.move_to(thumb0.get_center() + np.array([0.0, 0.0, THUMB_H / 2 + 0.26]))
        lab_z1 = Tex('\\text{guide}', color=_s1_step5__C_Z1, font_size=30).set_z_index(10)
        lab_z1.move_to(thumb1.get_center() + np.array([0.0, 0.0, -(THUMB_H / 2 + 0.28)]))
        img_follow = ImageMobject(pixels[-1]).scale_to_fit_height(THUMB_H).move_to(thumb1.get_center())
        img_follow_border = SurroundingRectangle(img_follow, color=_s1_step5__C_ZA, stroke_width=2.5, buff=0.03)
        _prompt_lines = ('``award-winning marine photo', 'of a colorful fish in a coral reef,', 'centered in the scene,', 'vibrant underwater scene,', "high detail''")
        scene_title = Tex('\\textit{Noise latent space} ($\\mathbb{R}^n$)', color=_s1_step5_INK, font_size=24).to_corner(UL, buff=0.45).shift(RIGHT * 1.8)
        prompt_bg = RoundedRectangle(corner_radius=0.12, width=3.1, height=2.55, stroke_color=_s1_step5_LGREY, stroke_width=1.5).set_fill(WHITE, opacity=0.95).to_corner(UR, buff=0.22)
        p_title = Tex('\\textbf{Prompt}', color=_s1_step5_INK, font_size=21)
        p_lines = VGroup(*[Tex(line, color=BLACK, font_size=17) for line in _prompt_lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        VGroup(p_title, p_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(prompt_bg.get_center())
        self.set_camera_orientation(phi=62 * DEGREES, theta=-42 * DEGREES, frame_center=np.array([0.35, 0.2, 0.0]))
        self.add(grid_lines, ax_x, ax_y, ax_z, vec_z0, vec_z1, arc_3d, vec_za)
        self.add_fixed_orientation_mobjects(lab_ax, lab_ay, lab_az, thumb0, border0, lab_z0, thumb1, border1, lab_z1, img_follow, img_follow_border, lab_za)
        self.add_fixed_in_frame_mobjects(scene_title, prompt_bg, p_title, p_lines)
        self.wait(0.6)
        self.play(FadeOut(grid_lines, ax_x, ax_y, ax_z, lab_ax, lab_ay, lab_az, vec_z0, vec_z1, arc_3d, vec_za, lab_za, border0, border1, img_follow, img_follow_border, lab_z0, lab_z1, scene_title, prompt_bg, p_title, p_lines), run_time=1.0)
        P1_IMG_H = 2.4
        P1_ANCHOR_X = -2.8
        P1_INTERP_X = 2.8
        P1_IMG_Y = 0.2
        for mob in (thumb0, thumb1):
            mob.clear_updaters()
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, frame_center=ORIGIN, added_anims=[thumb0.animate.scale_to_fit_height(P1_IMG_H).move_to([P1_ANCHOR_X, P1_IMG_Y, 0.0]), thumb1.animate.scale_to_fit_height(P1_IMG_H).move_to([P1_INTERP_X, P1_IMG_Y, 0.0])], run_time=1.2)
        self.wait(0.6)

    def play_deck_between(self, st: dict) -> None:
        """
        Start from the handoff end-state, shrink anchor/guide into the top
        corners, and unfold the interpolation deck between them.
        """
        deck = st['deck']
        anchor_grp = st['anchor_grp']
        guide_grp = st['guide_grp']
        placeholder_rank = st['placeholder_rank']
        placeholder = None
        layout = self._deck_final_layout(st)
        anchor_grp[0].set_z_index(100)
        guide_grp[0].set_z_index(100)
        if placeholder_rank is not None:
            placeholder = _s1_step5_build_placeholder_card(layout['target_h'])
        collapse_center = np.array([0.0, 0.95, 0.0])
        for card in deck:
            card.scale_to_fit_height(layout['target_h'])
            card.move_to(collapse_center)
            card.set_opacity(0)
        center = (len(deck) - 1) / 2
        for idx, card in enumerate(deck):
            card.set_z_index(10 + abs(idx - center))
        deck_unfold = AnimationGroup(*[card.animate.move_to(layout['final_centers'][idx]).scale(layout['final_scales'][idx]).set_opacity(0.0 if getattr(card, 'is_placeholder', False) else layout['final_opacities'][idx]) for idx, card in enumerate(deck)])
        self.play(anchor_grp.animate.scale(0.5).move_to(layout['anchor_target']), guide_grp.animate.scale(0.5).move_to(layout['guide_target']), deck_unfold, run_time=1.6)
        self._apply_deck_card_layout(deck, layout)
        deck_count_label = st['deck_count_label']
        deck_count_label.to_edge(UP, buff=0.2)
        self.add_fixed_in_frame_mobjects(deck_count_label)
        if placeholder is not None and placeholder_rank is not None:
            placeholder.scale_to_fit_height(layout['target_h'])
            placeholder.move_to(layout['placeholder_center'])
            placeholder.scale(layout['placeholder_scale'])
            placeholder.set_opacity(1.0)
            placeholder.set_z_index(20)
            self.add(placeholder)
            self.play(Write(deck_count_label), FadeIn(placeholder), run_time=0.4)
        else:
            self.play(Write(deck_count_label), run_time=0.4)
        st['_placeholder'] = placeholder
        self.wait(0.8)

    def play_lpips_formula(self, st: dict) -> None:
        """Animate the LPIPS formula."""
        formula = MathTex('\\mathrm{LPIPS}(\\mathrm{anchor},\\, x_n)', color=_s1_step5_INK, font_size=34).move_to([0.0, 0.0, 0.0])
        arrow = Arrow(start=[0.0, 1.6, 0.0], end=formula.get_top() + UP * 0.12, color=_s1_step5_INK, stroke_width=2.5, tip_length=0.18, buff=0.0)
        self.play(GrowArrow(arrow), Write(formula), run_time=0.8)
        self.wait(0.5)
        st['_lpips_formula'] = formula
        st['_lpips_arrow'] = arrow

    def play_preselection(self, st: dict) -> None:
        """Animate the preselection."""
        deck = st['deck']
        selected_indices = st['selected_indices']
        endpoint_indices = {0, st['N'] - 1}
        selected_thumbs = [_s1_step5_find_thumb(deck, i) for i in selected_indices if i not in endpoint_indices]
        other_thumbs = [t for t in deck if t not in selected_thumbs and t.img_idx not in endpoint_indices]
        title = Tex('\\textbf{Model-based preselection}', color=_s1_step5_INK, font_size=30)
        title.to_edge(UP, buff=0.36)
        selected_boxes = VGroup(*[SurroundingRectangle(t, color=_s1_step5_ORNG, stroke_width=2.5, buff=0.02).set_z_index(t.z_index + 0.1) for t in selected_thumbs])
        placeholder = st.get('_placeholder')
        fade_targets = [st['_lpips_arrow'], st['_lpips_formula'], st['deck_count_label']]
        if placeholder is not None:
            fade_targets.append(placeholder)
        self.play(FadeOut(*fade_targets), Write(title), *[t.animate.set_opacity(1.0) for t in selected_thumbs], *[t.animate.set_opacity(0.12) for t in other_thumbs], run_time=0.8)
        self.play(FadeIn(selected_boxes), run_time=0.4)
        st['_selected_boxes'] = selected_boxes
        self.wait(1.0)

    def play_final_reveal(self, st: dict) -> None:
        """Animate the final reveal."""
        deck = st['deck']
        selected_indices = st['selected_indices']
        anchor_grp = st['anchor_grp']
        guide_grp = st['guide_grp']
        endpoint_indices = {0, st['N'] - 1}
        selected_thumbs = [_s1_step5_find_thumb(deck, i) for i in selected_indices if i not in endpoint_indices]
        other_thumbs = [t for t in deck if t not in selected_thumbs]
        anchor_grp.set_z_index(len(deck) + 20)
        guide_grp.set_z_index(len(deck) + 20)
        IMG_H = 1.3
        BUFF = 0.12
        row = [anchor_grp] + selected_thumbs + [guide_grp]
        final_h, _, pos = _s1_step5_row_layout_for_mobs(row, target_h=IMG_H, buff=BUFF, max_width=config.frame_width - 0.8, y=0.0)
        row_anims = [mob.animate.scale_to_fit_height(final_h).move_to(p) for mob, p in zip(row, pos)]
        self.play(FadeOut(*other_thumbs, st['_selected_boxes']), run_time=0.4)
        self.play(*row_anims, run_time=1.2)
        self.wait(1.0)

class Study1Stage1Step5Handoff(_Study1Step5Base):
    """Scene 1 — step-4 3-D ending → anchor and guide settle on screen."""

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        state = _Study1Step5Base.build_common_state(self)
        _Study1Step5Base.play_step4_handoff(self, state)
        self.wait(0.5)

class Study1Stage1Step5Deck(_Study1Step5Base):
    """Scene 2 — deck of cards fans between anchor and guide."""

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        state = _Study1Step5Base.build_common_state(self)
        self.add(state['anchor_grp'], state['guide_grp'])
        _Study1Step5Base.play_deck_between(self, state)
        self.wait(0.5)

class Study1Stage1Step5LPIPS(_Study1Step5Base):
    """Scene 3 — LPIPS formula, then model-based preselection of 10 images."""

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        state = _Study1Step5Base.build_common_state(self)
        _Study1Step5Base.setup_deck_final_state(self, state)
        _Study1Step5Base.play_lpips_formula(self, state)
        _Study1Step5Base.play_preselection(self, state)
        _Study1Step5Base.play_final_reveal(self, state)
        self.wait(1.0)


class Study1Stage1Step5(_Study1Step5Base):
    """Merged handoff → deck → LPIPS preselection with next_section() continuity."""

    def construct(self) -> None:
        state = _Study1Step5Base.build_common_state(self)

        self.next_section("09_Step5Handoff")
        _Study1Step5Base.play_step4_handoff(self, state)
        self.wait(0.5)

        self.next_section("10_Step5Deck")
        # anchor_grp and guide_grp are already on screen from the handoff animation
        _Study1Step5Base.play_deck_between(self, state)
        self.wait(0.5)

        self.next_section("11_Step5LPIPS")
        # deck layout and anchor/guide corners are live — no rebuild needed
        _Study1Step5Base.play_lpips_formula(self, state)
        _Study1Step5Base.play_preselection(self, state)
        _Study1Step5Base.play_final_reveal(self, state)
        self.wait(1.0)


# --- inlined from study1_stimulus_setshowcase.py ---

_s1_stimshow_BG = WHITE
_s1_stimshow_INK = '#1C1C1E'
_s1_stimshow_STIMULI_TASK_DIR = env_path('STIMULI_TASK_DIR', REPO_ROOT / 'assets' / 'images' / 'study1' / 'stimuli_task')
_s1_stimshow_SHOWCASE_TARGETS = [('Tropical Karst', 'LAN-TRP'), ('Pine Mediterranean', 'PLA-PIE'), ('Observatory', 'BUI-OBS'), ('Sofa', 'ITE-SOF'), ('Passenger train', 'VEH-PAS')]

def _s1_stimshow_resolve_strip_paths(display_name: str, image_code: str) -> list[Path]:
    """Resolve the 10-image strip for one preselected stimulus set."""
    paths = [_s1_stimshow_STIMULI_TASK_DIR / f'{image_code}-{idx:02d}.png' for idx in range(10)]
    missing = [fp.name for fp in paths if not fp.exists()]
    if missing:
        raise FileNotFoundError(f"Could not resolve the full 10-image set for '{display_name}' with code '{image_code}' from {_s1_stimshow_STIMULI_TASK_DIR}. Missing: {missing}")
    return paths

def _s1_stimshow_build_row(image_paths: list[Path]) -> dict[str, Mobject]:
    """Build one horizontal row of preselected stimulus thumbnails."""
    thumbs = Group(*[ImageMobject(str(image_path)) for image_path in image_paths])
    for thumb in thumbs:
        thumb.height = 0.94
    thumbs.arrange(RIGHT, buff=0.035)
    return {'thumbs': thumbs}

class Study1StimulusSetShowcase(Scene):
    """Display several model-preselected 10-image stimulus sets as held strips."""
    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stimshow_BG
        title = Tex('\\textbf{Model-based preselected sets of 10 images for each object-scene}', color=_s1_stimshow_INK, font_size=24)
        title.to_edge(UP, buff=0.18)
        row_specs = [_s1_stimshow_build_row(_s1_stimshow_resolve_strip_paths(display_name, image_code)) for display_name, image_code in _s1_stimshow_SHOWCASE_TARGETS]
        anchor_mobs = Group()
        thumb_w = row_specs[0]['thumbs'][0].width
        thumb_h = row_specs[0]['thumbs'][0].height
        thumb_gap = 0.035
        row_gap = 0.05
        row_width = 10 * thumb_w + 9 * thumb_gap
        row_height = thumb_h
        x_left = -row_width / 2 + thumb_w / 2
        row_ys = np.linspace((len(row_specs) - 1) * (row_height + row_gap) / 2, -(len(row_specs) - 1) * (row_height + row_gap) / 2, len(row_specs))
        rows_target = Group(*[spec['thumbs'] for spec in row_specs])
        rows_target.move_to(DOWN * 0.36)
        available_width = config.frame_width - 0.06
        available_height = config.frame_height - 0.52
        if rows_target.width > available_width:
            rows_target.scale_to_fit_width(available_width)
        if rows_target.height > available_height:
            rows_target.scale_to_fit_height(available_height)
        thumb_w = row_specs[0]['thumbs'][0].width
        thumb_h = row_specs[0]['thumbs'][0].height
        row_width = 10 * thumb_w + 9 * thumb_gap
        row_height = thumb_h
        x_left = -row_width / 2 + thumb_w / 2
        row_ys = np.linspace((len(row_specs) - 1) * (row_height + row_gap) / 2, -(len(row_specs) - 1) * (row_height + row_gap) / 2, len(row_specs)) + np.array([-0.36] * len(row_specs))
        unfold_tracks = []
        for row_idx, spec in enumerate(row_specs):
            thumbs = spec['thumbs']
            anchor = thumbs[0]
            start_center = np.array([0.0, row_ys[row_idx], 0.0])
            final_centers = [np.array([x_left + thumb_idx * (thumb_w + thumb_gap), row_ys[row_idx], 0.0]) for thumb_idx in range(len(thumbs))]
            anchor_mobs.add(anchor)
            anchor.move_to(start_center)
            anchor.set_z_index(3)
            for thumb_idx, thumb in enumerate(thumbs):
                if thumb_idx == 0:
                    continue
                thumb.move_to(start_center)
                thumb.set_opacity(0)
                thumb.set_z_index(2)
            thumb_animations = [anchor.animate.move_to(final_centers[0])]
            for thumb_idx, thumb in enumerate(thumbs[1:], start=1):
                thumb_animations.append(Succession(Wait(0.05 * thumb_idx), thumb.animate.move_to(final_centers[thumb_idx]).set_opacity(1)))
            unfold_tracks.append(AnimationGroup(*thumb_animations, lag_ratio=0))
        self.play(FadeIn(title, shift=DOWN * 0.04), run_time=0.35)
        self.play(FadeIn(anchor_mobs, scale=0.9), run_time=0.4)
        self.wait(0.35)
        self.play(AnimationGroup(*unfold_tracks, lag_ratio=0.08, rate_func=smooth), run_time=2.6)
        self.wait(1.4)


# --- inlined from study1_stage2_psychophysical.py ---

_s1_stage2_BG = WHITE
_s1_stage2_INK = '#1C1C1E'
_s1_stage2_LGREY = '#D1D5DB'
_s1_stage2_MGREY = '#9CA3AF'
_s1_stage2_BLUE = '#2563EB'
_s1_stage2_AMBER = '#D97706'
_s1_stage2_STIM_DIR = env_path('STIMULI_REORDERED_DIR', REPO_ROOT / 'assets' / 'images' / 'stimuli_reordered')
_s1_stage2_STAGE2_ASSET_DIR = REPO_ROOT / 'assets' / 'images' / 'study1_stage2'

def _s1_stage2_fish_path(idx: int) -> str:
    """Return the fish stimulus path for one index."""
    return str(_s1_stage2_STIM_DIR / f'animal_fish-{idx:02d}.png')

def _s1_stage2_stimulus_path(prefix: str, idx: int) -> str:
    """Return the ordered stimulus path for a category prefix and index."""
    return str(_s1_stage2_STIM_DIR / f'{prefix}-{idx:02d}.png')
_s1_stage2_EMBED_Y = np.array([1.0, 0.93, 0.83, 0.7, 0.57, 0.44, 0.32, 0.2, 0.09, 0.02])

class Study1Stage2TripletTask(Scene):
    """
    Phase 1 — introduce the task mathematically.
    Phase 2 — illustrate with fish-00 (s_i, reference), fish-02 (s_j, probe),
               fish-07 (s_k, probe) arranged in an equilateral triangle inside a box.
    """
    _D = 2.22
    _IMG_H = 1.18
    _CY = -1.05

    def _positions(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return the positions."""
        d, h = (self._D, self._D * np.sqrt(3) / 2)
        cy = self._CY
        si = np.array([0.0, cy + 2 * h / 3, 0.0])
        sj = np.array([-d / 2, cy - h / 3, 0.0])
        sk = np.array([d / 2, cy - h / 3, 0.0])
        return (si, sj, sk)

    def _make_probe(self, idx: int, pos: np.ndarray) -> tuple[ImageMobject, SurroundingRectangle]:
        """Build the probe."""
        img = ImageMobject(_s1_stage2_fish_path(idx)).scale_to_fit_height(self._IMG_H).move_to(pos)
        bdr = SurroundingRectangle(img, color=_s1_stage2_LGREY, stroke_width=1.5, buff=0.05)
        return (img, bdr)

    def _index_tex(self, idx: int, color: str) -> MathTex:
        """Return the index TeX."""
        return MathTex(f's_{{{idx + 1}}}', color=color, font_size=28)

    def _response_row(self, ref_idx: int, selected_idx: int, other_idx: int) -> VGroup:
        """Return the response row."""
        parts = [MathTex('(', color=_s1_stage2_INK, font_size=28), MathTex(str(ref_idx + 1), color=_s1_stage2_INK, font_size=28), MathTex(',', color=_s1_stage2_INK, font_size=28), MathTex(str(selected_idx + 1), color=_s1_stage2_INK, font_size=28), MathTex(',', color=_s1_stage2_INK, font_size=28), MathTex(str(other_idx + 1), color=_s1_stage2_INK, font_size=28), MathTex(')', color=_s1_stage2_INK, font_size=28)]
        return VGroup(*parts).arrange(RIGHT, buff=0.06, aligned_edge=DOWN)

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage2_BG
        si_pos, sj_pos, sk_pos = self._positions()
        IMG_H = self._IMG_H
        trial_specs = [{'ref': 0, 'left': 2, 'right': 7, 'selected': 'left'}, {'ref': 4, 'left': 8, 'right': 3, 'selected': 'right'}, {'ref': 6, 'left': 1, 'right': 9, 'selected': 'left'}, {'ref': 8, 'left': 5, 'right': 2, 'selected': 'right'}]
        title = Tex('Psychophysical Validation', color=_s1_stage2_INK, font_size=38).move_to(ORIGIN)
        title_top_target = title.copy().to_edge(UP, buff=0.28)
        subtitle = Tex('Triplet similarity task \\quad $N = 1{,}113$ participants', color=_s1_stage2_INK, font_size=24).next_to(title_top_target, DOWN, buff=0.1)
        question = VGroup(Tex('Does the model-based preselection capture', color=_s1_stage2_INK, font_size=24), Tex('a human-perceived perceptual continuum?', color=_s1_stage2_INK, font_size=24)).arrange(DOWN, buff=0.08).next_to(subtitle, DOWN, buff=0.16)
        math1 = Tex('Given a set of images $\\mathcal{S} = \\{s_1, s_2, \\ldots, s_n\\}$,', color=_s1_stage2_INK, font_size=26)
        math2 = Tex('participants view triplets $(s_i,\\, s_j,\\, s_k)$', color=_s1_stage2_INK, font_size=26)
        math3 = Tex('and select which probe is more similar', color=_s1_stage2_INK, font_size=26)
        math4 = Tex('to the reference image $s_i$.', color=_s1_stage2_INK, font_size=26)
        math_block = VGroup(math1, math2, math3, math4).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        lbl_h = 0.38
        pad = 0.28
        box_top = si_pos[1] + IMG_H / 2 + pad
        box_bottom = sj_pos[1] - IMG_H / 2 - lbl_h - pad
        trial_center = np.array([0.0, (box_top + box_bottom) / 2, 0.0])
        trial_frame_side = max(self._D + IMG_H + 2 * pad, box_top - box_bottom) + 0.12
        trial_frame = Square(side_length=trial_frame_side, color=_s1_stage2_LGREY, stroke_width=1.5).set_fill('#F9FAFB', opacity=0.45).move_to(trial_center)
        math_block.scale_to_fit_width(3.95)
        math_block.next_to(trial_frame, LEFT, buff=0.55)
        math_block.align_to(trial_frame, UP).shift(DOWN * 0.82)
        computer_icon = ImageMobject(str(_s1_stage2_STAGE2_ASSET_DIR / 'computer.png')).scale_to_fit_width(0.56).move_to(trial_center + UP * (trial_frame_side / 2 + 0.42))
        si_img = ImageMobject(_s1_stage2_fish_path(trial_specs[0]['ref'])).scale_to_fit_height(IMG_H).move_to(si_pos)
        si_bdr = SurroundingRectangle(si_img, color=_s1_stage2_LGREY, stroke_width=1.5, buff=0.05)
        sj_img, sj_bdr = self._make_probe(trial_specs[0]['left'], sj_pos)
        sk_img, sk_bdr = self._make_probe(trial_specs[0]['right'], sk_pos)
        si_lbl = self._index_tex(trial_specs[0]['ref'], _s1_stage2_INK).next_to(si_img, DOWN, buff=0.16)
        sj_lbl = self._index_tex(trial_specs[0]['left'], _s1_stage2_INK).next_to(sj_img, DOWN, buff=0.16)
        sk_lbl = self._index_tex(trial_specs[0]['right'], _s1_stage2_INK).next_to(sk_img, DOWN, buff=0.16)
        probe_pair = Group(sj_img, sk_img)
        reference_tag = Tex('Reference', color=_s1_stage2_INK, font_size=24).next_to(si_img, UP, buff=0.18)
        probes_tag = Tex('Probes', color=_s1_stage2_INK, font_size=24).next_to(probe_pair, DOWN, buff=0.42)
        reference_focus = SurroundingRectangle(si_img, color=_s1_stage2_MGREY, stroke_width=2.1, buff=0.1)
        probes_focus = SurroundingRectangle(probe_pair, color=_s1_stage2_MGREY, stroke_width=2.1, buff=0.14)
        response_row_targets = VGroup(*[self._response_row(spec['ref'], spec['left'] if spec['selected'] == 'left' else spec['right'], spec['right'] if spec['selected'] == 'left' else spec['left']) for spec in trial_specs]).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        response_lhs = MathTex('\\mathit{T} \\; =', color=_s1_stage2_INK, font_size=30)
        response_lhs.next_to(response_row_targets, LEFT, buff=0.16).align_to(response_row_targets[0], UP)
        response_stack = VGroup(response_lhs, response_row_targets)
        response_title = Tex('Behavioural responses', color=_s1_stage2_INK, font_size=24).next_to(response_stack, UP, buff=0.28).align_to(response_stack, LEFT)
        response_panel_content = VGroup(response_title, response_lhs, response_row_targets)
        response_group = response_panel_content.move_to([4.35, -0.68, 0.0])
        response_rows = []
        for target in response_row_targets:
            row = target.copy()
            row.move_to(target.get_center()).align_to(target, LEFT)
            response_rows.append(row)
        continuation_dots = MathTex('\\vdots', color=_s1_stage2_MGREY, font_size=30)
        continuation_dots.next_to(response_rows[-1], DOWN, buff=0.16)
        continuation_dots.move_to([response_rows[-1].get_center()[0], continuation_dots.get_center()[1], 0.0])

        def emphasize_response_mapping(row: VGroup, selected_side: str) -> None:
            """Animate the response mapping."""
            selected_bdr = sj_bdr if selected_side == 'left' else sk_bdr
            self.play(AnimationGroup(Indicate(si_bdr, color=_s1_stage2_BLUE, scale_factor=1.06), Indicate(row.submobjects[1], color=_s1_stage2_BLUE, scale_factor=1.25), lag_ratio=0.0), run_time=0.75)
            self.wait(0.12)
            self.play(AnimationGroup(Indicate(selected_bdr, color=_s1_stage2_AMBER, scale_factor=1.08), Indicate(row.submobjects[3], color=_s1_stage2_AMBER, scale_factor=1.25), lag_ratio=0.0), run_time=0.75)
            self.wait(0.12)

        def highlight_choice(selected_side: str) -> None:
            """Animate the choice."""
            if selected_side == 'left':
                selected_img, selected_bdr, selected_lbl = (sj_img, sj_bdr, sj_lbl)
                other_img, other_bdr, other_lbl = (sk_img, sk_bdr, sk_lbl)
            else:
                selected_img, selected_bdr, selected_lbl = (sk_img, sk_bdr, sk_lbl)
                other_img, other_bdr, other_lbl = (sj_img, sj_bdr, sj_lbl)
            sel_bdr = SurroundingRectangle(selected_img, color=_s1_stage2_AMBER, stroke_width=4.2, buff=0.07)
            self.play(Transform(selected_bdr, sel_bdr), other_img.animate.set_opacity(0.28), other_bdr.animate.set_stroke(opacity=0.12), other_lbl.animate.set_opacity(0.28), selected_img.animate.set_opacity(1.0), selected_lbl.animate.set_opacity(1.0), run_time=0.55)
        self.play(Write(title), run_time=0.65)
        self.wait(0.15)
        self.play(title.animate.move_to(title_top_target), run_time=0.55)
        self.play(FadeIn(subtitle, shift=UP * 0.1), run_time=0.45)
        self.play(FadeIn(question, shift=UP * 0.12), run_time=0.6)
        self.wait(0.45)
        self.play(FadeIn(math_block, shift=UP * 0.1), run_time=0.35)
        self.wait(0.35)
        self.play(Create(trial_frame), FadeIn(computer_icon, shift=LEFT * 0.08), run_time=0.5)
        self.play(FadeIn(si_img), Create(si_bdr), FadeIn(si_lbl), run_time=0.6)
        self.wait(0.2)
        self.play(AnimationGroup(AnimationGroup(FadeIn(sj_img), Create(sj_bdr), FadeIn(sj_lbl)), AnimationGroup(FadeIn(sk_img), Create(sk_bdr), FadeIn(sk_lbl)), lag_ratio=0.3), run_time=0.8)
        self.play(FadeIn(reference_tag, shift=UP * 0.08), FadeIn(probes_tag, shift=UP * 0.08), run_time=0.35)
        self.play(FadeIn(reference_focus), run_time=0.45)
        self.wait(0.25)
        self.play(FadeIn(probes_focus), run_time=0.45)
        self.wait(1.0)
        self.wait(0.5)
        return

class Study1Stage2TripletTask2(Study1Stage2TripletTask):
    """Follow-up scene: example trials and participant triplet-set construction."""

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage2_BG
        si_pos, sj_pos, sk_pos = self._positions()
        IMG_H = self._IMG_H
        trial_specs = [{'ref': 0, 'left': 2, 'right': 7, 'selected': 'left'}, {'ref': 4, 'left': 8, 'right': 3, 'selected': 'right'}, {'ref': 6, 'left': 1, 'right': 9, 'selected': 'left'}, {'ref': 8, 'left': 5, 'right': 2, 'selected': 'right'}]
        title = Tex('Psychophysical Validation', color=_s1_stage2_INK, font_size=38).to_edge(UP, buff=0.28)
        subtitle = Tex('Triplet similarity task \\quad $N = 1{,}113$ participants', color=_s1_stage2_INK, font_size=24).next_to(title, DOWN, buff=0.1)
        question = VGroup(Tex('Does the model-based preselection capture', color=_s1_stage2_INK, font_size=24), Tex('a human-perceived perceptual continuum?', color=_s1_stage2_INK, font_size=24)).arrange(DOWN, buff=0.08).next_to(subtitle, DOWN, buff=0.16)
        lbl_h = 0.38
        pad = 0.28
        box_top = si_pos[1] + IMG_H / 2 + pad
        box_bottom = sj_pos[1] - IMG_H / 2 - lbl_h - pad
        trial_center = np.array([0.0, (box_top + box_bottom) / 2, 0.0])
        trial_frame_side = max(self._D + IMG_H + 2 * pad, box_top - box_bottom) + 0.12
        trial_frame = Square(side_length=trial_frame_side, color=_s1_stage2_LGREY, stroke_width=1.5).set_fill('#F9FAFB', opacity=0.45).move_to(trial_center)
        computer_icon = ImageMobject(str(_s1_stage2_STAGE2_ASSET_DIR / 'computer.png')).scale_to_fit_width(0.56).move_to(trial_center + UP * (trial_frame_side / 2 + 0.42))
        math1 = Tex('Given a set of images $\\mathcal{S} = \\{s_1, s_2, \\ldots, s_n\\}$,', color=_s1_stage2_INK, font_size=26)
        math2 = Tex('participants view triplets $(s_i,\\, s_j,\\, s_k)$', color=_s1_stage2_INK, font_size=26)
        math3 = Tex('and select which probe is more similar', color=_s1_stage2_INK, font_size=26)
        math4 = Tex('to the reference image $s_i$.', color=_s1_stage2_INK, font_size=26)
        math_block = VGroup(math1, math2, math3, math4).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        math_block.scale_to_fit_width(3.95)
        math_block.next_to(trial_frame, LEFT, buff=0.55)
        math_block.align_to(trial_frame, UP).shift(DOWN * 0.82)
        si_img = ImageMobject(_s1_stage2_fish_path(trial_specs[0]['ref'])).scale_to_fit_height(IMG_H).move_to(si_pos)
        si_bdr = SurroundingRectangle(si_img, color=_s1_stage2_LGREY, stroke_width=1.5, buff=0.05)
        sj_img, sj_bdr = self._make_probe(trial_specs[0]['left'], sj_pos)
        sk_img, sk_bdr = self._make_probe(trial_specs[0]['right'], sk_pos)
        si_lbl = self._index_tex(trial_specs[0]['ref'], _s1_stage2_INK).next_to(si_img, DOWN, buff=0.16)
        sj_lbl = self._index_tex(trial_specs[0]['left'], _s1_stage2_INK).next_to(sj_img, DOWN, buff=0.16)
        sk_lbl = self._index_tex(trial_specs[0]['right'], _s1_stage2_INK).next_to(sk_img, DOWN, buff=0.16)
        probe_pair = Group(sj_img, sk_img)
        reference_tag = Tex('Reference', color=_s1_stage2_INK, font_size=24).next_to(si_img, UP, buff=0.18)
        probes_tag = Tex('Probes', color=_s1_stage2_INK, font_size=24).next_to(probe_pair, DOWN, buff=0.42)
        reference_focus = SurroundingRectangle(si_img, color=_s1_stage2_MGREY, stroke_width=2.1, buff=0.1)
        probes_focus = SurroundingRectangle(probe_pair, color=_s1_stage2_MGREY, stroke_width=2.1, buff=0.14)
        response_row_targets = VGroup(*[self._response_row(spec['ref'], spec['left'] if spec['selected'] == 'left' else spec['right'], spec['right'] if spec['selected'] == 'left' else spec['left']) for spec in trial_specs]).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        response_lhs = MathTex('\\mathit{T} \\; =', color=_s1_stage2_INK, font_size=30)
        response_lhs.next_to(response_row_targets, LEFT, buff=0.16).align_to(response_row_targets[0], UP)
        response_stack = VGroup(response_lhs, response_row_targets)
        response_title = Tex('Behavioural responses', color=_s1_stage2_INK, font_size=24).next_to(response_stack, UP, buff=0.28).align_to(response_stack, LEFT)
        response_panel_content = VGroup(response_title, response_lhs, response_row_targets)
        response_panel_content.move_to([4.35, -0.68, 0.0])
        response_rows = []
        for target in response_row_targets:
            row = target.copy()
            row.move_to(target.get_center()).align_to(target, LEFT)
            response_rows.append(row)
        continuation_dots = MathTex('\\vdots', color=_s1_stage2_MGREY, font_size=30)
        continuation_dots.next_to(response_rows[-1], DOWN, buff=0.16)
        continuation_dots.move_to([response_rows[-1].get_center()[0], continuation_dots.get_center()[1], 0.0])

        def emphasize_response_mapping(row: VGroup, selected_side: str) -> None:
            """Animate the response mapping."""
            selected_bdr = sj_bdr if selected_side == 'left' else sk_bdr
            self.play(AnimationGroup(Indicate(si_bdr, color=_s1_stage2_BLUE, scale_factor=1.06), Indicate(row.submobjects[1], color=_s1_stage2_BLUE, scale_factor=1.25), lag_ratio=0.0), run_time=0.75)
            self.wait(0.12)
            self.play(AnimationGroup(Indicate(selected_bdr, color=_s1_stage2_AMBER, scale_factor=1.08), Indicate(row.submobjects[3], color=_s1_stage2_AMBER, scale_factor=1.25), lag_ratio=0.0), run_time=0.75)
            self.wait(0.12)

        def highlight_choice(selected_side: str) -> None:
            """Animate the choice."""
            if selected_side == 'left':
                selected_img, selected_bdr, selected_lbl = (sj_img, sj_bdr, sj_lbl)
                other_img, other_bdr, other_lbl = (sk_img, sk_bdr, sk_lbl)
            else:
                selected_img, selected_bdr, selected_lbl = (sk_img, sk_bdr, sk_lbl)
                other_img, other_bdr, other_lbl = (sj_img, sj_bdr, sj_lbl)
            sel_bdr = SurroundingRectangle(selected_img, color=_s1_stage2_AMBER, stroke_width=4.2, buff=0.07)
            self.play(Transform(selected_bdr, sel_bdr), other_img.animate.set_opacity(0.28), other_bdr.animate.set_stroke(opacity=0.12), other_lbl.animate.set_opacity(0.28), selected_img.animate.set_opacity(1.0), selected_lbl.animate.set_opacity(1.0), run_time=0.55)
        self.add(title, subtitle, question, math_block, trial_frame, computer_icon, si_img, si_bdr, si_lbl, sj_img, sj_bdr, sj_lbl, sk_img, sk_bdr, sk_lbl, reference_tag, probes_tag, reference_focus, probes_focus)
        self.wait(0.5)
        self.play(FadeOut(reference_tag, shift=UP * 0.06), FadeOut(probes_tag, shift=UP * 0.06), FadeOut(reference_focus), FadeOut(probes_focus), run_time=0.35)
        self.wait(0.2)
        highlight_choice(trial_specs[0]['selected'])
        self.play(FadeIn(response_title, shift=UP * 0.1), FadeIn(response_lhs, shift=RIGHT * 0.1), run_time=0.65)
        self.play(Write(response_rows[0]), run_time=0.45)
        emphasize_response_mapping(response_rows[0], trial_specs[0]['selected'])
        self.wait(0.45)
        for row_idx, spec in enumerate(trial_specs[1:], start=1):
            next_si_img = ImageMobject(_s1_stage2_fish_path(spec['ref'])).scale_to_fit_height(IMG_H).move_to(si_pos)
            next_sj_img, next_sj_bdr = self._make_probe(spec['left'], sj_pos)
            next_sk_img, next_sk_bdr = self._make_probe(spec['right'], sk_pos)
            next_si_lbl = self._index_tex(spec['ref'], _s1_stage2_INK).next_to(next_si_img, DOWN, buff=0.1)
            next_sj_lbl = self._index_tex(spec['left'], _s1_stage2_INK).next_to(next_sj_img, DOWN, buff=0.1)
            next_sk_lbl = self._index_tex(spec['right'], _s1_stage2_INK).next_to(next_sk_img, DOWN, buff=0.1)
            self.play(ReplacementTransform(si_img, next_si_img), ReplacementTransform(sj_img, next_sj_img), ReplacementTransform(sj_bdr, next_sj_bdr), ReplacementTransform(sk_img, next_sk_img), ReplacementTransform(sk_bdr, next_sk_bdr), ReplacementTransform(si_lbl, next_si_lbl), ReplacementTransform(sj_lbl, next_sj_lbl), ReplacementTransform(sk_lbl, next_sk_lbl), run_time=0.65)
            si_img, si_lbl = (next_si_img, next_si_lbl)
            sj_img, sj_bdr = (next_sj_img, next_sj_bdr)
            sk_img, sk_bdr = (next_sk_img, next_sk_bdr)
            sj_lbl, sk_lbl = (next_sj_lbl, next_sk_lbl)
            highlight_choice(spec['selected'])
            self.play(Write(response_rows[row_idx]), run_time=0.42)
            emphasize_response_mapping(response_rows[row_idx], spec['selected'])
            self.wait(0.3)
        self.play(Write(continuation_dots), run_time=0.45)
        self.wait(1.1)

class Study1Stage2SimilarityJudgementsExamples(Scene):
    """Introduce additional within-category triplets for object-scene classes."""

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage2_BG
        title_prev = Tex('Psychophysical Validation', color=_s1_stage2_INK, font_size=38).to_edge(UP, buff=0.28)
        subtitle_prev = Tex('Triplet similarity task \\quad $N = 1{,}113$ participants', color=_s1_stage2_INK, font_size=24).next_to(title_prev, DOWN, buff=0.1)
        question_prev = VGroup(Tex('Does the model-based preselection capture', color=_s1_stage2_INK, font_size=24), Tex('a human-perceived perceptual continuum?', color=_s1_stage2_INK, font_size=24)).arrange(DOWN, buff=0.08).next_to(subtitle_prev, DOWN, buff=0.16)
        math_prev = VGroup(Tex('Given a set of images $\\mathcal{S} = \\{s_1, s_2, \\ldots, s_n\\}$,', color=_s1_stage2_INK, font_size=26), Tex('participants view triplets $(s_i,\\, s_j,\\, s_k)$', color=_s1_stage2_INK, font_size=26), Tex('and select which probe is more similar', color=_s1_stage2_INK, font_size=26), Tex('to the reference image $s_i$.', color=_s1_stage2_INK, font_size=26)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        d = 2.22
        img_h = 1.18
        cy = -1.05
        h = d * np.sqrt(3) / 2
        si_pos = np.array([0.0, cy + 2 * h / 3, 0.0])
        sj_pos = np.array([-d / 2, cy - h / 3, 0.0])
        sk_pos = np.array([d / 2, cy - h / 3, 0.0])
        lbl_h = 0.38
        pad = 0.28
        box_top = si_pos[1] + img_h / 2 + pad
        box_bottom = sj_pos[1] - img_h / 2 - lbl_h - pad
        trial_center = np.array([0.0, (box_top + box_bottom) / 2, 0.0])
        trial_frame_side = max(d + img_h + 2 * pad, box_top - box_bottom) + 0.12
        trial_frame = Square(side_length=trial_frame_side, color=_s1_stage2_LGREY, stroke_width=1.5).set_fill('#F9FAFB', opacity=0.45).move_to(trial_center)
        math_prev.scale_to_fit_width(3.95)
        math_prev.next_to(trial_frame, LEFT, buff=0.55)
        math_prev.align_to(trial_frame, UP).shift(DOWN * 0.82)
        computer_icon = ImageMobject(str(_s1_stage2_STAGE2_ASSET_DIR / 'computer.png')).scale_to_fit_width(0.56).move_to(trial_center + UP * (trial_frame_side / 2 + 0.42))
        si_img = ImageMobject(_s1_stage2_fish_path(8)).scale_to_fit_height(img_h).move_to(si_pos)
        sj_img = ImageMobject(_s1_stage2_fish_path(5)).scale_to_fit_height(img_h).move_to(sj_pos)
        sk_img = ImageMobject(_s1_stage2_fish_path(2)).scale_to_fit_height(img_h).move_to(sk_pos)
        si_bdr = SurroundingRectangle(si_img, color=_s1_stage2_LGREY, stroke_width=1.5, buff=0.05)
        sj_bdr = SurroundingRectangle(sj_img, color=_s1_stage2_LGREY, stroke_width=1.5, buff=0.05)
        sk_bdr = SurroundingRectangle(sk_img, color=_s1_stage2_AMBER, stroke_width=4.2, buff=0.07)
        si_lbl = MathTex('s_{9}', color=_s1_stage2_INK, font_size=28).next_to(si_img, DOWN, buff=0.16)
        sj_lbl = MathTex('s_{6}', color=_s1_stage2_INK, font_size=28).next_to(sj_img, DOWN, buff=0.16).set_opacity(0.28)
        sk_lbl = MathTex('s_{3}', color=_s1_stage2_INK, font_size=28).next_to(sk_img, DOWN, buff=0.16)
        sj_img.set_opacity(0.28)
        sj_bdr.set_stroke(opacity=0.12)
        response_rows = VGroup(self._mini_response_row(1, 3, 8), self._mini_response_row(5, 4, 9), self._mini_response_row(7, 2, 10), self._mini_response_row(9, 3, 6)).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        response_lhs = MathTex('\\mathit{T} \\; =', color=_s1_stage2_INK, font_size=30).next_to(response_rows, LEFT, buff=0.16).align_to(response_rows[0], UP)
        response_title = Tex('Behavioural responses', color=_s1_stage2_INK, font_size=24)
        response_stack = VGroup(response_lhs, response_rows)
        response_title.next_to(response_stack, UP, buff=0.28).align_to(response_stack, LEFT)
        continuation_dots = MathTex('\\vdots', color=_s1_stage2_MGREY, font_size=30).next_to(response_rows[-1], DOWN, buff=0.16)
        continuation_dots.move_to([response_rows[-1].get_center()[0], continuation_dots.get_center()[1], 0.0])
        response_group = VGroup(response_title, response_lhs, response_rows, continuation_dots).move_to([4.35, -0.68, 0.0])
        previous_scene_group = Group(title_prev, subtitle_prev, question_prev, math_prev, trial_frame, computer_icon, si_img, si_bdr, si_lbl, sj_img, sj_bdr, sj_lbl, sk_img, sk_bdr, sk_lbl, response_group)
        title = Tex('Similarity judgements within object-scenes', color=_s1_stage2_INK, font_size=34).to_edge(UP, buff=0.3)
        categories = [('landscape_element_tropical_karst', 'Tropical karst', (1, 4, 8)), ('item_sofa', 'Sofa', (0, 3, 7)), ('vehicle_campervan', 'Campervan', (2, 5, 9)), ('plant_pine_med', 'Pine med', (1, 6, 8))]

        def mini_triplet(prefix: str, label: str, indices: tuple[int, int, int], center: np.ndarray) -> Group:
            """Build one compact triplet example card."""
            ref_i, left_i, right_i = indices
            frame = Square(side_length=2.45, color=_s1_stage2_LGREY, stroke_width=1.3).set_fill('#F9FAFB', opacity=0.55).move_to(center)
            top = center + UP * 0.55
            bottom_y = center[1] - 0.42
            left = np.array([center[0] - 0.48, bottom_y, 0.0])
            right = np.array([center[0] + 0.48, bottom_y, 0.0])
            img_ref = ImageMobject(_s1_stage2_stimulus_path(prefix, ref_i)).scale_to_fit_height(0.56).move_to(top)
            img_l = ImageMobject(_s1_stage2_stimulus_path(prefix, left_i)).scale_to_fit_height(0.56).move_to(left)
            img_r = ImageMobject(_s1_stage2_stimulus_path(prefix, right_i)).scale_to_fit_height(0.56).move_to(right)
            bdr_ref = SurroundingRectangle(img_ref, color=_s1_stage2_LGREY, stroke_width=1.2, buff=0.03)
            bdr_l = SurroundingRectangle(img_l, color=_s1_stage2_LGREY, stroke_width=1.2, buff=0.03)
            bdr_r = SurroundingRectangle(img_r, color=_s1_stage2_LGREY, stroke_width=1.2, buff=0.03)
            caption = Tex(label, color=_s1_stage2_INK, font_size=18).next_to(frame, DOWN, buff=0.18)
            return Group(frame, img_ref, bdr_ref, img_l, bdr_l, img_r, bdr_r, caption)
        centers = [np.array([-4.65, -0.05, 0.0]), np.array([-1.55, -0.05, 0.0]), np.array([1.55, -0.05, 0.0]), np.array([4.65, -0.05, 0.0])]
        mini_groups = Group(*[mini_triplet(prefix, label, idxs, center) for (prefix, label, idxs), center in zip(categories, centers)])
        self.add(previous_scene_group)
        self.wait(0.2)
        self.play(LaggedStart(*[mob.animate.shift(DOWN * 0.1).fade(1) for mob in previous_scene_group], lag_ratio=0.03), run_time=0.85, rate_func=smooth)
        self.play(Write(title), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(group, shift=UP * 0.12, scale=0.96) for group in mini_groups], lag_ratio=0.12), run_time=1.1)
        self.wait(1.2)

    def _mini_response_row(self, a: int, b: int, c: int) -> VGroup:
        """Build one compact behavioural-response row."""
        parts = [MathTex('(', color=_s1_stage2_INK, font_size=28), MathTex(str(a), color=_s1_stage2_INK, font_size=28), MathTex(',', color=_s1_stage2_INK, font_size=28), MathTex(str(b), color=_s1_stage2_INK, font_size=28), MathTex(',', color=_s1_stage2_INK, font_size=28), MathTex(str(c), color=_s1_stage2_INK, font_size=28), MathTex(')', color=_s1_stage2_INK, font_size=28)]
        return VGroup(*parts).arrange(RIGHT, buff=0.06, aligned_edge=DOWN)

class Study1Stage2OrdinalEmbedding(Scene):
    """
    Explains ordinal embedding intuitively as a sorting problem.

    Phase 1 — scrambled row of images (arbitrary order).
    Phase 2 — two example triplet constraints shown as arcs.
    Phase 3 — images animate to their perceptually correct positions.
    Phase 4 — embedding values appear; scale label replaces scramble label.
    """
    _SCRAMBLE = [7, 2, 5, 0, 8, 3, 9, 1, 6, 4]
    _IMG_H = 0.84
    _Y = 0.32
    _XS = np.linspace(-4.5, 4.5, 10)

    @staticmethod
    def _card(fish_idx: int, img_h: float, border_color=None) -> Group:
        """Return the card."""
        border_color = border_color or _s1_stage2_LGREY
        img = ImageMobject(_s1_stage2_fish_path(fish_idx)).scale_to_fit_height(img_h)
        bdr = SurroundingRectangle(img, color=border_color, stroke_width=1.3, buff=0.04)
        return Group(img, bdr)

    @staticmethod
    def _arc(x1: float, x2: float, y: float, img_h: float, color: str, angle_sign: float=1.0) -> ArcBetweenPoints:
        """Curved arc connecting two image centres, bowing upward."""
        edge_y = y + img_h / 2 + 0.05
        return ArcBetweenPoints(np.array([x1, edge_y, 0.0]), np.array([x2, edge_y, 0.0]), angle=angle_sign * PI / 3.5, color=color, stroke_width=2.2)

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage2_BG
        xs, y, IMG_H = (self._XS, self._Y, self._IMG_H)
        scramble = self._SCRAMBLE
        title = Tex('Ordinal Embedding', color=_s1_stage2_INK, font_size=38).to_edge(UP, buff=0.28)
        cards = [self._card(scramble[i], IMG_H).move_to([xs[i], y, 0.0]) for i in range(10)]
        target_xs = [xs[scramble[i]] for i in range(10)]
        axis_y = y - IMG_H / 2 - 0.18
        axis = Line([-5.1, axis_y, 0.0], [5.1, axis_y, 0.0], color=_s1_stage2_LGREY, stroke_width=1.3)
        tag_before = Tex('Arbitrary order', color=_s1_stage2_INK, font_size=19).move_to([0.0, y + IMG_H / 2 + 0.38, 0.0])
        PIPE_Y = -2.8
        pipe_task = Tex('Triplet task', color=_s1_stage2_INK, font_size=18)
        pipe_a1 = Tex('$\\longrightarrow$', color=_s1_stage2_MGREY, font_size=20)
        pipe_resp = VGroup(Tex('Behavioral responses', color=_s1_stage2_INK, font_size=18), Tex('$(N \\times T$ triplets$)$', color=_s1_stage2_INK, font_size=14)).arrange(DOWN, buff=0.05)
        pipe_a2 = Tex('$\\longrightarrow$', color=_s1_stage2_MGREY, font_size=20)
        pipe_algo = Tex('Ordinal Embedding', color=_s1_stage2_BLUE, font_size=18)
        pipe_a3 = Tex('$\\longrightarrow$', color=_s1_stage2_MGREY, font_size=20)
        pipe_scale = Tex('Perceptual scale', color=_s1_stage2_INK, font_size=18)
        pipeline = VGroup(pipe_task, pipe_a1, pipe_resp, pipe_a2, pipe_algo, pipe_a3, pipe_scale).arrange(RIGHT, buff=0.28).move_to([0.0, PIPE_Y, 0.0])
        x_si = xs[scramble.index(0)]
        x_sj = xs[scramble.index(2)]
        x_sk = xs[scramble.index(7)]
        GREEN_C = '#16A34A'
        RED_C = '#DC2626'
        arc_close = self._arc(x_si, x_sj, y, IMG_H, GREEN_C)
        arc_far = self._arc(x_si, x_sk, y, IMG_H, RED_C)
        lbl_close = Tex('$s_j$ close', color=GREEN_C, font_size=16).move_to(arc_close.get_center() + UP * 0.3)
        lbl_far = Tex('$s_k$ far', color=RED_C, font_size=16).move_to(arc_far.get_center() + UP * 0.28)
        val_y = axis_y - 0.26
        val_labels = VGroup(*[Tex(f'{_s1_stage2_EMBED_Y[k]:.2f}', color=_s1_stage2_MGREY, font_size=14).move_to([xs[k], val_y, 0.0]) for k in range(10)])
        tag_after = Tex('Perceptual scale', color=_s1_stage2_INK, font_size=19).move_to([0.0, y + IMG_H / 2 + 0.38, 0.0])
        self.play(Write(title), run_time=0.55)
        self.play(LaggedStart(*[FadeIn(c, scale=1.08) for c in cards], lag_ratio=0.05), run_time=0.85)
        self.play(Create(axis), FadeIn(tag_before), run_time=0.35)
        self.wait(0.2)
        self.play(FadeIn(pipe_task), run_time=0.35)
        self.wait(0.2)
        self.play(FadeIn(pipe_a1), FadeIn(pipe_resp), run_time=0.45)
        si_slot = scramble.index(0)
        hi_bdr = SurroundingRectangle(cards[si_slot][0], color=_s1_stage2_BLUE, stroke_width=2.5, buff=0.05)
        self.play(FadeIn(hi_bdr), run_time=0.25)
        self.play(Create(arc_close), FadeIn(lbl_close), Create(arc_far), FadeIn(lbl_far), run_time=0.7)
        self.wait(0.7)
        self.play(FadeOut(arc_close, lbl_close, arc_far, lbl_far, hi_bdr), FadeIn(pipe_a2), FadeIn(pipe_algo), run_time=0.5)
        self.wait(0.25)
        sort_anims = [cards[i].animate.move_to([target_xs[i], y, 0.0]) for i in range(10)]
        self.play(*sort_anims, FadeOut(tag_before), run_time=1.7, rate_func=smooth)
        self.play(FadeIn(pipe_a3), FadeIn(pipe_scale), FadeIn(val_labels, shift=UP * 0.05), FadeIn(tag_after), run_time=0.5)
        self.wait(1.3)

class Study1Stage2EmbeddingResult(Scene):
    """
    Behavioural responses on the left, ordinal embedding algorithm underneath,
    embedding plot on the right, and final ordered image strip below.
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage2_BG
        title = Tex('From behavioural responses to perceptual embedding', color=_s1_stage2_INK, font_size=34).to_edge(UP, buff=0.28)
        responses_title = Tex('Behavioural responses', color=_s1_stage2_INK, font_size=28)
        responses_main = MathTex('\\mathit{T}=\\{(i,j,k)\\}', color=_s1_stage2_INK, font_size=36)
        responses_examples = VGroup(MathTex('(1,3,8)', color=_s1_stage2_INK, font_size=25), MathTex('(5,4,9)', color=_s1_stage2_INK, font_size=25), MathTex('(7,2,10)', color=_s1_stage2_INK, font_size=25), MathTex('\\vdots', color=_s1_stage2_MGREY, font_size=25)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        responses_block = VGroup(responses_title, responses_main, responses_examples).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        responses_block.move_to([-5.0, 1.55, 0.0])
        algo_title = Tex('Ordinal embedding algorithm', color=_s1_stage2_BLUE, font_size=27)
        algo_sub = Tex('Estimate 1D stimulus positions', color=_s1_stage2_INK, font_size=20)
        algo_block = VGroup(algo_title, algo_sub).arrange(DOWN, buff=0.1)
        algo_block.move_to([-5.0, -0.35, 0.0])
        down_arrow = Arrow(start=responses_block.get_bottom() + DOWN * 0.02, end=algo_block.get_top() + UP * 0.02, buff=0.08, color=_s1_stage2_LGREY, stroke_width=1.8, tip_length=0.08, max_stroke_width_to_length_ratio=7).set_z_index(5)
        plot_center = np.array([3.0, 0.78, 0.0])
        axes = Axes(x_range=[1, 10.6, 1], y_range=[0, 1.05, 0.25], x_length=5.8, y_length=3.6, axis_config={'color': _s1_stage2_INK, 'stroke_width': 1.6, 'include_tip': False, 'tick_size': 0.06}).move_to(plot_center)
        plot_title = Tex('Estimated embedding', color=_s1_stage2_INK, font_size=25).next_to(axes, UP, buff=0.2)
        x_label = Tex('Image number', color=_s1_stage2_INK, font_size=22).next_to(axes.get_x_axis(), DOWN, buff=0.34)
        y_label = Tex('Embedding', color=_s1_stage2_INK, font_size=22).rotate(PI / 2).next_to(axes.get_y_axis(), LEFT, buff=0.65)
        x_nums = VGroup(*[Tex(str(i), color=_s1_stage2_INK, font_size=22).move_to(axes.c2p(i, 0) + DOWN * 0.24) for i in range(1, 11)])
        y_tick_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        y_nums = VGroup(*[Tex(f'{v:.2f}', color=_s1_stage2_INK, font_size=20).move_to(axes.c2p(1, v) + LEFT * 0.46) for v in y_tick_values])
        pts = [axes.c2p(i + 1, v) for i, v in enumerate(_s1_stage2_EMBED_Y)]
        curve = VMobject(stroke_color=_s1_stage2_BLUE, stroke_width=3.0)
        curve.set_points_smoothly(pts)
        dots = VGroup(*[Dot(p, radius=0.05, color=_s1_stage2_BLUE, fill_opacity=1.0) for p in pts])
        arrow_y = algo_title.get_center()[1]
        side_arrow = Arrow(start=np.array([algo_block.get_right()[0] + 0.4, arrow_y, 0.0]), end=np.array([algo_block.get_right()[0] + 1.2, arrow_y, 0.0]), buff=0.0, color=_s1_stage2_LGREY, stroke_width=1.6, tip_length=0.07, max_stroke_width_to_length_ratio=7).set_z_index(5)
        strip_xs = [axes.c2p(i + 1, 0)[0] for i in range(10)]
        strip_y = -2.08
        img_h = 0.5
        fish_imgs = Group(*[ImageMobject(_s1_stage2_fish_path(i)).scale_to_fit_height(img_h).move_to([strip_xs[i], strip_y, 0.0]) for i in range(10)])
        fish_borders = VGroup(*[SurroundingRectangle(fish_imgs[i], color=_s1_stage2_LGREY, stroke_width=0.8, buff=0.02) for i in range(10)])
        dot_to_img_connectors = VGroup(*[DashedLine(start=dots[i].get_center() + DOWN * 0.03, end=fish_imgs[i].get_top() + UP * 0.03, color=_s1_stage2_BLUE, stroke_width=1.0, dash_length=0.05).set_opacity(0.55) for i in range(10)])
        strip_title = Tex('Final ordered image set', color=_s1_stage2_INK, font_size=19).move_to([axes.get_center()[0], strip_y - 0.48, 0.0])
        self.play(Write(title), run_time=0.75)
        self.wait(0.2)
        self.play(FadeIn(responses_block, shift=UP * 0.08), run_time=0.85)
        self.wait(0.2)
        self.play(FadeIn(algo_block, shift=UP * 0.05), Create(down_arrow), run_time=0.8)
        self.wait(0.15)
        self.play(Create(side_arrow), run_time=0.3)
        self.play(FadeIn(plot_title, shift=UP * 0.05), Create(axes), FadeIn(x_label, y_label), FadeIn(x_nums, y_nums), run_time=1.1)
        self.wait(0.15)
        self.play(LaggedStart(*[FadeIn(dot, scale=1.15) for dot in dots], lag_ratio=0.05), run_time=0.4)
        self.play(Create(curve), run_time=1.0)
        self.wait(0.2)
        self.play(FadeIn(strip_title, shift=UP * 0.04), run_time=0.2)
        for i in range(10):
            self.play(Create(dot_to_img_connectors[i]), FadeIn(fish_imgs[i], scale=1.05), Create(fish_borders[i]), Indicate(dots[i], color=_s1_stage2_BLUE, scale_factor=1.25), run_time=0.16)
        self.wait(1.2)

class Study1Stage2ModelOrderToHeatmap(Scene):
    """Compare behaviourally reordered sets with the LPIPS-versus-embedding heatmap."""
    STIMULI_DIR = _s1_stage2_STIM_DIR
    HEATMAP_PDF = _s1_stage2_STAGE2_ASSET_DIR / 'lpips_vs_embedding_orders_heatmap.pdf'

    def _natural_key(self, path: Path):
        """Return a natural-sort key for a stimulus filename."""
        import re
        parts = re.split('(\\d+)', path.stem.lower())
        return [int(part) if part.isdigit() else part for part in parts]

    def _normalise(self, path: Path) -> str:
        """Normalize a stimulus filename for keyword matching."""
        return path.stem.lower().replace('_', ' ').replace('-', ' ')

    def _all_stimulus_paths(self) -> list[Path]:
        """Return all valid stimulus image paths in the task directory."""
        valid_suffixes = {'.png', '.jpg', '.jpeg', '.webp'}
        paths = [p for p in self.STIMULI_DIR.iterdir() if p.suffix.lower() in valid_suffixes]
        return sorted(paths, key=self._natural_key)

    def _select_category_paths(self, required_keywords: tuple[str, ...], n: int=10) -> list[Path]:
        """Select stimulus paths that best match the requested category keywords."""
        all_paths = self._all_stimulus_paths()
        exact = [p for p in all_paths if all((keyword in self._normalise(p) for keyword in required_keywords))]
        if len(exact) >= n:
            return exact[:n]
        relaxed = []
        used = {str(p) for p in exact}
        for p in all_paths:
            if str(p) in used:
                continue
            if required_keywords[0] in self._normalise(p):
                relaxed.append(p)
        merged = exact + relaxed
        if len(merged) >= n:
            return merged[:n]
        raise ValueError(f'Could not find {n} images for keywords {required_keywords}. Found {len(merged)}.')

    def _pdf_first_page_to_png(self, pdf_path: Path) -> str:
        """Convert the first page of the heatmap PDF into a PNG snapshot."""
        import hashlib
        import shutil
        import subprocess
        import tempfile
        out_name = f'{pdf_path.stem}_{hashlib.md5(str(pdf_path).encode()).hexdigest()[:10]}.png'
        out_path = str(Path(tempfile.gettempdir()) / out_name)
        if Path(out_path).exists():
            return out_path
        if shutil.which('sips') is not None:
            subprocess.run(['sips', '-s', 'format', 'png', str(pdf_path), '--out', out_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if Path(out_path).exists():
                return out_path
        if shutil.which('pdftoppm') is not None:
            prefix = str(Path(tempfile.gettempdir()) / f'{Path(out_name).stem}')
            subprocess.run(['pdftoppm', '-png', '-f', '1', '-singlefile', str(pdf_path), prefix], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            alt_path = prefix + '.png'
            if Path(alt_path).exists():
                return alt_path
        if shutil.which('magick') is not None:
            subprocess.run(['magick', '-density', '220', f'{pdf_path}[0]', out_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if Path(out_path).exists():
                return out_path
        raise FileNotFoundError('Could not convert heatmap PDF to PNG. Install sips, pdftoppm, or ImageMagick.')

    def _embedding_result_snapshot(self) -> Group:
        """Build the held end state of the previous embedding-result scene."""
        title = Tex('From behavioural responses to perceptual embedding', color=_s1_stage2_INK, font_size=34).to_edge(UP, buff=0.28)
        responses_title = Tex('Behavioural responses', color=_s1_stage2_INK, font_size=28)
        responses_main = MathTex('\\mathit{T}=\\{(i,j,k)\\}', color=_s1_stage2_INK, font_size=36)
        responses_examples = VGroup(MathTex('(1,3,8)', color=_s1_stage2_INK, font_size=25), MathTex('(5,4,9)', color=_s1_stage2_INK, font_size=25), MathTex('(7,2,10)', color=_s1_stage2_INK, font_size=25), MathTex('\\vdots', color=_s1_stage2_MGREY, font_size=25)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        responses_block = VGroup(responses_title, responses_main, responses_examples).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        responses_block.move_to([-5.0, 1.55, 0.0])
        algo_title = Tex('Ordinal embedding algorithm', color=_s1_stage2_BLUE, font_size=27)
        algo_sub = Tex('Estimate 1D stimulus positions', color=_s1_stage2_INK, font_size=20)
        algo_block = VGroup(algo_title, algo_sub).arrange(DOWN, buff=0.1)
        algo_block.move_to([-5.0, -0.35, 0.0])
        down_arrow = Arrow(start=responses_block.get_bottom() + DOWN * 0.02, end=algo_block.get_top() + UP * 0.02, buff=0.08, color=_s1_stage2_LGREY, stroke_width=1.8, tip_length=0.08, max_stroke_width_to_length_ratio=7).set_z_index(5)
        plot_center = np.array([3.0, 0.78, 0.0])
        axes = Axes(x_range=[1, 10.6, 1], y_range=[0, 1.05, 0.25], x_length=5.8, y_length=3.6, axis_config={'color': _s1_stage2_INK, 'stroke_width': 1.6, 'include_tip': False, 'tick_size': 0.06}).move_to(plot_center)
        plot_title = Tex('Estimated embedding', color=_s1_stage2_INK, font_size=25).next_to(axes, UP, buff=0.2)
        x_label = Tex('Image number', color=_s1_stage2_INK, font_size=22).next_to(axes.get_x_axis(), DOWN, buff=0.34)
        y_label = Tex('Embedding', color=_s1_stage2_INK, font_size=22).rotate(PI / 2).next_to(axes.get_y_axis(), LEFT, buff=0.65)
        x_nums = VGroup(*[Tex(str(i), color=_s1_stage2_INK, font_size=22).move_to(axes.c2p(i, 0) + DOWN * 0.24) for i in range(1, 11)])
        y_tick_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        y_nums = VGroup(*[Tex(f'{v:.2f}', color=_s1_stage2_INK, font_size=20).move_to(axes.c2p(1, v) + LEFT * 0.46) for v in y_tick_values])
        pts = [axes.c2p(i + 1, v) for i, v in enumerate(_s1_stage2_EMBED_Y)]
        curve = VMobject(stroke_color=_s1_stage2_BLUE, stroke_width=3.0)
        curve.set_points_smoothly(pts)
        dots = VGroup(*[Dot(p, radius=0.05, color=_s1_stage2_BLUE, fill_opacity=1.0) for p in pts])
        arrow_y = algo_title.get_center()[1]
        side_arrow = Arrow(start=np.array([algo_block.get_right()[0] + 0.4, arrow_y, 0.0]), end=np.array([algo_block.get_right()[0] + 1.2, arrow_y, 0.0]), buff=0.0, color=_s1_stage2_LGREY, stroke_width=1.6, tip_length=0.07, max_stroke_width_to_length_ratio=7).set_z_index(5)
        strip_xs = [axes.c2p(i + 1, 0)[0] for i in range(10)]
        strip_y = -2.08
        img_h = 0.5
        fish_imgs = Group(*[ImageMobject(_s1_stage2_fish_path(i)).scale_to_fit_height(img_h).move_to([strip_xs[i], strip_y, 0.0]) for i in range(10)])
        fish_borders = VGroup(*[SurroundingRectangle(fish_imgs[i], color=_s1_stage2_LGREY, stroke_width=0.8, buff=0.02) for i in range(10)])
        dot_to_img_connectors = VGroup(*[DashedLine(start=dots[i].get_center() + DOWN * 0.03, end=fish_imgs[i].get_top() + UP * 0.03, color=_s1_stage2_BLUE, stroke_width=1.0, dash_length=0.05).set_opacity(0.55) for i in range(10)])
        strip_title = Tex('Final ordered image set', color=_s1_stage2_INK, font_size=19).move_to([axes.get_center()[0], strip_y - 0.48, 0.0])
        return Group(title, responses_block, algo_block, down_arrow, side_arrow, plot_title, axes, x_label, y_label, x_nums, y_nums, curve, dots, strip_title, dot_to_img_connectors, fish_imgs, fish_borders)

    def _category_row(self, image_paths: list[Path], image_height: float=0.44) -> Group:
        """Build one horizontal category row with matching borders."""
        images = Group(*[ImageMobject(str(path)).scale_to_fit_height(image_height) for path in image_paths])
        images.arrange(RIGHT, buff=0.055)
        borders = Group(*[SurroundingRectangle(images[i], color=_s1_stage2_LGREY, stroke_width=0.75, buff=0.016) for i in range(len(images))])
        return Group(images, borders)

    def construct(self):
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage2_BG
        heatmap_png = self._pdf_first_page_to_png(self.HEATMAP_PDF)
        previous_scene = self._embedding_result_snapshot()
        self.add(previous_scene)
        self.wait(0.25)
        self.play(FadeOut(previous_scene), run_time=0.6)
        category_specs = [('pine_med', ('pine', 'med')), ('bottle', ('bottle',)), ('moorland_tor', ('moorland', 'tor')), ('train', ('train',)), ('modern_building', ('modern', 'building')), ('observatory', ('observatory',))]
        title = Tex('Behaviourally reordered sets', color=_s1_stage2_INK, font_size=30).to_edge(UP, buff=0.35)
        category_rows = Group(*[self._category_row(self._select_category_paths(keywords, n=10), image_height=0.65) for _, keywords in category_specs])
        category_rows.arrange(DOWN, buff=0.2)
        category_rows.move_to([0.0, -0.28, 0.0])
        left_target_rows = category_rows.copy()
        left_target_rows.scale(0.82)
        left_target_rows.arrange(DOWN, buff=0.16)
        left_target_rows.to_edge(LEFT, buff=0.28)
        left_target_rows.shift(DOWN * 0.18)
        heatmap = ImageMobject(heatmap_png).scale_to_fit_height(5.45)
        heatmap.to_edge(RIGHT, buff=0.35).shift(DOWN * 0.06)
        heatmap_title = Tex('LPIPS vs embedding orders', color=_s1_stage2_INK, font_size=24).next_to(heatmap, UP, buff=0.14)
        heatmap_group = Group(heatmap_title, heatmap)
        agreement_text = VGroup(Tex('Strong agreement', color=_s1_stage2_INK, font_size=24), Tex('($\\mathrm{Spearman\\ rank\\ correlation}$ of $\\rho = 0.73$)', color=_s1_stage2_INK, font_size=20), Tex('between LPIPS-based order and human similarity judgements', color=_s1_stage2_INK, font_size=20)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        agreement_text.next_to(heatmap, DOWN, buff=0.28)
        agreement_text.align_to(heatmap, LEFT)
        self.play(FadeIn(title, shift=UP * 0.05), LaggedStart(*[FadeIn(row, shift=UP * 0.05, scale=1.03) for row in category_rows], lag_ratio=0.08), run_time=1.2)
        self.wait(0.35)
        self.play(Transform(category_rows, left_target_rows), FadeIn(heatmap_group, shift=RIGHT * 0.18), run_time=1.2)
        self.play(FadeIn(agreement_text, shift=UP * 0.08), run_time=0.6)
        self.wait(1.2)
        self.wait(1.2)


# --- inlined from study1_stage3_memory.py ---

_s1_stage3_BG = WHITE
_s1_stage3_INK = '#1C1C1E'
_s1_stage3_LGREY = '#D1D5DB'
_s1_stage3_MGREY = '#9CA3AF'
_s1_stage3_STIM_DIR = env_path('STIMULI_REORDERED_DIR', REPO_ROOT / 'assets' / 'images' / 'stimuli_reordered')
_s1_stage3_MEMORY_TASK_STIM_DIR = env_path('MEMORY_TASK_STIM_DIR', REPO_ROOT / 'assets' / 'images' / 'study1' / 'memory_task')
_s1_stage3_STIM_INFO_CSV = env_path('STIM_INFO_CSV', REPO_ROOT / 'assets' / 'data' / 'study1' / 'stimuli_info.csv')
_s1_stage3_FIXATION_PATH = str(REPO_ROOT / 'assets' / 'images' / 'fixation_target.png')

def _s1_stage3_stimulus_path(prefix: str, idx: int) -> str:
    """Return the reordered-study stimulus path for one continuum image."""
    return str(_s1_stage3_STIM_DIR / f'{prefix}-{idx:02d}.png')

def _s1_stage3_memory_task_stimulus_path(name: str) -> str:
    """Return the path for a memory-task exemplar image."""
    return str(_s1_stage3_MEMORY_TASK_STIM_DIR / name)

def _s1_stage3_load_stimulus_lookup() -> dict[tuple[str, str], dict[str, str]]:
    """Load the Stage 3 stimulus metadata keyed by category and object."""
    with _s1_stage3_STIM_INFO_CSV.open() as f:
        rows = list(csv.DictReader(f))
    return {(row['category'], row['object']): row for row in rows}

def _s1_stage3_stimulus_image(prefix: str, idx: int, height: float, pos: tuple[float, float, float] | np.ndarray) -> ImageMobject:
    """Instantiate and position one Stage 3 stimulus card."""
    img = ImageMobject(_s1_stage3_stimulus_path(prefix, idx))
    img.scale_to_fit_height(height)
    img.move_to(pos)
    return img

def _s1_stage3_fixation_on(mob: Mobject | np.ndarray, height: float=0.18) -> ImageMobject:
    """Return a fixation target centered on a mobject or raw point."""
    fixation = ImageMobject(_s1_stage3_FIXATION_PATH)
    fixation.scale_to_fit_height(height)
    fixation.set_z_index(10)
    if isinstance(mob, np.ndarray):
        fixation.move_to(mob)
    else:
        fixation.move_to(mob.get_center())
    return fixation

def _s1_stage3__get_hex(color: ParsableManimColor | None) -> str | None:
    """Return an uppercase hex string for a Manim color, if present."""
    return color.to_hex().upper() if color else None

def _s1_stage3_recolor_svg(svg: SVGMobject, color_map: dict[str, ParsableManimColor]) -> None:
    """Recolor SVG strokes and fills using a hex-to-Manim mapping."""
    for submob in svg.family_members_with_points():
        stroke_hex = _s1_stage3__get_hex(submob.get_stroke_color())
        if stroke_hex in color_map:
            submob.set_stroke(color=color_map[stroke_hex], width=submob.get_stroke_width(), opacity=submob.get_stroke_opacity())
        fill_hex = _s1_stage3__get_hex(submob.get_fill_color())
        if fill_hex in color_map:
            submob.set_fill(color=color_map[fill_hex], opacity=submob.get_fill_opacity())

def _s1_stage3_restore_agg_nonrepeated_dashes(svg: SVGMobject) -> None:
    """Manim drops SVG dash arrays here, so restore them after loading."""
    candidates = [submob for submob in svg.submobjects if submob.get_fill_opacity() == 0 and abs(submob.get_stroke_width() - 1.71) < 0.1 and (abs(submob.get_stroke_opacity() - 0.6) < 0.1)]
    line_groups = {'series': [submob for submob in candidates if submob.get_center()[0] < 0], 'legend': [submob for submob in candidates if submob.get_center()[0] > 0]}
    for group in line_groups.values():
        if not group:
            continue
        target = min(group, key=lambda submob: submob.get_center()[1])
        num_dashes = max(4, int(round(target.width / 0.1)))
        dashed = DashedVMobject(target.copy(), num_dashes=num_dashes, dashed_ratio=0.5)
        dashed.set_stroke(color=target.get_stroke_color(), width=target.get_stroke_width(), opacity=target.get_stroke_opacity())
        dashed.set_fill(opacity=0)
        target.set_stroke(opacity=0)
        svg.add(dashed)

def _s1_stage3_svg_local_point(svg: SVGMobject, x: float, y: float, *, base_height: float=3.0) -> np.ndarray:
    """Convert SVG-local coordinates into scene coordinates."""
    scale = svg.height / base_height
    return svg.get_center() + np.array([x * scale, y * scale, 0.0])

def _s1_stage3_crisp_tex_label(text: str, center: np.ndarray, *, font_size: float, rotation: float=0.0, buff: float=0.04) -> VGroup:
    """Build a TeX label with a white backing rectangle for SVG overlays."""
    label = Tex(text, color=_s1_stage3_INK, font_size=font_size)
    if rotation:
        label.rotate(rotation)
    label.move_to(center)
    bg = BackgroundRectangle(label, color=WHITE, fill_opacity=1.0, buff=buff)
    bg.set_stroke(opacity=0)
    bg.set_z_index(9)
    label.set_z_index(10)
    return VGroup(bg, label)

def _s1_stage3_build_agg_tex_overlays(svg: SVGMobject) -> VGroup:
    """Build the aggregate-results SVG text overlays."""
    scale = svg.height / 3.0
    tick_fs = 16 * scale
    label_fs = 18 * scale
    overlays = VGroup()
    for y, text in [(1.287, '1.0'), (0.899, '0.9'), (0.512, '0.8'), (0.127, '0.7'), (-0.261, '0.6'), (-0.647, '0.5')]:
        overlays.add(_s1_stage3_crisp_tex_label(text, _s1_stage3_svg_local_point(svg, -1.95, y), font_size=tick_fs, buff=0.015))
    for x, text in [(-1.313, 'Hard'), (-0.583, 'Medium'), (0.148, 'Easy')]:
        overlays.add(_s1_stage3_crisp_tex_label(text, _s1_stage3_svg_local_point(svg, x, -1.11), font_size=tick_fs, buff=0.015))
    overlays.add(_s1_stage3_crisp_tex_label('Mean accuracy', _s1_stage3_svg_local_point(svg, -2.18, 0.24), font_size=label_fs, rotation=PI / 2, buff=0.03))
    overlays.add(_s1_stage3_crisp_tex_label('Difficulty level', _s1_stage3_svg_local_point(svg, -0.56, -1.31), font_size=label_fs, buff=0.03))
    overlays.add(_s1_stage3_crisp_tex_label('Chance level', _s1_stage3_svg_local_point(svg, 0.47, -0.49), font_size=label_fs, buff=0.03))
    overlays.add(_s1_stage3_crisp_tex_label('Target condition', _s1_stage3_svg_local_point(svg, 1.53, 0.5), font_size=label_fs, buff=0.03))
    overlays.add(_s1_stage3_crisp_tex_label('Repeated', _s1_stage3_svg_local_point(svg, 1.58, 0.19), font_size=label_fs, buff=0.025))
    overlays.add(_s1_stage3_crisp_tex_label('Non-repeated', _s1_stage3_svg_local_point(svg, 1.7, -0.02), font_size=label_fs, buff=0.025))
    return overlays

def _s1_stage3_build_block_tex_overlays(svg: SVGMobject) -> VGroup:
    """Build the blockwise-results SVG text overlays."""
    scale = svg.height / 3.0
    tick_fs = 15 * scale
    label_fs = 18 * scale
    overlays = VGroup()
    for y, text in [(1.053, '1.0'), (0.685, '0.9'), (0.319, '0.8'), (-0.047, '0.7'), (-0.413, '0.6'), (-0.779, '0.5')]:
        overlays.add(_s1_stage3_crisp_tex_label(text, _s1_stage3_svg_local_point(svg, -2.54, y), font_size=tick_fs, buff=0.015))
    for x, text in [(-1.97, 'Hard'), (-1.28, 'Medium'), (-0.59, 'Easy'), (0.32, 'Hard'), (1.01, 'Medium'), (1.7, 'Easy')]:
        overlays.add(_s1_stage3_crisp_tex_label(text, _s1_stage3_svg_local_point(svg, x, -1.19), font_size=tick_fs, buff=0.015))
    overlays.add(_s1_stage3_crisp_tex_label('Repeated', _s1_stage3_svg_local_point(svg, -1.28, 1.28), font_size=label_fs, buff=0.03))
    overlays.add(_s1_stage3_crisp_tex_label('Non-repeated', _s1_stage3_svg_local_point(svg, 1.03, 1.28), font_size=label_fs, buff=0.03))
    overlays.add(_s1_stage3_crisp_tex_label('Mean accuracy', _s1_stage3_svg_local_point(svg, -2.72, 0.06), font_size=label_fs, rotation=PI / 2, buff=0.03))
    overlays.add(_s1_stage3_crisp_tex_label('Difficulty level', _s1_stage3_svg_local_point(svg, -0.11, -1.34), font_size=label_fs, buff=0.03))
    overlays.add(_s1_stage3_crisp_tex_label('Block', _s1_stage3_svg_local_point(svg, 2.56, 0.63), font_size=label_fs, buff=0.03))
    for y, text in [(0.395, '1'), (0.215, '2'), (0.033, '3'), (-0.145, '4'), (-0.327, '5'), (-0.507, '6')]:
        overlays.add(_s1_stage3_crisp_tex_label(text, _s1_stage3_svg_local_point(svg, 2.67, y), font_size=tick_fs, buff=0.015))
    return overlays

def _s1_stage3_load_visible_svg(path: str | Path, *, height: float) -> SVGMobject:
    """Load an SVG and drop any full-canvas white background rect."""
    svg = SVGMobject(str(path), use_svg_cache=False)
    for submob in list(svg.submobjects):
        if _s1_stage3__get_hex(submob.get_stroke_color()) == '#FFFFFF' and _s1_stage3__get_hex(submob.get_fill_color()) == '#FFFFFF' and (submob.width > 0.9 * svg.width) and (submob.height > 0.9 * svg.height):
            svg.remove(submob)
            break
    svg.center()
    svg.scale_to_fit_height(height)
    _s1_stage3_recolor_svg(svg, {'#4D4D4D': _s1_stage3_INK, '#333333': _s1_stage3_INK, '#1A1A1A': _s1_stage3_INK, '#A9A9A9': _s1_stage3_INK})
    return svg

class Study1Stage3MemoryIntro(Scene):
    """Transition from similarity judgements into the memory-validation task."""

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage3_BG
        title = Tex('Memory validation task', color=_s1_stage3_INK, font_size=40).move_to(ORIGIN)
        title_top_target = title.copy().to_edge(UP, buff=0.28)
        question = VGroup(Tex('Does proximity along the perceptual continua', color=_s1_stage3_INK, font_size=26), Tex('of our image sets predict memory performance?', color=_s1_stage3_INK, font_size=26)).arrange(DOWN, buff=0.1).next_to(title_top_target, DOWN, buff=0.24)

        def set_image(prefix: str, idx: int, height: float, pos: tuple[float, float, float]) -> ImageMobject:
            """Load and position one Stage 3 exemplar image."""
            img = ImageMobject(_s1_stage3_stimulus_path(prefix, idx))
            img.scale_to_fit_height(height)
            img.move_to(pos)
            return img
        with _s1_stage3_STIM_INFO_CSV.open() as f:
            rows = list(csv.DictReader(f))
        lookup: dict[tuple[str, str], dict[str, str]] = {}
        for row in rows:
            lookup[row['category'], row['object']] = row
        set_specs = [('plant', 'pine_med'), ('landscape_element', 'lake_island'), ('building', 'observatory'), ('item', 'sofa')]
        question_bottom_y = question.get_bottom()[1]
        row_spacing = 1.05
        bottom_margin_y = -config.frame_height / 2 + 0.55
        row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
        row_y_positions = [row_block_center_y + row_spacing * offset for offset in (1.5, 0.5, -0.5, -1.5)]
        left_column_center_x = -config.frame_width / 4
        example_center = np.array([0.0, row_block_center_y, 0.0])
        example_side_offset = 1.55
        example_image_height = 1.95 * 1.3
        target_color = '#5B7493'
        foil_color = '#B67A5D'
        axis_color = '#C7CDD4'
        criterion_color = '#6B7280'
        initial_row_center_x = left_column_center_x
        selected_spacing = 1.05
        selected_xs = [left_column_center_x + selected_spacing * offset for offset in (-1.5, -0.5, 0.5, 1.5)]
        example_target = ImageMobject(_s1_stage3_memory_task_stimulus_path('LAN-MOU-T00.png'))
        example_target.scale_to_fit_height(example_image_height)
        example_target.move_to(example_center + LEFT * example_side_offset)
        example_target.set_z_index(5)
        example_foil = ImageMobject(_s1_stage3_memory_task_stimulus_path('LAN-MOU-D01.png'))
        example_foil.scale_to_fit_height(example_image_height)
        example_foil.move_to(example_center + RIGHT * example_side_offset)
        example_foil.set_z_index(4)
        example_left_row_center = np.array([left_column_center_x, row_block_center_y, 0.0])
        example_target_left_pos = example_left_row_center + LEFT * example_side_offset
        example_foil_left_pos = example_left_row_center + RIGHT * example_side_offset
        example_target_label = Tex('Target', color=target_color, font_size=26)
        example_target_label.move_to(example_target_left_pos + UP * (example_image_height / 2 + 0.28))
        example_target_label.set_z_index(6)
        example_foil_label = Tex('Foil', color=foil_color, font_size=26)
        example_foil_label.move_to(example_foil_left_pos + UP * (example_image_height / 2 + 0.28))
        example_foil_label.set_z_index(6)
        sdt_axes = Axes(x_range=[0.0, 1.85, 0.37], y_range=[0.0, 1.25, 0.5], x_length=5.1, y_length=2.25, axis_config={'color': axis_color, 'stroke_width': 1.5, 'include_ticks': False, 'include_tip': True, 'tip_width': 0.09, 'tip_height': 0.09})
        sdt_axes.move_to(np.array([3.48, row_block_center_y - 0.05, 0.0]))
        foil_mean = 0.56
        target_mean = 0.94
        signal_sigma = 0.16
        signal_peak = 0.92
        foil_curve = sdt_axes.plot(lambda x: signal_peak * np.exp(-0.5 * ((x - foil_mean) / signal_sigma) ** 2), x_range=[0.0, 1.63], color=foil_color, stroke_width=4)
        target_curve = sdt_axes.plot(lambda x: signal_peak * np.exp(-0.5 * ((x - target_mean) / signal_sigma) ** 2), x_range=[0.0, 1.63], color=target_color, stroke_width=4)
        foil_area = sdt_axes.get_area(foil_curve, x_range=[0.0, 1.63], color=foil_color, opacity=0.2)
        foil_area.set_stroke(width=0)
        target_area = sdt_axes.get_area(target_curve, x_range=[0.0, 1.63], color=target_color, opacity=0.2)
        target_area.set_stroke(width=0)
        criterion_x = 0.75
        criterion_line = DashedLine(sdt_axes.c2p(criterion_x, 0.0), sdt_axes.c2p(criterion_x, 1.12), dash_length=0.1, dashed_ratio=0.55, color=criterion_color, stroke_width=2.0)
        criterion_label = Tex('Criterion', color=_s1_stage3_INK, font_size=22)
        criterion_label.next_to(criterion_line, UP, buff=0.12)
        foil_curve_label = Tex('Foil signal', color=foil_color, font_size=18)
        foil_curve_label.move_to(sdt_axes.c2p(0.33, 0.88))
        target_curve_label = Tex('Target signal', color=target_color, font_size=18)
        target_curve_label.move_to(sdt_axes.c2p(1.25, 0.88))
        memory_strength_label = Tex('Memory strength', color=_s1_stage3_INK, font_size=22)
        memory_strength_label.next_to(sdt_axes.x_axis, DOWN, buff=0.2)
        probability_density_label = Tex('Probability density', color=_s1_stage3_INK, font_size=18)
        probability_density_label.rotate(PI / 2)
        probability_density_label.next_to(sdt_axes.y_axis, LEFT, buff=0.18)
        target_pair_highlight = SurroundingRectangle(Group(example_target_label, target_curve_label), buff=0.1, corner_radius=0.08, color=target_color, stroke_width=2.0)
        target_pair_highlight.set_fill(target_color, opacity=0.06)
        foil_pair_highlight = SurroundingRectangle(Group(example_foil_label, foil_curve_label), buff=0.1, corner_radius=0.08, color=foil_color, stroke_width=2.0)
        foil_pair_highlight.set_fill(foil_color, opacity=0.06)
        criterion_sweep_offset = 0.09
        criterion_right_shift = sdt_axes.c2p(criterion_x + criterion_sweep_offset, 0.0) - sdt_axes.c2p(criterion_x, 0.0)
        criterion_left_shift = sdt_axes.c2p(criterion_x - criterion_sweep_offset, 0.0) - sdt_axes.c2p(criterion_x, 0.0)
        sdt_group = VGroup(sdt_axes, foil_area, target_area, foil_curve, target_curve, criterion_line, criterion_label, foil_curve_label, target_curve_label, memory_strength_label, probability_density_label)
        panels = []
        for (category, obj), row_y in zip(set_specs, row_y_positions):
            row = lookup[category, obj]
            prefix = f'{category}_{obj}'
            cards = []
            for idx in range(10):
                cards.append(set_image(prefix, idx, 0.56, (0.0, 0.0, 0.0)))
            row_group = Group(*cards).arrange(RIGHT, buff=0.09).move_to([initial_row_center_x, row_y, 0.0])
            selected_indices = [int(row['target_position']), int(row['distractor_1_position']), int(row['distractor_2_position']), int(row['distractor_3_position'])]
            selected_targets = [np.array([selected_xs[0], row_y, 0.0]), np.array([selected_xs[1], row_y, 0.0]), np.array([selected_xs[2], row_y, 0.0]), np.array([selected_xs[3], row_y, 0.0])]
            panels.append({'row_group': row_group, 'cards': cards, 'selected_indices': selected_indices, 'selected_targets': selected_targets, 'center': np.array([initial_row_center_x, row_y, 0.0])})
        bottom_panel = panels[-1]
        bottom_row_dots = VGroup(*[MathTex('\\vdots', color=_s1_stage3_MGREY, font_size=24).next_to(card, DOWN, buff=0.1) for card in bottom_panel['cards']])
        bottom_dot_offsets = [dot.get_center() - card.get_center() for card, dot in zip(bottom_panel['cards'], bottom_row_dots)]
        self.play(Write(title), run_time=0.7)
        self.wait(0.15)
        self.play(title.animate.move_to(title_top_target), run_time=0.55)
        self.play(FadeIn(question, shift=UP * 0.12), run_time=0.6)
        self.wait(0.6)
        self.play(FadeIn(example_target, scale=0.96), FadeIn(example_foil, scale=0.96), run_time=0.7)
        self.wait(2.0)
        self.play(example_target.animate.move_to(example_center), example_foil.animate.move_to(example_center), run_time=0.7)
        self.wait(2.0)
        target_visible = True

        def swap_example(delay: float) -> None:
            """Toggle the overlaid target example during the intro alternation beat."""
            nonlocal target_visible
            target_visible = not target_visible
            self.play(example_target.animate.set_opacity(1.0 if target_visible else 0.0), run_time=0.1, rate_func=linear)
            self.wait(delay)
        for _ in range(8):
            swap_example(0.2)
        self.wait(2.0)
        self.play(example_target.animate.move_to(example_target_left_pos).set_opacity(1.0), example_foil.animate.move_to(example_foil_left_pos).set_opacity(1.0), run_time=0.65, rate_func=smooth)
        self.play(FadeIn(example_target_label, shift=UP * 0.1), FadeIn(example_foil_label, shift=UP * 0.1), LaggedStart(Create(sdt_axes), FadeIn(foil_area), FadeIn(target_area), Create(foil_curve), Create(target_curve), FadeIn(foil_curve_label, shift=UP * 0.08), FadeIn(target_curve_label, shift=UP * 0.08), FadeIn(memory_strength_label, shift=UP * 0.08), FadeIn(probability_density_label, shift=RIGHT * 0.08), lag_ratio=0.12), run_time=1.3)
        self.play(Create(criterion_line), FadeIn(criterion_label, shift=UP * 0.08), run_time=0.55)
        self.play(example_target_label.animate.scale(1.18), target_curve.animate.set_stroke(width=4.8, opacity=1.0), target_area.animate.set_fill(opacity=0.34), example_foil_label.animate.set_opacity(0.35), foil_curve.animate.set_stroke(opacity=0.28), foil_area.animate.set_fill(opacity=0.08), target_curve_label.animate.set_opacity(0.35), foil_curve_label.animate.set_opacity(0.25), run_time=0.8)
        self.wait(0.4)
        self.play(example_target_label.animate.scale(1 / 1.18), target_curve.animate.set_stroke(width=2.2, opacity=0.28), target_area.animate.set_fill(opacity=0.08), example_target_label.animate.set_opacity(0.35), example_foil_label.animate.set_opacity(1.0), foil_curve.animate.set_stroke(width=2.2, opacity=0.28), foil_area.animate.set_fill(opacity=0.08), target_curve_label.animate.set_opacity(0.25), foil_curve_label.animate.set_opacity(0.35), run_time=0.3)
        self.play(example_foil_label.animate.scale(1.18), foil_curve.animate.set_stroke(width=4.8, opacity=1.0), foil_area.animate.set_fill(opacity=0.34), run_time=0.85)
        self.wait(0.4)
        self.play(example_foil_label.animate.scale(1 / 1.18), example_target_label.animate.set_opacity(1.0), target_curve.animate.set_stroke(width=2.2, opacity=1.0), target_area.animate.set_fill(opacity=0.16), example_foil_label.animate.set_opacity(1.0), foil_curve.animate.set_stroke(width=2.2, opacity=1.0), foil_area.animate.set_fill(opacity=0.16), target_curve_label.animate.set_opacity(1.0), foil_curve_label.animate.set_opacity(1.0), run_time=0.85)
        self.play(Succession(AnimationGroup(criterion_line.animate.shift(criterion_right_shift), criterion_label.animate.shift(criterion_right_shift), run_time=1.6, rate_func=smooth), AnimationGroup(criterion_line.animate.shift(criterion_left_shift - criterion_right_shift), criterion_label.animate.shift(criterion_left_shift - criterion_right_shift), run_time=2.4, rate_func=smooth), AnimationGroup(criterion_line.animate.shift(-criterion_left_shift), criterion_label.animate.shift(-criterion_left_shift), run_time=1.8, rate_func=smooth)))
        self.wait(1.0)
        upper_row_center_y = row_block_center_y + 1.2
        upper_label_buff = 0.28
        subtitle_shift = UP * (0.1 * (upper_row_center_y - row_block_center_y))
        upper_example_center = np.array([left_column_center_x, upper_row_center_y, 0.0])
        upper_example_target_pos = upper_example_center + LEFT * example_side_offset
        upper_example_foil_pos = upper_example_center + RIGHT * example_side_offset
        upper_target_label_pos = upper_example_target_pos + UP * (example_image_height / 2 + upper_label_buff)
        upper_foil_label_pos = upper_example_foil_pos + UP * (example_image_height / 2 + upper_label_buff)
        upper_plot_center = np.array([3.48, upper_row_center_y - 0.05, 0.0])
        upper_plot_shift = upper_plot_center - sdt_axes.get_center()
        second_row_center_y = row_block_center_y - 1.5
        second_example_center = np.array([left_column_center_x, second_row_center_y, 0.0])
        second_example_target_pos = second_example_center + LEFT * example_side_offset
        second_example_foil_pos = second_example_center + RIGHT * example_side_offset
        second_plot_center = np.array([3.48, second_row_center_y - 0.05, 0.0])
        second_example_target = ImageMobject(_s1_stage3_memory_task_stimulus_path('LAN-MOU-T00.png'))
        second_example_target.scale_to_fit_height(example_image_height)
        second_example_target.move_to(second_example_target_pos)
        second_example_target.set_z_index(5)
        second_example_foil = ImageMobject(_s1_stage3_memory_task_stimulus_path('LAN-MOU-D03.png'))
        second_example_foil.scale_to_fit_height(example_image_height)
        second_example_foil.move_to(second_example_foil_pos)
        second_example_foil.set_z_index(4)
        second_sdt_axes = Axes(x_range=[0.0, 1.85, 0.37], y_range=[0.0, 1.25, 0.5], x_length=5.1, y_length=2.25, axis_config={'color': axis_color, 'stroke_width': 1.5, 'include_ticks': False, 'include_tip': True, 'tip_width': 0.09, 'tip_height': 0.09})
        second_sdt_axes.move_to(second_plot_center)
        second_foil_mean = foil_mean
        second_target_mean = 1.18
        second_signal_sigma = 0.16
        second_signal_peak = 0.92
        second_foil_curve = second_sdt_axes.plot(lambda x: second_signal_peak * np.exp(-0.5 * ((x - second_foil_mean) / second_signal_sigma) ** 2), x_range=[0.0, 1.63], color=foil_color, stroke_width=2.2)
        second_target_curve = second_sdt_axes.plot(lambda x: second_signal_peak * np.exp(-0.5 * ((x - second_target_mean) / second_signal_sigma) ** 2), x_range=[0.0, 1.63], color=target_color, stroke_width=2.2)
        second_foil_area = second_sdt_axes.get_area(second_foil_curve, x_range=[0.0, 1.63], color=foil_color, opacity=0.16)
        second_foil_area.set_stroke(width=0)
        second_target_area = second_sdt_axes.get_area(second_target_curve, x_range=[0.0, 1.63], color=target_color, opacity=0.16)
        second_target_area.set_stroke(width=0)
        second_criterion_x = 0.5 * (second_foil_mean + second_target_mean)
        second_criterion_line = DashedLine(second_sdt_axes.c2p(second_criterion_x, 0.0), second_sdt_axes.c2p(second_criterion_x, 1.12), dash_length=0.1, dashed_ratio=0.55, color=criterion_color, stroke_width=2.0)
        second_criterion_label = Tex('Criterion', color=_s1_stage3_INK, font_size=22)
        second_criterion_label.next_to(second_criterion_line, UP, buff=0.12)
        second_foil_curve_label = Tex('Foil signal', color=foil_color, font_size=18)
        second_foil_curve_label.move_to(second_sdt_axes.c2p(0.33, 0.88))
        second_target_curve_label = Tex('Target signal', color=target_color, font_size=18)
        second_target_curve_label.move_to(second_sdt_axes.c2p(1.45, 0.88))
        second_memory_strength_label = Tex('Memory strength', color=_s1_stage3_INK, font_size=22)
        second_memory_strength_label.next_to(second_sdt_axes.x_axis, DOWN, buff=0.2)
        second_probability_density_label = Tex('Probability density', color=_s1_stage3_INK, font_size=18)
        second_probability_density_label.rotate(PI / 2)
        second_probability_density_label.next_to(second_sdt_axes.y_axis, LEFT, buff=0.18)
        self.wait(0.4)
        self.play(question.animate.shift(subtitle_shift), example_target.animate.move_to(upper_example_target_pos), example_foil.animate.move_to(upper_example_foil_pos), example_target_label.animate.move_to(upper_target_label_pos), example_foil_label.animate.move_to(upper_foil_label_pos), sdt_group.animate.shift(upper_plot_shift), run_time=1.05, rate_func=smooth)
        self.wait(0.25)
        self.play(FadeIn(second_example_target, scale=0.96), FadeIn(second_example_foil, scale=0.96), run_time=0.7)
        self.wait(0.25)
        self.play(LaggedStart(Create(second_sdt_axes), FadeIn(second_foil_area), FadeIn(second_target_area), Create(second_foil_curve), Create(second_target_curve), Create(second_criterion_line), FadeIn(second_criterion_label, shift=UP * 0.08), FadeIn(second_foil_curve_label, shift=UP * 0.08), FadeIn(second_target_curve_label, shift=UP * 0.08), FadeIn(second_memory_strength_label, shift=UP * 0.08), FadeIn(second_probability_density_label, shift=RIGHT * 0.08), lag_ratio=0.1), run_time=1.35)
        self.wait(1.1)

class Study1Stage3MemoryExpDesignLegacy(Scene):
    """Show the delayed match-to-sample design alongside the selected memory sets."""

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage3_BG
        title = Tex('Memory validation task', color=_s1_stage3_INK, font_size=40).to_edge(UP, buff=0.28)
        question = VGroup(Tex('Does proximity along the perceptual continua', color=_s1_stage3_INK, font_size=26), Tex('of our image sets predict memory performance?', color=_s1_stage3_INK, font_size=26)).arrange(DOWN, buff=0.1).next_to(title, DOWN, buff=0.24)
        lookup = _s1_stage3_load_stimulus_lookup()
        set_specs = [('plant', 'pine_med'), ('landscape_element', 'lake_island'), ('building', 'observatory'), ('item', 'sofa')]
        question_bottom_y = question.get_bottom()[1]
        row_spacing = 1.05
        bottom_margin_y = -config.frame_height / 2 + 0.55
        row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
        row_y_positions = [row_block_center_y + row_spacing * offset for offset in (1.5, 0.5, -0.5, -1.5)]
        left_column_center_x = -config.frame_width / 4
        selected_spacing = 1.05
        selected_xs = [left_column_center_x + selected_spacing * offset for offset in (-1.5, -0.5, 0.5, 1.5)]
        collapsed_cards = []
        bottom_continuation_marks = []
        lake_target_card = None
        lake_d3_card = None
        for (category, obj), row_y in zip(set_specs, row_y_positions):
            row = lookup[category, obj]
            prefix = f'{category}_{obj}'
            selected_indices = [int(row['target_position']), int(row['distractor_1_position']), int(row['distractor_2_position']), int(row['distractor_3_position'])]
            for col_idx, stim_idx in enumerate(selected_indices):
                card = _s1_stage3_stimulus_image(prefix, stim_idx, 0.56, (selected_xs[col_idx], row_y, 0.0))
                card.scale(1.45)
                card.set_z_index(5)
                collapsed_cards.append(card)
                if category == 'landscape_element' and obj == 'lake_island' and (col_idx == 0):
                    lake_target_card = card
                if category == 'landscape_element' and obj == 'lake_island' and (col_idx == 3):
                    lake_d3_card = card
                if obj == 'sofa':
                    dot = MathTex('\\vdots', color=_s1_stage3_MGREY, font_size=24).next_to(card, DOWN, buff=0.19)
                    dot.set_z_index(5)
                    bottom_continuation_marks.append(dot)
        target_cards = Group(*collapsed_cards[0::4])
        foil_cards = Group(*[collapsed_cards[idx] for idx in range(len(collapsed_cards)) if idx % 4 != 0])
        continuation_marks = VGroup(*bottom_continuation_marks)
        target_rect = SurroundingRectangle(Group(target_cards, continuation_marks[0]), color=_s1_stage3_MGREY, stroke_width=1.5, buff=0.1, corner_radius=0.06)
        foil_rect = SurroundingRectangle(Group(foil_cards, *continuation_marks[1:]), color=_s1_stage3_MGREY, stroke_width=1.5, buff=0.1, corner_radius=0.06)
        target_label = Tex('Targets', color=_s1_stage3_INK, font_size=24).next_to(target_rect, UP, buff=0.12)
        foil_label = Tex('Foils', color=_s1_stage3_INK, font_size=24).next_to(foil_rect, UP, buff=0.12)
        arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
        dissimilar_arrow = Arrow(start=np.array([target_rect.get_center()[0] - 0.2, arrow_y, 0.0]), end=np.array([foil_rect.get_right()[0] - 0.1, arrow_y, 0.0]), buff=0.0, stroke_width=2.0, color=_s1_stage3_MGREY, tip_length=0.18, max_stroke_width_to_length_ratio=8, max_tip_length_to_length_ratio=0.1)
        dissimilar_text = Tex('More dissimilar', color=_s1_stage3_INK, font_size=22).next_to(dissimilar_arrow, DOWN, buff=0.1)
        self.add(title, question, *collapsed_cards, *continuation_marks, target_rect, foil_rect, target_label, foil_label, dissimilar_arrow, dissimilar_text)
        frame_side = 1.75
        right_margin_x = config.frame_width / 2 - 0.35
        stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
        stage_center_y = 0.5 * (row_y_positions[1] + row_y_positions[2])
        right_center = np.array([stage_center_x, stage_center_y, 0.0])
        lake_prefix = 'landscape_element_lake_island'
        lake_row = lookup['landscape_element', 'lake_island']
        target_idx = int(lake_row['target_position'])
        probe1_idx = int(lake_row['distractor_3_position'])
        probe2_idx = target_idx

        def stage_content(kind: str, center: np.ndarray, large: bool) -> Group:
            """Build the visual payload for one trial phase in either large or parked form."""
            image_height = 0.95 if large else 0.44
            fixation_height = 0.18 if large else 0.06
            if kind == 'target':
                img = _s1_stage3_stimulus_image(lake_prefix, target_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = _s1_stage3_fixation_on(img, height=fixation_height)
                return Group(img, fix)
            if kind == 'probe1':
                img = _s1_stage3_stimulus_image(lake_prefix, probe1_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = _s1_stage3_fixation_on(img, height=fixation_height)
                return Group(img, fix)
            if kind == 'probe2':
                img = _s1_stage3_stimulus_image(lake_prefix, probe2_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = _s1_stage3_fixation_on(img, height=fixation_height)
                return Group(img, fix)
            if kind in {'delay', 'buffer', 'iti'}:
                fix = _s1_stage3_fixation_on(center, height=fixation_height)
                return Group(fix)
            if kind == 'response':
                response_size = 18 if large else 8
                response_buff = 0.14 if large else 0.04
                fix = _s1_stage3_fixation_on(center, height=fixation_height)
                left_text = Tex('TWO', color=_s1_stage3_INK, font_size=response_size).next_to(fix, LEFT, buff=response_buff)
                right_text = Tex('ONE', color=_s1_stage3_INK, font_size=response_size).next_to(fix, RIGHT, buff=response_buff)
                arrow_length = 0.4 if large else 0.2
                arrow = Arrow(start=left_text.get_center() + RIGHT * (arrow_length / 2), end=left_text.get_center() + LEFT * (arrow_length / 2), color=_s1_stage3_INK, stroke_width=10 if large else 4, buff=0, tip_length=0.3 if large else 0.1)
                arrow.next_to(left_text, DOWN, buff=0.06 if large else 0.035)
                fix.set_z_index(8 if large else 6)
                left_text.set_z_index(8 if large else 6)
                right_text.set_z_index(8 if large else 6)
                arrow.set_z_index(8 if large else 6)
                return Group(left_text, fix, right_text, arrow)
        stage_specs = [('2s', 'Target', 'target'), ('8s', 'Delay', 'delay'), ('1s', 'Probe 1', 'probe1'), ('0.5s', 'Buffer', 'buffer'), ('1s', 'Probe 2', 'probe2'), ('2s', 'Response', 'response'), ('(M=4s)', 'ITI', 'iti')]
        stage_frame = RoundedRectangle(corner_radius=0.12, width=frame_side, height=frame_side, stroke_color=_s1_stage3_MGREY, stroke_width=1.6).move_to(right_center)
        stage_frame.set_fill(WHITE, opacity=1.0)
        stage_duration = Tex(stage_specs[0][0], color=_s1_stage3_INK, font_size=24).next_to(stage_frame, UP, buff=0.16)
        stage_label = Tex(stage_specs[0][1], color=_s1_stage3_INK, font_size=24).next_to(stage_frame, DOWN, buff=0.18)
        strip_side = 0.82
        strip_gap = 0.1
        strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
        quadrant_bottom_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1])
        strip_start_y = quadrant_bottom_y + strip_side / 2
        strip_final_y = right_center[1] - 0.12
        strip_start_centers = [np.array([right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap), strip_start_y, 0.0]) for i in range(len(stage_specs))]
        strip_final_centers = [np.array([right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap), strip_final_y, 0.0]) for i in range(len(stage_specs))]
        parked_cards = []
        for (_, _, kind), center in zip(stage_specs, strip_start_centers):
            parked_frame = RoundedRectangle(corner_radius=0.08, width=strip_side, height=strip_side, stroke_color=_s1_stage3_MGREY, stroke_width=1.2).move_to(center)
            parked_frame.set_fill(WHITE, opacity=1.0)
            parked_content = stage_content(kind, center, large=False)
            parked_group = Group(parked_frame, parked_content)
            parked_group.set_z_index(6)
            parked_cards.append(parked_group)
        strip_arrow_start_x = strip_start_centers[0][0] - strip_side / 2
        strip_arrow_y = ValueTracker(strip_start_y - strip_side / 2 - 0.18)
        strip_arrow_progress_x = ValueTracker(strip_arrow_start_x + 0.04)
        progress_arrow = always_redraw(lambda: Arrow(start=np.array([strip_arrow_start_x, strip_arrow_y.get_value(), 0.0]), end=np.array([max(strip_arrow_progress_x.get_value(), strip_arrow_start_x + 0.04), strip_arrow_y.get_value(), 0.0]), color=_s1_stage3_LGREY, stroke_width=1.3, buff=0.0, tip_length=0.14))
        target_copy = lake_target_card.copy()
        target_copy.move_to(lake_target_card.get_center())
        target_copy.set_z_index(8)
        target_copy.generate_target()
        target_copy.target.scale_to_fit_height(0.95)
        target_copy.target.move_to(right_center)
        target_fixation = _s1_stage3_fixation_on(right_center, height=0.18)
        active_content = Group(target_copy, target_fixation)
        self.play(Create(stage_frame), MoveToTarget(target_copy), FadeIn(target_fixation), FadeIn(stage_duration), FadeIn(stage_label), run_time=0.8)
        self.add(progress_arrow)
        self.wait(0.2)
        hold_before_park = 1
        park_run_time = 0.4
        hold_after_park = 0.08
        for idx, (duration, label, kind) in enumerate(stage_specs):
            self.wait(hold_before_park)
            self.play(TransformFromCopy(Group(stage_frame, active_content), parked_cards[idx]), strip_arrow_progress_x.animate.set_value(parked_cards[idx].get_right()[0]), run_time=park_run_time)
            self.wait(hold_after_park)
            if idx == len(stage_specs) - 1:
                continue
            next_duration = Tex(stage_specs[idx + 1][0], color=_s1_stage3_INK, font_size=24).next_to(stage_frame, UP, buff=0.16)
            next_label = Tex(stage_specs[idx + 1][1], color=_s1_stage3_INK, font_size=24).next_to(stage_frame, DOWN, buff=0.18)
            next_kind = stage_specs[idx + 1][2]
            step_run_time = 0.5
            if next_kind in ('probe1', 'probe2'):
                source_card = lake_d3_card if next_kind == 'probe1' else lake_target_card
                highlight_rect = SurroundingRectangle(source_card, color='#F63924', stroke_width=2.5, buff=0.06, corner_radius=0.05)
                highlight_rect.set_z_index(9)
                self.play(FadeIn(highlight_rect), run_time=0.25)
                self.wait(0.1)
                probe_copy = source_card.copy()
                probe_copy.move_to(source_card.get_center())
                probe_copy.set_z_index(8)
                probe_copy.generate_target()
                probe_copy.target.scale_to_fit_height(0.95)
                probe_copy.target.move_to(right_center)
                probe_fix = _s1_stage3_fixation_on(right_center, height=0.18)
                next_content = Group(probe_copy, probe_fix)
                self.play(FadeOut(active_content, shift=DOWN * 0.06), FadeOut(highlight_rect), MoveToTarget(probe_copy), FadeIn(probe_fix), ReplacementTransform(stage_duration, next_duration), ReplacementTransform(stage_label, next_label), run_time=0.9)
            else:
                next_content = stage_content(next_kind, right_center, large=True)
                self.play(FadeOut(active_content, shift=DOWN * 0.06), FadeIn(next_content, shift=UP * 0.06), ReplacementTransform(stage_duration, next_duration), ReplacementTransform(stage_label, next_label), run_time=step_run_time)
            active_content = next_content
            stage_duration = next_duration
            stage_label = next_label
            self.wait(0.3 if next_kind == 'delay' else 0.18)
        left_panel = Group(*collapsed_cards, continuation_marks, target_rect, foil_rect, target_label, foil_label, dissimilar_arrow, dissimilar_text)
        final_arrow_y = min(strip_final_y - strip_side * 1.12 / 2 - 0.2, right_center[1] - 1.15)
        promotion_anims = [parked.animate.move_to(target_center) for parked, target_center in zip(parked_cards, strip_final_centers)]
        self.play(FadeOut(active_content, shift=UP * 0.06), FadeOut(stage_frame, shift=UP * 0.06), FadeOut(stage_duration, shift=UP * 0.06), FadeOut(stage_label, shift=UP * 0.06), left_panel.animate.scale(0.8), strip_arrow_y.animate.set_value(final_arrow_y), *promotion_anims, run_time=0.85)
        final_duration_labels = VGroup(*[Tex(duration, color=_s1_stage3_INK, font_size=16).next_to(card, UP, buff=0.1) for (duration, _, _), card in zip(stage_specs, parked_cards)])
        final_stage_labels = VGroup(*[Tex(label, color=_s1_stage3_INK, font_size=16).next_to(card, DOWN, buff=0.1) for (_, label, _), card in zip(stage_specs, parked_cards)])
        time_label = MathTex('t', color=_s1_stage3_INK, font_size=24).next_to(progress_arrow, RIGHT, buff=0.1)
        self.play(LaggedStart(*[FadeIn(label, shift=UP * 0.05) for label in final_duration_labels], lag_ratio=0.05), LaggedStart(*[FadeIn(label, shift=UP * 0.05) for label in final_stage_labels], lag_ratio=0.05), FadeIn(time_label, shift=RIGHT * 0.05), run_time=1.0)
        self.wait(1.0)

class Study1Stage3MemoryExpDesignB(Scene):
    """Add difficulty labels and experiment-level counts to the design summary."""

    def construct(self) -> None:
        """Annotate the parked trial strip with difficulty, timing, and sample size."""
        self.camera.background_color = _s1_stage3_BG
        title = Tex('Memory validation task', color=_s1_stage3_INK, font_size=40).to_edge(UP, buff=0.28)
        question = VGroup(Tex('Does proximity along the perceptual continua', color=_s1_stage3_INK, font_size=26), Tex('of our image sets predict memory performance?', color=_s1_stage3_INK, font_size=26)).arrange(DOWN, buff=0.1).next_to(title, DOWN, buff=0.24)
        lookup = _s1_stage3_load_stimulus_lookup()
        set_specs = [('plant', 'pine_med'), ('landscape_element', 'lake_island'), ('building', 'observatory'), ('item', 'sofa')]
        question_bottom_y = question.get_bottom()[1]
        row_spacing = 1.05
        bottom_margin_y = -config.frame_height / 2 + 0.55
        row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
        row_y_positions = [row_block_center_y + row_spacing * o for o in (1.5, 0.5, -0.5, -1.5)]
        left_column_center_x = -config.frame_width / 4
        selected_spacing = 1.05
        selected_xs = [left_column_center_x + selected_spacing * o for o in (-1.5, -0.5, 0.5, 1.5)]
        collapsed_cards: list = []
        bottom_continuation_marks: list = []
        for (category, obj), row_y in zip(set_specs, row_y_positions):
            row = lookup[category, obj]
            prefix = f'{category}_{obj}'
            selected_indices = [int(row['target_position']), int(row['distractor_1_position']), int(row['distractor_2_position']), int(row['distractor_3_position'])]
            for col_idx, stim_idx in enumerate(selected_indices):
                card = _s1_stage3_stimulus_image(prefix, stim_idx, 0.56, (selected_xs[col_idx], row_y, 0.0))
                card.scale(1.45)
                card.set_z_index(5)
                collapsed_cards.append(card)
                if obj == 'sofa':
                    dot = MathTex('\\vdots', color=_s1_stage3_MGREY, font_size=24).next_to(card, DOWN, buff=0.19)
                    dot.set_z_index(5)
                    bottom_continuation_marks.append(dot)
        target_cards = Group(*collapsed_cards[0::4])
        foil_cards = Group(*[collapsed_cards[i] for i in range(len(collapsed_cards)) if i % 4 != 0])
        continuation_marks = VGroup(*bottom_continuation_marks)
        target_rect = SurroundingRectangle(Group(target_cards, continuation_marks[0]), color=_s1_stage3_MGREY, stroke_width=1.5, buff=0.1, corner_radius=0.06)
        foil_rect = SurroundingRectangle(Group(foil_cards, *continuation_marks[1:]), color=_s1_stage3_MGREY, stroke_width=1.5, buff=0.1, corner_radius=0.06)
        target_label = Tex('Targets', color=_s1_stage3_INK, font_size=24).next_to(target_rect, UP, buff=0.12)
        foil_label = Tex('Foils', color=_s1_stage3_INK, font_size=24).next_to(foil_rect, UP, buff=0.12)
        arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
        dissimilar_arrow = Arrow(start=np.array([target_rect.get_center()[0] - 0.2, arrow_y, 0.0]), end=np.array([foil_rect.get_right()[0] - 0.1, arrow_y, 0.0]), buff=0.0, stroke_width=2.0, color=_s1_stage3_MGREY, tip_length=0.18, max_stroke_width_to_length_ratio=8, max_tip_length_to_length_ratio=0.1)
        dissimilar_text = Tex('More dissimilar', color=_s1_stage3_INK, font_size=22).next_to(dissimilar_arrow, DOWN, buff=0.1)
        frame_side = 1.75
        right_margin_x = config.frame_width / 2 - 0.35
        stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
        stage_center_y = 0.5 * (row_y_positions[1] + row_y_positions[2])
        right_center = np.array([stage_center_x, stage_center_y, 0.0])
        lake_prefix = 'landscape_element_lake_island'
        lake_row = lookup['landscape_element', 'lake_island']
        target_idx = int(lake_row['target_position'])
        probe1_idx = int(lake_row['distractor_3_position'])
        probe2_idx = target_idx

        def stage_content(kind: str, center: np.ndarray, large: bool) -> Group:
            """Build the visual payload for one trial phase in either large or parked form."""
            image_height = 0.95 if large else 0.44
            fixation_height = 0.18 if large else 0.06
            if kind == 'target':
                img = _s1_stage3_stimulus_image(lake_prefix, target_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                return Group(img, _s1_stage3_fixation_on(img, height=fixation_height))
            if kind == 'probe1':
                img = _s1_stage3_stimulus_image(lake_prefix, probe1_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                return Group(img, _s1_stage3_fixation_on(img, height=fixation_height))
            if kind == 'probe2':
                img = _s1_stage3_stimulus_image(lake_prefix, probe2_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                return Group(img, _s1_stage3_fixation_on(img, height=fixation_height))
            if kind in {'delay', 'buffer', 'iti'}:
                return Group(_s1_stage3_fixation_on(center, height=fixation_height))
            response_size = 18 if large else 8
            response_buff = 0.14 if large else 0.04
            fix = _s1_stage3_fixation_on(center, height=fixation_height)
            left_text = Tex('TWO', color=_s1_stage3_INK, font_size=response_size).next_to(fix, LEFT, buff=response_buff)
            right_text = Tex('ONE', color=_s1_stage3_INK, font_size=response_size).next_to(fix, RIGHT, buff=response_buff)
            arrow_len = 0.4 if large else 0.2
            arr = Arrow(start=left_text.get_center() + RIGHT * (arrow_len / 2), end=left_text.get_center() + LEFT * (arrow_len / 2), color=_s1_stage3_INK, stroke_width=10 if large else 4, buff=0, tip_length=0.3 if large else 0.1)
            arr.next_to(left_text, DOWN, buff=0.06 if large else 0.035)
            for m in (fix, left_text, right_text, arr):
                m.set_z_index(8 if large else 6)
            return Group(left_text, fix, right_text, arr)
        stage_specs = [('2s', 'Target', 'target'), ('8s', 'Delay', 'delay'), ('1s', 'Probe 1', 'probe1'), ('0.5s', 'Buffer', 'buffer'), ('1s', 'Probe 2', 'probe2'), ('2s', 'Response', 'response'), ('(M=4s)', 'ITI', 'iti')]
        strip_side = 0.82
        strip_gap = 0.1
        strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
        strip_final_y = right_center[1] - 0.12
        strip_final_centers = [np.array([right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap), strip_final_y, 0.0]) for i in range(len(stage_specs))]
        parked_cards = []
        for (_, _, kind), center in zip(stage_specs, strip_final_centers):
            pf = RoundedRectangle(corner_radius=0.08, width=strip_side, height=strip_side, stroke_color=_s1_stage3_MGREY, stroke_width=1.2).move_to(center)
            pf.set_fill(WHITE, opacity=1.0)
            pc = stage_content(kind, center, large=False)
            pg = Group(pf, pc)
            pg.set_z_index(6)
            parked_cards.append(pg)
        final_duration_labels = VGroup(*[Tex(dur, color=_s1_stage3_INK, font_size=16).next_to(card, UP, buff=0.1) for (dur, _, _), card in zip(stage_specs, parked_cards)])
        final_stage_labels = VGroup(*[Tex(lbl, color=_s1_stage3_INK, font_size=16).next_to(card, DOWN, buff=0.1) for (_, lbl, _), card in zip(stage_specs, parked_cards)])
        final_arrow_y = min(strip_final_y - strip_side * 1.12 / 2 - 0.2, right_center[1] - 1.15)
        strip_arrow_start_x = right_center[0] - strip_total_width / 2
        progress_arrow = Arrow(start=np.array([strip_arrow_start_x, final_arrow_y, 0.0]), end=np.array([right_center[0] + strip_total_width / 2, final_arrow_y, 0.0]), color=_s1_stage3_LGREY, stroke_width=1.3, buff=0.0, tip_length=0.14)
        time_label = MathTex('t', color=_s1_stage3_INK, font_size=24).next_to(progress_arrow, RIGHT, buff=0.1)
        left_panel = Group(*collapsed_cards, continuation_marks, target_rect, foil_rect, target_label, foil_label, dissimilar_arrow, dissimilar_text)
        left_panel.scale(0.8)
        self.add(title, question, *collapsed_cards, *continuation_marks, target_rect, foil_rect, target_label, foil_label, dissimilar_arrow, dissimilar_text, *parked_cards, final_duration_labels, final_stage_labels, progress_arrow, time_label)
        self.play(dissimilar_arrow.animate.shift(DOWN * 0.38), dissimilar_text.animate.shift(DOWN * 0.38), FadeOut(foil_rect), run_time=0.65)
        foil_cols = [Group(*[collapsed_cards[4 * r + c] for r in range(4)], continuation_marks[c]) for c in (1, 2, 3)]
        for diff_label, color, col_group in [('Hard', '#C94040', foil_cols[0]), ('Medium', '#C87137', foil_cols[1]), ('Easy', '#3A7EC8', foil_cols[2])]:
            col_rect = SurroundingRectangle(col_group, color=color, stroke_width=1.8, buff=0.08, corner_radius=0.06)
            lbl = Tex(diff_label, color=color, font_size=22).next_to(col_group, DOWN, buff=0.18)
            self.play(Create(col_rect), FadeIn(lbl, shift=UP * 0.08), run_time=0.55)
            self.wait(0.35)
        self.wait(0.3)
        stats_block = VGroup(Tex('$N = 240$', color=_s1_stage3_INK, font_size=22), Tex('6 blocks $\\cdot$ half repeated, half new targets per block', color=_s1_stage3_INK, font_size=20)).arrange(DOWN, buff=0.12)
        timeline_bottom = min(final_stage_labels.get_bottom()[1], time_label.get_bottom()[1], progress_arrow.get_bottom()[1])
        stats_block.align_to(final_stage_labels, LEFT)
        stats_block.set_y(timeline_bottom - stats_block.get_height() / 2 - 0.32)
        self.play(LaggedStart(FadeIn(stats_block[0], shift=UP * 0.08), FadeIn(stats_block[1], shift=UP * 0.08), lag_ratio=0.35), run_time=0.8)
        self.wait(1.0)

class Study1Stage3MemoryExpResults(Scene):
    """Show the behavioural results of the memory validation task."""
    AGG_IMG = str(REPO_ROOT / 'assets' / 'images' / 'study1_stage3' / 'behavior_agg_manim.svg')
    BLOCK_IMG = str(REPO_ROOT / 'assets' / 'images' / 'study1_stage3' / 'behaviour_block_manim.svg')

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = _s1_stage3_BG

        def build_expdesignb_final_frame() -> Group:
            """Build the held design-summary frame reused before the results reveal."""
            title = Tex('Memory validation task', color=_s1_stage3_INK, font_size=40).to_edge(UP, buff=0.28)
            question = VGroup(Tex('Does proximity along the perceptual continua', color=_s1_stage3_INK, font_size=26), Tex('of our image sets predict memory performance?', color=_s1_stage3_INK, font_size=26)).arrange(DOWN, buff=0.1).next_to(title, DOWN, buff=0.24)
            lookup = _s1_stage3_load_stimulus_lookup()
            set_specs = [('plant', 'pine_med'), ('landscape_element', 'lake_island'), ('building', 'observatory'), ('item', 'sofa')]
            question_bottom_y = question.get_bottom()[1]
            row_spacing = 1.05
            bottom_margin_y = -config.frame_height / 2 + 0.55
            row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
            row_y_positions = [row_block_center_y + row_spacing * o for o in (1.5, 0.5, -0.5, -1.5)]
            left_column_center_x = -config.frame_width / 4
            selected_spacing = 1.05
            selected_xs = [left_column_center_x + selected_spacing * o for o in (-1.5, -0.5, 0.5, 1.5)]
            collapsed_cards: list[Mobject] = []
            bottom_continuation_marks: list[Mobject] = []
            for (category, obj), row_y in zip(set_specs, row_y_positions):
                row = lookup[category, obj]
                prefix = f'{category}_{obj}'
                selected_indices = [int(row['target_position']), int(row['distractor_1_position']), int(row['distractor_2_position']), int(row['distractor_3_position'])]
                for col_idx, stim_idx in enumerate(selected_indices):
                    card = _s1_stage3_stimulus_image(prefix, stim_idx, 0.56, (selected_xs[col_idx], row_y, 0.0))
                    card.scale(1.45)
                    card.set_z_index(5)
                    collapsed_cards.append(card)
                    if obj == 'sofa':
                        dot = MathTex('\\vdots', color=_s1_stage3_MGREY, font_size=24).next_to(card, DOWN, buff=0.19)
                        dot.set_z_index(5)
                        bottom_continuation_marks.append(dot)
            target_cards = Group(*collapsed_cards[0::4])
            foil_cards = Group(*[collapsed_cards[i] for i in range(len(collapsed_cards)) if i % 4 != 0])
            continuation_marks = VGroup(*bottom_continuation_marks)
            target_rect = SurroundingRectangle(Group(target_cards, continuation_marks[0]), color=_s1_stage3_MGREY, stroke_width=1.5, buff=0.1, corner_radius=0.06)
            foil_rect = SurroundingRectangle(Group(foil_cards, *continuation_marks[1:]), color=_s1_stage3_MGREY, stroke_width=1.5, buff=0.1, corner_radius=0.06)
            target_label = Tex('Targets', color=_s1_stage3_INK, font_size=24).next_to(target_rect, UP, buff=0.12)
            foil_label = Tex('Foils', color=_s1_stage3_INK, font_size=24).next_to(foil_rect, UP, buff=0.12)
            arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
            dissimilar_arrow = Arrow(start=np.array([target_rect.get_center()[0] - 0.2, arrow_y, 0.0]), end=np.array([foil_rect.get_right()[0] - 0.1, arrow_y, 0.0]), buff=0.0, stroke_width=2.0, color=_s1_stage3_MGREY, tip_length=0.18, max_stroke_width_to_length_ratio=8, max_tip_length_to_length_ratio=0.1)
            dissimilar_text = Tex('More dissimilar', color=_s1_stage3_INK, font_size=22).next_to(dissimilar_arrow, DOWN, buff=0.1)
            frame_side = 1.75
            right_margin_x = config.frame_width / 2 - 0.35
            stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
            stage_center_y = 0.5 * (row_y_positions[1] + row_y_positions[2])
            right_center = np.array([stage_center_x, stage_center_y, 0.0])
            lake_prefix = 'landscape_element_lake_island'
            lake_row = lookup['landscape_element', 'lake_island']
            target_idx = int(lake_row['target_position'])
            probe1_idx = int(lake_row['distractor_3_position'])
            probe2_idx = target_idx

            def stage_content(kind: str, center: np.ndarray) -> Group:
                """Return the stage content."""
                image_height = 0.44
                fixation_height = 0.06
                if kind == 'target':
                    img = _s1_stage3_stimulus_image(lake_prefix, target_idx, image_height, center)
                    img.set_z_index(6)
                    return Group(img, _s1_stage3_fixation_on(img, height=fixation_height))
                if kind == 'probe1':
                    img = _s1_stage3_stimulus_image(lake_prefix, probe1_idx, image_height, center)
                    img.set_z_index(6)
                    return Group(img, _s1_stage3_fixation_on(img, height=fixation_height))
                if kind == 'probe2':
                    img = _s1_stage3_stimulus_image(lake_prefix, probe2_idx, image_height, center)
                    img.set_z_index(6)
                    return Group(img, _s1_stage3_fixation_on(img, height=fixation_height))
                if kind in {'delay', 'buffer', 'iti'}:
                    return Group(_s1_stage3_fixation_on(center, height=fixation_height))
                fix = _s1_stage3_fixation_on(center, height=fixation_height)
                left_text = Tex('TWO', color=_s1_stage3_INK, font_size=8).next_to(fix, LEFT, buff=0.04)
                right_text = Tex('ONE', color=_s1_stage3_INK, font_size=8).next_to(fix, RIGHT, buff=0.04)
                arr = Arrow(start=left_text.get_center() + RIGHT * 0.1, end=left_text.get_center() + LEFT * 0.1, color=_s1_stage3_INK, stroke_width=4, buff=0, tip_length=0.1)
                arr.next_to(left_text, DOWN, buff=0.035)
                for mob in (fix, left_text, right_text, arr):
                    mob.set_z_index(6)
                return Group(left_text, fix, right_text, arr)
            stage_specs = [('2s', 'Target', 'target'), ('8s', 'Delay', 'delay'), ('1s', 'Probe 1', 'probe1'), ('0.5s', 'Buffer', 'buffer'), ('1s', 'Probe 2', 'probe2'), ('2s', 'Response', 'response'), ('(M=4s)', 'ITI', 'iti')]
            strip_side = 0.82
            strip_gap = 0.1
            strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
            strip_final_y = right_center[1] - 0.12
            strip_final_centers = [np.array([right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap), strip_final_y, 0.0]) for i in range(len(stage_specs))]
            parked_cards = []
            for (_, _, kind), center in zip(stage_specs, strip_final_centers):
                pf = RoundedRectangle(corner_radius=0.08, width=strip_side, height=strip_side, stroke_color=_s1_stage3_MGREY, stroke_width=1.2).move_to(center)
                pf.set_fill(WHITE, opacity=1.0)
                pg = Group(pf, stage_content(kind, center))
                pg.set_z_index(6)
                parked_cards.append(pg)
            final_duration_labels = VGroup(*[Tex(dur, color=_s1_stage3_INK, font_size=16).next_to(card, UP, buff=0.1) for (dur, _, _), card in zip(stage_specs, parked_cards)])
            final_stage_labels = VGroup(*[Tex(lbl, color=_s1_stage3_INK, font_size=16).next_to(card, DOWN, buff=0.1) for (_, lbl, _), card in zip(stage_specs, parked_cards)])
            final_arrow_y = min(strip_final_y - strip_side * 1.12 / 2 - 0.2, right_center[1] - 1.15)
            strip_arrow_start_x = right_center[0] - strip_total_width / 2
            progress_arrow = Arrow(start=np.array([strip_arrow_start_x, final_arrow_y, 0.0]), end=np.array([right_center[0] + strip_total_width / 2, final_arrow_y, 0.0]), color=_s1_stage3_LGREY, stroke_width=1.3, buff=0.0, tip_length=0.14)
            time_label = MathTex('t', color=_s1_stage3_INK, font_size=24).next_to(progress_arrow, RIGHT, buff=0.1)
            left_panel = Group(*collapsed_cards, continuation_marks, target_rect, foil_rect, target_label, foil_label, dissimilar_arrow, dissimilar_text)
            left_panel.scale(0.8)
            dissimilar_arrow.shift(DOWN * 0.38)
            dissimilar_text.shift(DOWN * 0.38)
            foil_cols = [Group(*[collapsed_cards[4 * r + c] for r in range(4)], continuation_marks[c]) for c in (1, 2, 3)]
            diff_groups = []
            for diff_label, color, col_group in [('Hard', '#C94040', foil_cols[0]), ('Medium', '#C87137', foil_cols[1]), ('Easy', '#3A7EC8', foil_cols[2])]:
                col_rect = SurroundingRectangle(col_group, color=color, stroke_width=1.8, buff=0.08, corner_radius=0.06)
                lbl = Tex(diff_label, color=color, font_size=22).next_to(col_group, DOWN, buff=0.18)
                diff_groups.append(Group(col_rect, lbl))
            stats_block = VGroup(Tex('$N = 240$', color=_s1_stage3_INK, font_size=22), Tex('6 blocks $\\cdot$ half repeated, half new targets per block', color=_s1_stage3_INK, font_size=20)).arrange(DOWN, buff=0.12)
            timeline_bottom = min(final_stage_labels.get_bottom()[1], time_label.get_bottom()[1], progress_arrow.get_bottom()[1])
            stats_block.align_to(final_stage_labels, LEFT)
            stats_block.set_y(timeline_bottom - stats_block.height / 2 - 0.32)
            return Group(title, question, *collapsed_cards, continuation_marks, target_rect, target_label, foil_label, dissimilar_arrow, dissimilar_text, *parked_cards, final_duration_labels, final_stage_labels, progress_arrow, time_label, *diff_groups, stats_block)
        previous_scene = build_expdesignb_final_frame()
        self.add(previous_scene)
        self.wait(0.2)
        title = Tex('Memory validation results', color=_s1_stage3_INK, font_size=40).to_edge(UP, buff=0.28)
        plot_height = 0.7 * (2 * config.frame_height / 3)
        agg_img = _s1_stage3_load_visible_svg(self.AGG_IMG, height=plot_height)
        block_img = _s1_stage3_load_visible_svg(self.BLOCK_IMG, height=plot_height)
        _s1_stage3_restore_agg_nonrepeated_dashes(agg_img)
        plots = VGroup(agg_img, block_img).arrange(RIGHT, buff=0.85)
        max_plot_area_width = config.frame_width - 0.8
        if plots.width > max_plot_area_width:
            plots.scale_to_fit_width(max_plot_area_width)
        agg_caption = Tex('Lower accuracy for more similar\\\\target--foil pairs', color=_s1_stage3_INK, font_size=22)
        block_caption = Tex('Repetition benefited\\\\working memory performance', color=_s1_stage3_INK, font_size=22)
        plot_vertical_shift = 0.3 * plot_height
        plot_top_y = title.get_bottom()[1] - 0.45 - plot_vertical_shift
        plots.set_y(plot_top_y - plots.height / 2)
        plots.set_x(0)
        agg_labels = _s1_stage3_build_agg_tex_overlays(agg_img)
        block_labels = _s1_stage3_build_block_tex_overlays(block_img)
        agg_plot = VGroup(agg_img, agg_labels)
        block_plot = VGroup(block_img, block_labels)
        panel_width = max(agg_plot.width, block_plot.width)
        for caption in (agg_caption, block_caption):
            if caption.width > panel_width * 0.94:
                caption.scale_to_fit_width(panel_width * 0.94)
        agg_caption.next_to(agg_plot, DOWN, buff=0.3)
        block_caption.next_to(block_plot, DOWN, buff=0.3)
        panels = VGroup(agg_plot, agg_caption, block_plot, block_caption)
        conclusion = Tex('Stimulus set captured a perceptual continuum.', color=_s1_stage3_INK, font_size=28)
        conclusion.next_to(panels, DOWN, buff=0.55)
        self.play(FadeOut(previous_scene, shift=DOWN * 0.08), FadeIn(title, shift=UP * 0.1), run_time=0.8)
        self.play(FadeIn(agg_plot, shift=UP * 0.08), run_time=0.75)
        self.play(Write(agg_caption), run_time=0.6)
        self.wait(0.15)
        self.play(FadeIn(block_plot, shift=UP * 0.08), run_time=0.75)
        self.play(Write(block_caption), run_time=0.6)
        self.wait(0.35)
        self.play(FadeIn(conclusion, shift=UP * 0.06), run_time=0.55)
        self.wait(1.2)

class Study1Stage1_2D(Scene):
    """Scenes 01–06 merged: Step1a, Step1b, Step2, Step2Showcase, Step3 (sections 05–06)."""

    def construct(self) -> None:
        self.next_section("01_Step1a")
        Study1Stage1Step1a.construct(self)
        self.next_section("02_Step1b")
        self.clear()
        Study1Stage1Step1b.construct(self)
        self.next_section("03_Step2")
        self.clear()
        Study1Stage1Step2.construct(self)
        self.next_section("04_Step2Showcase")
        self.clear()
        Study1Stage1Step2Showcase.construct(self)
        self.clear()
        self.segment = "merged"
        _Study1Step3Base.construct(self)
        del self.segment


class Study1Stage2(
    Study1Stage2ModelOrderToHeatmap,
    Study1Stage2SimilarityJudgementsExamples,
    Study1Stage2TripletTask,
):
    """Scenes 12–17 merged: StimulusSetShowcase through ModelOrderToHeatmap."""

    def construct(self) -> None:
        self.next_section("12_StimulusSetShowcase")
        Study1StimulusSetShowcase.construct(self)
        self.next_section("13_TripletTask")
        self.clear()
        Study1Stage2TripletTask.construct(self)
        self.next_section("14_TripletTask2")
        self.clear()
        Study1Stage2TripletTask2.construct(self)
        self.next_section("15_SimilarityJudgements")
        self.clear()
        Study1Stage2SimilarityJudgementsExamples.construct(self)
        self.next_section("16_EmbeddingResult")
        self.clear()
        Study1Stage2EmbeddingResult.construct(self)
        self.next_section("17_ModelOrderToHeatmap")
        self.clear()
        Study1Stage2ModelOrderToHeatmap.construct(self)


class Study1Stage3(Scene):
    """Scenes 18–23 merged: MemoryIntroA–D, MemoryExpDesign, MemoryExpResults."""

    # The merged scene replays Study1Stage3MemoryExpResults on itself, so it
    # needs the same asset paths that results scene expects on `self`.
    AGG_IMG = Study1Stage3MemoryExpResults.AGG_IMG
    BLOCK_IMG = Study1Stage3MemoryExpResults.BLOCK_IMG

    def construct(self) -> None:
        self.next_section("18_MemoryIntroA")
        Study1Stage3MemoryIntroA.construct(self)
        self.next_section("19_MemoryIntroB")
        self.clear()
        Study1Stage3MemoryIntroB.construct(self)
        self.next_section("20_MemoryIntroC")
        self.clear()
        Study1Stage3MemoryIntroC.construct(self)
        self.next_section("21_MemoryIntroD")
        self.clear()
        Study1Stage3MemoryIntroD.construct(self)
        self.next_section("22_MemoryExpDesign")
        self.clear()
        Study1Stage3MemoryExpDesign.construct(self)
        self.next_section("23_MemoryExpResults")
        self.clear()
        Study1Stage3MemoryExpResults.construct(self)


_Study1Stage1_2D = Study1Stage1_2D
_Study1Stage2 = Study1Stage2
_Study1Stage3 = Study1Stage3

_Study1Stage1Step1a = Study1Stage1Step1a
_Study1Stage1Step1b = Study1Stage1Step1b
_Study1Stage1Step2 = Study1Stage1Step2
_Study1Stage1Step2Showcase = Study1Stage1Step2Showcase
_Study1Stage1Step3 = Study1Stage1Step3
_Study1Stage1Step3Part1 = Study1Stage1Step3Part1
_Study1Stage1Step3Part2 = Study1Stage1Step3Part2
_Study1Stage1Step4 = Study1Stage1Step4
_Study1Stage1Step4Detailed = Study1Stage1Step4Detailed
_Study1Stage1Step4Interpolation = Study1Stage1Step4Interpolation
_Study1Stage1Step4Setup = Study1Stage1Step4Setup
_Study1Stage1Step5 = Study1Stage1Step5
_Study1Stage1Step5Deck = Study1Stage1Step5Deck
_Study1Stage1Step5Handoff = Study1Stage1Step5Handoff
_Study1Stage1Step5LPIPS = Study1Stage1Step5LPIPS
_Study1StimulusSetShowcase = Study1StimulusSetShowcase
_Study1Stage2TripletTask = Study1Stage2TripletTask
_Study1Stage2TripletTask2 = Study1Stage2TripletTask2
_Study1Stage2SimilarityJudgementsExamples = Study1Stage2SimilarityJudgementsExamples
_Study1Stage2OrdinalEmbedding = Study1Stage2OrdinalEmbedding
_Study1Stage2EmbeddingResult = Study1Stage2EmbeddingResult
_Study1Stage2ModelOrderToHeatmap = Study1Stage2ModelOrderToHeatmap
_Study1Stage3MemoryIntro = Study1Stage3MemoryIntro
_Study1Stage3MemoryExpResults = Study1Stage3MemoryExpResults

Study1Step1a = Study1Stage1Step1a
Study1Step1b = Study1Stage1Step1b
Study1Step2 = Study1Stage1Step2
Study1Step2Showcase = Study1Stage1Step2Showcase
Study1Step3 = Study1Stage1Step3
Study1Step3Part1 = Study1Stage1Step3Part1
Study1Step3Part2 = Study1Stage1Step3Part2
Study1Step4 = Study1Stage1Step4
Study1Step4Detailed = Study1Stage1Step4Detailed
Study1Step4Interpolation = Study1Stage1Step4Interpolation
Study1Step4Setup = Study1Stage1Step4Setup
Study1Step5Deck = Study1Stage1Step5Deck
Study1Step5Handoff = Study1Stage1Step5Handoff
Study1Step5LPIPS = Study1Stage1Step5LPIPS

BG = "#FFFFFF"
INK = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"

STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    REPO_ROOT / "assets" / "images" / "stimuli_reordered",
)
MEMORY_TASK_STIM_DIR = env_path(
    "MEMORY_TASK_STIM_DIR",
    REPO_ROOT / "assets" / "images" / "study1" / "memory_task",
)
STIM_INFO_CSV = env_path(
    "STIM_INFO_CSV",
    REPO_ROOT / "assets" / "data" / "study1" / "stimuli_info.csv",
)
FIXATION_PATH = str(REPO_ROOT / "assets" / "images" / "fixation_target.png")


def stimulus_path(prefix: str, idx: int) -> str:
    """Return the reordered-study stimulus path for one continuum image."""
    return str(STIM_DIR / f"{prefix}-{idx:02d}.png")


def memory_task_stimulus_path(name: str) -> str:
    """Return the path for a pre-rendered memory-task exemplar image."""
    return str(MEMORY_TASK_STIM_DIR / name)


def load_stimulus_lookup() -> dict[tuple[str, str], dict[str, str]]:
    """Load the study metadata rows keyed by `(category, object)`."""
    with STIM_INFO_CSV.open() as handle:
        rows = list(csv.DictReader(handle))
    return {(row["category"], row["object"]): row for row in rows}


def stimulus_image(
    prefix: str,
    idx: int,
    height: float,
    pos: tuple[float, float, float] | np.ndarray,
) -> ImageMobject:
    """Instantiate and position one continuum stimulus card."""
    image = ImageMobject(stimulus_path(prefix, idx))
    image.scale_to_fit_height(height)
    image.move_to(pos)
    return image


def fixation_on(
    mob: VMobject | np.ndarray,
    height: float = 0.18,
) -> ImageMobject:
    """Return a fixation target centered on a mobject or raw point."""
    fixation = ImageMobject(FIXATION_PATH)
    fixation.scale_to_fit_height(height)
    fixation.set_z_index(10)
    if isinstance(mob, np.ndarray):
        fixation.move_to(mob)
    else:
        fixation.move_to(mob.get_center())
    return fixation


_MEMORY_INTRO_SET_SPECS: tuple[tuple[str, str], ...] = (
    ("plant", "pine_med"),
    ("landscape_element", "lake_island"),
    ("building", "observatory"),
    ("item", "sofa"),
)

_MEMORY_INTRO_TOP_FOIL_MEAN = 0.56
_MEMORY_INTRO_TOP_TARGET_MEAN = 0.88
_MEMORY_INTRO_TOP_CRITERION_START_X = 0.75
_MEMORY_INTRO_TOP_CRITERION_LABEL_BUFF = 0.34
_MEMORY_INTRO_A_TOP_TARGET_MEAN = 0.634
_MEMORY_INTRO_A_TOP_TARGET_REPEATED_MEAN = 0.80
_MEMORY_INTRO_A_TOP_TARGET_LABEL_X = 1.10
_MEMORY_INTRO_SECOND_TARGET_MEAN = 0.80
_MEMORY_INTRO_SECOND_TARGET_REPEATED_MEAN = 1.25
_MEMORY_INTRO_SECOND_TARGET_LABEL_X = 1.39
_MEMORY_INTRO_B_CLAIM = r"Perceptual dissimilarity enhances discriminability"
_MEMORY_INTRO_C_CLAIM = r"Repeated exposure enhances memory discriminability"
_MEMORY_INTRO_TARGET_COLOR = "#5B7493"
_MEMORY_INTRO_FOIL_COLOR = "#B67A5D"
_MEMORY_INTRO_AXIS_COLOR = "#C7CDD4"
_MEMORY_INTRO_CRITERION_COLOR = "#6B7280"
_MEMORY_INTRO_REPETITION_COLOR = "#000000"
_MEMORY_INTRO_SIGNAL_SIGMA = 0.16
_MEMORY_INTRO_SIGNAL_PEAK = 0.92
_MEMORY_INTRO_SIGNAL_NARROW_SIGMA = 0.113
_MEMORY_INTRO_SIGNAL_FOIL_NARROW_SIGMA = 0.13
_MEMORY_INTRO_REPEATED_EXPOSURE_STEPS = (1.0 / 3.0, 2.0 / 3.0, 1.0)
_MEMORY_INTRO_REPETITION_LABEL_BUFF = 0.31
_MEMORY_INTRO_REPETITION_LABEL_RIGHT_SHIFT_FACTOR = 0.20
_MEMORY_INTRO_REPETITION_LABEL_PULSE_SCALE = 1.45
_MEMORY_INTRO_REPETITION_LABEL_TRANSITION_TIME = 0.30
_MEMORY_INTRO_REPETITION_FRAME_PULSE_WIDTH = 3.2
_MEMORY_INTRO_REPETITION_STEP_RUN_TIME = 2.40
_MEMORY_INTRO_REPETITION_STEP_PAUSE = 0.20
_MEMORY_INTRO_SIGNAL_X_RANGE = [0.0, 1.63]
_MEMORY_INTRO_CONTINUUM_CARD_HEIGHT = 0.56 * 1.45


def _normal_curve_intersection_x(
    *,
    left_mean: float,
    right_mean: float,
    left_sigma: float = _MEMORY_INTRO_SIGNAL_SIGMA,
    right_sigma: float = _MEMORY_INTRO_SIGNAL_SIGMA,
    left_peak: float = _MEMORY_INTRO_SIGNAL_PEAK,
    right_peak: float = _MEMORY_INTRO_SIGNAL_PEAK,
) -> float:
    """Return the x position where two Gaussian signal curves intersect.

    The helper assumes the foil distribution sits to the left of the target
    distribution and returns the midpoint when the curves are symmetric or when
    numerical root finding does not yield a real solution between the two means.
    """
    if np.isclose(left_sigma, right_sigma) and np.isclose(left_peak, right_peak):
        return 0.5 * (left_mean + right_mean)

    a = (1.0 / (2.0 * right_sigma**2)) - (1.0 / (2.0 * left_sigma**2))
    b = (left_mean / (left_sigma**2)) - (right_mean / (right_sigma**2))
    c = (
        (right_mean**2 / (2.0 * right_sigma**2))
        - (left_mean**2 / (2.0 * left_sigma**2))
        - np.log(right_peak / left_peak)
    )

    roots = np.roots([a, b, c])
    real_roots = [
        float(root.real)
        for root in roots
        if np.isclose(root.imag, 0.0) and left_mean <= root.real <= right_mean
    ]
    if not real_roots:
        return 0.5 * (left_mean + right_mean)
    midpoint = 0.5 * (left_mean + right_mean)
    return min(real_roots, key=lambda root: abs(root - midpoint))


def _validate_memory_intro_distribution_order(
    *,
    foil_mean: float,
    target_mean: float,
) -> None:
    """Assert the SDT target distribution remains to the right of the foil."""
    if target_mean <= foil_mean:
        raise ValueError(
            f"Target mean must be to the right of foil mean, got target_mean={target_mean:.3f}, "
            f"foil_mean={foil_mean:.3f}"
        )


def _build_memory_intro_plot(
    *,
    center: np.ndarray,
    foil_mean: float,
    target_mean: float,
    repeated_target_mean: float,
    foil_color: str,
    target_color: str,
    target_label_x: float,
    criterion_x: float,
    criterion_label_buff: float = 0.22,
    curve_stroke_width: float,
    area_opacity: float,
) -> dict[str, object]:
    """Build one static SDT plot with labels and styling for the memory intro.

    The returned mapping contains the plotted axes, the foil and target curves
    and filled areas, criterion line and label, supporting axis labels, and a
    pre-grouped `group` entry for callers that need to move the whole plot as a
    single visual unit.
    """
    _validate_memory_intro_distribution_order(
        foil_mean=foil_mean,
        target_mean=target_mean,
    )

    axes = Axes(
        x_range=[0.0, 1.85, 0.37],
        y_range=[0.0, 1.25, 0.5],
        x_length=5.10,
        y_length=2.25,
        axis_config={
            "color": _MEMORY_INTRO_AXIS_COLOR,
            "stroke_width": 1.5,
            "include_ticks": False,
            "include_tip": True,
            "tip_width": 0.09,
            "tip_height": 0.09,
        },
    )
    axes.move_to(center)

    foil_curve = axes.plot(
        lambda x: _MEMORY_INTRO_SIGNAL_PEAK
        * np.exp(-0.5 * ((x - foil_mean) / _MEMORY_INTRO_SIGNAL_SIGMA) ** 2),
        x_range=_MEMORY_INTRO_SIGNAL_X_RANGE,
        color=foil_color,
        stroke_width=curve_stroke_width,
    )
    target_curve = axes.plot(
        lambda x: _MEMORY_INTRO_SIGNAL_PEAK
        * np.exp(-0.5 * ((x - target_mean) / _MEMORY_INTRO_SIGNAL_SIGMA) ** 2),
        x_range=_MEMORY_INTRO_SIGNAL_X_RANGE,
        color=target_color,
        stroke_width=curve_stroke_width,
    )
    foil_area = axes.get_area(
        foil_curve,
        x_range=[_MEMORY_INTRO_SIGNAL_X_RANGE[0], _MEMORY_INTRO_SIGNAL_X_RANGE[1]],
        color=foil_color,
        opacity=area_opacity,
    )
    foil_area.set_stroke(width=0.0, opacity=0.0)
    target_area = axes.get_area(
        target_curve,
        x_range=[_MEMORY_INTRO_SIGNAL_X_RANGE[0], _MEMORY_INTRO_SIGNAL_X_RANGE[1]],
        color=target_color,
        opacity=area_opacity,
    )
    target_area.set_stroke(width=0.0, opacity=0.0)

    criterion_line = DashedLine(
        axes.c2p(criterion_x, 0.0),
        axes.c2p(criterion_x, 1.12),
        dash_length=0.10,
        dashed_ratio=0.55,
        color=_MEMORY_INTRO_CRITERION_COLOR,
        stroke_width=2.0,
    )
    criterion_label = Tex(r"Criterion", color=INK, font_size=22)
    criterion_label.next_to(criterion_line, UP, buff=criterion_label_buff)

    foil_curve_label = Tex(r"Foil\\signal", color=foil_color, font_size=18)
    foil_curve_label.move_to(axes.c2p(0.16, 0.84))
    target_curve_label = Tex(r"Target signal", color=target_color, font_size=18)
    target_curve_label.move_to(axes.c2p(min(target_label_x + 0.18, 1.58), 0.84))
    memory_strength_label = Tex(r"Memory strength", color=INK, font_size=22)
    memory_strength_label.next_to(axes.x_axis, DOWN, buff=0.20)
    probability_density_label = Tex(r"Probability density", color=INK, font_size=18)
    probability_density_label.rotate(np.pi / 2)
    probability_density_label.next_to(axes.y_axis, LEFT, buff=0.18)

    return {
        "axes": axes,
        "foil_curve": foil_curve,
        "target_curve": target_curve,
        "foil_area": foil_area,
        "target_area": target_area,
        "foil_mean": foil_mean,
        "target_mean": target_mean,
        "repeated_target_mean": repeated_target_mean,
        "foil_color": foil_color,
        "target_color": target_color,
        "curve_stroke_width": curve_stroke_width,
        "area_opacity": area_opacity,
        "criterion_top_y": 1.12,
        "criterion_line": criterion_line,
        "criterion_label": criterion_label,
        "criterion_label_buff": criterion_label_buff,
        "foil_curve_label": foil_curve_label,
        "target_curve_label": target_curve_label,
        "memory_strength_label": memory_strength_label,
        "probability_density_label": probability_density_label,
        "group": VGroup(
            axes,
            foil_area,
            target_area,
            foil_curve,
            target_curve,
            criterion_line,
            criterion_label,
            foil_curve_label,
            target_curve_label,
            memory_strength_label,
            probability_density_label,
        ),
    }


def _build_memory_intro_claim_title(
    text: str,
    *,
    anchor: np.ndarray,
) -> Tex:
    """Return a centered claim title that scales down to stay within frame bounds."""
    claim = Tex(
        text,
        color=INK,
        font_size=40,
    )
    max_width = config.frame_width - 1.2
    if claim.width > max_width:
        claim.scale_to_fit_width(max_width)
    claim.move_to(anchor)
    return claim


def _build_memory_intro_repeated_frame(
    *,
    target_examples: tuple[ImageMobject, ...],
) -> DashedVMobject:
    """Return the dashed frame used to highlight repeated target exemplars."""
    repeated_rect = SurroundingRectangle(
        Group(*target_examples),
        color=MGREY,
        stroke_width=1.8,
        buff=0.12,
        corner_radius=0.08,
    )
    repeated_rect.set_fill(opacity=0.0)
    dashed_frame = DashedVMobject(
        repeated_rect,
        num_dashes=54,
        dashed_ratio=0.58,
    )
    dashed_frame.set_stroke(
        color=MGREY,
        width=1.8,
        opacity=1.0,
    )
    dashed_frame.set_fill(opacity=0.0)
    dashed_frame.set_z_index(7)
    return dashed_frame


def _build_memory_intro_repetition_label(
    iteration: int,
    *,
    anchor_group: Group,
) -> Tex:
    """Return the repetition counter label positioned above the stacked plots."""
    label = Tex(
        rf"Repetition {iteration}",
        color=_MEMORY_INTRO_REPETITION_COLOR,
        font_size=22,
    )
    label.next_to(anchor_group, UP, buff=_MEMORY_INTRO_REPETITION_LABEL_BUFF)
    label.shift(
        RIGHT
        * anchor_group.width
        * _MEMORY_INTRO_REPETITION_LABEL_RIGHT_SHIFT_FACTOR
    )
    label.set_z_index(7)
    return label


def _memory_intro_signal_peak_for_sigma(sigma: float) -> float:
    """Scale the Gaussian peak so narrower signals retain comparable total mass."""
    return _MEMORY_INTRO_SIGNAL_PEAK * (_MEMORY_INTRO_SIGNAL_SIGMA / sigma)


def _build_memory_intro_dynamic_plot(
    plot: dict[str, object],
    *,
    repetition_tracker: ValueTracker,
) -> dict[str, object]:
    """Turn a static SDT plot description into a repetition-driven animated one.

    `repetition_tracker` is expected to move from 0.0 to 1.0 across the repeated
    exposure beats. As it advances, the foil and target distributions narrow,
    the target mean shifts rightward toward `repeated_target_mean`, and the
    criterion is recomputed from the current overlap point between the two
    signals. The returned mapping mirrors the static plot contract but swaps in
    live-updating curves, filled areas, and criterion elements plus a grouped
    `group` entry for whole-plot placement.
    """
    axes = plot["axes"]
    foil_color = plot["foil_color"]
    target_color = plot["target_color"]
    curve_stroke_width = max(
        mob.get_stroke_width()
        for mob in plot["target_curve"].family_members_with_points()
        + plot["foil_curve"].family_members_with_points()
    )
    area_opacity = max(
        mob.get_fill_opacity()
        for mob in plot["target_area"].family_members_with_points()
        + plot["foil_area"].family_members_with_points()
    )

    def current_foil_sigma() -> float:
        """Interpolate foil narrowing as repeated exposure increases."""
        progress = repetition_tracker.get_value()
        return _MEMORY_INTRO_SIGNAL_SIGMA + (
            _MEMORY_INTRO_SIGNAL_FOIL_NARROW_SIGMA - _MEMORY_INTRO_SIGNAL_SIGMA
        ) * progress

    def current_target_sigma() -> float:
        """Interpolate target narrowing as repeated exposure increases."""
        progress = repetition_tracker.get_value()
        return _MEMORY_INTRO_SIGNAL_SIGMA + (
            _MEMORY_INTRO_SIGNAL_NARROW_SIGMA - _MEMORY_INTRO_SIGNAL_SIGMA
        ) * progress

    def current_foil_mean() -> float:
        """Keep the foil mean fixed while only the target distribution shifts."""
        return plot["foil_mean"]

    def current_target_mean() -> float:
        """Move the target mean toward the repeated-exposure end state."""
        return plot["target_mean"] + (
            plot["repeated_target_mean"] - plot["target_mean"]
        ) * repetition_tracker.get_value()

    def current_criterion_x() -> float:
        """Recompute the criterion from the current foil/target overlap."""
        foil_sigma = current_foil_sigma()
        target_sigma = current_target_sigma()
        foil_mean = current_foil_mean()
        target_mean = current_target_mean()
        _validate_memory_intro_distribution_order(
            foil_mean=foil_mean,
            target_mean=target_mean,
        )
        return _normal_curve_intersection_x(
            left_mean=foil_mean,
            right_mean=target_mean,
            left_sigma=foil_sigma,
            right_sigma=target_sigma,
            left_peak=_memory_intro_signal_peak_for_sigma(foil_sigma),
            right_peak=_memory_intro_signal_peak_for_sigma(target_sigma),
        )

    def build_curve(mean: float, sigma: float, color: str) -> VMobject:
        """Construct a single Gaussian curve with the current dynamic parameters."""
        peak = _memory_intro_signal_peak_for_sigma(sigma)
        return axes.plot(
            lambda x: peak * np.exp(-0.5 * ((x - mean) / sigma) ** 2),
            x_range=_MEMORY_INTRO_SIGNAL_X_RANGE,
            color=color,
            stroke_width=curve_stroke_width,
        )

    def build_area(curve: VMobject, color: str) -> VMobject:
        """Return the filled area underneath one dynamic signal curve."""
        area = axes.get_area(
            curve,
            x_range=[_MEMORY_INTRO_SIGNAL_X_RANGE[0], _MEMORY_INTRO_SIGNAL_X_RANGE[1]],
            color=color,
            opacity=area_opacity,
        )
        area.set_stroke(width=0.0, opacity=0.0)
        return area

    # Keep the plot synchronized to the tracker rather than creating a separate
    # set of manually stepped assets for each repetition state.
    foil_curve = always_redraw(
        lambda: build_curve(current_foil_mean(), current_foil_sigma(), foil_color)
    )
    target_curve = always_redraw(
        lambda: build_curve(current_target_mean(), current_target_sigma(), target_color)
    )
    foil_area = always_redraw(
        lambda: build_area(build_curve(current_foil_mean(), current_foil_sigma(), foil_color), foil_color)
    )
    target_area = always_redraw(
        lambda: build_area(build_curve(current_target_mean(), current_target_sigma(), target_color), target_color)
    )
    criterion_line = DashedLine(
        axes.c2p(current_criterion_x(), 0.0),
        axes.c2p(current_criterion_x(), plot["criterion_top_y"]),
        dash_length=0.10,
        dashed_ratio=0.55,
        color=_MEMORY_INTRO_CRITERION_COLOR,
        stroke_width=2.0,
    )
    # The criterion moves with the current intersection so the decision boundary
    # continues to reflect the changing overlap between foil and target signals.
    criterion_line.add_updater(
        lambda mob: mob.put_start_and_end_on(
            axes.c2p(current_criterion_x(), 0.0),
            axes.c2p(current_criterion_x(), plot["criterion_top_y"]),
        )
    )

    criterion_label = plot["criterion_label"].copy()
    criterion_label.add_updater(
        lambda mob: mob.next_to(
            criterion_line,
            UP,
            buff=plot["criterion_label_buff"] + 0.10 * repetition_tracker.get_value(),
        )
    )
    criterion_line.update()
    criterion_label.update()

    return {
        "foil_curve": foil_curve,
        "target_curve": target_curve,
        "foil_area": foil_area,
        "target_area": target_area,
        "criterion_line": criterion_line,
        "criterion_label": criterion_label,
        "group": VGroup(
            axes,
            foil_area,
            target_area,
            foil_curve,
            target_curve,
            criterion_line,
            criterion_label,
            plot["foil_curve_label"],
            plot["target_curve_label"],
            plot["memory_strength_label"],
            plot["probability_density_label"],
        ),
    }


def _build_memory_intro_core(
    *,
    top_target_mean: float = _MEMORY_INTRO_TOP_TARGET_MEAN,
    top_target_label_x: float = 1.25,
    top_criterion_x: float = _MEMORY_INTRO_TOP_CRITERION_START_X,
) -> dict[str, object]:
    """Build the shared starting layout for the Stage 3 memory-intro sequence.

    The returned context bundles the title and question text, example target and
    foil stimuli with their landing positions, the top SDT plot, and the four
    continuum rows that later collapse into target-versus-foil summaries.
    """
    title = Tex(
        r"Memory validation task",
        color=INK,
        font_size=40,
    ).move_to(ORIGIN)
    title_top_target = title.copy().to_edge(UP, buff=0.28)

    question = VGroup(
        Tex(
            r"Does proximity along the perceptual continua",
            color=INK,
            font_size=26,
        ),
        Tex(
            r"of our image sets predict memory performance?",
            color=INK,
            font_size=26,
        ),
    ).arrange(DOWN, buff=0.10).next_to(title_top_target, DOWN, buff=0.24)

    lookup = load_stimulus_lookup()
    question_bottom_y = question.get_bottom()[1]
    row_spacing = 1.05
    bottom_margin_y = -config.frame_height / 2 + 0.55
    row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
    row_y_positions = [
        row_block_center_y + row_spacing * offset
        for offset in (1.5, 0.5, -0.5, -1.5)
    ]
    left_column_center_x = -config.frame_width / 4
    panel_center_x = 0.0
    selected_spacing = 1.05
    selected_xs = [
        panel_center_x + selected_spacing * offset
        for offset in (-1.5, -0.5, 0.5, 1.5)
    ]

    example_side_offset = 1.55
    example_image_height = 1.95 * 1.30
    example_center = np.array([0.0, row_block_center_y, 0.0])
    example_target = ImageMobject(memory_task_stimulus_path("LAN-MOU-T00.png"))
    example_target.scale_to_fit_height(example_image_height)
    example_target.move_to(example_center + LEFT * example_side_offset)
    example_target.set_z_index(5)

    example_foil = ImageMobject(memory_task_stimulus_path("LAN-MOU-D01.png"))
    example_foil.scale_to_fit_height(example_image_height)
    example_foil.move_to(example_center + RIGHT * example_side_offset)
    example_foil.set_z_index(4)

    example_left_row_center = np.array([left_column_center_x, row_block_center_y, 0.0])
    example_target_left_pos = example_left_row_center + LEFT * example_side_offset
    example_foil_left_pos = example_left_row_center + RIGHT * example_side_offset

    example_target_label = Tex(r"Target", color=_MEMORY_INTRO_TARGET_COLOR, font_size=26)
    example_target_label.move_to(
        example_target_left_pos + UP * (example_image_height / 2 + 0.28)
    )
    example_target_label.set_z_index(6)
    example_foil_label = Tex(r"Foil", color=_MEMORY_INTRO_FOIL_COLOR, font_size=26)
    example_foil_label.move_to(
        example_foil_left_pos + UP * (example_image_height / 2 + 0.28)
    )
    example_foil_label.set_z_index(6)
    plot = _build_memory_intro_plot(
        center=np.array([3.48, row_block_center_y - 0.05, 0.0]),
        foil_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
        target_mean=top_target_mean,
        repeated_target_mean=_MEMORY_INTRO_A_TOP_TARGET_REPEATED_MEAN,
        foil_color=_MEMORY_INTRO_FOIL_COLOR,
        target_color=_MEMORY_INTRO_TARGET_COLOR,
        target_label_x=top_target_label_x,
        criterion_x=top_criterion_x,
        criterion_label_buff=_MEMORY_INTRO_TOP_CRITERION_LABEL_BUFF,
        curve_stroke_width=4.0,
        area_opacity=0.20,
    )

    panels = []
    for (category, obj), row_y in zip(_MEMORY_INTRO_SET_SPECS, row_y_positions):
        row = lookup[(category, obj)]
        prefix = f"{category}_{obj}"
        cards = [
            stimulus_image(
                prefix,
                idx,
                _MEMORY_INTRO_CONTINUUM_CARD_HEIGHT,
                (0.0, 0.0, 0.0),
            )
            for idx in range(10)
        ]
        row_group = Group(*cards).arrange(RIGHT, buff=0.09).move_to([panel_center_x, row_y, 0.0])
        selected_indices = [
            int(row["target_position"]),
            int(row["distractor_1_position"]),
            int(row["distractor_2_position"]),
            int(row["distractor_3_position"]),
        ]
        panels.append(
            {
                "row_group": row_group,
                "cards": cards,
                "selected_indices": selected_indices,
                "row_y": row_y,
                "spec": (category, obj),
            }
        )

    return {
        "title": title,
        "title_top_target": title_top_target,
        "question": question,
        "lookup": lookup,
        "row_block_center_y": row_block_center_y,
        "row_y_positions": row_y_positions,
        "left_column_center_x": left_column_center_x,
        "example_side_offset": example_side_offset,
        "example_image_height": example_image_height,
        "example_target": example_target,
        "example_foil": example_foil,
        "example_target_left_pos": example_target_left_pos,
        "example_foil_left_pos": example_foil_left_pos,
        "example_target_label": example_target_label,
        "example_foil_label": example_foil_label,
        "selected_xs": selected_xs,
        "plot": plot,
        "panels": panels,
    }


def _set_memory_intro_a_rest_state(ctx: dict[str, object]) -> None:
    """Mutate the intro-A context into the resting single-plot presentation state."""
    ctx["title"].move_to(ctx["title_top_target"])
    ctx["example_target"].move_to(ctx["example_target_left_pos"]).set_opacity(1.0)
    ctx["example_foil"].move_to(ctx["example_foil_left_pos"]).set_opacity(1.0)

    plot = ctx["plot"]
    plot["target_curve"].set_stroke(width=2.2, opacity=1.0)
    plot["foil_curve"].set_stroke(width=2.2, opacity=1.0)
    plot["target_area"].set_fill(opacity=0.16)
    plot["foil_area"].set_fill(opacity=0.16)
    plot["target_curve_label"].set_opacity(1.0)
    plot["foil_curve_label"].set_opacity(1.0)


def _set_memory_intro_b_end_state(
    ctx: dict[str, object],
    followup: dict[str, object],
) -> None:
    """Apply the stacked two-example end state shared by Intro B and later scenes."""
    _set_memory_intro_a_rest_state(ctx)
    ctx["question"].shift(followup["subtitle_shift"])
    ctx["example_target"].move_to(followup["upper_example_target_pos"])
    ctx["example_foil"].move_to(followup["upper_example_foil_pos"])
    ctx["example_target_label"].move_to(followup["upper_target_label_pos"])
    ctx["example_foil_label"].move_to(followup["upper_foil_label_pos"])
    ctx["plot"]["group"].shift(followup["upper_plot_shift"])
    ctx["plot"]["memory_strength_label"].move_to(
        followup["second_plot"]["memory_strength_label"].get_center()
    )
    followup["second_plot"]["memory_strength_label"].set_opacity(0.0)


def _build_memory_intro_b_followup(ctx: dict[str, object]) -> dict[str, object]:
    """Build the second-example assets and offsets used to stack Intro B vertically."""
    upper_row_center_y = ctx["row_block_center_y"] + 1.20
    subtitle_shift = UP * (0.10 * (upper_row_center_y - ctx["row_block_center_y"]))
    upper_example_center = np.array([ctx["left_column_center_x"], upper_row_center_y, 0.0])
    upper_example_target_pos = upper_example_center + LEFT * ctx["example_side_offset"]
    upper_example_foil_pos = upper_example_center + RIGHT * ctx["example_side_offset"]
    upper_label_buff = 0.28
    upper_target_label_pos = upper_example_target_pos + UP * (ctx["example_image_height"] / 2 + upper_label_buff)
    upper_foil_label_pos = upper_example_foil_pos + UP * (ctx["example_image_height"] / 2 + upper_label_buff)
    upper_plot_center = np.array([3.48, upper_row_center_y - 0.05, 0.0])
    upper_plot_shift = upper_plot_center - ctx["plot"]["axes"].get_center()

    second_row_center_y = ctx["row_block_center_y"] - (1.50 * 1.10)
    second_example_center = np.array([ctx["left_column_center_x"], second_row_center_y, 0.0])
    second_example_target_pos = second_example_center + LEFT * ctx["example_side_offset"]
    second_example_foil_pos = second_example_center + RIGHT * ctx["example_side_offset"]
    second_plot_center = np.array([3.48, second_row_center_y - 0.05, 0.0])

    second_example_target = ImageMobject(memory_task_stimulus_path("LAN-MOU-T00.png"))
    second_example_target.scale_to_fit_height(ctx["example_image_height"])
    second_example_target.move_to(second_example_target_pos)
    second_example_target.set_z_index(5)

    second_example_foil = ImageMobject(memory_task_stimulus_path("LAN-MOU-D03.png"))
    second_example_foil.scale_to_fit_height(ctx["example_image_height"])
    second_example_foil.move_to(second_example_foil_pos)
    second_example_foil.set_z_index(4)

    second_plot = _build_memory_intro_plot(
        center=second_plot_center,
        foil_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
        target_mean=_MEMORY_INTRO_SECOND_TARGET_MEAN,
        repeated_target_mean=_MEMORY_INTRO_SECOND_TARGET_REPEATED_MEAN,
        foil_color=_MEMORY_INTRO_FOIL_COLOR,
        target_color=_MEMORY_INTRO_TARGET_COLOR,
        target_label_x=_MEMORY_INTRO_SECOND_TARGET_LABEL_X,
        criterion_x=0.5 * (
            _MEMORY_INTRO_TOP_FOIL_MEAN + _MEMORY_INTRO_SECOND_TARGET_MEAN
        ),
        curve_stroke_width=2.2,
        area_opacity=0.16,
    )

    return {
        "subtitle_shift": subtitle_shift,
        "upper_example_target_pos": upper_example_target_pos,
        "upper_example_foil_pos": upper_example_foil_pos,
        "upper_target_label_pos": upper_target_label_pos,
        "upper_foil_label_pos": upper_foil_label_pos,
        "upper_plot_shift": upper_plot_shift,
        "second_example_target": second_example_target,
        "second_example_foil": second_example_foil,
        "second_plot": second_plot,
    }


def _build_memory_intro_c_overlay(ctx: dict[str, object]) -> dict[str, object]:
    """Build the collapsed target/foil overlay derived from the continuum rows.

    The returned mapping contains copied summary cards, continuation marks for
    the final row, lookup handles for specific cards reused later, and the
    target-versus-foil framing elements shown once the continua collapse.
    """
    collapsed_cards = []
    source_cards = []
    continuation_marks = []
    selected_card_lookup = {}

    for panel in ctx["panels"]:
        category, obj = panel["spec"]
        for col_idx, selected_idx in enumerate(panel["selected_indices"]):
            source_card = panel["cards"][selected_idx]
            collapsed_card = source_card.copy()
            collapsed_card.move_to(np.array([ctx["selected_xs"][col_idx], panel["row_y"], 0.0]))
            collapsed_card.set_z_index(7)
            collapsed_cards.append(collapsed_card)
            source_cards.append(source_card)
            selected_card_lookup[(category, obj, col_idx)] = collapsed_card

            if obj == "sofa":
                dot = MathTex(r"\vdots", color=MGREY, font_size=24).next_to(
                    collapsed_card,
                    DOWN,
                    buff=0.19,
                )
                dot.set_z_index(7)
                continuation_marks.append(dot)

    continuation_group = VGroup(*continuation_marks)
    target_cards = Group(*collapsed_cards[0::4])
    foil_cards = Group(
        *[
            collapsed_cards[idx]
            for idx in range(len(collapsed_cards))
            if idx % 4 != 0
        ]
    )

    target_rect = SurroundingRectangle(
        Group(target_cards, continuation_group[0]),
        color=MGREY,
        stroke_width=1.5,
        buff=0.10,
        corner_radius=0.06,
    )
    foil_rect = SurroundingRectangle(
        Group(foil_cards, *continuation_group[1:]),
        color=MGREY,
        stroke_width=1.5,
        buff=0.10,
        corner_radius=0.06,
    )
    target_label = Tex(r"Targets", color=INK, font_size=24).next_to(
        target_rect,
        UP,
        buff=0.12,
    )
    foil_label = Tex(r"Foils", color=INK, font_size=24).next_to(
        foil_rect,
        UP,
        buff=0.12,
    )
    arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
    dissimilar_arrow = Arrow(
        start=np.array([target_rect.get_center()[0] - 0.20, arrow_y, 0.0]),
        end=np.array([foil_rect.get_right()[0] - 0.10, arrow_y, 0.0]),
        buff=0.0,
        stroke_width=2.0,
        color=MGREY,
        tip_length=0.18,
        max_stroke_width_to_length_ratio=8,
        max_tip_length_to_length_ratio=0.10,
    )
    dissimilar_text = Tex(
        r"More dissimilar",
        color=INK,
        font_size=22,
    ).next_to(dissimilar_arrow, DOWN, buff=0.10)

    return {
        "source_cards": source_cards,
        "collapsed_cards": collapsed_cards,
        "selected_card_lookup": selected_card_lookup,
        "continuation_marks": continuation_group,
        "target_rect": target_rect,
        "foil_rect": foil_rect,
        "target_label": target_label,
        "foil_label": foil_label,
        "dissimilar_arrow": dissimilar_arrow,
        "dissimilar_text": dissimilar_text,
    }


def _build_memory_foil_difficulty_annotations(
    collapsed_cards: list[VMobject],
    continuation_marks: VGroup,
) -> dict[str, object]:
    """Build the hard/medium/easy column annotations for the foil summary rows."""
    foil_cols = [
        Group(
            *[collapsed_cards[4 * row_idx + col_idx] for row_idx in range(4)],
            continuation_marks[col_idx],
        )
        for col_idx in (1, 2, 3)
    ]
    annotations = []
    for diff_label, color, col_group in [
        ("Hard", "#443983", foil_cols[0]),
        ("Medium", "#31688E", foil_cols[1]),
        ("Easy", "#35B779", foil_cols[2]),
    ]:
        col_rect = SurroundingRectangle(
            col_group,
            color=color,
            stroke_width=1.8,
            buff=0.08,
            corner_radius=0.06,
        )
        lbl = Tex(diff_label, color=color, font_size=22).next_to(col_group, DOWN, buff=0.18)
        annotations.append(VGroup(col_rect, lbl))

    return {
        "groups": foil_cols,
        "annotations": VGroup(*annotations),
    }


def _build_memory_exp_stats_block(
    final_stage_labels: VGroup,
    progress_arrow: VMobject,
    time_label: VMobject,
) -> VGroup:
    """Return the participant/block summary aligned beneath the final stage strip."""
    stats_block = VGroup(
        Tex(r"$N = 240$", color=INK, font_size=22),
        Tex(
            r"6 blocks $\cdot$ half repeated, half new targets per block",
            color=INK,
            font_size=20,
        ),
    ).arrange(DOWN, buff=0.12)
    timeline_bottom = min(
        final_stage_labels.get_bottom()[1],
        time_label.get_bottom()[1],
        progress_arrow.get_bottom()[1],
    )
    stats_block.align_to(final_stage_labels, LEFT)
    stats_block.set_y(timeline_bottom - stats_block.height / 2 - 0.32)
    return stats_block


def _memory_dissimilarity_shift_below_difficulty(
    dissimilar_arrow: VMobject,
    dissimilar_text: VMobject,
    difficulty_annotations: VGroup,
) -> np.ndarray:
    """Return the vertical shift needed to park the dissimilarity cue below labels."""
    desired_arrow_y = difficulty_annotations.get_bottom()[1] - 0.14
    return UP * (desired_arrow_y - dissimilar_arrow.get_center()[1])


def _build_memory_intro_c_end_state() -> dict[str, object]:
    """Assemble the frozen repeated-exposure state reused by later Stage 3 scenes."""
    criterion_intersection_x = _normal_curve_intersection_x(
        left_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
        right_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
    )
    ctx = _build_memory_intro_core(
        top_target_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
        top_target_label_x=_MEMORY_INTRO_A_TOP_TARGET_LABEL_X,
        top_criterion_x=criterion_intersection_x,
    )
    followup = _build_memory_intro_b_followup(ctx)
    overlay = _build_memory_intro_c_overlay(ctx)
    _set_memory_intro_b_end_state(ctx, followup)
    return {
        "ctx": ctx,
        "followup": followup,
        "overlay": overlay,
    }


class Study1Stage3MemoryIntroA(Scene):
    """Introduce the memory task and resolve it into a single SDT-style schematic."""

    def construct(self) -> None:
        """Animate the title, exemplar alternation, and first annotated SDT plot."""
        self.camera.background_color = BG
        criterion_intersection_x = _normal_curve_intersection_x(
            left_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
            right_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
        )
        ctx = _build_memory_intro_core(
            top_target_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
            top_target_label_x=_MEMORY_INTRO_A_TOP_TARGET_LABEL_X,
            top_criterion_x=criterion_intersection_x,
        )
        plot = ctx["plot"]

        self.play(Write(ctx["title"]), run_time=0.70)
        self.wait(0.15)
        self.play(ctx["title"].animate.move_to(ctx["title_top_target"]), run_time=0.55)
        self.play(FadeIn(ctx["question"], shift=UP * 0.12), run_time=0.60)
        self.wait(0.60)

        self.play(
            FadeIn(ctx["example_target"], scale=0.96),
            FadeIn(ctx["example_foil"], scale=0.96),
            run_time=0.70,
        )
        self.wait(2.00)
        self.play(
            ctx["example_target"].animate.move_to(np.array([0.0, ctx["row_block_center_y"], 0.0])),
            ctx["example_foil"].animate.move_to(np.array([0.0, ctx["row_block_center_y"], 0.0])),
            run_time=0.70,
        )
        self.wait(2.00)

        target_visible = True

        def swap_example(delay: float) -> None:
            """Toggle the overlaid exemplar to simulate alternating target visibility."""
            nonlocal target_visible
            target_visible = not target_visible
            self.play(
                ctx["example_target"].animate.set_opacity(1.0 if target_visible else 0.0),
                run_time=0.10,
                rate_func=linear,
            )
            self.wait(delay)

        for _ in range(8):
            swap_example(0.20)
        self.wait(2.00)

        self.play(
            ctx["example_target"].animate.move_to(ctx["example_target_left_pos"]).set_opacity(1.0),
            ctx["example_foil"].animate.move_to(ctx["example_foil_left_pos"]).set_opacity(1.0),
            run_time=0.65,
            rate_func=smooth,
        )
        self.play(
            FadeIn(ctx["example_target_label"], shift=UP * 0.10),
            FadeIn(ctx["example_foil_label"], shift=UP * 0.10),
            LaggedStart(
                Create(plot["axes"]),
                FadeIn(plot["foil_area"]),
                FadeIn(plot["target_area"]),
                Create(plot["foil_curve"]),
                Create(plot["target_curve"]),
                FadeIn(plot["foil_curve_label"], shift=UP * 0.08),
                FadeIn(plot["target_curve_label"], shift=UP * 0.08),
                FadeIn(plot["memory_strength_label"], shift=UP * 0.08),
                FadeIn(plot["probability_density_label"], shift=RIGHT * 0.08),
                lag_ratio=0.12,
            ),
            run_time=1.30,
        )
        self.play(
            Create(plot["criterion_line"]),
            FadeIn(plot["criterion_label"], shift=UP * 0.08),
            run_time=0.55,
        )
        self.play(
            ctx["example_target_label"].animate.scale(1.18),
            plot["target_curve"].animate.set_stroke(width=4.8, opacity=1.0),
            plot["target_area"].animate.set_fill(opacity=0.34),
            ctx["example_foil_label"].animate.set_opacity(0.35),
            plot["foil_curve"].animate.set_stroke(opacity=0.28),
            plot["foil_area"].animate.set_fill(opacity=0.08),
            plot["target_curve_label"].animate.set_opacity(0.35),
            plot["foil_curve_label"].animate.set_opacity(0.25),
            run_time=0.80,
        )
        self.wait(0.40)
        self.play(
            ctx["example_target_label"].animate.scale(1 / 1.18),
            plot["target_curve"].animate.set_stroke(width=2.2, opacity=0.28),
            plot["target_area"].animate.set_fill(opacity=0.08),
            ctx["example_target_label"].animate.set_opacity(0.35),
            ctx["example_foil_label"].animate.set_opacity(1.0),
            plot["foil_curve"].animate.set_stroke(width=2.2, opacity=0.28),
            plot["foil_area"].animate.set_fill(opacity=0.08),
            plot["target_curve_label"].animate.set_opacity(0.25),
            plot["foil_curve_label"].animate.set_opacity(0.35),
            run_time=0.30,
        )
        self.play(
            ctx["example_foil_label"].animate.scale(1.18),
            plot["foil_curve"].animate.set_stroke(width=4.8, opacity=1.0),
            plot["foil_area"].animate.set_fill(opacity=0.34),
            run_time=0.85,
        )
        self.wait(0.40)
        self.play(
            ctx["example_foil_label"].animate.scale(1 / 1.18),
            ctx["example_target_label"].animate.set_opacity(1.0),
            plot["target_curve"].animate.set_stroke(width=2.2, opacity=1.0),
            plot["target_area"].animate.set_fill(opacity=0.16),
            ctx["example_foil_label"].animate.set_opacity(1.0),
            plot["foil_curve"].animate.set_stroke(width=2.2, opacity=1.0),
            plot["foil_area"].animate.set_fill(opacity=0.16),
            plot["target_curve_label"].animate.set_opacity(1.0),
            plot["foil_curve_label"].animate.set_opacity(1.0),
            run_time=0.85,
        )
        self.wait(1.00)


class Study1Stage3MemoryIntroB(Scene):
    """Stack a second SDT example to make the dissimilarity comparison explicit."""

    def construct(self) -> None:
        """Transform Intro A into a two-example layout with a second stacked plot."""
        self.camera.background_color = BG
        criterion_intersection_x = _normal_curve_intersection_x(
            left_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
            right_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
        )
        ctx = _build_memory_intro_core(
            top_target_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
            top_target_label_x=_MEMORY_INTRO_A_TOP_TARGET_LABEL_X,
            top_criterion_x=criterion_intersection_x,
        )
        followup = _build_memory_intro_b_followup(ctx)
        _set_memory_intro_a_rest_state(ctx)

        self.add(
            ctx["title"],
            ctx["question"],
            ctx["example_target"],
            ctx["example_foil"],
            ctx["example_target_label"],
            ctx["example_foil_label"],
            ctx["plot"]["group"],
        )

        claim_title = _build_memory_intro_claim_title(
            _MEMORY_INTRO_B_CLAIM,
            anchor=ctx["title_top_target"].get_center(),
        )

        self.wait(0.40)
        self.play(
            FadeOut(ctx["title"], shift=UP * 0.06),
            FadeOut(ctx["question"], shift=UP * 0.06),
            FadeIn(claim_title, shift=UP * 0.06),
            run_time=0.65,
        )
        self.play(
            ctx["example_target"].animate.move_to(followup["upper_example_target_pos"]),
            ctx["example_foil"].animate.move_to(followup["upper_example_foil_pos"]),
            ctx["example_target_label"].animate.move_to(followup["upper_target_label_pos"]),
            ctx["example_foil_label"].animate.move_to(followup["upper_foil_label_pos"]),
            ctx["plot"]["group"].animate.shift(followup["upper_plot_shift"]),
            run_time=1.05,
            rate_func=smooth,
        )
        self.wait(0.25)
        self.play(
            FadeIn(followup["second_example_target"], scale=0.96),
            FadeIn(followup["second_example_foil"], scale=0.96),
            run_time=0.70,
        )
        self.wait(0.25)
        self.play(
            LaggedStart(
                Create(followup["second_plot"]["axes"]),
                FadeIn(followup["second_plot"]["foil_area"]),
                FadeIn(followup["second_plot"]["target_area"]),
                Create(followup["second_plot"]["foil_curve"]),
                Create(followup["second_plot"]["target_curve"]),
                Create(followup["second_plot"]["criterion_line"]),
                FadeIn(followup["second_plot"]["criterion_label"], shift=UP * 0.08),
                FadeIn(followup["second_plot"]["foil_curve_label"], shift=UP * 0.08),
                FadeIn(followup["second_plot"]["target_curve_label"], shift=UP * 0.08),
                FadeIn(followup["second_plot"]["probability_density_label"], shift=RIGHT * 0.08),
                lag_ratio=0.10,
            ),
            ctx["plot"]["memory_strength_label"].animate.move_to(
                followup["second_plot"]["memory_strength_label"].get_center()
            ),
            run_time=1.35,
        )
        self.wait(1.10)


class Study1Stage3MemoryIntroC(Scene):
    """Convert the two-example layout into a repeated-exposure discriminability story."""

    def construct(self) -> None:
        """Animate repeated exposure so both plots sharpen and separate over time."""
        self.camera.background_color = BG
        end_state = _build_memory_intro_c_end_state()
        ctx = end_state["ctx"]
        followup = end_state["followup"]
        repetition_tracker = ValueTracker(0.0)
        top_plot = _build_memory_intro_dynamic_plot(
            ctx["plot"],
            repetition_tracker=repetition_tracker,
        )
        second_plot = _build_memory_intro_dynamic_plot(
            followup["second_plot"],
            repetition_tracker=repetition_tracker,
        )
        dissimilarity_claim = _build_memory_intro_claim_title(
            _MEMORY_INTRO_B_CLAIM,
            anchor=ctx["title_top_target"].get_center(),
        )
        repetition_claim = _build_memory_intro_claim_title(
            _MEMORY_INTRO_C_CLAIM,
            anchor=ctx["title_top_target"].get_center(),
        )
        repeated_frame = _build_memory_intro_repeated_frame(
            target_examples=(ctx["example_target"], followup["second_example_target"]),
        )
        repetition_label_anchor = Group(ctx["plot"]["axes"], followup["second_plot"]["axes"])
        repetition_index_tracker = ValueTracker(1.0)
        repetition_label_pulse_tracker = ValueTracker(0.0)
        repetition_label_opacity_tracker = ValueTracker(0.0)
        repetition_label = always_redraw(
            lambda: _build_memory_intro_repetition_label(
                max(1, int(round(repetition_index_tracker.get_value()))),
                anchor_group=repetition_label_anchor,
            )
            .scale(
                1.0
                + (_MEMORY_INTRO_REPETITION_LABEL_PULSE_SCALE - 1.0)
                * repetition_label_pulse_tracker.get_value()
            )
            .set_opacity(repetition_label_opacity_tracker.get_value())
        )

        self.add(
            dissimilarity_claim,
            ctx["example_target"],
            ctx["example_foil"],
            ctx["example_target_label"],
            ctx["example_foil_label"],
            top_plot["group"],
            followup["second_example_target"],
            followup["second_example_foil"],
            second_plot["group"],
            repetition_label,
        )
        self.wait(0.40)
        self.play(
            FadeOut(dissimilarity_claim, shift=UP * 0.06),
            FadeIn(repetition_claim, shift=UP * 0.06),
            run_time=0.60,
        )
        self.wait(2.00)
        self.play(
            Create(repeated_frame),
            run_time=0.60,
        )
        self.wait(0.20)
        for pulse_idx, next_stage in enumerate(_MEMORY_INTRO_REPEATED_EXPOSURE_STEPS):
            repetition_index_tracker.set_value(float(pulse_idx + 1))
            step_animations = [repetition_tracker.animate.set_value(next_stage)]
            step_animations.append(
                repeated_frame.animate(rate_func=there_and_back).set_stroke(
                    width=_MEMORY_INTRO_REPETITION_FRAME_PULSE_WIDTH
                )
            )
            step_animations.append(
                repetition_label_pulse_tracker.animate(rate_func=there_and_back).set_value(1.0)
            )
            if pulse_idx == 0:
                step_animations.append(repetition_label_opacity_tracker.animate.set_value(1.0))
            self.play(
                *step_animations,
                run_time=_MEMORY_INTRO_REPETITION_STEP_RUN_TIME,
            )
            repetition_label_pulse_tracker.set_value(0.0)
            if pulse_idx < len(_MEMORY_INTRO_REPEATED_EXPOSURE_STEPS) - 1:
                self.wait(_MEMORY_INTRO_REPETITION_STEP_PAUSE)
        self.wait(0.40)


class Study1Stage3MemoryIntroD(Scene):
    """Collapse the continuum rows into grouped targets and graded foil columns."""

    def construct(self) -> None:
        """Replace the SDT view with the continuum summary and foil-difficulty grouping."""
        self.camera.background_color = BG
        end_state = _build_memory_intro_c_end_state()
        ctx = end_state["ctx"]
        followup = end_state["followup"]
        overlay = end_state["overlay"]
        repetition_tracker = ValueTracker(1.0)
        top_plot = _build_memory_intro_dynamic_plot(
            ctx["plot"],
            repetition_tracker=repetition_tracker,
        )
        second_plot = _build_memory_intro_dynamic_plot(
            followup["second_plot"],
            repetition_tracker=repetition_tracker,
        )
        repetition_claim = _build_memory_intro_claim_title(
            _MEMORY_INTRO_C_CLAIM,
            anchor=ctx["title_top_target"].get_center(),
        )
        repeated_frame = _build_memory_intro_repeated_frame(
            target_examples=(ctx["example_target"], followup["second_example_target"]),
        )
        repetition_label_anchor = Group(ctx["plot"]["axes"], followup["second_plot"]["axes"])
        repetition_label = _build_memory_intro_repetition_label(
            len(_MEMORY_INTRO_REPEATED_EXPOSURE_STEPS),
            anchor_group=repetition_label_anchor,
        )

        self.add(
            repetition_claim,
            ctx["example_target"],
            ctx["example_foil"],
            ctx["example_target_label"],
            ctx["example_foil_label"],
            top_plot["group"],
            followup["second_example_target"],
            followup["second_example_foil"],
            second_plot["group"],
            repeated_frame,
            repetition_label,
        )

        self.wait(0.25)
        self.play(
            FadeOut(repetition_claim, shift=UP * 0.06),
            FadeOut(repeated_frame, shift=LEFT * 0.04),
            FadeOut(repetition_label, shift=UP * 0.04),
            FadeIn(ctx["title"], shift=UP * 0.06),
            FadeIn(ctx["question"], shift=UP * 0.06),
            run_time=0.65,
        )
        self.wait(0.20)
        self.play(
            LaggedStart(
                *[FadeIn(panel["row_group"], shift=UP * 0.08) for panel in ctx["panels"]],
                lag_ratio=0.08,
            ),
            FadeOut(ctx["example_target"], shift=UP * 0.04),
            FadeOut(ctx["example_foil"], shift=UP * 0.04),
            FadeOut(ctx["example_target_label"], shift=UP * 0.04),
            FadeOut(ctx["example_foil_label"], shift=UP * 0.04),
            FadeOut(top_plot["group"], shift=UP * 0.04),
            FadeOut(followup["second_example_target"], shift=DOWN * 0.04),
            FadeOut(followup["second_example_foil"], shift=DOWN * 0.04),
            FadeOut(second_plot["group"], shift=DOWN * 0.04),
            run_time=1.10,
        )
        self.wait(0.20)
        self.play(
            AnimationGroup(
                *[FadeOut(panel["row_group"]) for panel in ctx["panels"]],
                lag_ratio=0.0,
            ),
            LaggedStart(
                *[
                    TransformFromCopy(source_card.copy(), collapsed_card)
                    for source_card, collapsed_card in zip(overlay["source_cards"], overlay["collapsed_cards"])
                ],
                lag_ratio=0.06,
            ),
            run_time=1.80,
        )
        self.play(
            FadeIn(overlay["continuation_marks"]),
            Create(overlay["target_rect"]),
            Create(overlay["foil_rect"]),
            FadeIn(overlay["target_label"], shift=UP * 0.08),
            FadeIn(overlay["foil_label"], shift=UP * 0.08),
            Create(overlay["dissimilar_arrow"]),
            FadeIn(overlay["dissimilar_text"], shift=UP * 0.08),
            run_time=1.10,
        )
        self.wait(3.00)
        difficulty_annotations = _build_memory_foil_difficulty_annotations(
            overlay["collapsed_cards"],
            overlay["continuation_marks"],
        )
        dissimilar_shift = _memory_dissimilarity_shift_below_difficulty(
            overlay["dissimilar_arrow"],
            overlay["dissimilar_text"],
            difficulty_annotations["annotations"],
        )
        self.play(
            overlay["dissimilar_arrow"].animate.shift(dissimilar_shift),
            overlay["dissimilar_text"].animate.shift(dissimilar_shift),
            FadeOut(overlay["foil_rect"]),
            run_time=0.65,
        )
        for annotation in difficulty_annotations["annotations"]:
            self.play(
                Create(annotation[0]),
                FadeIn(annotation[1], shift=UP * 0.08),
                run_time=0.55,
            )
            self.wait(0.35)
        self.wait(0.30)


class Study1Stage3MemoryExpDesign(Scene):
    """Turn the collapsed continuum summary into the delayed match-to-sample design."""

    def construct(self) -> None:
        """Build the trial card, park each phase into a strip, and reveal the summary layout."""
        self.camera.background_color = BG
        end_state = _build_memory_intro_c_end_state()
        ctx = end_state["ctx"]
        overlay = end_state["overlay"]
        difficulty_annotations = _build_memory_foil_difficulty_annotations(
            overlay["collapsed_cards"],
            overlay["continuation_marks"],
        )
        overlay["foil_rect"].set_opacity(0.0)
        dissimilar_shift = _memory_dissimilarity_shift_below_difficulty(
            overlay["dissimilar_arrow"],
            overlay["dissimilar_text"],
            difficulty_annotations["annotations"],
        )
        overlay["dissimilar_arrow"].shift(dissimilar_shift)
        overlay["dissimilar_text"].shift(dissimilar_shift)

        collapsed_cards = overlay["collapsed_cards"]
        continuation_marks = overlay["continuation_marks"]
        target_rect = overlay["target_rect"]
        foil_rect = overlay["foil_rect"]
        target_label = overlay["target_label"]
        foil_label = overlay["foil_label"]
        dissimilar_arrow = overlay["dissimilar_arrow"]
        dissimilar_text = overlay["dissimilar_text"]
        selected_card_lookup = overlay["selected_card_lookup"]
        lake_target_card = selected_card_lookup[("landscape_element", "lake_island", 0)]
        lake_d3_card = selected_card_lookup[("landscape_element", "lake_island", 3)]

        self.add(
            ctx["title"],
            ctx["question"],
            *collapsed_cards,
            continuation_marks,
            target_rect,
            foil_rect,
            target_label,
            foil_label,
            dissimilar_arrow,
            dissimilar_text,
            difficulty_annotations["annotations"],
        )

        # Phase 1: compact the target-versus-foil summary into the left panel so
        # the right half can host the trial-level delayed match-to-sample demo.
        left_panel = Group(
            *collapsed_cards,
            continuation_marks,
            target_rect,
            foil_rect,
            target_label,
            foil_label,
            dissimilar_arrow,
            dissimilar_text,
            difficulty_annotations["annotations"],
        )

        left_panel_target = left_panel.copy()
        left_panel_target.scale(0.80)
        left_half_center_x = -config.frame_width / 4
        left_panel_shift = np.array([left_half_center_x - left_panel_target.get_center()[0], 0.0, 0.0])
        self.wait(0.40)
        self.play(
            left_panel.animate.scale(0.80).shift(left_panel_shift),
            run_time=0.65,
            rate_func=smooth,
        )
        self.wait(0.20)

        # Phase 2: build the large right-side trial card and the parked strip
        # that will later hold each stage of the trial as a compact summary.
        frame_side = 1.75
        right_margin_x = config.frame_width / 2 - 0.35
        stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
        stage_center_y = 0.5 * (ctx["row_y_positions"][1] + ctx["row_y_positions"][2])
        right_center = np.array([stage_center_x, stage_center_y, 0.0])

        lake_prefix = "landscape_element_lake_island"
        lake_row = ctx["lookup"][("landscape_element", "lake_island")]
        target_idx = int(lake_row["target_position"])
        probe1_idx = int(lake_row["distractor_3_position"])
        probe2_idx = target_idx

        def stage_content(
            kind: str,
            center: np.ndarray,
            large: bool,
        ) -> Group:
            """Return the large or parked visual payload for one trial phase."""
            image_height = 0.95 if large else 0.44
            fixation_height = 0.18 if large else 0.06

            if kind == "target":
                img = stimulus_image(lake_prefix, target_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind == "probe1":
                img = stimulus_image(lake_prefix, probe1_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind == "probe2":
                img = stimulus_image(lake_prefix, probe2_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind in {"delay", "buffer", "iti"}:
                fix = fixation_on(center, height=fixation_height)
                return Group(fix)

            response_size = 18 if large else 8
            response_buff = 0.14 if large else 0.04
            fix = fixation_on(center, height=fixation_height)
            left_text = Tex(
                r"TWO",
                color=INK,
                font_size=response_size,
            ).next_to(fix, LEFT, buff=response_buff)
            right_text = Tex(
                r"ONE",
                color=INK,
                font_size=response_size,
            ).next_to(fix, RIGHT, buff=response_buff)
            arrow_length = 0.40 if large else 0.20
            arrow = Arrow(
                start=left_text.get_center() + RIGHT * (arrow_length / 2),
                end=left_text.get_center() + LEFT * (arrow_length / 2),
                color=INK,
                stroke_width=10 if large else 4,
                buff=0,
                tip_length=0.3 if large else 0.10,
            )
            arrow.next_to(left_text, DOWN, buff=0.06 if large else 0.035)
            fix.set_z_index(8 if large else 6)
            left_text.set_z_index(8 if large else 6)
            right_text.set_z_index(8 if large else 6)
            arrow.set_z_index(8 if large else 6)
            return Group(left_text, fix, right_text, arrow)

        stage_specs = [
            ("2s", "Target", "target"),
            ("8s", "Delay", "delay"),
            ("1s", "Probe 1", "probe1"),
            ("0.5s", "Buffer", "buffer"),
            ("1s", "Probe 2", "probe2"),
            ("2s", "Response", "response"),
            ("(M=4s)", "ITI", "iti"),
        ]

        stage_frame = RoundedRectangle(
            corner_radius=0.12,
            width=frame_side,
            height=frame_side,
            stroke_color=MGREY,
            stroke_width=1.6,
        ).move_to(right_center)
        stage_frame.set_fill(BG, opacity=1.0)
        stage_duration = Tex(stage_specs[0][0], color=INK, font_size=24).next_to(stage_frame, UP, buff=0.16)
        stage_label = Tex(stage_specs[0][1], color=INK, font_size=24).next_to(stage_frame, DOWN, buff=0.18)

        strip_side = 0.82
        strip_gap = 0.10
        strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
        quadrant_bottom_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1])
        strip_vertical_offset = 0.16
        strip_start_y = quadrant_bottom_y + strip_side / 2 - strip_vertical_offset
        strip_final_y = right_center[1] - 0.12 - strip_vertical_offset
        strip_start_centers = [
            np.array(
                [
                    right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                    strip_start_y,
                    0.0,
                ]
            )
            for i in range(len(stage_specs))
        ]
        strip_final_centers = [
            np.array(
                [
                    right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                    strip_final_y,
                    0.0,
                ]
            )
            for i in range(len(stage_specs))
        ]

        parked_cards = []
        for (_, _, kind), center in zip(stage_specs, strip_start_centers):
            parked_frame = RoundedRectangle(
                corner_radius=0.08,
                width=strip_side,
                height=strip_side,
                stroke_color=MGREY,
                stroke_width=1.2,
            ).move_to(center)
            parked_frame.set_fill(BG, opacity=1.0)
            parked_content = stage_content(kind, center, large=False)
            parked_group = Group(parked_frame, parked_content)
            parked_group.set_z_index(6)
            parked_cards.append(parked_group)

        strip_arrow_start_x = strip_start_centers[0][0] - strip_side / 2
        strip_arrow_y = ValueTracker(strip_start_y - strip_side / 2 - 0.18)
        strip_arrow_progress_x = ValueTracker(strip_arrow_start_x + 0.04)
        progress_arrow = always_redraw(
            lambda: Arrow(
                start=np.array([strip_arrow_start_x, strip_arrow_y.get_value(), 0.0]),
                end=np.array(
                    [
                        max(strip_arrow_progress_x.get_value(), strip_arrow_start_x + 0.04),
                        strip_arrow_y.get_value(),
                        0.0,
                    ]
                ),
                color=LGREY,
                stroke_width=1.3,
                buff=0.0,
                tip_length=0.14,
            )
        )

        target_copy = lake_target_card.copy()
        target_copy.move_to(lake_target_card.get_center())
        target_copy.set_z_index(8)
        target_copy.generate_target()
        target_copy.target.scale_to_fit_height(0.95)
        target_copy.target.move_to(right_center)
        target_fixation = fixation_on(right_center, height=0.18)
        active_content = Group(target_copy, target_fixation)

        self.play(
            Create(stage_frame),
            MoveToTarget(target_copy),
            FadeIn(target_fixation),
            FadeIn(stage_duration),
            FadeIn(stage_label),
            run_time=0.80,
        )
        self.add(progress_arrow)
        self.wait(0.20)

        hold_before_park = 1
        park_run_time = 0.4
        hold_after_park = 0.08

        # Phase 3: step through the full trial on the large card while copying
        # each completed phase into the parked strip underneath.
        for idx, (_, _, kind) in enumerate(stage_specs):
            self.wait(hold_before_park)

            self.play(
                TransformFromCopy(Group(stage_frame, active_content), parked_cards[idx]),
                strip_arrow_progress_x.animate.set_value(parked_cards[idx].get_right()[0]),
                run_time=park_run_time,
            )

            self.wait(hold_after_park)

            if idx == len(stage_specs) - 1:
                continue

            next_duration = Tex(stage_specs[idx + 1][0], color=INK, font_size=24).next_to(stage_frame, UP, buff=0.16)
            next_label = Tex(stage_specs[idx + 1][1], color=INK, font_size=24).next_to(stage_frame, DOWN, buff=0.18)
            next_kind = stage_specs[idx + 1][2]
            step_run_time = 0.5

            if next_kind in {"probe1", "probe2"}:
                source_card = lake_d3_card if next_kind == "probe1" else lake_target_card
                highlight_rect = SurroundingRectangle(
                    source_card,
                    color="#F63924",
                    stroke_width=2.5,
                    buff=0.06,
                    corner_radius=0.05,
                )
                highlight_rect.set_z_index(9)
                self.play(FadeIn(highlight_rect), run_time=0.25)
                self.wait(0.10)
                probe_copy = source_card.copy()
                probe_copy.move_to(source_card.get_center())
                probe_copy.set_z_index(8)
                probe_copy.generate_target()
                probe_copy.target.scale_to_fit_height(0.95)
                probe_copy.target.move_to(right_center)
                probe_fix = fixation_on(right_center, height=0.18)
                next_content = Group(probe_copy, probe_fix)
                self.play(
                    FadeOut(active_content, shift=DOWN * 0.06),
                    FadeOut(highlight_rect),
                    MoveToTarget(probe_copy),
                    FadeIn(probe_fix),
                    FadeOut(stage_duration),
                    FadeIn(next_duration),
                    FadeOut(stage_label),
                    FadeIn(next_label),
                    run_time=0.90,
                )
            else:
                next_content = stage_content(next_kind, right_center, large=True)
                self.play(
                    FadeOut(active_content, shift=DOWN * 0.06),
                    FadeIn(next_content, shift=UP * 0.06),
                    FadeOut(stage_duration),
                    FadeIn(next_duration),
                    FadeOut(stage_label),
                    FadeIn(next_label),
                    run_time=step_run_time,
                )
            active_content = next_content
            stage_duration = next_duration
            stage_label = next_label
            self.wait(0.30 if next_kind == "delay" else 0.18)

        # Phase 4: promote the parked strip into its final summary position once
        # the large trial card has served its explanatory role.
        final_arrow_y = min(strip_final_y - (strip_side * 1.12) / 2 - 0.20, right_center[1] - 1.15)
        promotion_anims = [
            parked.animate.move_to(target_center)
            for parked, target_center in zip(parked_cards, strip_final_centers)
        ]
        self.play(
            FadeOut(active_content, shift=UP * 0.06),
            FadeOut(stage_frame, shift=UP * 0.06),
            FadeOut(stage_duration, shift=UP * 0.06),
            FadeOut(stage_label, shift=UP * 0.06),
            strip_arrow_y.animate.set_value(final_arrow_y),
            *promotion_anims,
            run_time=0.85,
        )

        # Phase 5: annotate the parked strip with durations, stage names, and
        # the experiment-level block summary used in the held end state.
        final_duration_labels = VGroup(
            *[
                Tex(duration, color=INK, font_size=16).next_to(card, UP, buff=0.10)
                for (duration, _, _), card in zip(stage_specs, parked_cards)
            ]
        )
        final_stage_labels = VGroup(
            *[
                Tex(label, color=INK, font_size=16).next_to(card, DOWN, buff=0.10)
                for (_, label, _), card in zip(stage_specs, parked_cards)
            ]
        )
        time_label = MathTex("t", color=INK, font_size=24).next_to(progress_arrow, RIGHT, buff=0.10)

        self.play(
            LaggedStart(*[FadeIn(label, shift=UP * 0.05) for label in final_duration_labels], lag_ratio=0.05),
            LaggedStart(*[FadeIn(label, shift=UP * 0.05) for label in final_stage_labels], lag_ratio=0.05),
            FadeIn(time_label, shift=RIGHT * 0.05),
            run_time=1.00,
        )
        stats_block = _build_memory_exp_stats_block(
            final_stage_labels,
            progress_arrow,
            time_label,
        )
        self.play(
            LaggedStart(
                FadeIn(stats_block[0], shift=UP * 0.08),
                FadeIn(stats_block[1], shift=UP * 0.08),
                lag_ratio=0.35,
            ),
            run_time=0.80,
        )
        self.wait(1.00)


_Study1Stage3MemoryExpDesign = Study1Stage3MemoryExpDesign
Study1Stage3MemoryExpDesignA = Study1Stage3MemoryExpDesign


_STUDY1_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    Study1Stage1Step1a,
    Study1Stage1Step1b,
    Study1Stage1Step2,
    Study1Stage1Step2Showcase,
    Study1Stage1Step3Part1,
    Study1Stage1Step3Part2,
    Study1Stage1Step4Setup,
    Study1Stage1Step4Interpolation,
    Study1Stage1Step5Handoff,
    Study1Stage1Step5Deck,
    Study1Stage1Step5LPIPS,
    Study1StimulusSetShowcase,
    Study1Stage2TripletTask,
    Study1Stage2TripletTask2,
    Study1Stage2SimilarityJudgementsExamples,
    Study1Stage2EmbeddingResult,
    Study1Stage2ModelOrderToHeatmap,
    Study1Stage3MemoryIntroA,
    Study1Stage3MemoryIntroB,
    Study1Stage3MemoryIntroC,
    Study1Stage3MemoryIntroD,
    Study1Stage3MemoryExpDesign,
    Study1Stage3MemoryExpResults,
)
_STUDY1_SECTION_NAMES: tuple[str, ...] = (
    "study1_stage1_step1a",
    "study1_stage1_step1b",
    "study1_stage1_step2",
    "study1_stage1_step2_showcase",
    "study1_stage1_step3_part1",
    "study1_stage1_step3_part2",
    "study1_stage1_step4_setup",
    "study1_stage1_step4_interpolation",
    "study1_stage1_step5_handoff",
    "study1_stage1_step5_deck",
    "study1_stage1_step5_lpips",
    "study1_stimulus_set_showcase",
    "study1_stage2_triplet_task",
    "study1_stage2_triplet_task2",
    "study1_stage2_similarity_judgements_examples",
    "study1_stage2_embedding_result",
    "study1_stage2_model_order_to_heatmap",
    "study1_stage3_memory_intro_a",
    "study1_stage3_memory_intro_b",
    "study1_stage3_memory_intro_c",
    "study1_stage3_memory_intro_d",
    "study1_stage3_memory_exp_design",
    "study1_stage3_memory_exp_results",
)


class Study1(
    Study1Stage1Step5,
    Study1Stage1Step4,
    Study1Stage1Step3,
    Study1Stage2,
    Study1Stage3,
):
    """
    Unified production render for Study 1.

    This master scene emits the full narrative from one continuous Manim scene
    via ``--save_sections``.
    """

    _SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = tuple(
        zip(_STUDY1_SECTION_NAMES, _STUDY1_MASTER_SECTION_ORDER)
    )
    _SCENE_INSTANCE_OVERRIDES: tuple[str, ...] = ("segment",)

    def _reset_master_scene_state(self) -> None:
        """Reset mobjects and camera placement before replaying one legacy scene."""
        self.clear()
        self.camera.background_color = WHITE
        if hasattr(self.camera, "frame_center"):
            self.camera.frame_center = ORIGIN.copy()
        self.set_camera_orientation(
            phi=0 * DEGREES,
            theta=-90 * DEGREES,
            gamma=0 * DEGREES,
            zoom=1,
            frame_center=ORIGIN,
        )

    def _hold_previous_section_frame(self) -> None:
        """Pin the previous section's last frame into the next section."""
        self.wait(1 / config.frame_rate)

    def _run_legacy_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        """Replay one existing Study 1 scene inside the master section render."""
        self.next_section(section_name)
        if carry_previous_frame:
            self._hold_previous_section_frame()
        self._reset_master_scene_state()
        instance_overrides: dict[str, tuple[bool, object | None]] = {}
        for attr_name in self._SCENE_INSTANCE_OVERRIDES:
            if attr_name not in scene_cls.__dict__:
                continue
            had_instance_value = attr_name in self.__dict__
            instance_overrides[attr_name] = (had_instance_value, self.__dict__.get(attr_name))
            setattr(self, attr_name, scene_cls.__dict__[attr_name])
        try:
            scene_cls.construct(self)
        finally:
            for attr_name, (had_instance_value, previous_value) in instance_overrides.items():
                if had_instance_value:
                    setattr(self, attr_name, previous_value)
                else:
                    self.__dict__.pop(attr_name, None)

    def construct(self) -> None:
        """Render the full Study 1 narrative as one sectioned scene."""
        _ensure_study1_output_dirs(str(getattr(config, "output_file", self.__class__.__name__)))
        self._reset_master_scene_state()
        for idx, (section_name, scene_cls) in enumerate(self._SECTION_SCENES):
            self._run_legacy_section(
                section_name,
                scene_cls,
                carry_previous_frame=idx > 0,
            )

_HIDDEN_STUDY1_SCENES: tuple[type[Scene], ...] = tuple(
    dict.fromkeys(
        value
        for value in globals().values()
        if isinstance(value, type)
        and issubclass(value, Scene)
        and value is not Scene
        and value.__module__.startswith(__name__)
    )
)

for _scene_cls in _HIDDEN_STUDY1_SCENES:
    _scene_cls.__module__ = "_study1_internal"

Study1.__module__ = __name__
__all__ = ["Study1"]
