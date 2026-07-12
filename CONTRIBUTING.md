# Contributing to Cyberpunk: Edge-Runner Simulator

Thanks for your interest in improving the game! This document explains how to
set up a development environment and what we expect from contributions.

## Development setup

You will need **Python 3.9 or newer**.

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/cyberpunk-edgerunner-sim.git
cd cyberpunk-edgerunner-sim

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies (includes pytest + ruff)
pip install -r requirements.txt
```

## Running the game

```bash
# Web version (FastAPI + SPA)
python -m server.main
# → http://localhost:8000

# Terminal version
python cyberpunk.py
```

## Testing & linting

```bash
# Run the test suite
pytest

# Check code style
ruff check .
```

Please make sure **both** pass before opening a pull request.

## Commit & PR conventions

- Use [Conventional Commits](https://www.conventionalcommits.org/) with
  lowercase type prefixes, e.g.:

  ```
  feat(api): add new gig type
  fix(server): clamp humanity on restart
  docs: clarify installation steps
  ```

- **Pull request titles and descriptions must be written in English**, even if
  your discussion in the issue is in another language. This keeps the project
  accessible to the wider community.

## Branching

- `main` is the stable, deployed branch (it auto-syncs to the Hugging Face Space).
- Open feature/pull-request branches from `main`, e.g. `feat/gig-balance`.

## Reporting bugs & requesting features

Please use the provided GitHub issue templates
([Bug report](.github/ISSUE_TEMPLATE/bug_report.yml),
[Feature request](.github/ISSUE_TEMPLATE/feature_request.yml)).

By contributing, you agree that your contributions will be licensed under the
MIT License.
