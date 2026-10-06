# ==================================================================================================
# src/eNuts/apps/main.py
# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import windll
from sys import platform
from traceback import format_exc

# ==================================================================================================
from adbutils import adb
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# ==================================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================================
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import MainWindow

# ==================================================================================================
C_DARK_THEMES = frozenset({"dark", "dracula", "ironman", "material"})


def _applyThemePalette(app: QApplication, theme: str) -> None:
    """Override system palette so text is never black-on-dark (or white-on-light)."""
    lPal = QPalette(app.palette())
    if theme in C_DARK_THEMES:
        lFg = QColor("#f5f7fa")
        lBg = QColor("#0e1014")
        lBase = QColor("#1e242c")
        lAlt = QColor("#161a20")
        lDisabled = QColor("#6b7280")
        lHighlight = QColor("#e31b23")
        lHighlightedText = QColor("#ffffff")
    else:
        lFg = QColor("#1a1a1a")
        lBg = QColor("#f5f5f5")
        lBase = QColor("#ffffff")
        lAlt = QColor("#eeeeee")
        lDisabled = QColor("#9e9e9e")
        lHighlight = QColor("#1976d2")
        lHighlightedText = QColor("#ffffff")

    for lRole in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.BrightText,
        QPalette.ColorRole.ToolTipText,
        QPalette.ColorRole.PlaceholderText,
    ):
        lPal.setColor(QPalette.ColorGroup.Active, lRole, lFg)
        lPal.setColor(QPalette.ColorGroup.Inactive, lRole, lFg)
        lPal.setColor(QPalette.ColorGroup.Disabled, lRole, lDisabled)

    for lRole, lColor in (
        (QPalette.ColorRole.Window, lBg),
        (QPalette.ColorRole.Base, lBase),
        (QPalette.ColorRole.AlternateBase, lAlt),
        (QPalette.ColorRole.Button, lBase),
        (QPalette.ColorRole.ToolTipBase, lBase),
        (QPalette.ColorRole.Highlight, lHighlight),
        (QPalette.ColorRole.HighlightedText, lHighlightedText),
    ):
        lPal.setColor(QPalette.ColorGroup.Active, lRole, lColor)
        lPal.setColor(QPalette.ColorGroup.Inactive, lRole, lColor)
        lPal.setColor(QPalette.ColorGroup.Disabled, lRole, lColor)

    app.setPalette(lPal)


# ==================================================================================================
async def main(app: QApplication, *args, **kwargs):
    debug("[main] enter async main")
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()
    debug("[main] config loaded")

    lShutdownEvent: Event = Event()
    app.aboutToQuit.connect(lambda: debug("[main] aboutToQuit fired") or lShutdownEvent.set())
    app.setQuitOnLastWindowClosed(True)
    debug("[main] quitOnLastWindowClosed=True")

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        lTheme = str(getattr(cfg, "style", None) or "ironman").strip().lower()
        debug(f"[main] theme={lTheme!r} — applying palette + stylesheet")
        _applyThemePalette(app, lTheme)
        app.setStyleSheet(cfg.styleSheet)
        debug("[main] stylesheet applied")

        debug("[main] constructing MainWindow…")
        lWin: MainWindow = MainWindow(*args, **kwargs)
        debug(
            f"[main] MainWindow constructed id={id(lWin)} "
            f"visible={lWin.isVisible()} size={lWin.size().width()}x{lWin.size().height()}"
        )

        debug("[main] calling show()")
        lWin.show()
        debug(
            f"[main] after show() visible={lWin.isVisible()} "
            f"active={lWin.isActiveWindow()} "
            f"topLevel={lWin.isWindow()} "
            f"geometry={lWin.geometry().getRect()}"
        )

        debug("[main] waiting on shutdown event")
        await lShutdownEvent.wait()
        debug("[main] shutdown event set — exiting wait")

    except CancelledError:
        debug("[main] CancelledError")
        raise

    except Exception as ex:
        error(f"[main] Unhandled exception: {type(ex).__name__}: {ex}")
        error(f"[main] traceback:\n{format_exc()}")

    finally:
        if not lShutdownEvent.is_set():
            debug("[main] finally: forcing shutdown event")
            lShutdownEvent.set()

    debug("[main] app.quit()")
    app.quit()


# ==================================================================================================
def program(*args):
    debug("[main] program() start")
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    set_event_loop(loop)
    debug("[main] event loop set — run_until_complete(main)")
    with loop:
        loop.run_until_complete(main(app))
    debug("[main] program() end")


# ==================================================================================================
if __name__ == "__main__":
    program()
