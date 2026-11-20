# maze

[![CI](https://github.com/eastyou/maze/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/maze/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

给课堂和家庭用的迷宫生成器：指定宽高和种子，一条命令生成一页 A4 迷宫，可选附答案页。**零依赖，不联网，矢量 SVG，打印清晰。**

迷宫用深度优先搜索挖成，保证任意两格之间只有一条路，不会出现无解或环路；答案页用广度优先搜索求最短通路。

## 特性

- **完美迷宫**：DFS 随机挖洞，所有格子连通且没有环
- **入口出口明确**：左上角开口进，右下角开口出，配绿色/红色箭头
- **答案页可选**：`--solution` 追加一页，用红线标出最短通路并统计步数
- **尺寸可调**：5~60 格，自动按 A4 可用区域缩放，格子保持正方形
- **固定种子**：`--seed` 复现同一张迷宫，方便批量出题
- **矢量输出**：墙和通路都是 SVG 线段，放大打印不糊
- **参数校验**：宽高、种子、标题不合法时给出中文提示，退出码为 2
- **65 个单元测试**：覆盖连通性、墙壁对称、通路合法性、墙体去重与 HTML 输出

## 安装

```bash
pip install maze
```

也可以直接下载源码，在项目目录里运行：

```bash
python -m maze --help
```

## 用法

生成一张 15×22 的迷宫，附答案页：

```bash
maze --width 15 --height 22 --seed 2026 --solution -o 迷宫.html
```

给低年级学生生成简单的小迷宫，不要答案：

```bash
maze --width 8 --height 8 --title "课间小迷宫" -o 小迷宫.html
```

打印一整页大迷宫，答案留给老师：

```bash
maze --width 25 --height 35 --seed 42 --solution -o 挑战迷宫.html
```

## 参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--width` | `15` | 宽度格数，5~60 |
| `--height` | `22` | 高度格数，5~60 |
| `--seed` | 无 | 随机种子，相同种子生成相同迷宫 |
| `--solution` | 关闭 | 追加一页带通路的答案 |
| `--title` | `迷宫` | 页面标题，答案页自动加「（答案）」 |
| `-o, --output` | `迷宫.html` | 输出文件路径 |

## 生成规则

1. 所有格子初始四面都是墙
2. 从左上角开始深度优先搜索，随机选择未访问的邻居，打通两格之间的墙
3. 每个格子只访问一次，因此恰好打通「格数 − 1」条通道，形成无环的完美迷宫
4. 打开左上角的上边界和右下角的下边界，作为入口与出口
5. 求解时从入口做广度优先搜索，得到唯一的最短通路

命令结束时会在终端报告最短通路步数；答案页页脚也会标注同样的数字。

## 打印

浏览器打开 HTML，按 `Ctrl/Cmd + P`，纸张选 A4 纵向，边距选「无」，缩放 100%。迷宫区域为 180×250 毫米，四周留有页边距，不会被裁掉。

如果想让学生自己画路线，只打印第一页即可；答案页永远是最后一页。

## 开发

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE) © 2026 eastyou
