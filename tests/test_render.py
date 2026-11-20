"""迷宫 SVG / HTML 渲染的单元测试。"""

from __future__ import annotations

import unittest

from maze.maze import MazeError, generate_maze, wall_segments
from maze.render import (
    AREA_HEIGHT_MM,
    AREA_WIDTH_MM,
    maze_geometry,
    render_html,
    render_svg,
    solution_points,
)


class GeometryTest(unittest.TestCase):
    def test_cells_are_square(self) -> None:
        cell, _, _ = maze_geometry(generate_maze(20, 10, seed=1))
        self.assertAlmostEqual(cell, 9.0)

    def test_maze_fits_print_area(self) -> None:
        for width, height in ((5, 5), (15, 22), (60, 60), (10, 50)):
            maze = generate_maze(width, height, seed=1)
            cell, offset_x, offset_y = maze_geometry(maze)
            self.assertLessEqual(maze.width * cell, AREA_WIDTH_MM + 1e-9)
            self.assertLessEqual(maze.height * cell, AREA_HEIGHT_MM + 1e-9)
            self.assertGreaterEqual(offset_x, 0)
            self.assertLessEqual(offset_x + maze.width * cell, 210)
            self.assertGreaterEqual(offset_y, 22)
            self.assertLessEqual(offset_y + maze.height * cell, 272)

    def test_solution_points_include_entrance_and_exit(self) -> None:
        maze = generate_maze(10, 10, seed=2)
        points = solution_points(maze)
        self.assertEqual(len(points), len(maze.solution()) + 2)
        self.assertLess(points[0][1], points[1][1])
        self.assertGreater(points[-1][1], points[-2][1])


class SvgTest(unittest.TestCase):
    def setUp(self) -> None:
        self.maze = generate_maze(15, 12, seed=3)

    def test_viewbox(self) -> None:
        svg = render_svg(self.maze)
        self.assertIn('viewBox="0 0 210 297"', svg)
        self.assertTrue(svg.endswith("</svg>"))

    def test_wall_line_count(self) -> None:
        svg = render_svg(self.maze)
        self.assertEqual(svg.count("<line"), len(wall_segments(self.maze)))

    def test_entrance_and_exit_labels(self) -> None:
        svg = render_svg(self.maze)
        self.assertIn(">入口</text>", svg)
        self.assertIn(">出口</text>", svg)

    def test_no_solution_by_default(self) -> None:
        svg = render_svg(self.maze)
        self.assertNotIn("<polyline", svg)
        self.assertIn("从入口走到出口", svg)

    def test_solution_polyline(self) -> None:
        svg = render_svg(self.maze, show_solution=True)
        self.assertIn("<polyline", svg)
        self.assertIn('stroke="#ef4444"', svg)

    def test_solution_has_start_and_end_dots(self) -> None:
        svg = render_svg(self.maze, show_solution=True)
        self.assertEqual(svg.count("<circle"), 2)

    def test_answer_title(self) -> None:
        svg = render_svg(self.maze, show_solution=True)
        self.assertIn("（答案）", svg)

    def test_footer_reports_steps(self) -> None:
        steps = len(self.maze.solution()) - 1
        svg = render_svg(self.maze, show_solution=True)
        self.assertIn("通路 %d 步" % steps, svg)

    def test_page_numbers(self) -> None:
        svg = render_svg(self.maze, index=1, total=2)
        self.assertIn("第 2 / 2 页", svg)

    def test_title_is_escaped(self) -> None:
        svg = render_svg(self.maze, title="<迷宫>")
        self.assertIn("&lt;迷宫&gt;", svg)
        self.assertNotIn("<迷宫>", svg)

    def test_rejects_blank_title(self) -> None:
        with self.assertRaises(MazeError):
            render_svg(self.maze, title="  ")

    def test_rejects_bad_page_numbers(self) -> None:
        with self.assertRaises(MazeError):
            render_svg(self.maze, index=2, total=2)
        with self.assertRaises(MazeError):
            render_svg(self.maze, index=0, total=0)
        with self.assertRaises(MazeError):
            render_svg(self.maze, index=0.5, total=2)  # type: ignore[arg-type]
        with self.assertRaises(MazeError):
            render_svg(self.maze, index=0, total=2.0)  # type: ignore[arg-type]


class HtmlTest(unittest.TestCase):
    def setUp(self) -> None:
        self.maze = generate_maze(12, 12, seed=8)

    def test_one_page_without_solution(self) -> None:
        html = render_html(self.maze, show_solution=False)
        self.assertEqual(html.count('<section class="sheet">'), 1)

    def test_two_pages_with_solution(self) -> None:
        html = render_html(self.maze, show_solution=True)
        self.assertEqual(html.count('<section class="sheet">'), 2)
        self.assertEqual(html.count("<svg"), 2)

    def test_doctype_and_language(self) -> None:
        html = render_html(self.maze)
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn('lang="zh-CN"', html)

    def test_print_styles(self) -> None:
        html = render_html(self.maze)
        self.assertIn("@page { size: A4 portrait; margin: 0; }", html)
        self.assertIn(".toolbar { display: none; }", html)

    def test_toolbar_mentions_size(self) -> None:
        html = render_html(self.maze)
        self.assertIn("12×12 格", html)

    def test_title_is_escaped(self) -> None:
        html = render_html(self.maze, title="<迷宫>")
        self.assertIn("&lt;迷宫&gt;", html)
        self.assertNotIn("<迷宫>", html)

    def test_blank_title_rejected(self) -> None:
        with self.assertRaises(MazeError):
            render_html(self.maze, title="")


if __name__ == "__main__":
    unittest.main()
