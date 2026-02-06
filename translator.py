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

    def _make_translation_request(self, text: str, target_lang: str) -> str:
        """统一的翻译API调用方法"""
        payload = {
            "model": "qwen3-4b",
            "messages": [
                {"role": "system", "content": "你是一个专业翻译助手，只输出译文，不要解释。"},
                {"role": "user", "content": f"请翻译成{target_lang}：{text}"}
            ]
        }

        try:
            r = requests.post(self.url, json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[错误] {e}"

    def translate(self, text, target_lang="中文"):
        """翻译单个文本"""
        return self._make_translation_request(text, target_lang)

    def translate_from_file(self, text: str, target_lang: str, progress_callback=None) -> str:
        """翻译文件内容"""
        # 遍历所有已注册的处理器
        for handler in self.handlers:
            if handler.can_handle(text):
                # 交给处理器执行完整翻译流程
                return handler.translate(text, target_lang, progress_callback)

        # 没有找到合适的处理器
        raise ValueError("没有找到可以处理该文本格式的翻译处理器")

    def _translate_single(self, text: str, target_lang: str) -> str:
        """处理器使用的单条翻译方法"""
        return self._make_translation_request(text, target_lang)
