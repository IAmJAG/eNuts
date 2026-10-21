# ==================================================================================
"""Test-only seed maps for policy smoke/unit tests.

Not part of production PolicyOptions / Vocabulary responsibility.
"""

# ==================================================================================
SEED_ACTIONS: dict[str, str] = {
    "down": "finger/right mouse button down",
    "up": "finger/right mouse button up",
    "move": "finger/mouse move",
    "inject": "send key or text",
}

SEED_ARGUMENT_KINDS: dict[str, str] = {
    "coordinate": "normalized point (x, y)",
    "box": "normalized box (left, top, width, height)",
    "key": "keyboard key code (open-ended value)",
    "text": "text string (open-ended value)",
}
