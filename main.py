import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QComboBox, QProgressBar
)

from config_manager import config_manager
from conversation_worker import ConversationManager
from llama_server import LlamaServer
from translation_manager import TranslationManager


class TranslatorGUI(QWidget):
    """
        GUI for translator
    """

    def __init__(self):
        super().__init__()
        self._current_reply_started = None
        self.translation_manager = TranslationManager()
        self.setWindowTitle("AI 对话工具 - PySide6 + llama.cpp")
        self.resize(600, 500)


        # 预加载配置以确保只读取一次
        config_manager.load_config()

        # 初始化对话管理系统
        self.conversation_manager = ConversationManager(config_manager.get_api_url())
        self.conversation_manager.set_gui_update_callback(self.on_conversation_message)
        self.conversation_manager.start()

        layout = QVBoxLayout()

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        layout.addWidget(self.chat_box)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入要对话的内容...")
        layout.addWidget(self.input_box)

        self.send_btn = QPushButton("对话")
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

        # 设置定时器定期处理消息队列
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_conversation_messages)
        self.timer.start(100)  # 每100毫秒检查一次

        # 启动 llama-server
        self.server = LlamaServer()
        self.server.start()

    def on_conversation_message(self, msg_type, content, metadata):
        """处理来自对话系统的消息"""
        if msg_type == "ai_response":
            if content:  # 部分回复内容
                # 如果是第一条回复，先添加前缀
                if not hasattr(self, '_current_reply_started') or not self._current_reply_started:
                    self.chat_box.append("AI：")
                    self._current_reply_started = True

                # 追加回复内容
                self.chat_box.insertPlainText(content)

                # 强制GUI刷新
                QApplication.processEvents()

            elif metadata.get("complete"):  # 完整回复结束
                # 添加换行和分隔符
                self.chat_box.append("\n" + "-" * 30 + "\n")
                self._current_reply_started = False

                # 重新启用发送按钮
                self.send_btn.setEnabled(True)
                self.send_btn.setText("对话")

        elif msg_type == "system":
            self.chat_box.append(f"[系统] {content}\n")

        elif msg_type == "error":
            self.chat_box.append(f"[错误] {content}\n")
            # 出错时也要重新启用按钮
            self.send_btn.setEnabled(True)
            self.send_btn.setText("对话")

    def handle_translate(self):
        """
            处理对话消息发送
        :return: none
        """
        text = self.input_box.text().strip()
        if not text:
            return

        # 显示用户输入
        self.chat_box.append(f"你：{text}")

        # 通过消息队列发送给AI工作线程
        self.conversation_manager.send_message(text)

        # 清空输入框
        self.input_box.clear()

        # 禁用发送按钮防止重复点击
        self.send_btn.setEnabled(False)
        self.send_btn.setText("发送中...")

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

    def process_conversation_messages(self):
        """处理对话系统输出队列中的消息"""
        try:
            self.conversation_manager.process_output_messages()
        except Exception as e:
            print(f"处理对话消息时出错: {e}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        print("开始关闭应用程序...")

        try:
            # 停止定时器
            if hasattr(self, 'timer'):
                print("正在停止定时器...")
                self.timer.stop()
                print("定时器已停止")
        except Exception as e:
            print(f"停止定时器时出错: {e}")

        try:
            # 停止对话系统
            if hasattr(self, 'conversation_manager'):
                print("正在停止对话系统...")
                self.conversation_manager.stop()
                print("对话系统已停止")
        except Exception as e:
            print(f"停止对话系统时出错: {e}")

        try:
            # 停止服务器
            if hasattr(self, 'server'):
                print("正在停止服务器...")
                self.server.stop()
                print("服务器已停止")
        except Exception as e:
            print(f"停止服务器时出错: {e}")

        print("正在接受关闭事件...")
        event.accept()
        print("关闭事件已接受")


if __name__ == "__main__":
    print("正在启动应用程序...")
    app = QApplication(sys.argv)
    gui = TranslatorGUI()
    gui.show()
    print("应用程序已启动，进入事件循环...")
    exit_code = app.exec()
    print(f"事件循环已退出，退出码: {exit_code}")
    sys.exit(exit_code)
