# ==================================================================================================
# src/eNuts/apps/main.py
# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import windll
from sys import platform

# ==================================================================================================
from adbutils import adb
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# ==================================================================================================
from fluxCore.emitters import SCRCPYEmitter
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================================
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import MainWindow


# ==================================================================================================
async def main(app: QApplication, *args, **kwargs):
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()

    lShutdownEvent: Event = Event()
    app.aboutToQuit.connect(lShutdownEvent.set)
    app.setQuitOnLastWindowClosed(True)

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    lEmitter: SCRCPYEmitter | None = None

    try:
        app.setStyleSheet(cfg.styleSheet)

        lWin: MainWindow = MainWindow(*args, **kwargs)
        lWin.show()

        # ----- SCRCPYEmitter: receive packets only (verbose logs, no display) -----
        lDevices = adb.device_list()
        verbose(f"main: adb devices count={len(lDevices)}")
        if lDevices:
            # Prefer second device when present (training port); else first.
            lDevice = lDevices[1] if len(lDevices) > 1 else lDevices[0]
            lSerial = lDevice.serial
            verbose(f"main: using device serial={lSerial!r}")
            lEmitter = SCRCPYEmitter(serial=lSerial)
            await lEmitter.initialize(GPUReady=False)
            lEmitter.start()
            verbose("main: SCRCPYEmitter started")
        else:
            warning("main: no adb devices — SCRCPYEmitter not started")

        await lShutdownEvent.wait()

    except CancelledError:
        raise

    except Exception as ex:
        error(f"Unhandled exception: {type(ex).__name__}: {ex}")

    finally:
        if lEmitter is not None and lEmitter.isRunning:
            verbose("main: stopping SCRCPYEmitter")
            lEmitter.stop()
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
