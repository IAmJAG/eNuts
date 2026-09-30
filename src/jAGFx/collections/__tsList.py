# ==================================================================================
# src/jAGFx/collections/__tsList.py
# ==================================================================================
from threading import RLock


# ==================================================================================
class TSList(list):
    """
    Thread-Safe List
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = RLock()

    @property
    def Lock(self):
        return self._lock

    def __getitem__(self, index):
        with self.Lock:
            return super().__getitem__(index)

    def __setitem__(self, index, value):
        with self.Lock:
            super().__setitem__(index, value)

    def __delitem__(self, index):
        with self.Lock:
            super().__delitem__(index)

    def __len__(self):
        with self.Lock:
            return super().__len__()

    def append(self, value):
        with self.Lock:
            super().append(value)

    def extend(self, iterable):
        with self.Lock:
            super().extend(iterable)

    def insert(self, index, value):
        with self.Lock:
            super().insert(index, value)

    def remove(self, value):
        with self.Lock:
            super().remove(value)

    def pop(self, index=-1):
        with self.Lock:
            return super().pop(index)

    def clear(self):
        with self.Lock:
            super().clear()

    def index(self, value, start=0, end=None):
        with self.Lock:
            return super().index(value, start, end if end is not None else len(self))

    def count(self, value):
        with self.Lock:
            return super().count(value)

    def sort(self, *args, **kwargs):
        with self.Lock:
            super().sort(*args, **kwargs)

    def reverse(self):
        with self.Lock:
            super().reverse()

    def copy(self):
        with self.Lock:
            return TSList(super().copy())
