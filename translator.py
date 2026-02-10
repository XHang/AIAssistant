"""
   翻译相关文件
"""
from typing import List
import requests
from config_manager import config_manager
from handler import HANDLER_REGISTRY
from handler.base import BaseHandler


class Translator:
    """
        翻译类
    """

    def __init__(self):
        self.url = config_manager.get_api_url()

        # ⭐ 自动实例化所有已注册的 Handler
        self.handlers: List[BaseHandler] = [
            cls(self.url) for cls in HANDLER_REGISTRY
        ]

    def translate_from_file(self, text: str, target_lang: str, progress_callback=None) -> str:
        """翻译文件内容"""
        # 遍历所有已注册的处理器
        for handler in self.handlers:
            if handler.can_handle(text):
                # 交给处理器执行完整翻译流程
                return handler.translate(text, target_lang, progress_callback)

        # 没有找到合适的处理器
        raise ValueError("没有找到可以处理该文本格式的翻译处理器")


