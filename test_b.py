#!/usr/bin/env python3
"""Exercise the public Bash commands with an isolated home directory."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().with_name("b.sh")


class BookmarkTests(unittest.TestCase):
    def test_commands(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            home.mkdir()
            first = root / "directory with spaces"
            first.mkdir()
            second = root / "second"
            second.mkdir()
            environment = dict(os.environ, HOME=str(home))

            def run(commands, success=True):
                result = subprocess.run(
                    ["bash", "--noprofile", "--norc", "-c", commands,
                     "test", str(SCRIPT), str(first), str(second)],
                    cwd=root,
                    env=environment,
                    capture_output=True,
                    text=True,
                )
                if success:
                    self.assertEqual(result.returncode, 0, result.stderr)
                else:
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                return result

            run('source "$1"; b missing', success=False)
            run('"$1" register work "$2"')
            bookmarks = home / ".bmarks"
            self.assertEqual(bookmarks.stat().st_mode & 0o777, 0o600)
            self.assertEqual(bookmarks.read_text(), f"work\t{first}\n")
            run('source "$1"; b work && [[ $PWD == "$2" ]]')
            run('source "$1"; b register other ./second && b other && [[ $PWD == "$3" ]]')
            run('source "$1"; b register work "$3" && b work && [[ $PWD == "$3" ]]')
            run('source "$1"; b other && [[ $PWD == "$3" ]]')

            before = bookmarks.read_bytes()
            for command in (
                'b register',
                'b register bad /does/not/exist',
                'b register "bad name" "$2"',
                'b register register "$2"',
                'b register bad "$2" extra',
                'b register bad $\'tab\\tpath\'',
                'b register bad $\'new\\nline\'',
                'b unknown',
                'b',
                'b work extra',
            ):
                with self.subTest(command=command):
                    run('source "$1"; ' + command, success=False)
                    self.assertEqual(bookmarks.read_bytes(), before)

            run('"$1" work', success=False)
            run('source "$1"; b --help')
            unusual = root / "newline\n"
            unusual.mkdir()
            (root / "link").symlink_to(unusual, target_is_directory=True)
            run('source "$1"; b register invalid ./link', success=False)
            self.assertEqual(bookmarks.read_bytes(), before)
            second.rmdir()
            run('source "$1"; b work', success=False)

            # Stored paths are data even when they contain shell syntax.
            literal = root / '$(touch owned); "quoted" \\ folder'
            literal.mkdir()
            run(
                f'source "$1"; b register literal \'{literal}\' '
                f'&& b literal && [[ $PWD == \'{literal}\' ]]'
            )
            self.assertFalse((root / "owned").exists())


if __name__ == "__main__":
    unittest.main()
