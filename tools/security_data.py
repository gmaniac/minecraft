"""Wildforge Security — 12 devices.

ACTIVE entities (ticked by the script): motion sensor, laser tripwire, auto turret,
laser emitter. Placed from a crafted item; owner-configurable targeting.
BLOCKS (interact-driven): camera, monitor, owner door, keypad, floodlight, siren, hub.
ITEM: keycard.

Palette keys: body, trim, glass, accent, dark  (reuses the vehicle region map).
"""

# kind drives behavior in scripts/security/index.js
ACTIVE = [
    {"id": "motion_sensor", "name": "Motion Sensor", "kind": "sensor", "health": 30, "scale": 0.8,
     "palette": {"body": "#3a3f44", "trim": "#8a8f95", "glass": "#2a3640", "accent": "#46d06a",
                  "dark": "#15181c"}},
    {"id": "laser_tripwire", "name": "Laser Tripwire", "kind": "tripwire", "health": 30,
     "scale": 0.8, "palette": {"body": "#3a3f44", "trim": "#8a8f95", "glass": "#2a3640",
                                "accent": "#e0432a", "dark": "#15181c"}},
    {"id": "auto_turret", "name": "Auto Turret", "kind": "turret", "health": 80, "scale": 1.0,
     "palette": {"body": "#4a4f55", "trim": "#9a9fa5", "glass": "#2a3640", "accent": "#e0a52a",
                  "dark": "#15181c"}},
    {"id": "laser_emitter", "name": "Laser Emitter", "kind": "laser", "health": 80, "scale": 1.0,
     "palette": {"body": "#3a2f44", "trim": "#9a8fa5", "glass": "#2a3640", "accent": "#ff2a5a",
                  "dark": "#15121c"}},
]

# component: custom block component name (registered in script); full=True -> full cube
BLOCKS = [
    {"id": "security_camera", "name": "Security Camera", "component": "wf:camera", "facing": True,
     "h": 8, "geo": "camera",
     "palette": {"body": "#2a2e33", "trim": "#8a8f95", "glass": "#1aa0e0", "accent": "#e0432a",
                  "dark": "#15181c"}},
    {"id": "monitor", "name": "Security Monitor", "component": "wf:monitor", "facing": True,
     "h": 14, "geo": "monitor",
     "palette": {"body": "#23272c", "trim": "#5a5f65", "glass": "#1aa0e0", "accent": "#46d06a",
                  "dark": "#101316"}},
    {"id": "owner_door", "name": "Security Door", "component": "wf:door", "facing": True,
     "h": 16, "geo": "door", "door": True,
     "palette": {"body": "#5a5f66", "trim": "#3a3f45", "glass": "#1aa0e0", "accent": "#e0a52a",
                  "dark": "#202428"}},
    {"id": "keypad", "name": "Keypad Lock", "component": "wf:keypad", "facing": True, "h": 12,
     "geo": "keypad",
     "palette": {"body": "#2a2e33", "trim": "#8a8f95", "glass": "#46d06a", "accent": "#e0a52a",
                  "dark": "#15181c"}},
    {"id": "floodlight", "name": "Floodlight", "component": None, "facing": False, "h": 16,
     "geo": None, "light": 15,
     "palette": {"body": "#cfd2d6", "trim": "#8a8f95", "glass": "#fff3c4", "accent": "#fff3c4",
                  "dark": "#5a5f65"}},
    {"id": "alarm_siren", "name": "Alarm Siren", "component": "wf:siren", "facing": False, "h": 12,
     "geo": "siren",
     "palette": {"body": "#9a2a2a", "trim": "#e0432a", "glass": "#ffd24a", "accent": "#ffd24a",
                  "dark": "#3a1010"}},
    {"id": "control_hub", "name": "Control Hub", "component": "wf:hub", "facing": True, "h": 16,
     "geo": "hub",
     "palette": {"body": "#23272c", "trim": "#5a5f65", "glass": "#1aa0e0", "accent": "#46d06a",
                  "dark": "#101316"}},
]

KEYCARD = {"id": "keycard", "name": "Keycard"}
