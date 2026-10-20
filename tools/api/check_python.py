"""Check a declared Python surface without calling its constructors or methods.

Mypy performs native structural subtyping; reflection only prevents missing/Any
annotations from being accepted as evidence of type conformance. Imports execute.
"""

import argparse
import importlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, get_args, get_type_hints


ROOT = Path(__file__).resolve().parents[2]


def contains_any(annotation: object) -> bool:
    """Reject Any even when nested in an otherwise annotated generic."""
    return annotation is Any or any(contains_any(arg) for arg in get_args(annotation))


def annotation_errors(surface: dict) -> list[str]:
    """Inspect declarations only; never instantiate records or exercise accessors."""
    module, name = surface["target"].rsplit(".", 1)
    target = getattr(importlib.import_module(module), name)
    errors = []
    for member in surface["members"]:
        name = member["name"]
        try:
            declaration = inspect.getattr_static(target, name)
        except AttributeError:
            errors.append(f"{name}: missing member")
            continue
        if member["kind"] == "attribute":
            if not isinstance(declaration, property):
                errors.append(f"{name}: prototype requires an explicitly typed property")
                continue
            functions = [declaration.fget]
            if not member["readonly"]:
                functions.append(declaration.fset)
        else:
            if (isinstance(declaration, classmethod)
                    or isinstance(declaration, staticmethod) != member["static"]):
                errors.append(f"{name}: static/instance method mismatch")
            if isinstance(declaration, (staticmethod, classmethod)):
                declaration = declaration.__func__
            if callable(declaration):
                parameters = inspect.signature(declaration).parameters
                for param in member["parameters"]:
                    actual = parameters.get(param["name"])
                    if param["optional"] and (actual is None or actual.default is not None):
                        errors.append(f"{name}.{param['name']}: expected explicit None default")
            functions = [declaration]
        for function in functions:
            if function is None or not callable(function):
                errors.append(f"{name}: missing accessor/callable")
                continue
            try:
                hints = get_type_hints(function)
            except (NameError, TypeError) as error:
                errors.append(f"{name}: unverified annotations ({error})")
                continue
            parameters = inspect.signature(function).parameters
            required = {param for param in parameters if param not in {"self", "cls"}}
            for key in sorted(required | {"return"}):
                if key not in hints or contains_any(hints[key]):
                    errors.append(f"{name}.{key}: unverified annotation (missing or Any)")
    return errors


def main() -> int:
    """Generate expected declarations and check the actual imported/source class."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=ROOT / "api/dicom4ortho.webidl")
    parser.add_argument("--bindings", type=Path, default=ROOT / "python/api-bindings.json")
    args = parser.parse_args()
    # Never depend on the editable install of another worktree.
    sys.path.insert(0, str(ROOT / "python"))
    with tempfile.TemporaryDirectory(prefix="d4o-api-") as directory:
        output = Path(directory) / "expected"
        subprocess.run([
            "node", str(ROOT / "tools/api/generate.mjs"), "--spec", str(args.spec),
            "--bindings", str(args.bindings), "--output", str(output),
        ], check=True)
        surface = json.loads((output / "surface.json").read_text(encoding="utf-8"))
        errors = annotation_errors(surface)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        env = os.environ.copy()
        env["MYPYPATH"] = os.pathsep.join([
            str(ROOT / "python"), str(output), env.get("MYPYPATH", ""),
        ])
        # Follow the implementation's .py declarations, NOT generated replacement stubs.
        result = subprocess.run([
            sys.executable, "-m", "mypy", "--strict", "--follow-imports=silent",
            "--no-incremental", "--cache-dir=/dev/null", str(output / "probe.py"),
        ], env=env, check=False)
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
