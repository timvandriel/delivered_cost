from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot


class WorkerSignals(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    log = pyqtSignal(str)


class DeliveredCostWorker(QRunnable):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        from .delvCost import run

        try:

            def log_fn(msg):
                self.signals.log.emit(msg)

            class PBarWrapper:
                def __init__(self, emit_func):
                    self._val = 0
                    self._max = 12
                    self._emit = emit_func

                def setValue(self, val):
                    self._val = val
                    self._emit.emit(val)

                def value(self):
                    return self._val

                def setmaximum(self, val):
                    self._max = val

                def maximum(self):
                    return self._max

            self.args["pbar"] = PBarWrapper(self.signals.progress)
            self.args["log"] = log_fn

            result = run(**self.args)
            self.signals.finished.emit(result)

        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            self.signals.error.emit(f"Error: {str(e)}\n{tb}")
