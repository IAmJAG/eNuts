# ==================================================================================================
# src/eNuts/apps/main.py
# ==================================================================================================
from asyncio import set_event_loop

# ==================================================================================================
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop


# ==================================================================================================
async def _training(app: QApplication, *args):
    debug("Training")
    app.quit()

# ==================================================================================================
def program(*args):
    debug("App Main Started")
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    set_event_loop(loop)
    with loop:
        loop.run_until_complete(_training(app))
    
    
# ==================================================================================================
if __name__ == "__main__":
    program()