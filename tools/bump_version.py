#!/usr/bin/env python3
"""Single-source version bumping for Wildforge.

The repo-root VERSION file is the source of truth. This stamps that version into
both pack manifests: header.version, every module version, and the inter-pack
(uuid-based) dependency versions. The @minecraft/* module dependencies are left
alone.

Usage:
    python tools/bump_version.py            # bump patch  (0.8.0 -> 0.8.1)
    python tools/bump_version.py patch
    python tools/bump_version.py minor      # 0.8.1 -> 0.9.0
    python tools/bump_version.py major      # 0.9.0 -> 1.0.0
    python tools/bump_version.py set 1.2.3  # set explicitly

Convention: patch = fixes, minor = new features/content, major = big releases.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(ROOT, "VERSION")
MANIFESTS = [os.path.join(ROOT, "Wildforge_BP", "manifest.json"),
             os.path.join(ROOT, "Wildforge_RP", "manifest.json")]


def read_version():
    with open(VERSION_FILE) as f:
        return [int(x) for x in f.read().strip().split(".")]


def write_version(v):
    with open(VERSION_FILE, "w") as f:
        f.write(".".join(str(x) for x in v) + "\n")


def stamp_manifests(v):
    for path in MANIFESTS:
        with open(path) as f:
            m = json.load(f)
        m["header"]["version"] = list(v)
        for mod in m.get("modules", []):
            mod["version"] = list(v)
        for dep in m.get("dependencies", []):
            if "uuid" in dep:                # inter-pack dependency -> our own version
                dep["version"] = list(v)
        with open(path, "w") as f:
            json.dump(m, f, indent=2, ensure_ascii=False)
            f.write("\n")


def main(argv):
    v = read_version()
    if not argv:
        v[2] += 1
    elif argv[0] == "patch":
        v[2] += 1
    elif argv[0] == "minor":
        v[1] += 1
        v[2] = 0
    elif argv[0] == "major":
        v[0] += 1
        v[1] = v[2] = 0
    elif argv[0] == "set" and len(argv) > 1:
        v = [int(x) for x in argv[1].split(".")]
    else:
        print(__doc__)
        return 1
    write_version(v)
    stamp_manifests(v)
    print(f"version -> {'.'.join(str(x) for x in v)}  (stamped into both manifests)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
