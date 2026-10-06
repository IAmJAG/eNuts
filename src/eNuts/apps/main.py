# ==================================================================================================
# src/eNuts/apps/main.py
# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import windll
from sys import platform, stdout
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


def _topLevelSummary(app: QApplication) -> str:
    lWidgets = app.topLevelWidgets()
    lParts = [
        f"{type(w).__name__}(name={w.objectName()!r},vis={w.isVisible()},win={w.isWindow()})"
        for w in lWidgets
    ]
    return f"count={len(lWidgets)} {lParts}"


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
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()

    lShutdownEvent: Event = Event()

    def _onAboutToQuit() -> None:
        print(f"[main] aboutToQuit topLevels={_topLevelSummary(app)}", flush=True)
        debug(f"[main] aboutToQuit topLevels={_topLevelSummary(app)}")
        lShutdownEvent.set()

    app.aboutToQuit.connect(_onAboutToQuit)
    # DIAGNOSTIC: False so parentless Page/Header/CommandBar reparent during build
    # cannot trigger automatic QApplication.quit(). Restore True after show() if needed.
    app.setQuitOnLastWindowClosed(False)
    print("[main] quitOnLastWindowClosed=False (diagnostic)", flush=True)

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        lTheme = str(getattr(cfg, "style", None) or "ironman").strip().lower()
        _applyThemePalette(app, lTheme)
        app.setStyleSheet(cfg.styleSheet)

        print(f"[main] before MainWindow topLevels={_topLevelSummary(app)}", flush=True)
        lWin: MainWindow = MainWindow(*args, **kwargs)
        print(
            f"[main] after MainWindow visible={lWin.isVisible()} "
            f"topLevels={_topLevelSummary(app)}",
            flush=True,
        )

        lWin.show()
        app.setQuitOnLastWindowClosed(True)
        print(
            f"[main] after show visible={lWin.isVisible()} "
            f"topLevels={_topLevelSummary(app)}",
            flush=True,
        )

        await lShutdownEvent.wait()

    except CancelledError:
        raise

    except Exception as ex:
        print(f"[main] EXCEPTION {type(ex).__name__}: {ex}\n{format_exc()}", flush=True)
        error(f"[main] Unhandled exception: {type(ex).__name__}: {ex}")
        error(f"[main] traceback:\n{format_exc()}")

    finally:
        if not lShutdownEvent.is_set():
            lShutdownEvent.set()

    app.quit()


# ==================================================================================================
def program(*args):
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    set_event_loop(loop)
    with loop:
        loop.run_until_complete(main(app))


# ==================================================================================================
if __name__ == "__main__":
    program()
