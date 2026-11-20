"""maze：可打印迷宫生成器。"""

from __future__ import annotations

from .maze import (
    ALL_WALLS,
    EAST,
    MAX_SIZE,
    MIN_SIZE,
    NORTH,
    SOUTH,
    WEST,
    Maze,
    MazeError,
    generate_maze,
    wall_segments,
)
from .render import maze_geometry, render_html, render_svg, solution_points

__version__ = "0.1.0"

__all__ = [
    "ALL_WALLS",
    "EAST",
    "MAX_SIZE",
    "MIN_SIZE",
    "NORTH",
    "SOUTH",
    "WEST",
    "Maze",
    "MazeError",
    "generate_maze",
    "maze_geometry",
    "render_html",
    "render_svg",
    "solution_points",
    "wall_segments",
    "__version__",
]
