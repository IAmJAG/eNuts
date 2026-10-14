# ==================================================================================
class _commandBarButtonBase:
    def emit(self, signal: str, *args, **kwargs):
        try:                
            with self._lock:
                try:
                    self.setDisabled(True)
                    super().emit(signal, *args, **kwargs)

                except Exception as ex:
                    raise ex

                finally:
                    self.setDisabled(False)

        except Exception as ex:
            raise ex

        finally:
            self.setDisabled(False)

    def text(self) -> str:
        return super().text()

    def setText(self, text: str): 
        super().setText(text)