# Streamlining & Modularization Plan

## Objectives
- Eliminate redundant scripts and duplicated logic while keeping required features intact.
- Restructure the codebase into importable, well-namespaced modules that expose a small number of public entry points.
- Replace ad-hoc validation utilities with automated tests and clearly documented debug workflows.
- Simplify developer ergonomics: one installation path, one CLI surface, and predictable data locations.

## Current Pain Points
- Three separate deck-generation entry points (`generate_hsk_deck.py`, `create_hsk_deck.py`, `generate_hsk_deck_cli.py`) each re-implement portions of the `HSKDeckBuilder` flow, creating maintenance risk and duplicated side effects.【F:generate_hsk_deck.py†L1-L99】【F:create_hsk_deck.py†L1-L65】【F:generate_hsk_deck_cli.py†L1-L45】
- Utility helpers (`card_utils.py`, `pinyin_converter.py`, `parquet_utils.py`, `hsk_scorer.py`) sit in the repo root instead of the package namespace, making imports inconsistent and encouraging script-level duplication.【F:card_utils.py†L1-L52】【F:pinyin_converter.py†L1-L80】
- `scripts/validation/` still contains 13 legacy scripts that overlap with the `tests/` suite and MIGRATION_PLAN targets, yet continue to accumulate drift.【F:scripts/validation/verify_final_sorting.py†L1-L20】【F:MIGRATION_PLAN.md†L11-L69】
- Root-level analytics scripts (`plot_vocab_distribution.py`, `generate_level_report.py`, `check_hsk1_distribution.py`) duplicate logic that should live inside `src/tian_hanzi` and be exposed through a consistent CLI or notebook API.【F:plot_vocab_distribution.py†L1-L60】【F:generate_level_report.py†L1-L80】

## Target Architecture
```
src/tian_hanzi/
├── cli/                      # Shared Typer/Click command groups
│   ├── deck.py               # deck build commands
│   ├── analytics.py          # reporting & plotting commands
│   └── validate.py           # smoke/integration checks
├── core/
│   ├── data_sources.py       # data loading, caching, I/O
│   ├── deck_pipeline.py      # orchestrates deck build steps
│   ├── components.py         # component productivity logic
│   ├── cards.py              # card templating (ruby text etc.)
│   └── scoring.py            # scoring helpers currently in hsk_scorer
├── analytics/
│   ├── distributions.py      # replaces plot/check scripts
│   └── reports.py            # level summaries, export helpers
└── tests/ (mirrors package structure with unit + integration suites)
```
Supporting directories:
- `scripts/legacy/` retains only wrappers needed for backwards compatibility; others deleted or replaced with CLI docs.
- `docs/` houses operator guides, data schema references, and migration checklists.

## Workstreams & Actions

### 1. Baseline Audit & Cleanup
1. Inventory every executable script and classify as **keep → module**, **migrate → test**, or **archive**.
   - Produce a machine-readable manifest (`scripts_manifest.yaml`) to track owners and status.
2. Remove redundant entry points:
   - Keep `generate_hsk_deck_cli.py` temporarily as a thin shim that delegates to `tian_hanzi.cli.deck.main()`; delete `generate_hsk_deck.py` and `create_hsk_deck.py` after porting functionality.
   - Publish a deprecation note in `CHANGELOG.md` and update `README.md` usage instructions.
3. Move shared utilities (`card_utils.py`, `pinyin_converter.py`, `parquet_utils.py`, `hsk_scorer.py`) under `src/tian_hanzi/core/` with clear public exports to enforce a single source of truth.

### 2. Modularize the Deck Pipeline
1. Split `HSKDeckBuilder` into composable services:
   - `data_sources.HSKDataRepository` handles filesystem access and caching for vocabulary, hanzi, and reference CSV/Parquet assets currently scattered across `HSKDeckBuilder` methods.【F:generate_hsk_deck.py†L24-L112】
   - `components.ComponentAnalyzer` encapsulates decomposition, productivity counting, and filtering rules; accepts dependency-free inputs for easier unit testing.
   - `deck_pipeline.DeckBuilder` orchestrates the workflow, using dependency injection so the CLI can swap implementations (e.g., offline testing mocks).
2. Extract card formatting helpers into `cards.py` and ensure both CLI deck generation and sample creation share the same rendering utilities formerly in `card_utils.py`.
3. Introduce a `config` object or dataclass to describe runtime options (levels, output paths, caching flags) rather than passing raw dictionaries between functions.

### 3. Unified CLI Surface
1. Adopt `typer` (already a dependency via `requirements.txt` if not add) to expose a single `tian-hanzi` console script via `pyproject.toml`/`setup.py` entry points.
2. Implement subcommands:
   - `tian-hanzi deck build` → deck generation (replaces multiple scripts).
   - `tian-hanzi analyze distribution` → wraps plotting/report generation.
   - `tian-hanzi validate run` → executes curated smoke checks.
3. Provide backward-compatible shim scripts in `scripts/legacy/` for one release, each printing a deprecation warning and delegating to the CLI.
4. Update docs and `run_hsk_pipeline.sh` to invoke the new CLI.

### 4. Testing & Validation Strategy
1. Translate high-value validation scripts into pytest suites following the mapping in `MIGRATION_PLAN.md`; delete each script once its coverage lives in tests.
2. Add integration tests exercising the CLI commands with temporary directories to ensure modular components compose correctly.
3. Replace notebook/manual workflows with deterministic fixtures (e.g., sample HSK datasets) stored under `tests/data/` to shrink reliance on large real datasets.
4. Configure GitHub Actions (if not already) to run linting, type checks, and pytest on pull requests to guard against regression after cleanup.

### 5. Documentation & Developer Experience
1. Produce a concise “How to build the deck” guide aligned with the new CLI; remove outdated instructions referencing deleted scripts.
2. Maintain a living architectural overview (diagrams or Mermaid) explaining module boundaries, data flow, and extension points.
3. Update `CONTRIBUTING.md` with new module layout, testing expectations, and coding standards (type hints, logging, error handling).
4. Document the deprecation/removal timeline for legacy scripts in `PIPELINE_UPDATES.md` so downstream consumers can plan migrations.

### 6. Dependency & Packaging Hygiene
1. Replace `setup.py` with `pyproject.toml` (PEP 621) and manage dependencies via Poetry or Hatch; ensure extras cover optional tooling (analysis, notebooks).
2. Audit `requirements.txt` for unused packages introduced by legacy scripts and drop them to reduce install footprint.
3. Adopt `ruff` or `flake8` + `isort` to enforce style and catch dead imports created by the refactor.
4. Add `__all__` exports in each module to explicitly control the public API surface.

### 7. Data & Artifact Management
1. Centralize output directories under a configurable `data/` root with subfolders (`raw`, `processed`, `exports`) managed by `data_sources` helpers.
2. Introduce caching/incremental build support: skip expensive recomputation when upstream files unchanged.
3. Provide cleanup commands (`tian-hanzi data purge`) to delete derived artifacts, keeping the repo lean.

## Timeline & Milestones
1. **Week 1** – Audit + manifest, move utilities into package, create CLI skeleton, add deprecation warnings.
2. **Week 2** – Refactor deck pipeline into modules, port CLI commands, ensure parity via integration tests.
3. **Week 3** – Migrate validation scripts to pytest, delete superseded scripts, update documentation.
4. **Week 4** – Packaging overhaul (`pyproject.toml`), dependency pruning, finalize docs, archive remaining legacy assets.

## Expected Outcomes
- Reduce root-level Python files from 12 to ≤3 (CLI shim + setup metadata) by consolidating logic under `src/tian_hanzi`.
- Achieve DRY architecture: one deck builder implementation consumed by CLI, tests, and notebook analyses.
- Lower onboarding time for contributors through consistent tooling and documentation.
- Enable future automation (CI/CD, data refresh) with well-defined module boundaries and minimal redundant code paths.
