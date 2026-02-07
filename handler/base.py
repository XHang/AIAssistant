import requests


class BaseHandler:
    """所有格式处理器的抽象基类"""

    def __init__(self, api_url):
        """初始化处理器，api_url由子类传递"""
        self.url = api_url

    def can_handle(self, text: str) -> bool:
        """判断是否可以处理该文本"""
        raise NotImplementedError

    def load(self, text: str):
        """初始化内部状态（比如解析 JSON、YAML 等） 解析原始文本，准备好内部数据结构"""
        raise NotImplementedError

    def get_total(self) -> int:
        """返回需要翻译的条目总数"""
        raise NotImplementedError

    def get_text(self, index: int) -> str:
        """根据索引返回待翻译的原文"""
        raise NotImplementedError

    def set_text(self, index: int, translated: str):
        """根据索引写回翻译后的文本"""
        raise NotImplementedError

    def serialize(self) -> str:
        """返回处理后的文本"""
        raise NotImplementedError

    def keep_the_same(self, text: str) -> bool:
        """判断是否保持原文"""
        raise NotImplementedError

    def translate(self, text: str, target_lang: str, progress_callback=None) -> str:
        """统一的翻译流程（模板方法）"""
        self.load(text)

        total = self.get_total()
        for i in range(total):
            original = self.get_text(i)
            if not self.keep_the_same(original):
                translated = self._translate_single(original, target_lang)
                print(f"original text:{original},Translated text: {translated}")
                self.set_text(i, translated)

            if progress_callback:
                progress_callback(i + 1, total)

        return self.serialize()

    def _translate_single(self, text: str, target_lang: str) -> str:
        """统一的翻译 API 调用"""
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
