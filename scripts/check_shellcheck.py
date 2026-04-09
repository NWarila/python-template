#!/usr/bin/env python3
# Managed by nwarila/python-template — do not edit manually.
# Source: https://github.com/nwarila/python-template
"""Lint shell scripts with ShellCheck.

Usage:
    python .github/scripts/check_shellcheck.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def _find_project_root() -> Path:
    d = SCRIPT_DIR
    while d != d.parent:
        if (d / "pyproject.toml").exists():
            return d
        d = d.parent
    print("Error: could not find pyproject.toml", file=sys.stderr)
    sys.exit(1)


PROJECT_ROOT = _find_project_root()


def main() -> int:
    shellcheck = shutil.which("shellcheck")
    if shellcheck is None:
        print(
            "Error: shellcheck not found on PATH.\n"
            "  Install: scoop install shellcheck  (Windows)\n"
            "           brew install shellcheck    (macOS)\n"
            "           apt install shellcheck     (Linux)",
            file=sys.stderr,
        )
        return 1
    scripts = sorted((PROJECT_ROOT / ".github" / "scripts").glob("*.sh"))
    if not scripts:
        print("No shell scripts found to check.")
        return 0
    result = subprocess.run(
        [shellcheck, *[str(s) for s in scripts]],
        cwd=PROJECT_ROOT,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
