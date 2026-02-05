import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QFileDialog, QMessageBox,QComboBox,QProgressBar
)
from PySide6.QtCore import Signal, QObject
from llama_server import LlamaServer
from translator import Translator

class WorkerSignals(QObject):
    finished = Signal(str, str, str)  # result, target_lang, file_path
    progress = Signal(int, int)  # done, total
    error = Signal(str)  # error message

class FileTranslateWorker(threading.Thread):
    def __init__(self, translator, content, target_lang, file_path):
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

class TranslatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.input_file_path = None
        self.setWindowTitle("AI 翻译工具 - PySide6 + llama.cpp")
        self.resize(600, 500)

        # 启动 llama-server
        self.server = LlamaServer()
        self.server.start()

        # 翻译器
        self.translator = Translator()

        layout = QVBoxLayout()

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入要翻译的内容...")

        self.send_btn = QPushButton("翻译")
        self.send_btn.clicked.connect(self.handle_translate)

        self.file_btn = QPushButton("选择文件并翻译")
        self.file_btn.clicked.connect(self.handle_file_translate)

        self.lang_box = QComboBox()
        self.lang_box.addItems(["中文", "英文", "日文", "韩文", "法文"])
        self.lang_box.setCurrentText("中文")  # 默认中文

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)  # 默认隐藏

        layout.addWidget(self.progress)
        layout.addWidget(self.lang_box)
        layout.addWidget(self.chat_box)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_btn)
        layout.addWidget(self.file_btn)

        self.setLayout(layout)

    def handle_translate(self):
        text = self.input_box.text().strip()
        if not text:
            return

        self.chat_box.append(f"你：{text}")
        result = self.translator.translate(text,self.lang_box.currentText())
        self.chat_box.append(f"AI：{result}\n")
        self.input_box.clear()

    def handle_file_translate(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要翻译的文件", "", "文本文件 (*.txt)")
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            QMessageBox.warning(self, "错误", "无法读取文件")
            return

        target_lang = self.lang_box.currentText()

        # ⭐ 保存输入文件路径
        self.input_file_path = file_path

        # ⭐ 显示进度条
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        # ⭐ 创建并启动后台线程
        self.worker = FileTranslateWorker(self.translator, content, target_lang, file_path)
        self.worker.signals.progress.connect(self.update_progress_bar)
        self.worker.signals.finished.connect(self.on_translation_finished)
        self.worker.signals.error.connect(self.on_translation_error)
        self.worker.start()
        
        # ⭐ 禁用按钮防止重复点击
        self.file_btn.setEnabled(False)
        self.file_btn.setText("翻译中...")
    
    def update_progress_bar(self, done, total):
        percent = int(done / total * 100)
        self.progress.setValue(percent)
    
    def on_translation_finished(self, result, target_lang, file_path):
        # ⭐ 翻译完成后隐藏进度条
        self.progress.setVisible(False)
        
        # ⭐ 恢复按钮状态
        self.file_btn.setEnabled(True)
        self.file_btn.setText("选择文件并翻译")
        
        # ⭐ 保存结果到与输入文件相同的文件夹
        import os
        input_dir = os.path.dirname(file_path)
        input_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_filename = f"{input_filename}_translated.txt"
        output_path = os.path.join(input_dir, output_filename)
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
            QMessageBox.information(self, "完成", f"翻译完成（{target_lang}），已保存到：{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文件失败：{str(e)}")
    
    def on_translation_error(self, error_msg):
        # ⭐ 隐藏进度条
        self.progress.setVisible(False)
        
        # ⭐ 恢复按钮状态
        self.file_btn.setEnabled(True)
        self.file_btn.setText("选择文件并翻译")
        
        # ⭐ 显示错误信息
        QMessageBox.critical(self, "翻译错误", f"翻译过程中发生错误：\n{error_msg}")

    def closeEvent(self, event):
        self.server.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TranslatorGUI()
    gui.show()
    sys.exit(app.exec())
