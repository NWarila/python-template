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
    argparse.ArgumentParser(description="Run pip-audit for dependency vulnerability scanning.").parse_args()

    return _run(["pip-audit", "--strict"], "Pip-Audit")


if __name__ == "__main__":
    sys.exit(main())
