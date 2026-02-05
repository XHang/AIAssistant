import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QFileDialog, QMessageBox,QComboBox,QProgressBar
)
from llama_server import LlamaServer
from translator import Translator

class TranslatorGUI(QWidget):
    def __init__(self):
        super().__init__()
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

        # ⭐ 显示进度条
        self.progress.setVisible(True)
        self.progress.setValue(0)

        # ⭐ 回调函数：更新进度条
        def update_progress(done, total):
            percent = int(done / total * 100)
            self.progress.setValue(percent)

        # ⭐ 调用翻译器（传入回调）
        result = self.translator.translate_from_file(
            content,
            target_lang,
            progress_callback=update_progress
        )

        # ⭐ 翻译完成后隐藏进度条
        self.progress.setVisible(False)

        output_path = "output_translated.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)

        QMessageBox.information(self, "完成", f"翻译完成（{target_lang}），已保存到：{output_path}")

    def closeEvent(self, event):
        self.server.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TranslatorGUI()
    gui.show()
    sys.exit(app.exec())
