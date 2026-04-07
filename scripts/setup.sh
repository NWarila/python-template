#!/usr/bin/env bash
# Managed by nwarila/python-template — do not edit manually.
# Source: https://github.com/nwarila/python-template
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Project root: ${PROJECT_ROOT}"
cd "$PROJECT_ROOT"

# ---------------------------------------------------------------------------
# Detect toolchain
# ---------------------------------------------------------------------------
if [ -f "uv.lock" ]; then
    echo ""
    echo "Detected uv.lock — using uv toolchain."
    echo ""

    uv venv .venv
    uv sync

    echo ""
    echo "Setup complete (uv)."
    echo "  Activate: source .venv/bin/activate"
else
    echo ""
    echo "No uv.lock found — using pip + venv toolchain."
    echo ""

    python3 -m venv .venv

    .venv/bin/python -m pip install --upgrade pip

    # Check for [project.optional-dependencies] dev in pyproject.toml
    HAS_DEV_EXTRAS=false
    if [ -f "pyproject.toml" ]; then
        if grep -qE '^\[project\.optional-dependencies\]' pyproject.toml; then
            # Look for a "dev" key after the section header
            if awk '
                /^\[project\.optional-dependencies\]/ { in_section=1; next }
                /^\[/                                  { in_section=0 }
                in_section && /^dev\s*=/               { found=1; exit }
                END { exit !found }
            ' pyproject.toml 2>/dev/null; then
                HAS_DEV_EXTRAS=true
            fi
        fi
    fi

    if [ "$HAS_DEV_EXTRAS" = true ]; then
        echo "Installing package with dev extras..."
        .venv/bin/python -m pip install -e ".[dev]"
    else
        echo "Installing package (no dev extras detected)..."
        .venv/bin/python -m pip install -e .
    fi

    echo ""
    echo "Setup complete (pip + venv)."
    echo "  Activate: source .venv/bin/activate"
fi
