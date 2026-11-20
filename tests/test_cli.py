"""命令行入口的单元测试。"""

from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from maze.cli import main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_cli(self, argv: list) -> tuple:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_generate_default(self) -> None:
        output = self.tmp / "m.html"
        code, out, err = self.run_cli(["-o", str(output)])
        self.assertEqual(code, 0, err)
        self.assertTrue(output.exists())
        self.assertIn("15×22 格", out)
        self.assertIn("最短通路", out)

    def test_solution_page(self) -> None:
        output = self.tmp / "m.html"
        code, out, err = self.run_cli(
            ["--solution", "-o", str(output), "--seed", "2026"]
        )
        self.assertEqual(code, 0, err)
        content = output.read_text(encoding="utf-8")
        self.assertEqual(content.count('<section class="sheet">'), 2)
        self.assertIn("答案页已附", out)

    def test_no_solution_page(self) -> None:
        output = self.tmp / "m.html"
        self.assertEqual(self.run_cli(["-o", str(output)])[0], 0)
        content = output.read_text(encoding="utf-8")
        self.assertEqual(content.count('<section class="sheet">'), 1)

    def test_seed_reproduces_same_file(self) -> None:
        first = self.tmp / "a.html"
        second = self.tmp / "b.html"
        base = ["--width", "10", "--height", "10", "--seed", "7", "--solution"]
        self.assertEqual(self.run_cli(base + ["-o", str(first)])[0], 0)
        self.assertEqual(self.run_cli(base + ["-o", str(second)])[0], 0)
        self.assertEqual(
            first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8")
        )

    def test_different_seed_differs(self) -> None:
        first = self.tmp / "a.html"
        second = self.tmp / "b.html"
        self.assertEqual(
            self.run_cli(["--seed", "1", "-o", str(first), "--width", "12"])[0], 0
        )
        self.assertEqual(
            self.run_cli(["--seed", "2", "-o", str(second), "--width", "12"])[0], 0
        )
        self.assertNotEqual(
            first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8")
        )

    def test_custom_size_and_title(self) -> None:
        output = self.tmp / "m.html"
        code, out, _ = self.run_cli(
            ["--width", "8", "--height", "8", "--title", "课堂小迷宫", "-o", str(output)]
        )
        self.assertEqual(code, 0)
        self.assertIn("8×8 格", out)
        self.assertIn("课堂小迷宫", output.read_text(encoding="utf-8"))

    def test_default_output_name(self) -> None:
        cwd = os.getcwd()
        os.chdir(self.tmp)
        try:
            code, _, err = self.run_cli(["--width", "6", "--height", "6"])
            self.assertEqual(code, 0, err)
            self.assertTrue((self.tmp / "迷宫.html").exists())
        finally:
            os.chdir(cwd)

    def test_invalid_width(self) -> None:
        code, _, err = self.run_cli(["--width", "4"])
        self.assertEqual(code, 2)
        self.assertIn("宽度", err)

    def test_invalid_height(self) -> None:
        code, _, err = self.run_cli(["--height", "61"])
        self.assertEqual(code, 2)
        self.assertIn("高度", err)

    def test_invalid_title(self) -> None:
        code, _, err = self.run_cli(["--title", "   "])
        self.assertEqual(code, 2)
        self.assertIn("标题", err)

    def test_write_failure(self) -> None:
        code, _, err = self.run_cli(["-o", str(self.tmp)])
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)

    def test_help_exits_zero(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
