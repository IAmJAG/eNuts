# ==================================================================================
from atexit import register
from logging import Handler
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue


# ==================================================================================
class DynamicQueueHandler(QueueHandler):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DynamicQueueHandler, cls).__new__(cls)
            
        return cls._instance
    
    def __init__(self, queue: Queue = None):        
        super().__init__(queue or Queue(-1))
        self.listener = QueueListener(self.queue)        
        register(self.listener.stop)

    def AddHandler(self, handler: Handler):
        if handler not in self.listener.handlers:
            self.listener.handlers = (handler,) + self.listener.handlers

    def RemoveHandler(self, handler: Handler):
        self.listener.handlers = tuple(h for h in self.listener.handlers if h != handler)

    def Start(self):
        self.listener.start()

    def close(self):
        if self.listener is not None and self.listener._thread is not None: self.listener.stop()    
        super().close()