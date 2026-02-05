import json

from translator_handler.base import BaseHandler
from translator_handler.registry import register_handler


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
