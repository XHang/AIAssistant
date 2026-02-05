import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel
)
from PySide6.QtCore import Signal, QObject, Qt

class WorkerSignals(QObject):
    progress = Signal(int)
    finished = Signal(str)

class TestWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        
    def run(self):
        # 模拟长时间任务
        for i in range(101):
            self.signals.progress.emit(i)
            # 模拟工作延迟
            import time
            time.sleep(0.05)
        self.signals.finished.emit("任务完成!")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多线程测试")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        
        self.label = QLabel("点击按钮开始后台任务")
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.button = QPushButton("开始任务")
        self.button.clicked.connect(self.start_worker)
        
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
        
    def start_worker(self):
        self.progress.setVisible(True)
        self.button.setEnabled(False)
        self.button.setText("任务进行中...")
        
        self.worker = TestWorker()
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.on_finished)
        self.worker.start()
        
    def update_progress(self, value):
        self.progress.setValue(value)
        
    def on_finished(self, message):
        self.progress.setVisible(False)
        self.button.setEnabled(True)
        self.button.setText("开始任务")
        self.label.setText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())