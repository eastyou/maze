"""把迷宫渲染成可打印的 A4 SVG 与 HTML。"""

from __future__ import annotations

import html
from typing import List, Tuple

from .maze import Maze, MazeError, wall_segments

PAGE_WIDTH_MM = 210.0
PAGE_HEIGHT_MM = 297.0
AREA_LEFT_MM = 15.0
AREA_TOP_MM = 22.0
AREA_WIDTH_MM = 180.0
AREA_HEIGHT_MM = 250.0


def _num(value: float) -> str:
    text = "%.3f" % value
    return text.rstrip("0").rstrip(".") if "." in text else text


def maze_geometry(maze: Maze) -> Tuple[float, float, float]:
    """返回（格子边长, 左上角 x, 左上角 y），单位毫米。"""
    cell = min(AREA_WIDTH_MM / maze.width, AREA_HEIGHT_MM / maze.height)
    offset_x = (PAGE_WIDTH_MM - maze.width * cell) / 2
    offset_y = AREA_TOP_MM + (AREA_HEIGHT_MM - maze.height * cell) / 2
    return cell, offset_x, offset_y


def solution_points(maze: Maze) -> List[Tuple[float, float]]:
    """通路折线，从入口外沿到出口外沿。"""
    cell, offset_x, offset_y = maze_geometry(maze)
    stub = max(0.8, cell * 0.3)
    points: List[Tuple[float, float]] = [
        (offset_x + cell / 2, offset_y - stub)
    ]
    for x, y in maze.solution():
        points.append(
            (offset_x + (x + 0.5) * cell, offset_y + (y + 0.5) * cell)
        )
    points.append(
        (offset_x + (maze.width - 0.5) * cell, offset_y + maze.height * cell + stub)
    )
    return points


def _wall_markup(maze: Maze) -> List[str]:
    cell, offset_x, offset_y = maze_geometry(maze)
    width = max(0.3, min(0.9, cell * 0.16))
    parts: List[str] = []
    for x1, y1, x2, y2 in wall_segments(maze):
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" '
            'stroke="#0f172a" stroke-width="%s" stroke-linecap="square"/>'
            % (
                _num(offset_x + x1 * cell),
                _num(offset_y + y1 * cell),
                _num(offset_x + x2 * cell),
                _num(offset_y + y2 * cell),
                _num(width),
            )
        )
    return parts


def _entrance_markup(maze: Maze) -> List[str]:
    cell, offset_x, offset_y = maze_geometry(maze)
    center_x = offset_x + cell / 2
    size = max(1.4, min(2.6, cell * 0.5))
    parts = [
        '<polygon points="%s,%s %s,%s %s,%s" fill="#16a34a"/>'
        % (
            _num(center_x - size),
            _num(offset_y - size * 2.6),
            _num(center_x + size),
            _num(offset_y - size * 2.6),
            _num(center_x),
            _num(offset_y - size * 0.6),
        ),
        '<text x="%s" y="%s" font-size="3.6" text-anchor="middle" '
        'fill="#16a34a">入口</text>'
        % (_num(center_x), _num(offset_y - size * 3.2)),
    ]
    exit_x = offset_x + (maze.width - 0.5) * cell
    bottom = offset_y + maze.height * cell
    parts.extend(
        [
            '<polygon points="%s,%s %s,%s %s,%s" fill="#dc2626"/>'
            % (
                _num(exit_x - size),
                _num(bottom + size * 0.6),
                _num(exit_x + size),
                _num(bottom + size * 0.6),
                _num(exit_x),
                _num(bottom + size * 2.6),
            ),
            '<text x="%s" y="%s" font-size="3.6" text-anchor="middle" '
            'fill="#dc2626">出口</text>'
            % (_num(exit_x), _num(bottom + size * 4.2)),
        ]
    )
    return parts


def _solution_markup(maze: Maze) -> List[str]:
    cell, offset_x, offset_y = maze_geometry(maze)
    points = solution_points(maze)
    polyline = " ".join("%s,%s" % (_num(x), _num(y)) for x, y in points)
    radius = max(0.7, min(1.6, cell * 0.22))
    last = (maze.width - 1, maze.height - 1)
    return [
        '<polyline points="%s" fill="none" stroke="#ef4444" stroke-width="%s" '
        'stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
        % (polyline, _num(max(0.5, min(1.3, cell * 0.3)))),
        '<circle cx="%s" cy="%s" r="%s" fill="#16a34a"/>'
        % (
            _num(offset_x + cell / 2),
            _num(offset_y + cell / 2),
            _num(radius),
        ),
        '<circle cx="%s" cy="%s" r="%s" fill="#dc2626"/>'
        % (
            _num(offset_x + (last[0] + 0.5) * cell),
            _num(offset_y + (last[1] + 0.5) * cell),
            _num(radius),
        ),
    ]


def render_svg(
    maze: Maze,
    title: str = "迷宫",
    show_solution: bool = False,
    index: int = 0,
    total: int = 1,
) -> str:
    """生成一页 SVG。"""
    if not isinstance(title, str) or not title.strip():
        raise MazeError("标题不能为空")
    if isinstance(index, bool) or not isinstance(index, int):
        raise MazeError("页码必须是整数")
    if isinstance(total, bool) or not isinstance(total, int):
        raise MazeError("总页数必须是整数")
    if total < 1 or not 0 <= index < total:
        raise MazeError("页码超出范围：%d（共 %d 页）" % (index + 1, total))

    label = title.strip() + ("（答案）" if show_solution else "")
    steps = len(maze.solution()) - 1

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%smm" height="%smm" '
        'viewBox="0 0 %s %s">'
        % (
            _num(PAGE_WIDTH_MM),
            _num(PAGE_HEIGHT_MM),
            _num(PAGE_WIDTH_MM),
            _num(PAGE_HEIGHT_MM),
        ),
        '<rect width="%s" height="%s" fill="#ffffff"/>'
        % (_num(PAGE_WIDTH_MM), _num(PAGE_HEIGHT_MM)),
        '<text x="%s" y="10.5" font-size="5.6" font-weight="600" '
        'text-anchor="middle" fill="#0f172a">%s</text>'
        % (_num(PAGE_WIDTH_MM / 2), html.escape(label)),
    ]
    if show_solution:
        parts.extend(_solution_markup(maze))
    parts.extend(_wall_markup(maze))
    parts.extend(_entrance_markup(maze))

    if show_solution:
        footer = "maze · %d×%d 格 · 通路 %d 步" % (maze.width, maze.height, steps)
    else:
        footer = "maze · %d×%d 格 · 从入口走到出口" % (maze.width, maze.height)
    parts.append(
        '<text x="15" y="291" font-size="2.8" fill="#94a3b8">%s</text>'
        % html.escape(footer)
    )
    parts.append(
        '<text x="195" y="291" font-size="2.8" text-anchor="end" '
        'fill="#94a3b8">第 %d / %d 页</text>' % (index + 1, total)
    )
    parts.append("</svg>")
    return "\n".join(parts)


STYLE = """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 8mm 0 12mm;
    background: #e2e8f0;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  .toolbar {
    width: 210mm;
    margin: 0 auto 6mm;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    color: #334155;
    font-size: 13px;
  }
  .toolbar strong { font-size: 15px; letter-spacing: 1px; }
  .toolbar span { color: #64748b; font-size: 12px; }
  .sheet {
    width: 210mm;
    height: 297mm;
    margin: 0 auto 8mm;
    background: #fff;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14);
    overflow: hidden;
    page-break-after: always;
    break-after: page;
  }
  .sheet:last-child { page-break-after: auto; break-after: auto; }
  .sheet svg { display: block; }
  @page { size: A4 portrait; margin: 0; }
  @media print {
    body { background: #fff; padding: 0; }
    .toolbar { display: none; }
    .sheet { margin: 0; box-shadow: none; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
"""


def render_html(
    maze: Maze, title: str = "迷宫", show_solution: bool = True
) -> str:
    """生成完整 HTML；答案页另起一页。"""
    if not isinstance(title, str) or not title.strip():
        raise MazeError("标题不能为空")

    pages = 2 if show_solution else 1
    sheets: List[str] = []
    for page in range(pages):
        sheets.append(
            '<section class="sheet">%s</section>'
            % render_svg(
                maze,
                title=title,
                show_solution=page == 1,
                index=page,
                total=pages,
            )
        )

    toolbar = (
        '<div class="toolbar"><strong>%s</strong>'
        "<span>共 %d×%d 格 · 从上方入口进入，下方出口走出%s</span></div>"
        % (
            html.escape(title.strip()),
            maze.width,
            maze.height,
            " · 第二页为答案" if show_solution else "",
        )
    )

    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n%s\n</body>\n</html>\n"
        % (
            html.escape(title.strip()),
            STYLE,
            toolbar,
            "\n".join(sheets),
        )
    )
