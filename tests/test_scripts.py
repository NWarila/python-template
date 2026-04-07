"""Smoke tests for check scripts.

Each test runs a check script against a minimal temporary Python project
and verifies exit codes. These tests validate that the scripts are
functional, generic, and produce correct results.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_script(project: Path, script_name: str, *extra_args: str) -> subprocess.CompletedProcess[str]:
    """Run a check script inside the given project directory."""
    script = project / "scripts" / script_name
    return subprocess.run(  # noqa: S603 - controlled test invocation of local scripts
        [sys.executable, str(script), *extra_args],
        cwd=project,
        capture_output=True,
        text=True,
    )


class TestCheckLint:
    """Tests for check_lint.py."""

    def test_clean_project_passes(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "check_lint.py")
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_fix_flag_accepted(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "check_lint.py", "--fix")
        assert result.returncode == 0

    def test_bad_formatting_fails(self, tmp_project: Path) -> None:
        bad_file = tmp_project / "src" / "smoke_project" / "bad.py"
        bad_file.write_text("x=1\ny =    2\n")
        result = _run_script(tmp_project, "check_lint.py")
        assert result.returncode != 0


class TestCheckTypes:
    """Tests for check_types.py."""

    def test_clean_project_passes(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "check_types.py")
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_type_error_fails(self, tmp_project: Path) -> None:
        bad_file = tmp_project / "src" / "smoke_project" / "bad.py"
        bad_file.write_text("def add(a: int, b: int) -> int:\n    return a + b\n\nx: str = add(1, 2)\n")
        result = _run_script(tmp_project, "check_types.py")
        assert result.returncode != 0


class TestCheckTests:
    """Tests for check_tests.py."""

    def test_passing_tests_succeed(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "check_tests.py")
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_failing_test_fails(self, tmp_project: Path) -> None:
        (tmp_project / "tests" / "test_fail.py").write_text("def test_always_fails() -> None:\n    assert False\n")
        result = _run_script(tmp_project, "check_tests.py")
        assert result.returncode != 0


class TestCheckSecurity:
    """Tests for check_security.py."""

    def test_runs_without_error(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "check_security.py")
        # pip-audit may or may not find issues depending on the environment,
        # but the script itself should not crash
        assert result.returncode in (0, 1)

    def test_help_flag(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "check_security.py", "--help")
        assert result.returncode == 0
        assert "security" in result.stdout.lower() or "audit" in result.stdout.lower()


class TestCheckSpelling:
    """Tests for check_spelling.py."""

    def test_clean_project_passes(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "check_spelling.py")
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_typo_detected(self, tmp_project: Path) -> None:
        (tmp_project / "src" / "smoke_project" / "typo.py").write_text(
            "# This file has a " + "".join(["t", "eh"]) + " typo in it.\n"
        )
        result = _run_script(tmp_project, "check_spelling.py")
        assert result.returncode != 0


class TestCheckPackage:
    """Tests for check_package.py."""

    def test_package_build_succeeds(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "check_package.py")
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        # dist/ should be cleaned up
        assert not (tmp_project / "dist").exists()

    def test_no_build_system_skips(self, tmp_project: Path) -> None:
        # Remove [build-system] from pyproject.toml
        pyproject = tmp_project / "pyproject.toml"
        content = pyproject.read_text()
        lines = content.split("\n")
        filtered = []
        skip = False
        for line in lines:
            if line.startswith("[build-system]"):
                skip = True
                continue
            if skip and line.startswith("["):
                skip = False
            if not skip:
                filtered.append(line)
        pyproject.write_text("\n".join(filtered))

        result = _run_script(tmp_project, "check_package.py")
        assert result.returncode == 0
        assert "skipping" in result.stdout.lower() or "skip" in result.stdout.lower()


class TestQa:
    """Tests for qa.py orchestrator."""

    def test_help_flag(self, tmp_project: Path) -> None:
        result = _run_script(tmp_project, "qa.py", "--help")
        assert result.returncode == 0
        assert "skip" in result.stdout.lower()

    def test_skip_flag(self, tmp_project: Path) -> None:
        result = _run_script(
            tmp_project,
            "qa.py",
            "--skip",
            "types",
            "--skip",
            "tests",
            "--skip",
            "security",
            "--skip",
            "package",
        )
        assert "SKIP" in result.stdout
