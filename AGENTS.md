# AGENTS.md

Guidance for coding agents working in `dicom4ortho`.

Get background of project and what it should do from [Introduction](./README.md#introduction).

Get more context from [context](./docs/context/cp1570_ft_add_dental_acquisition_attributes_into_VL_IOD.txt)

## 1) Repository Snapshot

- Language: Python (`>=3.10`).
- Packaging/build backend: `setuptools` via `pyproject.toml`.
- Test framework in practice: `unittest` (despite README examples mentioning `pytest`).
- Primary linting tool: `pylint`.
- DICOM dependencies: `pydicom`, `pynetdicom`, `pillow`, `requests`.
- Python implementation and tests: `python/dicom4ortho/` and `python/test/`.
- Some tests require Docker + Orthanc (`python/test/docker-compose.yml`).
- This is a multi-language-ready layout, not a shared executable core. Keep
  root packaging/Make entry points compatible; see `docs/REPOSITORY_LAYOUT.md`.

## 2) Rules Files Discovered

- Cursor rules: none found (`.cursor/rules/` and `.cursorrules` absent).
- Copilot rules: none found (`.github/copilot-instructions.md` absent).
- Additional coding context exists in `docs/context/general_coding.md` and should be treated as guidance.

## 3) Environment Setup

Recommended local setup:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Alternative install (non-editable):

```bash
pip install dicom4ortho[dev]
```

## 4) Build, Lint, and Test Commands

### Core commands

- Lint:
  - `make lint`
  - Equivalent: `pylint --errors-only python/dicom4ortho`
- Test suite:
  - `PYTHONPATH=python python -m unittest discover -s python/test -t python`
  - Run commands from the repository root after editable installation.
  - `make test` (starts/stops Docker around tests)
- Build package:
  - `python -m build`
  - `make build` (runs lint + test + build, using the committed terminology lock)

### Run a single test (important)

Use `unittest` dotted paths:

```bash
# Single test file/module
PYTHONPATH=python python -m unittest test.test_models

# Single test class
PYTHONPATH=python python -m unittest test.test_models.TestDicomBase

# Single test method
PYTHONPATH=python python -m unittest test.test_models.TestDicomBase.test_patient_sex_valid
```

You can also use `pytest` if installed, but repository conventions are `unittest`:

```bash
pytest python/test/test_models.py::TestDicomBase::test_patient_sex_valid
```

### Integration / end-to-end tests

- E2E tests in `python/test/test_e2e.py` expect Orthanc endpoints (DIMSE/STOW-RS).
- Start dependencies manually if not using `make test`:

```bash
docker compose -f ./python/test/docker-compose.yml up -d
PYTHONPATH=python python -m unittest test.test_e2e
docker compose -f ./python/test/docker-compose.yml down
```

## 5) Makefile Caveats Agents Must Know

- `make test` is not unit-only; it always touches Docker.
- When using an existing Orthanc mock, `make test COMPOSE=true` skips only
  Compose lifecycle commands. Tests still use localhost HTTP 8202/DIMSE 4242;
  forward these ports to `orthanc-mock:8042`/`:4242` on the container network.
- `make build` uses the committed `_generated_codes.py` terminology lock and does not
  access the network.
- `make update_codes` explicitly fetches DICOM CIDs from NEMA FHIR ValueSets,
  DCM concept names from NEMA `dcm.owl`, ADA 1100 CodeSystems from Open Ortho,
  and DENT-OIP `views.csv`. It writes the committed terminology lock with one
  `SOURCE_PROVENANCE` mapping of observed URLs, SHA-256s, and FHIR version/date
  metadata. Review its generated diff before committing it.
- Lock source path: `python/dicom4ortho/_generated_codes.py`. The root generator
  command remains `python tools/generate_codes.py`.
- `make check_codes` performs the same fetch and validation in memory and fails
  when its output differs from the committed lock. It is suitable for manual or
  scheduled terminology drift detection; normal builds and runtime stay offline.
- Safer build-only command: `python -m build`.

## 6) Code Style and Conventions

### Formatting and layout

- Follow PEP 8 baseline with project-specific limits.
- Use 4-space indentation.
- Max line length: 100 (from `.pylintrc`).
- Keep modules under roughly 1000 lines when feasible (`pylintrc` target).
- Prefer readable, explicit code over compact/clever forms.

### Imports

- Keep imports at top of module.
- Group in this order: standard library, third-party, local package.
- Avoid wildcard imports.
- Prefer explicit symbol imports when they improve readability.
- Preserve existing import style within touched files unless refactoring intentionally.

### Naming

Derived from `.pylintrc`:

- Functions/methods/variables/arguments: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_CASE`.
- Modules: `snake_case`.
- Keep DICOM attribute names exactly as required by pydicom/DICOM standard (often `PascalCase` tag names on dataset fields).

### Types and signatures

- Add type hints to new/modified public functions when practical.
- Use `Optional[...]` / `| None` for nullable values explicitly.
- Use concrete container types (`list[str]`, `dict[str, Any]`) where helpful.
- Keep compatibility with current runtime target (Python 3.10+).

### Error handling

- Prefer exceptions for invalid states and programmer errors.
- Log context-rich messages for operational failures (I/O, network, parsing).
- Catch narrowly (specific exceptions), not broad `except` unless unavoidable.
- Do not silently swallow failures; if intentionally ignored, log at least a debug/warning message.
- Follow `docs/context/general_coding.md`: avoid returning null-like values unless there is a clear contract reason.

### Logging

- Use module-level logger pattern:
  - `import logging`
  - `logger = logging.getLogger(__name__)`
- Prefer structured logging with format placeholders:
  - `logger.info("Saved file %s", filename)`
- Avoid `print()` in library/runtime paths unless CLI output is intended.

### Testing style

- Existing suite uses `unittest.TestCase`; keep new tests compatible.
- Name test modules as `python/test/test_*.py`.
- Prefer deterministic tests; isolate filesystem/network effects.
- For network tests, use local mock/server patterns already used by project.

## 7) Project-Specific Implementation Guidance

- Shared functionality is defined in `docs/API_CONTRACT.md`, not a shared public API.
  Language APIs may be idiomatic; test adapters exercise real implementation behavior.
  Shared DENT-OIP/GXV conformance tests are planned, not currently available.
- Preserve DICOM semantics over generic refactors.
- Do not change tag names, UID roots, transfer syntax behavior, or sequence semantics without clear requirement and tests.
- Keep compatibility with both file-based and in-memory image workflows (`input_image_filename` and `input_image_bytes`).
- For send paths (`dimse`/`wado`), validate required parameters early and log actionable errors.

## 8) Agent Workflow Checklist

Before coding:

1. Read relevant module(s) and neighboring tests.
2. Identify whether change impacts DICOM tags/UIDs/transfer syntaxes.
3. Decide minimal test scope (single test first, then broader run).

After coding:

1. Run targeted single test(s).
2. Run module-level tests.
3. Run full `unittest` suite if change is broad.
4. Run `make lint` (or equivalent pylint command).
5. Build with `python -m build` when packaging changes are involved.

## 9) Useful Paths

- Package code: `python/dicom4ortho/`
- DICOM transport modules: `python/dicom4ortho/dicom/`
- Tests: `python/test/`
- Docker test services: `python/test/docker-compose.yml`
- Lint config: `.pylintrc`
- Build config: `pyproject.toml`
- Supporting coding guidance: `docs/context/general_coding.md`
