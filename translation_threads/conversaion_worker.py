import queue

from PySide6.QtCore import QThread, Signal


class AIWorkerThread(QThread):
    message_received = Signal(str)
    error = Signal(str)

    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.send_queue = queue.Queue()
        self.running = True

    def run(self):
        while self.running:
            user_msg = self.send_queue.get()
            try:
                for chunk in self.api.stream_chat(user_msg):
                    self.message_received.emit(chunk)
            except Exception as e:
                self.error.emit(str(e))

    def send(self, text):
        self.send_queue.put(text)

    def stop(self):
        self.running = False
        self.send_queue.put(None)
