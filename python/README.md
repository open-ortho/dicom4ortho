# Python implementation

This directory groups the existing `dicom4ortho` Python package, its tests and
fixtures, and its examples. Import names, APIs, CLI entry points, DICOM behavior,
dependencies, and the committed terminology lock are unchanged by the move.
There is no shared executable core or additional language implementation.

## Development commands

Run commands from the **repository root**, which retains the single
`pyproject.toml`, Makefile, `.pylintrc`, and release configuration:

```sh
pip install -e ".[dev]"
make lint
make test                 # starts/stops Orthanc through Docker Compose
python -m build           # creates the wheel and sdist in root dist/
make build                # lint, complete tests, then build
```

For explicit test discovery, or a single module:

```sh
python -m unittest discover -s python/test -t python
PYTHONPATH=python python -m unittest test.test_models
pytest python/test/test_cli.py
```

If an Orthanc mock is already running, `make test COMPOSE=true` leaves its
lifecycle untouched. The tests still require the configured localhost endpoints
(HTTP port 8202, DIMSE port 4242); forward those ports to the service when running
in a separate agent container. This does not mock or skip the network tests.

Python-specific terminology generation remains behind the existing root tooling:

```sh
make update_codes         # fetch/validate upstream inputs, rewrite the lock
make check_codes          # fetch/validate in memory, fail on drift
```

Normal builds, tests, and runtime do not refresh terminology. The generator
continues to write `python/dicom4ortho/_generated_codes.py`; its source URLs and
provenance rules are unchanged.

See [usage and installation](../README.md), [the runnable CSV example](examples/README.md),
and [the repository layout contract](../docs/REPOSITORY_LAYOUT.md).
