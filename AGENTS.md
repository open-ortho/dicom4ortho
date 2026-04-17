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
- Some tests require Docker + Orthanc (`test/docker-compose.yml`).

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
  - Equivalent: `pylint --errors-only dicom4ortho`
- Test suite:
  - `python -m unittest`
  - Preferred explicit discovery: `python -m unittest discover -s test -p "test_*.py"`
  - `make test` (starts/stops Docker around tests)
- Build package:
  - `python -m build`
  - `make build` (runs lint + test + build + resource update)

### Run a single test (important)

Use `unittest` dotted paths:

```bash
# Single test file/module
python -m unittest test.test_models

# Single test class
python -m unittest test.test_models.TestDicomBase

# Single test method
python -m unittest test.test_models.TestDicomBase.test_patient_sex_valid
```

You can also use `pytest` if installed, but repository conventions are `unittest`:

```bash
pytest test/test_models.py::TestDicomBase::test_patient_sex_valid
```

### Integration / end-to-end tests

- E2E tests in `test/test_e2e.py` expect Orthanc endpoints (DIMSE/STOW-RS).
- Start dependencies manually if not using `make test`:

```bash
docker compose -f ./test/docker-compose.yml up -d
python -m unittest test.test_e2e
docker compose -f ./test/docker-compose.yml down
```

## 5) Makefile Caveats Agents Must Know

- `make test` is not unit-only; it always touches Docker.
- `make build` invokes `update_resources`.
- `update_resources` may run `git add` and `git commit` automatically for resource CSV updates.
- Avoid running `make build` if you must not create commits or touch git state.
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
- Name test modules as `test/test_*.py`.
- Prefer deterministic tests; isolate filesystem/network effects.
- For network tests, use local mock/server patterns already used by project.

## 7) Project-Specific Implementation Guidance

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

- Package code: `dicom4ortho/`
- DICOM transport modules: `dicom4ortho/dicom/`
- Tests: `test/`
- Docker test services: `test/docker-compose.yml`
- Lint config: `.pylintrc`
- Build config: `pyproject.toml`
- Supporting coding guidance: `docs/context/general_coding.md`
