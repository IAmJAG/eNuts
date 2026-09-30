# ==================================================================================
# src/jAGFx/collections/__tsDictionary.py
# ==================================================================================
from threading import RLock


# ==================================================================================
class TSDictionary(dict):
    """
    Thread-Safe Dictionary
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = RLock()

    @property
    def Lock(self):
        return self._lock

    def __getitem__(self, key):
        with self.Lock:
            return super().__getitem__(key)

    def __setitem__(self, key, value):
        with self.Lock:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        with self.Lock:
            super().__delitem__(key)

    def __contains__(self, key):
        with self.Lock:
            return super().__contains__(key)

    def __len__(self):
        with self.Lock:
            return super().__len__()

    def __iter__(self):
        with self.Lock:
            return iter(super().copy())

    def keys(self):
        with self.Lock:
            return list(super().keys())

    def values(self):
        with self.Lock:
            return list(super().values())

    def items(self):
        with self.Lock:
            return list(super().items())

    def get(self, key, default=None):
        with self.Lock:
            return super().get(key, default)

    def pop(self, key, default=None):
        with self.Lock:
            return super().pop(key, default)

    def update(self, other=None, **kwargs):
        with self.Lock:
            super().update(other, **kwargs)

    def clear(self):
        with self.Lock:
            super().clear()
