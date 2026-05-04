from __future__ import annotations

from manim import *


BG = WHITE
INK = "#1C1C1E"
GREY = "#D1D5DB"
MGREY = "#6B7280"
BLUE = "#2563EB"
ORANGE = "#D97706"
GREEN = "#16A34A"
ROSE = "#DC2626"


class FrameSelectionProbe10s(Scene):
    """
    Ten-second probe clip for stable-frame selection.

    Hold windows:
        0.0s - 1.6s   state 1
        2.4s - 4.0s   state 2
        4.8s - 6.4s   state 3
        7.2s - 10.0s  state 4

    Transition windows:
        1.6s - 2.4s
        4.0s - 4.8s
        6.4s - 7.2s
    """

    _STATE_SPECS: tuple[dict[str, object], ...] = (
        {
            "name": "State 1",
            "label": "First stable window",
            "color": BLUE,
            "fill": "#EFF6FF",
            "progress": 0.10,
            "time": "0.0-1.6 s",
        },
        {
            "name": "State 2",
            "label": "Second stable window",
            "color": ORANGE,
            "fill": "#FFF7ED",
            "progress": 0.37,
            "time": "2.4-4.0 s",
        },
        {
            "name": "State 3",
            "label": "Third stable window",
            "color": GREEN,
            "fill": "#ECFDF5",
            "progress": 0.64,
            "time": "4.8-6.4 s",
        },
        {
            "name": "State 4",
            "label": "Final stable window",
            "color": ROSE,
            "fill": "#FEF2F2",
            "progress": 0.92,
            "time": "7.2-10.0 s",
        },
    )

    def _bullet_row(self, text: str) -> VGroup:
        bullet = Dot(radius=0.05, color=GREY)
        label = Tex(text, color=INK, font_size=20)
        return VGroup(bullet, label).arrange(RIGHT, buff=0.14, aligned_edge=DOWN)

    def _bullet_block(self) -> VGroup:
        rows = VGroup(
            self._bullet_row(r"10 s synthetic clip with four stable windows"),
            self._bullet_row(r"three short transitions separate the windows"),
            self._bullet_row(r"one representative frame should be selected per hold"),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        frame = RoundedRectangle(
            width=7.75,
            height=1.72,
            corner_radius=0.14,
            stroke_color=GREY,
            stroke_width=1.2,
        ).set_fill(WHITE, opacity=1.0)
        rows.align_to(frame, LEFT).shift(RIGHT * 0.30)
        rows.move_to(frame.get_center())
        return VGroup(frame, rows)

    def _state_group(self, index: int) -> VGroup:
        spec = self._STATE_SPECS[index]
        color = spec["color"]

        card = RoundedRectangle(
            width=5.85,
            height=3.05,
            corner_radius=0.16,
            stroke_color=GREY,
            stroke_width=1.5,
        ).set_fill(spec["fill"], opacity=1.0)

        accent_bar = RoundedRectangle(
            width=5.10,
            height=0.28,
            corner_radius=0.12,
            stroke_width=0,
        ).set_fill(color, opacity=0.95)
        accent_bar.move_to(card.get_top() + DOWN * 0.34)

        index_badge = Circle(radius=0.42, stroke_width=0).set_fill(color, opacity=1.0)
        index_badge.move_to(card.get_left() + RIGHT * 0.82 + UP * 0.28)
        index_text = Tex(rf"\textbf{{{index + 1}}}", color=WHITE, font_size=28)
        index_text.move_to(index_badge.get_center())

        title = Tex(rf"\textbf{{{spec['name']}}}", color=INK, font_size=30)
        title.move_to(card.get_left() + RIGHT * 3.10 + UP * 0.30)

        subtitle = Tex(str(spec["label"]), color=MGREY, font_size=22)
        subtitle.move_to(card.get_center() + UP * 0.10)

        time_chip = RoundedRectangle(
            width=2.25,
            height=0.48,
            corner_radius=0.18,
            stroke_width=0,
        ).set_fill(color, opacity=0.16)
        time_chip.move_to(card.get_center() + DOWN * 0.68)
        time_text = Tex(str(spec["time"]), color=color, font_size=18)
        time_text.move_to(time_chip.get_center())

        hold_label = Tex(r"\textit{stable hold for frame extraction}", color=INK, font_size=18)
        hold_label.move_to(card.get_center() + DOWN * 1.12)

        group = VGroup(
            card,
            accent_bar,
            index_badge,
            index_text,
            title,
            subtitle,
            time_chip,
            time_text,
            hold_label,
        )
        group.move_to([0.0, 0.08, 0.0])
        return group

    def _timeline(self) -> VGroup:
        track = Line(LEFT * 5.30, RIGHT * 5.30, color=GREY, stroke_width=4.0)
        track.move_to(DOWN * 2.60)

        hold_segments = VGroup()
        transition_segments = VGroup()
        labels = VGroup()

        previous_progress = 0.0
        for idx, spec in enumerate(self._STATE_SPECS):
            progress = float(spec["progress"])
            color = spec["color"]

            hold_segment = Line(
                track.point_from_proportion(max(previous_progress, progress - 0.10)),
                track.point_from_proportion(min(1.0, progress + 0.10)),
                color=color,
                stroke_width=8.0,
            )
            hold_segments.add(hold_segment)

            label = Tex(str(spec["time"]), color=MGREY, font_size=15)
            label.next_to(hold_segment, DOWN, buff=0.18)
            labels.add(label)

            if idx < len(self._STATE_SPECS) - 1:
                next_progress = float(self._STATE_SPECS[idx + 1]["progress"])
                transition = Line(
                    track.point_from_proportion(progress + 0.10),
                    track.point_from_proportion(next_progress - 0.10),
                    color=GREY,
                    stroke_width=4.0,
                )
                transition_segments.add(transition)

            previous_progress = progress

        title = Tex(r"\textbf{Known stable windows}", color=INK, font_size=22)
        title.next_to(track, UP, buff=0.22)

        return VGroup(track, transition_segments, hold_segments, title, labels)

    def construct(self) -> None:
        self.camera.background_color = BG

        title = Tex(r"\textbf{Automatic Frame Selection Probe}", color=INK, font_size=34).to_edge(UP, buff=0.28)
        subtitle = Tex(
            r"Simple test clip with known stable holds and short transitions",
            color=MGREY,
            font_size=20,
        )
        subtitle.next_to(title, DOWN, buff=0.14)

        bullets = self._bullet_block()
        bullets.move_to([0.0, 2.00, 0.0])

        state_group = self._state_group(0)
        timeline = self._timeline()
        marker = Dot(radius=0.12, color=self._STATE_SPECS[0]["color"])
        marker.move_to(timeline[0].point_from_proportion(float(self._STATE_SPECS[0]["progress"])))

        self.add(title, subtitle, bullets, state_group, timeline, marker)
        self.wait(1.6)

        for transition_target in (1, 2, 3):
            next_state_group = self._state_group(transition_target)
            next_progress = float(self._STATE_SPECS[transition_target]["progress"])
            next_color = self._STATE_SPECS[transition_target]["color"]

            self.play(
                Transform(state_group, next_state_group),
                marker.animate.move_to(timeline[0].point_from_proportion(next_progress)).set_color(next_color),
                run_time=0.8,
                rate_func=smooth,
            )

            if transition_target < 3:
                self.wait(1.6)
            else:
                self.wait(2.8)
