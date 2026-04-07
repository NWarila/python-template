#!/usr/bin/env python3
# Managed by nwarila/python-template — do not edit manually.
# Source: https://github.com/nwarila/python-template

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def _run(cmd: list[str], label: str) -> int:
    print(f"\n--- {label} ---")
    result = subprocess.run(cmd)
    if result.returncode != 0 and os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::error::{label} failed with exit code {result.returncode}")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run codespell for typo detection.")
    parser.add_argument("--fix", action="store_true", help="Auto-fix spelling mistakes")
    args = parser.parse_args()

    cmd = ["codespell"]
    if args.fix:
        cmd.append("--write-changes")

    return _run(cmd, "Codespell")


if __name__ == "__main__":
    sys.exit(main())
