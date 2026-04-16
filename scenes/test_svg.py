from pathlib import Path

from manim import *

config.background_color = WHITE

ROOT = Path(__file__).resolve().parents[1]
SIMPLE_FIGURE_PATH = ROOT / "assets" / "images" / "study1_stage3" / "behaviour_agg.svg"
STUDY2_TIMERES_PATH = ROOT / "assets" / "images" / "study2" / "study2_results_ses02ses01timeres.svg"
STUDY2_GLM_PATH = ROOT / "assets" / "images" / "study2" / "study2_results_ses02ses01glm.svg"
STUDY2_TEMPGEN_PATH = ROOT / "assets" / "images" / "study2" / "study2_results_ses01tempgen.svg"
STUDY2_WITHIN_TIMERES_PATH = ROOT / "assets" / "images" / "study2" / "study2_results_ses01timeres.svg"

INK = "#262626"
PURPLE = "#7B51A0"
GREEN = "#3C9553"


def _get_hex(color) -> str | None:
    return color.to_hex().upper() if color else None


def _load_svg(path: Path, *, frame_width_ratio: float, frame_height_ratio: float) -> SVGMobject:
    svg = SVGMobject(str(path))
    frame_width = config.frame_width * frame_width_ratio
    frame_height = config.frame_height * frame_height_ratio
    svg.scale(min(frame_width / svg.width, frame_height / svg.height))
    svg.center()
    return svg


def _hide_background_rect(svg: SVGMobject) -> None:
    for submob in svg.submobjects:
        if _get_hex(submob.get_stroke_color()) == "#FFFFFF" and _get_hex(submob.get_fill_color()) == "#FFFFFF":
            if submob.width > 0.9 * svg.width and submob.height > 0.9 * svg.height:
                submob.set_stroke(opacity=0)
                submob.set_fill(opacity=0)
                return


def _hide_white_regions(svg: SVGMobject, min_area_ratio: float = 0.02) -> None:
    min_area = svg.width * svg.height * min_area_ratio
    for submob in svg.submobjects:
        fill_hex = _get_hex(submob.get_fill_color())
        stroke_hex = _get_hex(submob.get_stroke_color())
        if fill_hex == "#FFFFFF" and submob.width * submob.height >= min_area:
            submob.set_fill(opacity=0)
            if stroke_hex == "#FFFFFF":
                submob.set_stroke(opacity=0)


def _plot_frame_from_long_lines(svg: SVGMobject, *, min_span_ratio: float = 0.7) -> VGroup:
    candidates = [
        submob
        for submob in svg.submobjects
        if (
            len(submob.get_all_points()) == 4
            and submob.get_stroke_opacity() > 0
            and (
                submob.width >= svg.width * min_span_ratio
                or submob.height >= svg.height * min_span_ratio
            )
        )
    ]
    verticals = [submob for submob in candidates if submob.height > submob.width]
    horizontals = [submob for submob in candidates if submob.width >= submob.height]
    if len(verticals) < 2 or len(horizontals) < 2:
        raise ValueError("Could not identify plot frame from long SVG lines")
    left = min(verticals, key=lambda mob: mob.get_center()[0])
    right = max(verticals, key=lambda mob: mob.get_center()[0])
    bottom = min(horizontals, key=lambda mob: mob.get_center()[1])
    top = max(horizontals, key=lambda mob: mob.get_center()[1])
    return VGroup(left, right, bottom, top)


def _timeres_select_many(svg: SVGMobject, *, stroke_hex: str | None = None, fill_hex: str | None = None, min_points: int = 0):
    stroke_hex = stroke_hex.upper() if stroke_hex else None
    fill_hex = fill_hex.upper() if fill_hex else None

    matches = []
    for submob in svg.submobjects:
        point_count = len(submob.get_all_points())
        if point_count < min_points:
            continue

        stroke_value = _get_hex(submob.get_stroke_color())
        fill_value = _get_hex(submob.get_fill_color())

        if stroke_hex and stroke_value != stroke_hex:
            continue

        if fill_hex and fill_value != fill_hex:
            continue

        matches.append(submob)

    return matches


def _timeres_select_single(svg: SVGMobject, *, stroke_hex: str | None = None, fill_hex: str | None = None, min_points: int = 0):
    matches = _timeres_select_many(svg, stroke_hex=stroke_hex, fill_hex=fill_hex, min_points=min_points)
    if len(matches) != 1:
        raise ValueError(f"Expected 1 match, found {len(matches)} for stroke={stroke_hex} fill={fill_hex}")
    return matches[0]


def _timeres_plot_frame(svg: SVGMobject) -> VGroup:
    return VGroup(*_timeres_select_many(svg, stroke_hex=INK, min_points=4))


def _timeres_dark_text_paths(svg: SVGMobject) -> list[VMobject]:
    return [
        submob
        for submob in svg.submobjects
        if _get_hex(submob.get_fill_color()) == INK and submob.get_fill_opacity() > 0.5
    ]


def _timeres_axis_text_groups(svg: SVGMobject) -> tuple[VGroup, VGroup, VGroup, VGroup]:
    plot_frame = _timeres_plot_frame(svg)
    left = plot_frame.get_left()[0]
    bottom = plot_frame.get_bottom()[1]
    width = plot_frame.width
    height = plot_frame.height
    dark_text = _timeres_dark_text_paths(svg)

    x_title = VGroup(*[submob for submob in dark_text if submob.get_center()[1] < bottom - 0.10 * height])
    y_title = VGroup(*[submob for submob in dark_text if submob.get_center()[0] < left - 0.20 * width])
    x_ticks = VGroup(
        *[
            submob
            for submob in dark_text
            if bottom - 0.13 * height < submob.get_center()[1] < bottom - 0.03 * height
        ]
    )
    y_ticks = VGroup(
        *[
            submob
            for submob in dark_text
            if left - 0.18 * width < submob.get_center()[0] < left - 0.05 * width
        ]
    )

    return x_title, y_title, x_ticks, y_ticks


def _timeres_hide_axis_titles(svg: SVGMobject) -> None:
    x_title, y_title, _, _ = _timeres_axis_text_groups(svg)
    x_title.set_opacity(0)
    y_title.set_opacity(0)


def _timeres_hide_idealized_hrfs(svg: SVGMobject) -> None:
    plot_frame = _timeres_plot_frame(svg)
    cutoff_y = plot_frame.get_top()[1] - 0.22 * plot_frame.height
    target_colors = {GREEN, PURPLE, "#7570B3", "#000000"}

    for submob in svg.submobjects:
        stroke_value = _get_hex(submob.get_stroke_color())
        fill_value = _get_hex(submob.get_fill_color())

        if submob.get_center()[1] < cutoff_y:
            continue

        if stroke_value in target_colors or fill_value in target_colors:
            submob.set_opacity(0)


def _timeres_axis_titles(svg: SVGMobject) -> VGroup:
    plot_frame = _timeres_plot_frame(svg)
    _, _, x_ticks, y_ticks = _timeres_axis_text_groups(svg)

    x_title = Tex(r"Test time (s)", color=BLACK)
    x_title.scale_to_fit_width(plot_frame.width * 0.42)
    x_title.next_to(x_ticks, DOWN, buff=0.12)

    y_title = Tex(r"Accuracy", color=BLACK)
    y_title.rotate(PI / 2)
    y_title.scale_to_fit_height(plot_frame.height * 0.26)
    y_title.next_to(y_ticks, LEFT, buff=0.16)

    return VGroup(x_title, y_title)


def _timeres_significance_bands(svg: SVGMobject) -> VGroup:
    return VGroup(*_timeres_select_many(svg, stroke_hex="#C49A00", min_points=4))


def _glm_plot_frame(svg: SVGMobject) -> VGroup:
    return VGroup(
        *[
            submob
            for submob in svg.submobjects
            if _get_hex(submob.get_stroke_color()) == INK and len(submob.get_all_points()) == 4
        ]
    )


def _glm_group(svg: SVGMobject, color_hex: str, side: str) -> VGroup:
    frame_center_x = _glm_plot_frame(svg).get_center()[0]
    color_hex = color_hex.upper()

    return VGroup(
        *[
            submob
            for submob in svg.submobjects
            if (
                _get_hex(submob.get_stroke_color()) == color_hex
                or _get_hex(submob.get_fill_color()) == color_hex
            )
            and (
                submob.get_center()[0] < frame_center_x if side == "left" else submob.get_center()[0] > frame_center_x
            )
        ]
    )


def _glm_scatter_points(group: VGroup) -> list[VMobject]:
    return sorted(
        [
            submob
            for submob in group
            if submob.get_fill_opacity() < 0.5 and len(submob.get_all_points()) == 32
        ],
        key=lambda mob: (mob.get_center()[1], mob.get_center()[0]),
    )


def _glm_chance_line(svg: SVGMobject) -> VMobject:
    plot_frame = _glm_plot_frame(svg)
    x_tol = plot_frame.width * 0.02
    y_tol = plot_frame.height * 0.02

    candidates = [
        submob
        for submob in svg.submobjects
        if (
            len(submob.get_all_points()) == 4
            and abs(submob.get_left()[0] - plot_frame.get_left()[0]) <= x_tol
            and abs(submob.get_right()[0] - plot_frame.get_right()[0]) <= x_tol
            and plot_frame.get_bottom()[1] + y_tol < submob.get_center()[1] < plot_frame.get_top()[1] - y_tol
            and submob.height <= plot_frame.height * 0.02
        )
    ]
    if not candidates:
        raise ValueError("Could not identify GLM chance line in SVG")
    return max(candidates, key=lambda mob: mob.width)


def _glm_summary_marker(group: VGroup) -> tuple[VMobject, VMobject]:
    filled = [
        submob
        for submob in group
        if submob.get_fill_opacity() > 0.9 and len(submob.get_all_points()) <= 20
    ]
    stroked = [
        submob
        for submob in group
        if submob.get_fill_opacity() == 0 and len(submob.get_all_points()) <= 20
    ]

    if len(filled) != 1 or len(stroked) != 1:
        raise ValueError(f"Expected one filled and one stroked summary marker, found {len(filled)} and {len(stroked)}")

    return filled[0], stroked[0]


def _glm_significance_marker(svg: SVGMobject, color_hex: str, side: str) -> VGroup:
    plot_top = _glm_plot_frame(svg).get_top()[1]
    frame_center_x = _glm_plot_frame(svg).get_center()[0]
    color_hex = color_hex.upper()

    return VGroup(
        *[
            submob
            for submob in svg.submobjects
            if (
                _get_hex(submob.get_fill_color()) == color_hex
                or _get_hex(submob.get_stroke_color()) == color_hex
            )
            and submob.get_center()[1] > plot_top
            and (
                submob.get_center()[0] < frame_center_x if side == "left" else submob.get_center()[0] > frame_center_x
            )
        ]
    )


def _glm_hide_color_groups(svg: SVGMobject) -> None:
    for submob in svg.submobjects:
        if _get_hex(submob.get_fill_color()) in {PURPLE, GREEN} or _get_hex(submob.get_stroke_color()) in {PURPLE, GREEN}:
            submob.set_opacity(0)


def _glm_bottom_label(plot_frame: VGroup, x: float, tex: str) -> MathTex:
    label = MathTex(tex, color=BLACK)
    label.scale_to_fit_width(plot_frame.width * 0.21)
    label.move_to([x, plot_frame.get_bottom()[1] - 0.19, 0.0])
    return label


class SimpleFigure(Scene):
    def construct(self):
        fig = _load_svg(SIMPLE_FIGURE_PATH, frame_width_ratio=0.56, frame_height_ratio=0.72)
        fig.set_opacity(0)

        self.add(fig)
        self.play(fig.animate.set_opacity(1), run_time=2)
        self.wait(1)


class Study2TimeResLineTest(Scene):
    def construct(self):
        svg = _load_svg(STUDY2_TIMERES_PATH, frame_width_ratio=0.62, frame_height_ratio=0.62)
        _hide_background_rect(svg)
        _timeres_hide_axis_titles(svg)
        _timeres_hide_idealized_hrfs(svg)

        plot_base = svg.copy()
        _hide_background_rect(plot_base)
        _timeres_hide_axis_titles(plot_base)
        _timeres_hide_idealized_hrfs(plot_base)

        animated_line = _timeres_select_single(svg, stroke_hex="#000000", min_points=50)
        ci_band = _timeres_select_single(svg, fill_hex="#6E6E6E", min_points=100)
        significance_bands = _timeres_significance_bands(svg)

        _timeres_select_single(plot_base, stroke_hex="#000000", min_points=50).set_opacity(0)
        _timeres_select_single(plot_base, fill_hex="#6E6E6E", min_points=100).set_opacity(0)
        _timeres_significance_bands(plot_base).set_opacity(0)

        plot_frame = _timeres_plot_frame(plot_base)
        plot_rest = VGroup(*[submob for submob in plot_base.submobjects if submob not in plot_frame.submobjects])
        axis_titles = _timeres_axis_titles(plot_base)

        ci_band.set_stroke(opacity=0)
        ci_band.set_fill(color="#6E6E6E", opacity=0.28)
        ci_band.set_z_index(1)

        animated_line.set_fill(opacity=0)
        animated_line.set_stroke(color=BLACK, width=6)
        animated_line.set_z_index(2)

        significance_bands.set_stroke(color="#C49A00", width=4.8)
        significance_bands.set_z_index(2)

        self.play(
            AnimationGroup(
                Create(plot_frame),
                FadeIn(plot_rest, shift=UP * 0.08),
                LaggedStart(Write(axis_titles[0]), Write(axis_titles[1]), lag_ratio=0.15),
                lag_ratio=0.18,
            ),
            run_time=1.8,
        )
        self.play(Create(animated_line), run_time=2.6)
        self.play(
            AnimationGroup(
                FadeIn(ci_band),
                LaggedStart(*[Create(band) for band in significance_bands], lag_ratio=0.12),
                lag_ratio=0.0,
            ),
            run_time=0.9,
        )
        self.wait(1)


class Study2TimeResElementsTest(Scene):
    def construct(self):
        svg = _load_svg(STUDY2_TIMERES_PATH, frame_width_ratio=0.62, frame_height_ratio=0.62)
        _hide_background_rect(svg)
        _timeres_hide_axis_titles(svg)
        _timeres_hide_idealized_hrfs(svg)

        base = svg.copy()
        _hide_background_rect(base)
        _timeres_hide_axis_titles(base)
        _timeres_hide_idealized_hrfs(base)

        band = _timeres_select_single(svg, fill_hex="#6E6E6E", min_points=100)
        main_line = _timeres_select_single(svg, stroke_hex="#000000", min_points=50)
        significance_bands = _timeres_significance_bands(svg)

        _timeres_select_single(base, fill_hex="#6E6E6E", min_points=100).set_opacity(0)
        _timeres_select_single(base, stroke_hex="#000000", min_points=50).set_opacity(0)
        _timeres_significance_bands(base).set_opacity(0)
        base.set_opacity(0.22)

        band.set_stroke(opacity=0)
        band.set_fill(color=GREY_BROWN, opacity=0.22)

        main_line.set_fill(opacity=0)
        main_line.set_stroke(color=BLACK, width=6)

        significance_bands.set_stroke(color="#C49A00", width=4.8)
        axis_titles = _timeres_axis_titles(base)

        self.play(FadeIn(base, shift=UP * 0.08), Write(axis_titles), run_time=1.4)
        self.play(Create(main_line), run_time=2.2)
        self.play(
            AnimationGroup(
                FadeIn(band),
                LaggedStart(*[Create(sig_band) for sig_band in significance_bands], lag_ratio=0.12),
                lag_ratio=0.0,
            ),
            run_time=0.9,
        )
        self.wait(1)


class Study2WithinSessionTimeResTest(Scene):
    def construct(self):
        svg = _load_svg(STUDY2_WITHIN_TIMERES_PATH, frame_width_ratio=0.62, frame_height_ratio=0.62)
        _hide_background_rect(svg)
        _timeres_hide_axis_titles(svg)
        _timeres_hide_idealized_hrfs(svg)

        plot_base = svg.copy()
        _hide_background_rect(plot_base)
        _timeres_hide_axis_titles(plot_base)
        _timeres_hide_idealized_hrfs(plot_base)

        animated_line = _timeres_select_single(svg, stroke_hex="#000000", min_points=50)
        ci_band = _timeres_select_single(svg, fill_hex="#6E6E6E", min_points=100)
        significance_bands = _timeres_significance_bands(svg)

        _timeres_select_single(plot_base, stroke_hex="#000000", min_points=50).set_opacity(0)
        _timeres_select_single(plot_base, fill_hex="#6E6E6E", min_points=100).set_opacity(0)
        _timeres_significance_bands(plot_base).set_opacity(0)

        plot_frame = _timeres_plot_frame(plot_base)
        plot_rest = VGroup(*[submob for submob in plot_base.submobjects if submob not in plot_frame.submobjects])
        axis_titles = _timeres_axis_titles(plot_base)

        ci_band.set_stroke(opacity=0)
        ci_band.set_fill(color="#6E6E6E", opacity=0.28)
        ci_band.set_z_index(1)

        animated_line.set_fill(opacity=0)
        animated_line.set_stroke(color=BLACK, width=6)
        animated_line.set_z_index(2)

        significance_bands.set_stroke(color="#C49A00", width=4.8)
        significance_bands.set_z_index(2)

        self.play(
            AnimationGroup(
                Create(plot_frame),
                FadeIn(plot_rest, shift=UP * 0.08),
                LaggedStart(Write(axis_titles[0]), Write(axis_titles[1]), lag_ratio=0.15),
                lag_ratio=0.18,
            ),
            run_time=1.8,
        )
        self.play(Create(animated_line), run_time=2.6)
        self.play(
            AnimationGroup(
                FadeIn(ci_band),
                LaggedStart(*[Create(band) for band in significance_bands], lag_ratio=0.12),
                lag_ratio=0.0,
            ),
            run_time=0.9,
        )
        self.wait(1)


class Study2GLMScatterRevealTest(Scene):
    def construct(self):
        svg = _load_svg(STUDY2_GLM_PATH, frame_width_ratio=0.68, frame_height_ratio=0.76)
        _hide_background_rect(svg)

        base = svg.copy()
        _hide_background_rect(base)
        _glm_hide_color_groups(base)

        plot_frame = _glm_plot_frame(base)
        chance_template = _glm_chance_line(base)
        plot_rest = VGroup(
            *[
                submob
                for submob in base.submobjects
                if submob not in plot_frame.submobjects and submob is not chance_template
            ]
        )

        left_group = _glm_group(svg, PURPLE, "left")
        right_group = _glm_group(svg, GREEN, "right")
        left_sig = _glm_significance_marker(svg, PURPLE, "left")
        right_sig = _glm_significance_marker(svg, GREEN, "right")
        left_visual = VGroup(*[submob for submob in left_group if submob not in left_sig])
        right_visual = VGroup(*[submob for submob in right_group if submob not in right_sig])

        left_points = _glm_scatter_points(left_visual)
        right_points = _glm_scatter_points(right_visual)
        left_extras = VGroup(*[submob for submob in left_visual if submob not in left_points])
        right_extras = VGroup(*[submob for submob in right_visual if submob not in right_points])

        left_label = _glm_bottom_label(plot_frame, left_group.get_center()[0], r"S_2 \rightarrow S_1")
        right_label = _glm_bottom_label(plot_frame, right_group.get_center()[0], r"S_2 \rightarrow D_1")
        chance_y = chance_template.get_center()[1]
        chance_color = chance_template.get_stroke_color()
        chance_line = DashedLine(
            np.array([plot_frame.get_left()[0], chance_y, 0.0]),
            np.array([plot_frame.get_right()[0], chance_y, 0.0]),
            color=chance_color,
            stroke_width=2.0,
            dash_length=0.08,
            dashed_ratio=0.55,
        )
        chance_label = Tex(
            "Chance",
            color=chance_color,
            font_size=14,
        ).move_to(np.array([plot_frame.get_right()[0] - 0.26, chance_y + 0.14, 0.0]))

        self.play(
            AnimationGroup(
                Create(plot_frame),
                FadeIn(plot_rest, shift=UP * 0.08),
                Create(chance_line),
                FadeIn(chance_label, shift=UP * 0.04),
                lag_ratio=0.18,
            ),
            run_time=1.4,
        )
        self.play(
            AnimationGroup(
                LaggedStart(*[FadeIn(dot, scale=0.75) for dot in left_points], lag_ratio=0.04),
                FadeIn(left_extras, shift=UP * 0.04),
                Write(left_label),
                lag_ratio=0.18,
            ),
            run_time=1.8,
        )
        self.play(
            AnimationGroup(
                LaggedStart(*[FadeIn(dot, scale=0.75) for dot in right_points], lag_ratio=0.04),
                FadeIn(right_extras, shift=UP * 0.04),
                Write(right_label),
                lag_ratio=0.18,
            ),
            run_time=1.8,
        )
        self.play(
            AnimationGroup(
                LaggedStart(*[FadeIn(marker, shift=UP * 0.03) for marker in left_sig], lag_ratio=0.12),
                FadeIn(right_sig, shift=UP * 0.03),
                lag_ratio=0.22,
            ),
            run_time=0.8,
        )
        self.wait(1)


class Study2TempGenMatrixTest(Scene):
    def construct(self):
        center = ORIGIN + DOWN * 0.15
        plot_height = config.frame_height * 0.74

        title = Tex("Temporal generalisation", color=BLACK, font_size=28).to_edge(UP, buff=0.35)
        underlay = (
            ImageMobject(str(STUDY2_TEMPGEN_PATH.with_suffix(".png")))
            .set_height(plot_height)
            .move_to(center)
        )
        underlay.set_opacity(0.86)

        overlay = (
            SVGMobject(str(STUDY2_TEMPGEN_PATH))
            .set_height(plot_height)
            .move_to(center)
        )
        _hide_white_regions(overlay)
        overlay_frame = _plot_frame_from_long_lines(overlay, min_span_ratio=0.62)
        plot_frame = overlay_frame.copy()
        overlay_frame.set_opacity(0)
        plot_frame.set_z_index(4)
        underlay.set_z_index(1)
        overlay.set_z_index(3)
        underlay.set_opacity(0.18)

        diag_start = plot_frame.get_corner(DL)
        diag_end = plot_frame.get_corner(UR)
        diag_color = interpolate_color(ManimColor(PURPLE), ManimColor(GREEN), 0.38)
        sweep = ValueTracker(0.0)

        def sweep_point(alpha: float) -> np.ndarray:
            return interpolate(diag_start, diag_end, float(np.clip(alpha, 0.0, 1.0)))

        diag_glow = always_redraw(
            lambda: Line(
                diag_start,
                sweep_point(sweep.get_value()),
                color=diag_color,
                stroke_width=18,
            ).set_stroke(opacity=0.16).set_z_index(5)
        )
        diag_trace = always_redraw(
            lambda: Line(
                diag_start,
                sweep_point(sweep.get_value()),
                color=diag_color,
                stroke_width=5.5,
            ).set_stroke(opacity=0.95).set_z_index(6)
        )
        cursor_dot = always_redraw(
            lambda: Dot(
                sweep_point(sweep.get_value()),
                radius=0.056,
                color=interpolate_color(ManimColor(PURPLE), ManimColor(GREEN), sweep.get_value()),
                fill_opacity=1.0,
            ).set_stroke(WHITE, width=1.5).set_z_index(7)
        )
        x_cursor = always_redraw(
            lambda: Line(
                np.array([sweep_point(sweep.get_value())[0], plot_frame.get_bottom()[1] - 0.02, 0.0]),
                np.array([sweep_point(sweep.get_value())[0], plot_frame.get_bottom()[1] + 0.09, 0.0]),
                color=diag_color,
                stroke_width=3.0,
            ).set_z_index(6)
        )
        y_cursor = always_redraw(
            lambda: Line(
                np.array([plot_frame.get_left()[0] - 0.09, sweep_point(sweep.get_value())[1], 0.0]),
                np.array([plot_frame.get_left()[0] + 0.02, sweep_point(sweep.get_value())[1], 0.0]),
                color=diag_color,
                stroke_width=3.0,
            ).set_z_index(6)
        )
        x_guide = always_redraw(
            lambda: DashedLine(
                np.array([sweep_point(sweep.get_value())[0], plot_frame.get_bottom()[1], 0.0]),
                sweep_point(sweep.get_value()),
                color=GREY_B,
                stroke_width=1.4,
                dash_length=0.05,
                dashed_ratio=0.62,
            ).set_z_index(5)
        )
        y_guide = always_redraw(
            lambda: DashedLine(
                np.array([plot_frame.get_left()[0], sweep_point(sweep.get_value())[1], 0.0]),
                sweep_point(sweep.get_value()),
                color=GREY_B,
                stroke_width=1.4,
                dash_length=0.05,
                dashed_ratio=0.62,
            ).set_z_index(5)
        )
        diag_residue = Line(diag_start, diag_end, color=diag_color, stroke_width=8).set_stroke(opacity=0.18)
        diag_residue.set_z_index(4)

        self.play(
            FadeIn(title, shift=UP * 0.05),
            AnimationGroup(
                Create(plot_frame),
                FadeIn(underlay, shift=UP * 0.08),
                lag_ratio=0.16,
            ),
            run_time=0.85,
        )
        self.play(
            FadeIn(x_cursor),
            FadeIn(y_cursor),
            FadeIn(x_guide),
            FadeIn(y_guide),
            FadeIn(cursor_dot, scale=0.85),
            FadeIn(diag_glow),
            FadeIn(diag_trace),
            run_time=0.25,
        )
        self.play(sweep.animate.set_value(1.0), run_time=1.65, rate_func=smooth)
        self.play(
            Flash(diag_end, color=diag_color, line_length=0.18, num_lines=10, flash_radius=0.16),
            run_time=0.45,
        )
        self.play(
            FadeIn(diag_residue),
            underlay.animate.set_opacity(0.86),
            FadeIn(overlay, shift=UP * 0.06),
            FadeOut(x_cursor),
            FadeOut(y_cursor),
            FadeOut(x_guide),
            FadeOut(y_guide),
            FadeOut(cursor_dot, scale=1.15),
            FadeOut(diag_glow),
            FadeOut(diag_trace),
            run_time=0.95,
        )
        self.play(FadeOut(diag_residue), run_time=0.35)
        self.wait(1)
