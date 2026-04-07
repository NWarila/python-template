#!/usr/bin/env python3
# Managed by nwarila/python-template — do not edit manually.
# Source: https://github.com/nwarila/python-template

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tomllib
from pathlib import Path


def _load_pyproject() -> dict:
    path = Path("pyproject.toml")
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _run(cmd: list[str], label: str) -> int:
    print(f"\n--- {label} ---")
    result = subprocess.run(cmd)
    if result.returncode != 0 and os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::error::{label} failed with exit code {result.returncode}")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run mypy type checking.")
    parser.add_argument("--paths", nargs="+", help="Override source paths to check")
    args = parser.parse_args()

    pyproject = _load_pyproject()
    paths = args.paths or pyproject.get("tool", {}).get("ruff", {}).get("src", ["src"])

    return _run(["mypy", *paths], "Mypy")


if __name__ == "__main__":
    sys.exit(main())
