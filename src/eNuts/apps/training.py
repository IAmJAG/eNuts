# ==================================================================================================
from asyncio import set_event_loop

# ==================================================================================================
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# ==================================================================================================
from .main import main as _mainImpl


# ==================================================================================================
async def training(app: QApplication, *args, **kwargs):
    """Delegate to main implementation (SCRCPYEmitter + MainWindow)."""
    await _mainImpl(app, *args, **kwargs)


# ==================================================================================================
def program(*args):
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    set_event_loop(loop)
    with loop:
        loop.run_until_complete(training(app))


# ==================================================================================================
if __name__ == "__main__":
    program()
