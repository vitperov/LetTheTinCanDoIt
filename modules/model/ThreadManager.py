from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal

class Worker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)

class ThreadManager(QObject):
    def __init__(self):
        super().__init__()
        self.threads = []

    def execute_async(self, callable, callback, error_callback):
        thread = QThread()
        worker = Worker(callable)
        worker.moveToThread(thread)

        # Connect signals for thread management
        thread.started.connect(lambda: print("Thread started:", thread))
        thread.started.connect(lambda: QTimer.singleShot(0, worker.run))
        worker.finished.connect(callback)
        worker.error.connect(error_callback)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda: print("Thread finished:", thread))
        thread.finished.connect(lambda: self._remove_thread(thread))
        thread.finished.connect(thread.deleteLater)

        # Track thread to prevent garbage collection
        self.threads.append(thread)
        thread.start()

    def _remove_thread(self, thread):
        if thread in self.threads:
            self.threads.remove(thread)
            print("Removed thread:", thread)
