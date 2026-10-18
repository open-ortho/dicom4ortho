#!/usr/bin/env bash
# Sourced by the Nix shell from the repository root. Never discard an existing
# environment: activation scripts and installed command shebangs embed its path.

if [ -f .venv/bin/activate ] && ! (
    unset VIRTUAL_ENV
    source .venv/bin/activate && [ "${VIRTUAL_ENV:-}" -ef "$PWD/.venv" ]
); then
    echo "Existing .venv activation refers to another checkout path." >&2
    echo 'Move .venv aside to keep a backup, then run nix develop again.' >&2
    return 1
fi

if [ ! -x .venv/bin/python ]; then
    echo "Creating .venv and installing dicom4ortho[dev] …"
    python3 -m venv .venv || return 1
    .venv/bin/python -m pip install --quiet --upgrade pip || return 1
fi

# Use the interpreter directly, not a possibly stale pip console-script shebang.
# Reinstalling the editable package also refreshes its relocated source mapping.
.venv/bin/python -m pip install --quiet -e ".[dev]" || return 1
source .venv/bin/activate
