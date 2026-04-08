# python-template

Reusable Python quality-gate scripts, a reusable CI workflow, released script copies for self-dogfooding, and reference configurations that define a consistent developer experience across all Python repositories in the **nwarila** GitHub organization.

This repo is the Python-specific layer of a two-layer governance model. For org-wide community health files, issue templates, and baseline CI, see [nwarila/.github](https://github.com/nwarila/.github).

## Architecture

| Layer | Repo | Responsibility |
| --- | --- | --- |
| Org governance | `nwarila/.github` | Community health files, issue and PR templates, baseline CI, workflow templates |
| Python QA | `nwarila/python-template` | Check scripts, reusable workflow, setup action, released script mirror, reference configs |

Downstream Python repos consume both layers through different mechanisms. The `.github` repo provides defaults through GitHub's built-in inheritance; this repo ships Python-specific scripts and configs through tagged reusable workflows and release-triggered sync PRs.

## What This Repo Provides

- **Canonical QA scripts** in `scripts/` for linting, typing, tests, security, spelling, packaging, and local orchestration.
- **Released script mirror** in `.github/scripts/`, used by this repo's own CI so the template validates the same artifacts it ships.
- **Composite setup action** in `.github/actions/setup-python/` for Python plus dependency bootstrap.
- **Reusable CI workflow** in `.github/workflows/python-qa.yml` for downstream repositories.
- **Reference baselines** in `reference/`, including `pyproject.toml`, `.pre-commit-config.yaml`, VSCode settings, `gitignore`, `gitattributes`, and `repo-ci.yml`.
- **Release automation** through `auto-release.yml`, `self-update.yml`, and `sync-downstream.yml`.

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
|   |   |-- .version               # Release tag currently mirrored into this directory
|   |   `-- ...                    # Released copies of the QA scripts
|   `-- workflows/
|       |-- auto-release.yml       # Creates a release when scripts/ changes land on main
|       |-- python-qa.yml          # Reusable CI workflow for downstream repos
|       |-- self-update.yml        # Refreshes .github/scripts/ from the latest release
|       |-- sync-downstream.yml    # Release-triggered sync PRs for downstream repos
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
|   |-- setup.sh                   # Unix venv bootstrap
|   `-- setup.ps1                  # Windows venv bootstrap
|-- sync-manifest.json             # Downstream repo list and source-to-dest mappings
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

### Sync

When this repo publishes a release, `sync-downstream.yml` reads `sync-manifest.json` and opens PRs in downstream repos to update template-owned files such as `.github/scripts/` and reference configs.

## Self-Dogfooding Model

This repo tests the released form of the standard, not only the development source.

1. `scripts/` is the canonical source of truth for the QA scripts.
2. When `scripts/` changes merge to `main`, `auto-release.yml` creates the next patch release.
3. `self-update.yml` downloads the latest released scripts into `.github/scripts/` and updates `.github/scripts/.version`.
4. `template-ci.yml` runs the checks from `.github/scripts/`, which mirrors what downstream repos receive from releases.
5. `sync-downstream.yml` distributes the source `scripts/` tree into downstream `.github/scripts/`, and `python-qa.yml` executes that released path in the caller repo.

This keeps the release pipeline exercised continuously and helps catch drift between source scripts and shipped scripts.

## Git Hygiene Standard

The org-standard `.gitignore` uses an explicit allowlist model and starts with `**`, matching the control-plane style used in `nwarila/.github`. Repos intentionally allow tracked roots and keep generated artifacts ignored even inside allowed paths.

The org-standard `.gitattributes` is comment-rich and standardized, defining LF normalization and markdown diff behavior in a format aligned with `nwarila/.github`.

## Quick Start For A New Repo

1. Copy the reference configs from `reference/` into your repo, including `reference/repo-ci.yml` as the starting CI workflow.
2. Extend `.gitignore` by allowlisting any repo-specific tracked roots beyond the standard baseline.
3. Customize `pyproject.toml` for your project metadata, dependencies, and entry points.
4. Add the repo to `sync-manifest.json` if it should receive automated sync PRs.
5. Call the reusable workflow from your repo's CI and install the dev tooling locally.

## Design Principles

- **Local must match CI.** The same scripts define the quality bar in both environments.
- **Scripts are standalone and stdlib-only.** Each check script shells out to configured tools without shared helper modules.
- **`pyproject.toml` is the center of gravity.** Tool configuration stays centralized instead of spreading across dotfiles.
- **Cross-platform first.** Setup scripts and QA scripts are designed for Linux, macOS, and Windows.
- **Git hygiene is standardized.** `.gitignore` and `.gitattributes` align with the org baseline.
- **Visible quality matters.** Separate jobs, clear logs, and consistent configs make the standard easy to review and trust.

## License

See [LICENSE](LICENSE).
