"""迷宫生成与求解的单元测试。"""

from __future__ import annotations

import unittest
from collections import deque
from typing import List, Set, Tuple

from maze.maze import (
    EAST,
    NORTH,
    SOUTH,
    WEST,
    Maze,
    MazeError,
    generate_maze,
    wall_segments,
)


def reachable_cells(maze: Maze) -> Set[Tuple[int, int]]:
    seen: Set[Tuple[int, int]] = {(0, 0)}
    queue: deque = deque([(0, 0)])
    while queue:
        x, y = queue.popleft()
        for neighbor in maze.open_neighbors(x, y):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


class GenerateMazeTest(unittest.TestCase):
    def test_dimensions(self) -> None:
        maze = generate_maze(9, 7, seed=1)
        self.assertEqual(maze.width, 9)
        self.assertEqual(maze.height, 7)
        self.assertEqual(len(maze.cells), 63)

    def test_seed_is_kept(self) -> None:
        self.assertEqual(generate_maze(6, 6, seed=42).seed, 42)
        self.assertIsNone(generate_maze(6, 6).seed)

    def test_all_cells_are_reachable(self) -> None:
        maze = generate_maze(12, 10, seed=3)
        self.assertEqual(len(reachable_cells(maze)), 120)

    def test_perfect_maze_edge_count(self) -> None:
        maze = generate_maze(10, 8, seed=5)
        edges = sum(len(maze.open_neighbors(x, y)) for y in range(8) for x in range(10))
        self.assertEqual(edges // 2, 10 * 8 - 1)
        self.assertEqual(edges % 2, 0)

    def test_walls_are_symmetric(self) -> None:
        maze = generate_maze(8, 8, seed=11)
        for y in range(maze.height):
            for x in range(maze.width):
                if x + 1 < maze.width:
                    self.assertEqual(
                        maze.has_wall(x, y, EAST), maze.has_wall(x + 1, y, WEST)
                    )
                if y + 1 < maze.height:
                    self.assertEqual(
                        maze.has_wall(x, y, SOUTH), maze.has_wall(x, y + 1, NORTH)
                    )

    def test_entrance_and_exit_are_open(self) -> None:
        maze = generate_maze(7, 7, seed=2)
        self.assertFalse(maze.has_wall(0, 0, NORTH))
        self.assertFalse(maze.has_wall(maze.width - 1, maze.height - 1, SOUTH))

    def test_other_border_walls_stay_closed(self) -> None:
        maze = generate_maze(7, 7, seed=2)
        self.assertTrue(maze.has_wall(0, 0, WEST))
        self.assertTrue(maze.has_wall(0, 0, SOUTH))
        self.assertTrue(maze.has_wall(maze.width - 1, maze.height - 1, EAST))
        for x in range(1, maze.width):
            self.assertTrue(maze.has_wall(x, 0, NORTH))

    def test_same_seed_reproduces(self) -> None:
        self.assertEqual(
            generate_maze(14, 14, seed=2026).cells,
            generate_maze(14, 14, seed=2026).cells,
        )

    def test_different_seed_changes_layout(self) -> None:
        self.assertNotEqual(
            generate_maze(14, 14, seed=1).cells,
            generate_maze(14, 14, seed=2).cells,
        )

    def test_minimum_size(self) -> None:
        maze = generate_maze(5, 5, seed=0)
        self.assertEqual(len(reachable_cells(maze)), 25)

    def test_maximum_size(self) -> None:
        maze = generate_maze(60, 60, seed=7)
        self.assertEqual(len(reachable_cells(maze)), 3600)

    def test_width_too_small(self) -> None:
        with self.assertRaises(MazeError) as ctx:
            generate_maze(4, 10)
        self.assertIn("宽度", str(ctx.exception))

    def test_height_too_large(self) -> None:
        with self.assertRaises(MazeError) as ctx:
            generate_maze(10, 61)
        self.assertIn("高度", str(ctx.exception))

    def test_size_must_be_integer(self) -> None:
        for value in (10.0, "10", True):
            with self.assertRaises(MazeError):
                generate_maze(value, 10)  # type: ignore[arg-type]

    def test_seed_must_be_integer(self) -> None:
        for value in (1.5, "2026", True):
            with self.assertRaises(MazeError):
                generate_maze(10, 10, seed=value)  # type: ignore[arg-type]


class SolutionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.maze = generate_maze(15, 12, seed=9)
        self.path = self.maze.solution()

    def test_starts_and_ends_at_corners(self) -> None:
        self.assertEqual(self.path[0], (0, 0))
        self.assertEqual(self.path[-1], (14, 11))

    def test_path_is_continuous(self) -> None:
        for (x1, y1), (x2, y2) in zip(self.path, self.path[1:]):
            self.assertEqual(abs(x1 - x2) + abs(y1 - y2), 1)
            self.assertIn((x2, y2), self.maze.open_neighbors(x1, y1))

    def test_path_has_no_repeated_cells(self) -> None:
        self.assertEqual(len(self.path), len(set(self.path)))

    def test_path_is_not_shorter_than_manhattan(self) -> None:
        self.assertGreaterEqual(len(self.path) - 1, 14 + 11)

    def test_path_stays_in_bounds(self) -> None:
        for x, y in self.path:
            self.assertTrue(0 <= x < self.maze.width)
            self.assertTrue(0 <= y < self.maze.height)


class MazeValidationTest(unittest.TestCase):
    def test_wrong_cell_count(self) -> None:
        with self.assertRaises(MazeError) as ctx:
            Maze(width=5, height=5, cells=(0,) * 24)
        self.assertIn("墙壁数量", str(ctx.exception))

    def test_invalid_wall_bits(self) -> None:
        with self.assertRaises(MazeError):
            Maze(width=5, height=5, cells=(16,) * 25)

    def test_invalid_size(self) -> None:
        with self.assertRaises(MazeError):
            Maze(width=4, height=5, cells=(0,) * 20)

    def test_index_out_of_bounds(self) -> None:
        maze = generate_maze(5, 5, seed=1)
        with self.assertRaises(MazeError):
            maze.index(5, 0)
        with self.assertRaises(MazeError):
            maze.index(-1, 0)

    def test_unknown_direction(self) -> None:
        maze = generate_maze(5, 5, seed=1)
        with self.assertRaises(MazeError):
            maze.has_wall(0, 0, 16)

    def test_open_neighbors_of_corner(self) -> None:
        maze = generate_maze(5, 5, seed=1)
        for x, y in maze.open_neighbors(0, 0):
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)


class WallSegmentsTest(unittest.TestCase):
    def test_perfect_maze_wall_count(self) -> None:
        for width, height, seed in ((9, 9, 1), (15, 12, 2), (5, 5, 3)):
            maze = generate_maze(width, height, seed=seed)
            internal = (width - 1) * height + width * (height - 1) - (width * height - 1)
            border = 2 * width + 2 * height - 2
            self.assertEqual(len(wall_segments(maze)), internal + border)

    def test_segments_are_unique(self) -> None:
        maze = generate_maze(12, 10, seed=4)
        segments = wall_segments(maze)
        self.assertEqual(len(segments), len(set(segments)))

    def test_segments_are_axis_aligned(self) -> None:
        maze = generate_maze(8, 8, seed=6)
        for x1, y1, x2, y2 in wall_segments(maze):
            self.assertTrue(x1 == x2 or y1 == y2)

    def test_segments_stay_within_grid(self) -> None:
        maze = generate_maze(8, 8, seed=6)
        for x1, y1, x2, y2 in wall_segments(maze):
            self.assertTrue(0 <= x1 <= maze.width)
            self.assertTrue(0 <= x2 <= maze.width)
            self.assertTrue(0 <= y1 <= maze.height)
            self.assertTrue(0 <= y2 <= maze.height)

    def test_segment_list_is_stable(self) -> None:
        maze = generate_maze(8, 8, seed=6)
        self.assertEqual(wall_segments(maze), wall_segments(maze))


if __name__ == "__main__":
    unittest.main()
