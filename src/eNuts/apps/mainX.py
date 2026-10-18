# ==================================================================================================
from asyncio import CancelledError, set_event_loop

# ==================================================================================================
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop


# ==================================================================================================
async def main(*args, **kwargs):
    ...

# ==================================================================================================
def program(*args):
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)
    set_event_loop(loop, *args, **kwargs)

    with loop:
        loop.run_until_complete(main(app))

# ==================================================================================================
if __name__ == "__main__":
    program()
