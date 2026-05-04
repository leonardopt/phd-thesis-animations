"""
Slide clips: SDXL as a neural network.
Three separate scenes — fish, Mediterranean pine, observatory.

Each shows: prompt (static) + 3b1b-style network activating + single image
denoising in place (noise → clean via cross-fades).

Render one at a time:
    uv run manim scenes/sdxl_network.py SDXLNetworkFish -qh
    uv run manim scenes/sdxl_network.py SDXLNetworkPine -qh
    uv run manim scenes/sdxl_network.py SDXLNetworkObservatory -qh
"""
import shutil

import numpy as np
from manim import *
from utils import noise_sequence, stim_path

# ── Layout ─────────────────────────────────────────────────────────────────────
NET_X         = -1.6    # centre x of the neural network
NET_Y         = -0.2    # centre y of the neural network
IMG_X         =  4.8    # centre x of the output image
IMG_Y         = -0.3    # centre y of the output image
IMG_H         =  4.0    # display height (square)

# ── Network geometry ───────────────────────────────────────────────────────────
LAYER_SIZES   = [3, 5, 7, 5, 3]
LAYER_SPACING = 1.2    # centre-to-centre between adjacent layers
NODE_SPACING  = 0.52   # vertical centre-to-centre within a layer
NODE_RADIUS   = 0.13

# ── Denoising frames: noise → clean ───────────────────────────────────────────
ALPHAS = [1.0, 0.66, 0.33, 0.0]   # 128×128 images; last is original resized


# ──────────────────────────────────────────────────────────────────────────────
def _build_network(cx, cy):
    """Return (layers, connections).  layers = list of VGroup (one per layer)."""
    n = len(LAYER_SIZES)
    xs = [cx + (i - (n - 1) / 2) * LAYER_SPACING for i in range(n)]

    layers = []
    for x, size in zip(xs, LAYER_SIZES):
        ys = [cy + (j - (size - 1) / 2) * NODE_SPACING for j in range(size)]
        layers.append(VGroup(*[
            Circle(radius=NODE_RADIUS, color=GRAY_B, stroke_width=1.0, fill_opacity=0)
            .move_to([x, y, 0])
            for y in ys
        ]))

    conns = VGroup()
    for li in range(n - 1):
        for a in layers[li]:
            for b in layers[li + 1]:
                conns.add(Line(
                    a.get_center(), b.get_center(),
                    stroke_width=0.35, stroke_opacity=0.22, color=GRAY_C,
                ))

    return layers, conns


def _ripple(layers):
    """Left-to-right activation ripple: list of per-layer LaggedStart anims."""
    return [
        LaggedStart(
            *[node.animate.set_fill(BLUE_C, opacity=0.88) for node in layer],
            lag_ratio=0.18,
        )
        for layer in layers
    ]


# ──────────────────────────────────────────────────────────────────────────────
class _SDXLBase(Scene):
    SRC       = ""
    PROMPT_L1 = ""
    PROMPT_L2 = ""

    def construct(self):
        self.camera.background_color = WHITE
        paths, tmpdir = noise_sequence(stim_path(self.SRC), ALPHAS, size=128)
        try:
            self._run(paths)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _run(self, paths):
        # ── Prompt — static from frame 0 ──────────────────────────────────────
        p_txt = VGroup(
            Tex(self.PROMPT_L1, font_size=17, color=BLACK),
            Tex(self.PROMPT_L2, font_size=17, color=BLACK),
        ).arrange(DOWN, buff=0.07, aligned_edge=LEFT)
        p_bg = SurroundingRectangle(
            p_txt, color=GRAY_C, stroke_width=1.0,
            fill_color=GRAY_E, fill_opacity=0.45, buff=0.18, corner_radius=0.12,
        )
        p_grp = VGroup(p_bg, p_txt)
        p_grp.to_corner(UL, buff=0.35)
        p_lbl = Tex(r"\textit{prompt}", font_size=14, color=GRAY_C)
        p_lbl.next_to(p_grp, DOWN, buff=0.10)
        self.add(p_grp, p_lbl)   # no animation — present from frame 0

        # ── Neural network skeleton ────────────────────────────────────────────
        layers, conns = _build_network(NET_X, NET_Y)
        all_nodes = VGroup(*layers)

        # Labels above network
        net_top_y = max(n.get_top()[1] for layer in layers for n in layer)
        net_lbl = Tex(r"\textbf{Stable Diffusion XL}", font_size=18, color=BLACK)
        net_lbl.move_to([NET_X, net_top_y + 0.38, 0])
        net_sub = Tex(r"\textit{(neural network)}", font_size=13, color=GRAY_C)
        net_sub.next_to(net_lbl, DOWN, buff=0.06)

        # Arrow: noise → left of network
        left_x  = min(n.get_center()[0] for layer in layers for n in layer) - NODE_RADIUS
        a_in = Arrow(
            np.array([left_x - 1.25, NET_Y, 0]),
            np.array([left_x - 0.06, NET_Y, 0]),
            buff=0.0, stroke_width=2.0, color=BLACK,
            max_tip_length_to_length_ratio=0.22,
        )
        noise_lbl = Tex(r"\textit{noise}", font_size=14, color=GRAY_C)
        noise_lbl.next_to(a_in, UP, buff=0.09)

        # Arrow: right of network → image
        right_x = max(n.get_center()[0] for layer in layers for n in layer) + NODE_RADIUS
        img_left = IMG_X - IMG_H / 2   # approximate left edge of square image
        a_out = Arrow(
            np.array([right_x + 0.06, NET_Y, 0]),
            np.array([img_left - 0.12, IMG_Y, 0]),
            buff=0.0, stroke_width=2.0, color=BLACK,
            max_tip_length_to_length_ratio=0.22,
        )

        # ── Output images — all same position, cross-faded ────────────────────
        imgs = []
        for path in paths:
            im = ImageMobject(path)
            im.height = IMG_H
            im.move_to([IMG_X, IMG_Y, 0])
            imgs.append(im)

        out_lbl = Tex(r"\textit{output}", font_size=15, color=GRAY_C)
        out_lbl.next_to(imgs[0], DOWN, buff=0.13)

        # ── Animation ─────────────────────────────────────────────────────────

        # 1. Network skeleton fades in
        self.play(
            FadeIn(conns), FadeIn(all_nodes),
            FadeIn(net_lbl), FadeIn(net_sub),
            FadeIn(a_in), FadeIn(noise_lbl),
            run_time=0.6,
        )
        self.wait(0.2)

        # 2. Activation ripple left → right (one layer at a time)
        for anim in _ripple(layers):
            self.play(anim, run_time=0.30)

        # 3. Arrow out + first frame (pure noise) appears
        self.play(Create(a_out), run_time=0.40)
        self.play(FadeIn(imgs[0]), FadeIn(out_lbl), run_time=0.45)
        self.wait(0.35)

        # 4. Denoising cross-fades: noise → clean
        for i in range(1, len(imgs)):
            self.play(
                FadeOut(imgs[i - 1]),
                FadeIn(imgs[i]),
                run_time=0.55,
            )
            self.wait(0.25)

        # 5. Hold on final clean image
        self.wait(2.5)


# ──────────────────────────────────────────────────────────────────────────────
class SDXLNetworkFish(_SDXLBase):
    SRC       = "animal_fish-05"
    PROMPT_L1 = r"``award-winning marine photo of a colorful fish in a coral reef,"
    PROMPT_L2 = r"centered, vibrant underwater scene, high detail''"


class SDXLNetworkPine(_SDXLBase):
    SRC       = "plant_pine_med-05"
    PROMPT_L1 = r"``a Mediterranean pine on a rocky coastline,"
    PROMPT_L2 = r"high resolution photography, cinematic''"


class SDXLNetworkObservatory(_SDXLBase):
    SRC       = "building_observatory-05"
    PROMPT_L1 = r"``film shot of an observatory on a remote hilly landscape,"
    PROMPT_L2 = r"high resolution photography, exploratory, cinematic''"
