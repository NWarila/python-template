# python-template

Reusable quality-gate scripts, a reusable CI workflow, and reference configurations that define a consistent developer experience across all Python repositories in the **nwarila** GitHub organization.

This repo is the Python-specific layer of a two-layer governance model. For org-wide community health files, issue templates, and baseline CI, see [nwarila/.github](https://github.com/nwarila/.github).

## Architecture

| Layer | Repo | Responsibility |
|-------|------|----------------|
| Org governance | `nwarila/.github` | Community health files, issue/PR templates, baseline CI, workflow templates |
| Python QA | `nwarila/python-template` | Check scripts, reusable workflow, VSCode configs, pre-commit config, environment setup |

Downstream Python repos consume both layers through different mechanisms. The `.github` repo provides defaults via GitHub's built-in inheritance; this repo syncs scripts and configs through release-triggered pull requests.

## What This Repo Provides

- **6 check scripts** -- one per quality gate, each runnable standalone.
- **`qa.py`** -- local orchestrator that discovers and runs all checks (`--fix`, `--skip`).
- **`setup.sh` / `setup.ps1`** -- cross-platform virtual-environment bootstrap (uv-aware).
- **Reusable CI workflow** (`python-qa.yml`) -- separate job per check, callable from any repo.
- **Reference configs** -- `pyproject.toml`, `.pre-commit-config.yaml`, VSCode tasks/settings/extensions, `.gitignore`, `.gitattributes`.
- **Release-triggered sync** (`sync-downstream.yml`) -- opens PRs in downstream repos when this template is released.

## Quality Gates

| Check | Tool | Config Source |
|-------|------|---------------|
| Lint + Format | ruff | `[tool.ruff]` in pyproject.toml |
| Type Checking | mypy | `[tool.mypy]` in pyproject.toml |
| Tests + Coverage | pytest + pytest-cov | `[tool.pytest.ini_options]` in pyproject.toml |
| Security | pip-audit | -- |
| Spelling | codespell | `[tool.codespell]` in pyproject.toml |
| Packaging | build + twine | `[build-system]` in pyproject.toml |

## Repository Structure

```text
python-template/
├── .github/
│   └── workflows/
│       ├── python-qa.yml          # Reusable CI workflow (called by downstream repos)
│       ├── sync-downstream.yml    # Release-triggered sync to downstream repos
│       └── template-ci.yml        # CI for this repo itself
├── actions/
│   └── setup-python/
│       └── action.yml             # Composite action for Python + dependency setup
├── scripts/
│   ├── check_lint.py              # ruff lint + format
│   ├── check_types.py             # mypy
│   ├── check_tests.py             # pytest + coverage
│   ├── check_security.py          # pip-audit
│   ├── check_spelling.py          # codespell
│   ├── check_package.py           # build + twine check
│   ├── qa.py                      # Local orchestrator
│   ├── setup.sh                   # Unix venv bootstrap
│   └── setup.ps1                  # Windows venv bootstrap
├── reference/
│   ├── pyproject.toml             # Reference project config
│   ├── pre-commit-config.yaml     # Pre-commit hook definitions
│   ├── settings.json              # VSCode editor settings
│   ├── tasks.json                 # VSCode task definitions
│   ├── extensions.json            # VSCode recommended extensions
│   ├── gitattributes              # Reference .gitattributes
│   ├── gitignore                  # Reference .gitignore
│   └── markdownlint-cli2.jsonc    # Markdown lint config
├── sync-manifest.json             # Downstream repo list and file mappings
└── pyproject.toml                 # Config for this repo
```

## How Downstream Repos Use It

### CI

Downstream repos call the reusable workflow from their own CI:

```yaml
jobs:
  qa:
    uses: nwarila/python-template/.github/workflows/python-qa.yml@v1
```

Each quality gate runs as a separate job, providing clear pass/fail signals per check.

### Local Development

Developers run the same scripts that CI runs:

```bash
.venv/bin/python scripts/qa.py                    # Run all checks
.venv/bin/python scripts/qa.py --fix              # Auto-fix where possible
.venv/bin/python scripts/qa.py --skip tests security
```

VSCode tasks are provided so every check is also available from the command palette.

### Pre-commit Hooks

The synced `.pre-commit-config.yaml` calls the same tools with the same configuration, so issues are caught before code leaves the developer's machine.

### Script Sync

When a new release is published on this repo, `sync-downstream.yml` opens a pull request in each downstream repo listed in `sync-manifest.json`, updating scripts and configs to the latest version.

## Quick Start for a New Repo

1. Copy the reference configs from `reference/` into your repo (`.gitignore`, `.gitattributes`, `pyproject.toml`, `.pre-commit-config.yaml`, VSCode files).
2. Customize `pyproject.toml` for your project (name, dependencies, entry points).
3. Add the repo to `sync-manifest.json` in this template so future updates are synced automatically.
4. Call the reusable workflow from your repo's CI configuration.

## Design Principles

- **Local must match CI.** The same scripts run in both environments; no surprise failures after push.
- **Scripts are standalone and stdlib-only.** Each check script uses only the Python standard library and shells out to the configured tools.
- **pyproject.toml is the center of gravity.** All tool configuration lives in one file, not scattered across dotfiles.
- **Cross-platform first.** Setup scripts and check scripts work on Linux, macOS, and Windows.
- **Opinionated defaults, documented escape hatches.** Sensible choices are made upfront; overrides are possible through standard tool configuration.

## License

See [LICENSE](LICENSE).
