#!/usr/bin/env bash
# Sourced by the Nix shell from the repository root. Never discard an existing
# environment: activation scripts and installed command shebangs embed its path.

_dicom4ortho_activate_venv() {
    local restore_disabled_hashing=0 activation_status
    # Nix disables command hashing. Python's activate ends with `hash -r`, which
    # then returns 1 even after successful activation. Restore Nix's setting after
    # activation instead of treating that incidental status as a setup failure.
    case "$-" in
        *h*) ;;
        *) restore_disabled_hashing=1; set -h ;;
    esac
    if source .venv/bin/activate; then
        activation_status=0
    else
        activation_status=$?
    fi
    if [ "$restore_disabled_hashing" -eq 1 ]; then
        set +h
    fi
    return "$activation_status"
}

if [ -f .venv/bin/activate ] && ! (
    unset VIRTUAL_ENV
    _dicom4ortho_activate_venv && [ "${VIRTUAL_ENV:-}" -ef "$PWD/.venv" ]
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
_dicom4ortho_activate_venv || return 1
unset -f _dicom4ortho_activate_venv
