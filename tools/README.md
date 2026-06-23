# MotorCraft toolchain

Procedural generation + validation + packaging for the combined add-on.

## Layout
- `mclib/geometry.py` — Bedrock `.geo.json` builder (bones, cubes, box-UV).
- `mclib/texture.py` — Pillow box-UV net painter (`Tex`, `shade`, `hex_rgba`).
- `gen_icons.py` — pack icons for BP + RP.
- `gen_test_critter.py` — M0 reference generator (model + texture) proving the libs.
- `validate.py` — structural + cross-reference checks (geometry/texture/lang/UUID).
- `build.sh` — validates, then zips `MotorCraft_BP` + `MotorCraft_RP` → `MotorCraft.mcaddon`.

## Usage
```bash
PYTHONPATH=tools python3 tools/gen_<thing>.py   # (re)generate models/textures
python3 tools/validate.py                        # check references
bash tools/build.sh                              # validate + package the .mcaddon
```

Per-domain generators (dragons, pets, …) land here as each milestone is built, each
driven by a parameter block per entity so large rosters stay maintainable.

## "Working" guarantee
This environment can't launch Minecraft. `validate.py` + `node --check` on scripts +
conformance to the shipped Dragons patterns are the automated ceiling; final in-game
verification is a manual checklist in the pack README.
