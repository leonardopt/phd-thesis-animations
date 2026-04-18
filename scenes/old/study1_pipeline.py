from manim import *

# ── Stage data ────────────────────────────────────────────────────────────────

STAGES = [
    dict(
        label="S1",
        title="Design Prompts",
        desc="108 scenes · 6 categories",
        color=BLUE_D,
        panel_title="108 Object-Scenes",
        panel_body=(
            "6 semantic categories:\n"
            "Natural — animals · plants · landscapes\n"
            "Artificial — items · buildings · vehicles\n"
            "Each scene described with a text prompt"
        ),
    ),
    dict(
        label="S2",
        title="Generate Variations",
        desc="60 images per scene",
        color=BLUE_C,
        panel_title="Stable Diffusion XL",
        panel_body=(
            "Same prompt → 60 different images\n"
            "High-resolution: 1024 × 1024 px\n"
            "Natural variation across exemplars"
        ),
    ),
    dict(
        label="S3",
        title="Select Anchors",
        desc="Max. perceptual distance",
        color=TEAL_C,
        panel_title="Anchor Selection  (LPIPS)",
        panel_body=(
            "LPIPS: Learned Perceptual Image Patch Similarity\n"
            "Pick the pair that looks most different\n"
            "→ Defines the two endpoints of the perceptual axis"
        ),
    ),
    dict(
        label="S4",
        title="Interpolate",
        desc="200 intermediate images",
        color=GREEN_C,
        panel_title="Spherical Interpolation (SLERP)",
        panel_body=(
            "Interpolate between anchors in latent noise space\n"
            "Spherical path → smooth visual morphing\n"
            "→ 200 intermediate images per scene"
        ),
    ),
    dict(
        label="S5",
        title="Select Final Set",
        desc="10 validated images",
        color=YELLOW_C,
        panel_title="Perceptual Scaling",
        panel_body=(
            "Select 10 images at equal perceptual steps\n"
            "Validated by human similarity judgments  (N = 1,113)\n"
            "→ Final stimulus set for fMRI experiments"
        ),
    ),
]

# ── Layout constants ──────────────────────────────────────────────────────────
NODE_Y = 1.8
NODE_XS = [-5.0, -2.5, 0.0, 2.5, 5.0]
PANEL_Y = -1.2
PANEL_W = 7.5
PANEL_H = 2.4


# ── Scene ─────────────────────────────────────────────────────────────────────

class Study1Pipeline(Scene):
    def construct(self):
        title = Text("Study 1: Stimulus Generation Pipeline", font_size=32, weight=BOLD)
        self.play(Write(title))
        self.wait(0.4)
        self.play(title.animate.to_edge(UP, buff=0.3).scale(0.75))

        nodes = self._build_nodes()
        connectors = self._build_connectors(nodes)

        for i, (node_grp, stage) in enumerate(zip(nodes, STAGES)):
            if i > 0:
                self.play(Create(connectors[i - 1]), run_time=0.4)

            self.play(FadeIn(node_grp), run_time=0.5)

            panel, pointer = self._build_panel_and_pointer(stage, nodes[i])
            self.play(FadeIn(panel), Create(pointer), run_time=0.5)
            self.wait(3.0)
            self.play(FadeOut(panel), FadeOut(pointer), run_time=0.4)

        # Full pipeline visible — show summary
        summary = Text(
            "108 prompts  →  60 variations  →  anchor pair  →  200 interpolations  →  10 stimuli",
            font_size=14, color=GRAY_B,
        ).to_edge(DOWN, buff=0.45)
        self.play(Write(summary))
        self.wait(3)

    # ── builders ─────────────────────────────────────────────────────────────

    def _build_nodes(self):
        nodes = []
        for stage, x in zip(STAGES, NODE_XS):
            circle = Circle(radius=0.42, stroke_width=0)
            circle.set_fill(stage["color"], opacity=0.9)
            circle.move_to(RIGHT * x + UP * NODE_Y)

            number = Text(stage["label"], font_size=20, weight=BOLD, color=BLACK)
            number.move_to(circle.get_center())

            title_txt = Text(stage["title"], font_size=13, color=WHITE)
            title_txt.next_to(circle, UP, buff=0.14)

            desc_txt = Text(stage["desc"], font_size=11, color=GRAY_B)
            desc_txt.next_to(circle, DOWN, buff=0.14)

            nodes.append(VGroup(circle, number, title_txt, desc_txt))
        return nodes

    def _build_connectors(self, nodes):
        connectors = []
        for i in range(len(nodes) - 1):
            a = Arrow(
                nodes[i][0].get_right(),
                nodes[i + 1][0].get_left(),
                buff=0.08, stroke_width=2,
                max_tip_length_to_length_ratio=0.2,
                color=GRAY_C,
            )
            connectors.append(a)
        return connectors

    def _build_panel_and_pointer(self, stage, node_grp):
        bg = RoundedRectangle(
            width=PANEL_W, height=PANEL_H,
            corner_radius=0.2,
            stroke_color=stage["color"], stroke_width=1.5,
            fill_color=stage["color"], fill_opacity=0.12,
        )
        bg.move_to(UP * PANEL_Y)

        panel_title = Text(stage["panel_title"], font_size=20, weight=BOLD, color=stage["color"])
        panel_title.next_to(bg.get_top(), DOWN, buff=0.25)

        panel_body = Text(stage["panel_body"], font_size=15, color=WHITE, line_spacing=1.35)
        panel_body.next_to(panel_title, DOWN, buff=0.2)

        panel = VGroup(bg, panel_title, panel_body)

        circle = node_grp[0]
        pointer = Arrow(
            circle.get_bottom() + DOWN * 0.05,
            bg.get_top() + UP * 0.05,
            buff=0.05, stroke_width=1.5,
            max_tip_length_to_length_ratio=0.15,
            color=stage["color"],
        )
        return panel, pointer
