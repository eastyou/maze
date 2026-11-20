"""迷宫生成、连通性检查与最短通路求解。"""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

MIN_SIZE = 5
MAX_SIZE = 60

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST

DIRECTIONS: Dict[int, Tuple[int, int]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}
OPPOSITE = {NORTH: SOUTH, EAST: WEST, SOUTH: NORTH, WEST: EAST}
DIRECTION_NAMES = {NORTH: "上", EAST: "右", SOUTH: "下", WEST: "左"}


class MazeError(ValueError):
    """迷宫参数或数据不合法。"""


@dataclass(frozen=True)
class Maze:
    """按格子保存墙壁位掩码的完美迷宫。"""

    width: int
    height: int
    cells: Tuple[int, ...]
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        _validate_size(self.width, self.height)
        if len(self.cells) != self.width * self.height:
            raise MazeError(
                "墙壁数量与尺寸不符：应为 %d，实际 %d"
                % (self.width * self.height, len(self.cells))
            )
        if any(value & ~ALL_WALLS for value in self.cells):
            raise MazeError("墙壁位掩码超出范围")

    def index(self, x: int, y: int) -> int:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise MazeError("坐标越界：(%d, %d)" % (x, y))
        return y * self.width + x

    def walls_at(self, x: int, y: int) -> int:
        return self.cells[self.index(x, y)]

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        if direction not in DIRECTIONS:
            raise MazeError("未知方向：%r" % (direction,))
        return bool(self.walls_at(x, y) & direction)

    def open_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """返回与 (x, y) 连通且没有墙的相邻格子。"""
        neighbors: List[Tuple[int, int]] = []
        for direction in (NORTH, EAST, SOUTH, WEST):
            if self.has_wall(x, y, direction):
                continue
            dx, dy = DIRECTIONS[direction]
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))
        return neighbors

    def solution(self) -> List[Tuple[int, int]]:
        """从左上角到右下角的最短通路。"""
        start = (0, 0)
        goal = (self.width - 1, self.height - 1)
        parents: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        queue: deque = deque([start])

        while queue:
            node = queue.popleft()
            if node == goal:
                break
            for neighbor in self.open_neighbors(node[0], node[1]):
                if neighbor not in parents:
                    parents[neighbor] = node
                    queue.append(neighbor)

        if goal not in parents:
            raise MazeError("迷宫不连通，无法求解")

        path: List[Tuple[int, int]] = []
        current: Optional[Tuple[int, int]] = goal
        while current is not None:
            path.append(current)
            current = parents[current]
        path.reverse()
        return path


def _validate_size(width: int, height: int) -> None:
    for value, label in ((width, "宽度"), (height, "高度")):
        if isinstance(value, bool) or not isinstance(value, int):
            raise MazeError("%s必须是整数格数，收到 %r" % (label, value))
        if not MIN_SIZE <= value <= MAX_SIZE:
            raise MazeError(
                "%s必须在 %d~%d 格之间，收到 %d"
                % (label, MIN_SIZE, MAX_SIZE, value)
            )


def generate_maze(width: int, height: int, seed: Optional[int] = None) -> Maze:
    """用深度优先搜索挖出一条没有环的完美迷宫。"""
    _validate_size(width, height)
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
        raise MazeError("随机种子必须是整数，收到 %r" % (seed,))

    rng = random.Random(seed)
    total = width * height
    walls = [ALL_WALLS] * total
    visited = [False] * total
    visited[0] = True
    stack: List[Tuple[int, int]] = [(0, 0)]

    while stack:
        x, y = stack[-1]
        options: List[int] = []
        for direction in (NORTH, EAST, SOUTH, WEST):
            dx, dy = DIRECTIONS[direction]
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if not visited[ny * width + nx]:
                    options.append(direction)

        if not options:
            stack.pop()
            continue

        direction = rng.choice(options)
        dx, dy = DIRECTIONS[direction]
        nx, ny = x + dx, y + dy
        walls[y * width + x] &= ~direction
        walls[ny * width + nx] &= ~OPPOSITE[direction]
        visited[ny * width + nx] = True
        stack.append((nx, ny))

    # 左上角开入口，右下角开出口。
    walls[0] &= ~NORTH
    walls[-1] &= ~SOUTH
    return Maze(width=width, height=height, cells=tuple(walls), seed=seed)


def wall_segments(maze: Maze) -> List[Tuple[float, float, float, float]]:
    """把墙壁转成不重复的线段，坐标以格为单位。"""
    segments: List[Tuple[float, float, float, float]] = []
    for y in range(maze.height):
        for x in range(maze.width):
            walls = maze.walls_at(x, y)
            if walls & NORTH:
                segments.append((float(x), float(y), float(x + 1), float(y)))
            if walls & WEST:
                segments.append((float(x), float(y), float(x), float(y + 1)))
            if y == maze.height - 1 and walls & SOUTH:
                segments.append((float(x), float(y + 1), float(x + 1), float(y + 1)))
            if x == maze.width - 1 and walls & EAST:
                segments.append((float(x + 1), float(y), float(x + 1), float(y + 1)))
    return segments
