# Repository layout and implementation boundaries

The repository groups code by implementation language. Python is the current
implementation; additional languages can be added independently. There is no
shared executable core.

```text
python/
  dicom4ortho/        # Python package imported as dicom4ortho
  test/              # Python tests, fixtures, and Orthanc Compose configuration
  examples/          # Python/CLI examples
  README.md          # Python contributor instructions
tools/               # maintenance entry points, including the terminology generator
docs/                # project context, architecture, and release instructions
.github/workflows/   # repository CI and Python publication
pyproject.toml       # single Python packaging configuration and root build entry
Makefile             # build, test, and maintenance commands
LICENSE
README.md
```

## Packaging and maintenance entry points

Keeping a single root `pyproject.toml` avoids duplicating package metadata or
adding a custom backend/forwarding shim. Setuptools discovers only
`dicom4ortho*` under `python/`; the wheel installs `dicom4ortho`, not a `python`
package. Run installation and build commands from the repository root:

```sh
pip install -e ".[dev]"
python -m build
```

The root Makefile provides lint, test, build, maintenance, and publishing targets;
use `make help` to list them. Builds produce wheels and source distributions in
root `dist/`. Installed applications use the package and its bundled resources,
not paths within this checkout.

`tools/generate_codes.py` writes
`python/dicom4ortho/_generated_codes.py`. Normal builds and runtime use this
committed terminology lock offline. Explicit `make update_codes` and
`make check_codes` operations fetch and validate upstream terminology; see
[the terminology documentation](TERMINOLOGY.md) for source details.

## Development environment and tests

The Nix shell installs development dependencies into `.venv`, refreshes the
editable package mapping, and activates the environment. Make runs Python tools
through one selectable `PYTHON` interpreter.

Virtual-environment activation and console scripts embed absolute paths. If the
checkout directory moves, preserve the old environment as a backup and recreate
it at the new location. See [the Python contributor instructions](../python/README.md).

Run `make test`, or use explicit unittest discovery:

```sh
PYTHONPATH=python python -m unittest discover -s python/test -t python
```

The explicit path keeps the local `test` package ahead of Python's standard-library
package of the same name. Root `pytest` uses the same suite. Fixtures are resolved
relative to their test modules, not the shell's working directory.

## Additional implementations

Add a language directory when a real implementation starts, with its own build,
dependencies, tests, and release process. Each implementation owns its runtime
code; Python/DICOM/image logic does not become a shared executable core.
Specifications, terminology definitions, and conformance cases are suitable
language-neutral boundaries for coordination between implementations.

The Swift package introduced for #82 uses this layout:

```text
python/
  dicom4ortho/
  test/
  examples/
Package.swift                # SwiftPM Git-URL entry point
apple/
  Sources/
    DICOM4Ortho/              # dental mapping and DICOMKit integration
  Tests/
    DICOM4OrthoTests/
...
```

The [Swift interface](../apple/README.md) is independent of UI/camera frameworks
and Python. DICOMKit owns serialization and codecs. The package exposes image
creation, view templates, and declared-view extraction; application capture/delivery
workflows are not library lifecycle requirements. Python retains its root packaging
and Make entry points unchanged. SwiftPM requires the root manifest when resolving
this Git URL; explicit target paths keep Swift files under `apple/`.
