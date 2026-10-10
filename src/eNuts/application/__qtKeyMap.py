# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import Qt

# ==================================================================================
from fluxCore.action.android.enums import eKeyCode, eMetaState


# ==================================================================================
# Host (Qt) → Android keycode. Lives in eNuts — fluxCore stays Qt-free.
# ==================================================================================
_C_QT_TO_ANDROID: dict[int, eKeyCode] = {
    Qt.Key.Key_0: eKeyCode.KEYCODE_0,
    Qt.Key.Key_1: eKeyCode.KEYCODE_1,
    Qt.Key.Key_2: eKeyCode.KEYCODE_2,
    Qt.Key.Key_3: eKeyCode.KEYCODE_3,
    Qt.Key.Key_4: eKeyCode.KEYCODE_4,
    Qt.Key.Key_5: eKeyCode.KEYCODE_5,
    Qt.Key.Key_6: eKeyCode.KEYCODE_6,
    Qt.Key.Key_7: eKeyCode.KEYCODE_7,
    Qt.Key.Key_8: eKeyCode.KEYCODE_8,
    Qt.Key.Key_9: eKeyCode.KEYCODE_9,
    Qt.Key.Key_A: eKeyCode.KEYCODE_A,
    Qt.Key.Key_B: eKeyCode.KEYCODE_B,
    Qt.Key.Key_C: eKeyCode.KEYCODE_C,
    Qt.Key.Key_D: eKeyCode.KEYCODE_D,
    Qt.Key.Key_E: eKeyCode.KEYCODE_E,
    Qt.Key.Key_F: eKeyCode.KEYCODE_F,
    Qt.Key.Key_G: eKeyCode.KEYCODE_G,
    Qt.Key.Key_H: eKeyCode.KEYCODE_H,
    Qt.Key.Key_I: eKeyCode.KEYCODE_I,
    Qt.Key.Key_J: eKeyCode.KEYCODE_J,
    Qt.Key.Key_K: eKeyCode.KEYCODE_K,
    Qt.Key.Key_L: eKeyCode.KEYCODE_L,
    Qt.Key.Key_M: eKeyCode.KEYCODE_M,
    Qt.Key.Key_N: eKeyCode.KEYCODE_N,
    Qt.Key.Key_O: eKeyCode.KEYCODE_O,
    Qt.Key.Key_P: eKeyCode.KEYCODE_P,
    Qt.Key.Key_Q: eKeyCode.KEYCODE_Q,
    Qt.Key.Key_R: eKeyCode.KEYCODE_R,
    Qt.Key.Key_S: eKeyCode.KEYCODE_S,
    Qt.Key.Key_T: eKeyCode.KEYCODE_T,
    Qt.Key.Key_U: eKeyCode.KEYCODE_U,
    Qt.Key.Key_V: eKeyCode.KEYCODE_V,
    Qt.Key.Key_W: eKeyCode.KEYCODE_W,
    Qt.Key.Key_X: eKeyCode.KEYCODE_X,
    Qt.Key.Key_Y: eKeyCode.KEYCODE_Y,
    Qt.Key.Key_Z: eKeyCode.KEYCODE_Z,
    Qt.Key.Key_Space: eKeyCode.KEYCODE_SPACE,
    Qt.Key.Key_Return: eKeyCode.KEYCODE_ENTER,
    Qt.Key.Key_Enter: eKeyCode.KEYCODE_ENTER,
    Qt.Key.Key_Backspace: eKeyCode.KEYCODE_DEL,
    Qt.Key.Key_Delete: eKeyCode.KEYCODE_FORWARD_DEL,
    Qt.Key.Key_Tab: eKeyCode.KEYCODE_TAB,
    Qt.Key.Key_Escape: eKeyCode.KEYCODE_ESCAPE,
    Qt.Key.Key_Up: eKeyCode.KEYCODE_DPAD_UP,
    Qt.Key.Key_Down: eKeyCode.KEYCODE_DPAD_DOWN,
    Qt.Key.Key_Left: eKeyCode.KEYCODE_DPAD_LEFT,
    Qt.Key.Key_Right: eKeyCode.KEYCODE_DPAD_RIGHT,
    Qt.Key.Key_Home: eKeyCode.KEYCODE_MOVE_HOME,
    Qt.Key.Key_End: eKeyCode.KEYCODE_MOVE_END,
    Qt.Key.Key_PageUp: eKeyCode.KEYCODE_PAGE_UP,
    Qt.Key.Key_PageDown: eKeyCode.KEYCODE_PAGE_DOWN,
    Qt.Key.Key_Insert: eKeyCode.KEYCODE_INSERT,
    Qt.Key.Key_Comma: eKeyCode.KEYCODE_COMMA,
    Qt.Key.Key_Period: eKeyCode.KEYCODE_PERIOD,
    Qt.Key.Key_Slash: eKeyCode.KEYCODE_SLASH,
    Qt.Key.Key_Backslash: eKeyCode.KEYCODE_BACKSLASH,
    Qt.Key.Key_Semicolon: eKeyCode.KEYCODE_SEMICOLON,
    Qt.Key.Key_Apostrophe: eKeyCode.KEYCODE_APOSTROPHE,
    Qt.Key.Key_Minus: eKeyCode.KEYCODE_MINUS,
    Qt.Key.Key_Equal: eKeyCode.KEYCODE_EQUALS,
    Qt.Key.Key_BracketLeft: eKeyCode.KEYCODE_LEFT_BRACKET,
    Qt.Key.Key_BracketRight: eKeyCode.KEYCODE_RIGHT_BRACKET,
    Qt.Key.Key_F1: eKeyCode.KEYCODE_F1,
    Qt.Key.Key_F2: eKeyCode.KEYCODE_F2,
    Qt.Key.Key_F3: eKeyCode.KEYCODE_F3,
    Qt.Key.Key_F4: eKeyCode.KEYCODE_F4,
    Qt.Key.Key_F5: eKeyCode.KEYCODE_F5,
    Qt.Key.Key_F6: eKeyCode.KEYCODE_F6,
    Qt.Key.Key_F7: eKeyCode.KEYCODE_F7,
    Qt.Key.Key_F8: eKeyCode.KEYCODE_F8,
    Qt.Key.Key_F9: eKeyCode.KEYCODE_F9,
    Qt.Key.Key_F10: eKeyCode.KEYCODE_F10,
    Qt.Key.Key_F11: eKeyCode.KEYCODE_F11,
    Qt.Key.Key_F12: eKeyCode.KEYCODE_F12,
    Qt.Key.Key_VolumeUp: eKeyCode.KEYCODE_VOLUME_UP,
    Qt.Key.Key_VolumeDown: eKeyCode.KEYCODE_VOLUME_DOWN,
    Qt.Key.Key_VolumeMute: eKeyCode.KEYCODE_VOLUME_MUTE,
    Qt.Key.Key_Back: eKeyCode.KEYCODE_BACK,
    Qt.Key.Key_Menu: eKeyCode.KEYCODE_MENU,
}


# ==================================================================================
def MapQtKeyToAndroid(key: int) -> eKeyCode | None:
    return _C_QT_TO_ANDROID.get(int(key))


def MapQtModifiersToMeta(modifiers: int) -> eMetaState:
    lValue = 0
    try:
        if modifiers & int(Qt.KeyboardModifier.ShiftModifier):
            lValue |= eMetaState.SHIFT_ON.value
        if modifiers & int(Qt.KeyboardModifier.ControlModifier):
            lValue |= eMetaState.CTRL_ON.value
        if modifiers & int(Qt.KeyboardModifier.AltModifier):
            lValue |= eMetaState.ALT_ON.value
        if modifiers & int(Qt.KeyboardModifier.MetaModifier):
            lValue |= eMetaState.META_ON.value
        return eMetaState(lValue) if lValue else eMetaState.NONE
    except Exception:
        return eMetaState.NONE
