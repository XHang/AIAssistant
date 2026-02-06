import os
from PySide6.QtCore import QObject, Signal
from translation_threads.file_translate_worker import FileTranslateWorker
from translator import Translator


class TranslationSignals(QObject):
    """翻译信号类"""
    progress = Signal(int, int)
    finished = Signal(str, str, str)
    error = Signal(str)


class TranslationManager:
    """翻译管理器"""
    
    def __init__(self):
        self.translator = Translator()
        self.worker = None
        self.input_file_path = None
        self.current_handler = None
        self.signals = TranslationSignals()
        
    def translate_text(self, text, target_language):
        """翻译文本"""
        return self.translator.translate(text, target_language)
        
    def translate_file(self, file_path, target_language, progress_callback=None,
                       finished_callback=None, error_callback=None):
        """翻译文件"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except OSError:
            raise Exception("无法读取文件")

        # 保存输入文件路径
        self.input_file_path = file_path

        # 查找合适的处理器并保存引用
        for handler in self.translator.handlers:
            if handler.can_handle(content):
                self.current_handler = handler
                # 加载内容到处理器
                self.current_handler.load(content)
                break
        else:
            self.current_handler = None
            raise Exception("未找到合适的翻译处理器")

        # 创建并启动后台线程
        self.worker = FileTranslateWorker(self.translator, content, target_language, file_path)
        
        if progress_callback:
            self.worker.signals.progress.connect(progress_callback)
        if finished_callback:
            self.worker.signals.finished.connect(finished_callback)
        if error_callback:
            self.worker.signals.error.connect(error_callback)
            
        self.worker.start()

    def is_translating(self):
        """检查是否正在翻译"""
        return self.worker and self.worker.is_alive()

    def save_temp_translation_file(self):
        """保存临时翻译文件"""
        if not self.input_file_path or not self.current_handler:
            return False

        try:
            # 生成临时文件路径
            input_dir = os.path.dirname(self.input_file_path)
            input_filename = os.path.splitext(os.path.basename(self.input_file_path))[0]
            temp_filename = f"{input_filename}_temp.txt"
            temp_path = os.path.join(input_dir, temp_filename)

            # 获取当前翻译状态并保存
            temp_content = self.current_handler.serialize()
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(temp_content)

            print(f"临时文件已保存到: {temp_path}")
            return True
        except Exception as e:
            print(f"保存临时文件失败: {e}")
            return False
