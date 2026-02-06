import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QComboBox, QProgressBar
)
from llama_server import LlamaServer
from config_manager import config_manager
from translation_manager import TranslationManager


class TranslatorGUI(QWidget):
    """
        GUI for translator
    """

    def __init__(self):
        super().__init__()
        self.translation_manager = TranslationManager()
        self.setWindowTitle("AI 翻译工具 - PySide6 + llama.cpp")
        self.resize(600, 500)

        # 启动 llama-server
        self.server = LlamaServer()
        self.server.start()

        # 预加载配置以确保只读取一次
        config_manager.load_config()

        layout = QVBoxLayout()

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        layout.addWidget(self.chat_box)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入要翻译的内容...")
        layout.addWidget(self.input_box)

        self.send_btn = QPushButton("翻译")
        self.send_btn.clicked.connect(self.handle_translate)
        layout.addWidget(self.send_btn)

        self.file_btn = QPushButton("选择文件并翻译")
        self.file_btn.clicked.connect(self.handle_file_translate)
        layout.addWidget(self.file_btn)

        self.lang_box = QComboBox()
        self.lang_box.addItems(["中文", "英文", "日文", "韩文", "法文"])
        self.lang_box.setCurrentText("中文")  # 默认中文
        layout.addWidget(self.lang_box)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)  # 默认隐藏
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def handle_translate(self):
        """
            deal with directly translate
        :return: none
        """
        text = self.input_box.text().strip()
        if not text:
            return

        self.chat_box.append(f"你：{text}")
        result = self.translation_manager.translate_text(text, self.lang_box.currentText())
        self.chat_box.append(f"AI：{result}\n")
        self.input_box.clear()

    def handle_file_translate(self):
        """
            deal with file translate
        :return: none
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要翻译的文件", "")
        if not file_path:
            return

        target_lang = self.lang_box.currentText()

        try:
            # 调用翻译管理器进行文件翻译
            self.translation_manager.translate_file(
                file_path, 
                target_lang,
                progress_callback=self.update_progress_bar,
                finished_callback=self.on_translation_finished,
                error_callback=self.on_translation_error
            )
            
            # 显示进度条
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            # 禁用按钮防止重复点击
            self.file_btn.setEnabled(False)
            self.file_btn.setText("翻译中...")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def update_progress_bar(self, done, total):
        percent = int(done / total * 100)
        self.progress.setValue(percent)

    def on_translation_finished(self, result, target_lang, file_path):
        """
            finish translation
        :param result: the translated result
        :param target_lang: target language
        :param file_path: output path
        """
        # 翻译完成后隐藏进度条
        self.progress.setVisible(False)

        # 恢复按钮状态
        self.file_btn.setEnabled(True)
        self.file_btn.setText("选择文件并翻译")

        # 保存结果到与输入文件相同的文件夹
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
        """
            when errors occur while translate being progressing
        :param error_msg: error msg
        """
        # 隐藏进度条
        self.progress.setVisible(False)

        # 恢复按钮状态
        self.file_btn.setEnabled(True)
        self.file_btn.setText("选择文件并翻译")

        # 显示错误信息
        QMessageBox.critical(self, "翻译错误", f"翻译过程中发生错误：\n{error_msg}")

    def closeEvent(self, event):
        """
            execute when close the app
        :param event: close event
        """
        # 检查是否有翻译线程正在运行
        if self.translation_manager.is_translating():
            # 直接保存临时文件，无需用户确认
            if self.translation_manager.save_temp_translation_file():
                print("翻译进度已自动保存为临时文件")
            else:
                print("临时文件保存失败")

        # 停止服务器
        self.server.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TranslatorGUI()
    gui.show()
    sys.exit(app.exec())
