import json
import re

from handler.base import BaseHandler
from handler.registry import register_handler


@register_handler
class JSONHandler(BaseHandler):
    def __init__(self, api_url):
        self.url = api_url
        self._data = None
        self._keys = None

    def can_handle(self, text: str) -> bool:
        try:
            data = json.loads(text)
            is_json:bool =  isinstance(data, dict)
            return is_json
        except:
            return False

    def load(self, text: str):
        self._data = json.loads(text)
        self._keys = [k for k, v in self._data.items() if isinstance(v, str)]

    def get_total(self) -> int:
        return len(self._keys)

    def get_text(self, index: int) -> str:
        key = self._keys[index]
        return self._data[key]

    def set_text(self, index: int, translated: str):
        key = self._keys[index]
        self._data[key] = translated

    def serialize(self) -> str:
        return json.dumps(self._data, ensure_ascii=False, indent=4)

    def keep_the_same(self, text:str)->bool:
        # 检测是否包含日语字符（平假名、片假名）
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')
        return not bool(japanese_pattern.search(text))