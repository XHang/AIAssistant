from PySide6.QtCore import Signal, QObject
import threading
from translator import Translator

class WorkerSignals(QObject):
    finished = Signal(str, str, str)  # result, target_lang, file_path
    progress = Signal(int, int)  # done, total
    error = Signal(str)  # error message


class FileTranslateWorker(threading.Thread):
    def __init__(self, translator: Translator, content: str, target_lang: str, file_path: str):
        super().__init__()
        self.translator = translator
        self.content = content
        self.target_lang = target_lang
        self.file_path = file_path
        self.signals = WorkerSignals()

    def run(self):
        try:
            # 回调函数：发送进度信号
            def update_progress(done, total):
                self.signals.progress.emit(done, total)

            # 执行翻译
            result = self.translator.translate_from_file(
                self.content,
                self.target_lang,
                progress_callback=update_progress
            )

            # 发送完成信号（包含文件路径）
            self.signals.finished.emit(result, self.target_lang, self.file_path)
        except Exception as e:
            self.signals.error.emit(str(e))