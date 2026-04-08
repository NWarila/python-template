# python-template

[![CI](https://github.com/nwarila/python-template/actions/workflows/template-ci.yml/badge.svg)](https://github.com/nwarila/python-template/actions/workflows/template-ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://nwarila.github.io/python-template/coverage.json)](https://github.com/nwarila/python-template/actions/workflows/template-ci.yml)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.11-3776ab?logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)](https://github.com/nwarila/python-template)
[![License](https://img.shields.io/github/license/nwarila/python-template)](LICENSE)

Reusable Python quality-gate scripts, a reusable CI workflow, and reference configurations that define a consistent developer experience across all Python repositories in the **nwarila** GitHub organization.

This repo is the Python-specific layer of a two-layer governance model. For org-wide community health files, issue templates, and baseline CI, see [nwarila/.github](https://github.com/nwarila/.github).

## Architecture

| Layer | Repo | Responsibility |
| --- | --- | --- |
| Org governance | `nwarila/.github` | Community health files, issue and PR templates, baseline CI, workflow templates |
| Python QA | `nwarila/python-template` | Check scripts, reusable workflow, setup action, sync manifest, reference configs |

Downstream Python repos consume both layers through different mechanisms. The `.github` repo provides defaults through GitHub's built-in inheritance; this repo ships Python-specific scripts and configs through tagged releases that downstream repos pull on their own schedule.

## What This Repo Provides

- **Canonical QA scripts** in `scripts/` for linting, typing, tests, security, spelling, packaging, and local orchestration.
- **Sync manifest** (`sync-manifest.json`) defining source-to-destination file mappings for downstream repos.
- **Reusable sync workflow** (`self-update.yml`) that downstream repos call via `uses:` to pull updates automatically.
- **Composite setup action** in `.github/actions/setup-python/` for Python plus dependency bootstrap.
- **Reusable CI workflow** in `.github/workflows/python-qa.yml` for downstream repositories.
- **Reference baselines** in `reference/`, including `pyproject.toml`, `.pre-commit-config.yaml`, VSCode settings, `gitignore`, `gitattributes`, and `repo-ci.yml`.
- **Release automation** through `auto-release.yml` (creates releases when `scripts/` changes) and `self-update.yml` (this repo's own pull from its releases for dogfooding).

## Quality Gates

| Check | Tool | Config Source |
| --- | --- | --- |
| Lint + Format | ruff | `[tool.ruff]` in `pyproject.toml` |
| Type Checking | mypy | `[tool.mypy]` in `pyproject.toml` |
| Tests + Coverage | pytest + pytest-cov | `[tool.pytest.ini_options]` in `pyproject.toml` |
| Security | pip-audit | Environment and dependency metadata |
| Spelling | codespell | `[tool.codespell]` in `pyproject.toml` |
| Packaging | build + twine | `[build-system]` in `pyproject.toml` |

## Repository Structure

```text
python-template/
|-- .github/
|   |-- actions/
|   |   `-- setup-python/
|   |       `-- action.yml         # Composite action for Python + dependency setup
|   |-- scripts/
|   |   |-- .version               # Release tag currently pulled into this directory
|   |   `-- ...                    # Copies of QA scripts pulled from the latest release
|   `-- workflows/
|       |-- auto-release.yml       # Creates a release when scripts/ changes land on main
|       |-- python-qa.yml          # Reusable CI workflow for downstream repos
|       |-- self-update.yml        # Pulls released files via manifest (dogfood)
|       `-- template-ci.yml        # CI for this repo, running released scripts
|-- reference/
|   |-- pyproject.toml             # Reference project config
|   |-- pre-commit-config.yaml     # Pre-commit hook definitions
|   |-- settings.json              # VSCode editor settings
|   |-- tasks.json                 # VSCode task definitions
|   |-- extensions.json            # VSCode recommended extensions
|   |-- gitignore                  # Reference .gitignore
|   |-- gitattributes              # Reference .gitattributes
|   |-- markdownlint-cli2.jsonc    # Markdown lint config
|   `-- repo-ci.yml                # Starter CI workflow for downstream repos
|-- scripts/
|   |-- check_lint.py              # ruff lint + format
|   |-- check_types.py             # mypy
|   |-- check_tests.py             # pytest + coverage
|   |-- check_security.py          # pip-audit
|   |-- check_spelling.py          # codespell
|   |-- check_package.py           # build + twine check
|   |-- qa.py                      # Local orchestrator
|   |-- sync.py                    # Manifest-driven file sync for template updates
|   |-- setup.sh                   # Unix venv bootstrap
|   `-- setup.ps1                  # Windows venv bootstrap
|-- sync-manifest.json             # Source-to-dest file mappings for downstream sync
|-- pyproject.toml                 # Config for this repo
`-- README.md
```

## How Downstream Repos Use It

### CI

Downstream repos copy `reference/repo-ci.yml` into `.github/workflows/ci.yml` and call the reusable workflow from a tagged release:

```yaml
jobs:
  python-qa:
    uses: nwarila/python-template/.github/workflows/python-qa.yml@v1
```

The reusable workflow runs each quality gate as a separate job and publishes a single stable `ci-passed` aggregator result.

### Local Development

Downstream repos run the synced `.github/scripts/` directly:

```bash
.venv/bin/python .github/scripts/qa.py
.venv/bin/python .github/scripts/qa.py --fix
.venv/bin/python .github/scripts/qa.py --skip tests security
```

VSCode tasks in `reference/tasks.json` expose the same checks in the editor.

### Pre-commit Hooks

The synced `.pre-commit-config.yaml` calls the same tools with the same `pyproject.toml` configuration so issues are caught before code leaves the developer's machine.

### Template Sync

Downstream repos call the reusable `self-update.yml` workflow from a thin wrapper:

```yaml
# .github/workflows/template-sync.yml
name: Template Sync
on:
  schedule:
    - cron: "0 6 * * 1" # Weekly Monday 06:00 UTC
  workflow_dispatch:
permissions:
  contents: write
  pull-requests: write
jobs:
  sync:
    uses: nwarila/python-template/.github/workflows/self-update.yml@v1
```

The workflow checks for new releases, reads `sync-manifest.json` to know which files to copy and where, and opens a PR using the repo's own `GITHUB_TOKEN`. No PAT required.

Supported sync modes:

- **`overwrite`** — full replacement (scripts, pre-commit config, VSCode settings)
- **`marker-preserve`** — replaces template-owned `// #region` sections while preserving repo-specific content (e.g. `tasks.json`)

## Update Flow

1. `scripts/` is the canonical source of truth for the QA scripts.
2. When `scripts/` changes merge to `main`, `auto-release.yml` creates the next patch release.
3. Downstream repos call `self-update.yml` as a reusable workflow — it checks for new releases, clones at the tag, reads `sync-manifest.json`, and opens a PR.
4. This repo dogfoods the same workflow directly (nightly schedule).
5. `template-ci.yml` runs the checks from `.github/scripts/`, validating the released artifacts.

Each repo controls its own update cadence — the template publishes releases, consumers pull when ready. No cross-repo credentials, no push permissions, no coupling.

## Git Hygiene Standard

The org-standard `.gitignore` uses an explicit allowlist model and starts with `**`, matching the control-plane style used in `nwarila/.github`. Repos intentionally allow tracked roots and keep generated artifacts ignored even inside allowed paths.

The org-standard `.gitattributes` is comment-rich and standardized, defining LF normalization and markdown diff behavior in a format aligned with `nwarila/.github`.

## Quick Start For A New Repo

1. Copy the reference configs from `reference/` into your repo, including `reference/repo-ci.yml` as the starting CI workflow.
2. Add a `template-sync.yml` wrapper workflow that calls `self-update.yml` via `uses:` (see Template Sync above).
3. Extend `.gitignore` by allowlisting any repo-specific tracked roots beyond the standard baseline.
4. Customize `pyproject.toml` for your project metadata, dependencies, and entry points.
5. Call the reusable workflow from your repo's CI and install the dev tooling locally.

## Design Principles

- **Local must match CI.** The same scripts define the quality bar in both environments.
- **Scripts are standalone and stdlib-only.** Each check script shells out to configured tools without shared helper modules.
- **`pyproject.toml` is the center of gravity.** Tool configuration stays centralized instead of spreading across dotfiles.
- **Cross-platform first.** Setup scripts and QA scripts are designed for Linux, macOS, and Windows.
- **Git hygiene is standardized.** `.gitignore` and `.gitattributes` align with the org baseline.
- **Each repo owns its own updates.** Sync is pull-based — no cross-repo credentials, no push permissions, no coupling.
- **Manifest-driven sync over submodules or packages.** Git submodules pin to a commit with no selective file mapping, no merge strategies, and no PR review of incoming changes. Package dependencies require a runtime install and don't handle config files. The manifest approach syncs both scripts and configs with per-file merge strategies (`overwrite` vs `marker-preserve`) and delivers changes as reviewable PRs.
- **Visible quality matters.** Separate jobs, clear logs, and consistent configs make the standard easy to review and trust.

## License

See [LICENSE](LICENSE).
