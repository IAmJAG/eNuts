# ==================================================================================
from enum import IntEnum


# ==================================================================================
class eMetaState(IntEnum):

    NONE = 0x00000000

    # --- ALT Keys ---
    ALT_ON = 0x00000002  # Soft/generic Alt state
    ALT_LEFT_ON = 0x00000010  # Left Alt key held
    ALT_RIGHT_ON = 0x00000020  # Right Alt key held

    # --- SHIFT Keys ---
    SHIFT_ON = 0x00000001  # Soft/generic Shift state
    SHIFT_LEFT_ON = 0x00000040  # Left Shift key held
    SHIFT_RIGHT_ON = 0x00000080  # Right Shift key held

    # --- SYM Key ---
    SYM_ON = 0x00000100  # Symbol modifier key active

    # --- FUNCTION Key ---
    FUNCTION_ON = 0x00000800  # Function (Fn) key held

    # --- CTRL Keys ---
    CTRL_ON = 0x00001000  # Generic Control state
    CTRL_LEFT_ON = 0x00002000  # Left Control key held
    CTRL_RIGHT_ON = 0x00004000  # Right Control key held

    # --- META Keys (Windows / Command) ---
    META_ON = 0x00010000  # Generic Meta state
    META_LEFT_ON = 0x00020000  # Left Windows/Command key held
    META_RIGHT_ON = 0x00040000  # Right Windows/Command key held

    # --- LOCK Modifiers (Toggles) ---
    CAPS_LOCK_ON = 0x00100000  # Caps Lock is toggled active
    NUM_LOCK_ON = 0x00200000  # Num Lock is toggled active
    SCROLL_LOCK_ON = 0x00400000  # Scroll Lock is toggled active
