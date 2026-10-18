# Repository layout and compatibility contract

Issue [#78](https://github.com/open-ortho/dicom4ortho/issues/78) prepares the
repository for independent implementations in additional languages. This change
is **refactoring only**: no new runtime functionality and no shared executable
core, language bindings, or new SDKs.

```text
python/
  dicom4ortho/        # existing Python import/package name and runtime behavior
  test/              # Python tests, fixtures, and Orthanc Compose configuration
  examples/          # Python/CLI examples
  README.md          # Python contributor instructions
tools/               # existing root maintenance entry points, including generator
docs/                # project context, architecture, and release instructions
.github/workflows/   # repository CI and Python publication
pyproject.toml       # single Python packaging configuration and root build entry
Makefile             # unchanged root target names
LICENSE
README.md
```

## Why packaging and maintenance entry points stay at the root

Keeping a single root `pyproject.toml` avoids duplicating package metadata or
adding a custom backend/forwarding shim. Setuptools discovers only
`dicom4ortho*` under `python/`; the wheel still installs `dicom4ortho`, not a
`python` package. Root source installation and build commands remain valid:

```sh
pip install -e ".[dev]"
python -m build
```

Root Make targets retain their names and purposes. They address the relocated
package/test/fixture paths; build and deploy still use root `dist/`. The generator
stays at `tools/generate_codes.py` so existing maintenance commands and generated
file instructions remain valid. Its output path follows the source relocation;
its source selection, validation, generation, and offline lock are unchanged.

Source contributors must reinstall an existing editable installation once after
updating to this layout, so it points to `python/dicom4ortho`. The Nix shell also
refreshes that mapping on entry. Published package consumers need no migration.

Moving the checkout directory is a separate concern: existing virtual-environment
activation and console scripts embed absolute paths. The Nix setup checks the
activation path and refuses a moved environment rather than silently using a
different Python; preserve it as a backup and recreate it at the new location.
Python tool invocations in Make use one selectable `PYTHON` interpreter instead
of independently locating console scripts such as `pylint`.

## What must remain the same

- Distribution name, version, runtime dependencies, imports, public APIs, CLI
  commands, package resources, and installed runtime file layout.
- DICOM tags/sequence semantics, UID generation, image/transfer-syntax behavior,
  file/in-memory workflows, validation, and transport.
- The current design merged through PR #70: authoritative NEMA and Open Ortho
  inputs, explicit terminology refresh/check commands, and the committed
  `_generated_codes.py` lock. The obsolete CSV terminology resolver is not restored.
- Wheel/sdist artifact names and types for the unchanged version. Archive
  timestamps and relocated source paths are not byte-identity requirements;
  updated contributor documentation may change the package's long description.
- Root `help`, `default`, `lint`, `test`, `clean`, `build`, `fetch_resources`,
  `update_codes`, `check_codes`, `deploy`, `all`, and `install-dev` Make targets.

Python test discovery is explicit now that tests are grouped by implementation:
`PYTHONPATH=python python -m unittest discover -s python/test -t python`, or
`make test`. The explicit path keeps the local `test` package ahead of Python's
standard-library package of the same name, even in a fresh editable install. Root
`pytest` uses the same relocated suite. Fixture paths are resolved from their
test modules, not the shell's working directory.

## Future implementations

Add a language directory only when a real implementation starts, with its own
build, dependencies, tests, and release process. No empty JVM/Swift directories
or speculative abstractions are introduced. Shared specifications, terminology
definitions, and conformance cases can be considered in later scoped work;
executable Python/DICOM/image logic is not extracted into a common core.

Moving paths must not be mixed with fixing pre-existing DICOM or transport
behavior. Baseline validator warnings/failures must be recorded when comparing
test runs, not hidden by weakening assertions or changing runtime code.

## Warning-cleanup follow-up

During validation, a separate, explicitly requested cleanup replaces deprecated
license metadata with the equivalent SPDX `MIT` expression and keeps `LICENSE`
packaged. This requires setuptools 77.0.3 or newer at build time; runtime
dependencies and the package version are unchanged.

The same cleanup replaces deprecated Pillow pixel access and closes image input
files in the comparison tests. Raw pixel-byte regression cases cover bilevel,
grayscale, and RGB images, including the minimum supported Pillow version.
Consequently, the relocation's original source-byte identity applies to the
mechanical move, not to this later warning cleanup. Public APIs and DICOM pixel
encoding behavior remain unchanged; substantive DICOM validator findings are
neither suppressed nor addressed here.
