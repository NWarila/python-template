#!/usr/bin/env python3
# Managed by nwarila/python-template — do not edit manually.
# Source: https://github.com/nwarila/python-template
"""Lint GitHub Actions workflow files with actionlint.

Usage:
    python .github/scripts/check_actionlint.py
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
    actionlint = shutil.which("actionlint")
    if actionlint is None:
        print(
            "Error: actionlint not found on PATH.\n"
            "  Install: scoop install actionlint  (Windows)\n"
            "           brew install actionlint    (macOS)\n"
            "           go install github.com/rhysd/actionlint/cmd/actionlint@latest  (Go)",
            file=sys.stderr,
        )
        return 1
    result = subprocess.run(
        [actionlint],
        cwd=PROJECT_ROOT,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
