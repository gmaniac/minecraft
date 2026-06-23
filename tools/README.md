# Wildforge toolchain

Procedural generation + validation + packaging for the combined add-on.

## Layout
- `mclib/geometry.py` — Bedrock `.geo.json` builder (bones, cubes, box-UV).
- `mclib/texture.py` — Pillow box-UV net painter (`Tex`, `shade`, `hex_rgba`).
- `gen_icons.py` — pack icons for BP + RP.
- `gen_test_critter.py` — M0 reference generator (model + texture) proving the libs.
- `validate.py` — structural + cross-reference checks (geometry/texture/lang/UUID).
- `build.sh` — validates, then zips `Wildforge_BP` + `Wildforge_RP` → `Wildforge.mcaddon`.

## Usage
```bash
PYTHONPATH=tools python3 tools/gen_<thing>.py   # (re)generate models/textures
python3 tools/bump_version.py minor              # bump version when you change things
python3 tools/validate.py                        # check references + version consistency
bash tools/build.sh                              # validate + package the .mcaddon
```

Per-domain generators (dragons, pets, …) land here as each milestone is built, each
driven by a parameter block per entity so large rosters stay maintainable.

## Versioning
`VERSION` (repo root) is the single source of truth. **Bump it whenever you ship a
change** — `validate.py` fails if the manifests don't match it, so an unbumped change
won't build.
- `bump_version.py patch` — fixes (0.8.0 → 0.8.1)
- `bump_version.py minor` — new features/content (0.8.1 → 0.9.0)
- `bump_version.py major` — major release (0.9.0 → 1.0.0)

It stamps the version into both manifests (header, modules, inter-pack dependency);
the `@minecraft/*` module dependencies are left alone.

## "Working" guarantee
This environment can't launch Minecraft. `validate.py` + `node --check` on scripts +
conformance to the shipped Dragons patterns are the automated ceiling; final in-game
verification is a manual checklist in the pack README.
