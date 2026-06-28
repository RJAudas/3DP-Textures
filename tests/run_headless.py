"""Headless test runner.

Run with::

    blender --background --python tests/run_headless.py

Discovers ``test_*`` modules in this directory, runs every ``test_*`` function,
and exits non-zero if any fail (Constitution Principle V / Definition of Done).
"""

import importlib
import os
import sys
import traceback

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _discover_modules():
    if _THIS_DIR not in sys.path:
        sys.path.insert(0, _THIS_DIR)
    names = []
    for fname in sorted(os.listdir(_THIS_DIR)):
        if fname.startswith("test_") and fname.endswith(".py"):
            names.append(fname[:-3])
    return names


def main():
    modules = _discover_modules()
    total = 0
    failures = []

    for mod_name in modules:
        module = importlib.import_module(mod_name)
        funcs = [getattr(module, n) for n in sorted(dir(module))
                 if n.startswith("test_") and callable(getattr(module, n))]
        for func in funcs:
            total += 1
            label = "%s.%s" % (mod_name, func.__name__)
            try:
                func()
                print("PASS  %s" % label)
            except Exception as exc:  # noqa: BLE001 - report every failure
                failures.append((label, exc))
                print("FAIL  %s: %s" % (label, exc))
                traceback.print_exc()

    print("\n%d passed, %d failed (of %d)" % (total - len(failures), len(failures), total))

    if failures:
        # Exit non-zero so CI / scripts detect the failure.
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
