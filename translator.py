import requests
import json
from translator_handler  import HANDLER_REGISTRY


class Translator:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.url = f"http://127.0.0.1:{config['port']}/v1/chat/completions"

         # ⭐ 自动实例化所有已注册的 Handler
        self.handlers = [cls(self.url ) for cls in HANDLER_REGISTRY]


    def translate(self, text, target_lang="中文"):
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

        # ⭐ 统一的翻译流程（模板方法）

    def translate_from_file(self, text: str, target_lang: str, progress_callback=None) -> str:
        # 遍历所有已注册的处理器
        for handler in self.handlers:
            if handler.can_handle(text):
                # 交给处理器执行完整翻译流程
                return handler.translate(text, target_lang, progress_callback)

        # 没有找到合适的处理器
        raise ValueError("没有找到可以处理该文本格式的翻译处理器")

    # ⭐ 统一的翻译 API 调用
    def _translate_single(self, text: str, target_lang: str) -> str:
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
