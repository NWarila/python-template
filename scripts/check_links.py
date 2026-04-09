#!/usr/bin/env python3
# Managed by nwarila/python-template — do not edit manually.
# Source: https://github.com/nwarila/python-template
"""Check links in Markdown files with lychee.

Usage:
    python .github/scripts/check_links.py
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


def _load_excluded_domains() -> list[str]:
    """Load excluded domains from .lychee.toml if present, else use defaults."""
    config = PROJECT_ROOT / ".lychee.toml"
    if config.exists():
        return []  # Let lychee read its own config
    return [
        "linkedin.com",
    ]


def main() -> int:
    lychee = shutil.which("lychee")
    if lychee is None:
        print(
            "Error: lychee not found on PATH.\n"
            "  Install: scoop install lychee   (Windows)\n"
            "           brew install lychee    (macOS)\n"
            "           cargo install lychee   (Rust)",
            file=sys.stderr,
        )
        return 1
    cmd = [lychee, "--no-progress"]
    for domain in _load_excluded_domains():
        cmd.extend(["--exclude", domain])
    cmd.append("**/*.md")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
