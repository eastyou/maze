"""命令行入口：生成可打印的迷宫与答案页。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .maze import MazeError, generate_maze
from .render import render_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maze",
        description="迷宫生成器：按格数生成完美迷宫，可选附答案页",
    )
    parser.add_argument("--version", action="version", version="maze 0.1.0")
    parser.add_argument("--width", type=int, default=15, help="宽度格数，5~60，默认 15")
    parser.add_argument("--height", type=int, default=22, help="高度格数，5~60，默认 22")
    parser.add_argument("--seed", type=int, default=None, help="随机种子，便于复现")
    parser.add_argument(
        "--solution", action="store_true", help="附加一页带通路的答案"
    )
    parser.add_argument("--title", default="迷宫", help="页面标题")
    parser.add_argument("-o", "--output", default="迷宫.html", help="输出 HTML 路径")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        maze = generate_maze(args.width, args.height, seed=args.seed)
        page = render_html(maze, title=args.title, show_solution=args.solution)
    except MazeError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    steps = len(maze.solution()) - 1
    print(
        "已生成 %s：%d×%d 格，最短通路 %d 步"
        % (args.output, maze.width, maze.height, steps)
    )
    if args.solution:
        print("答案页已附在迷宫页之后")
    print("用浏览器打开后按 Ctrl/Cmd + P，纸张选 A4 纵向即可打印")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
