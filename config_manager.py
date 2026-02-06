import json
from typing import Dict, Any


class ConfigManager:
    """
    全局配置管理器
    负责读取、缓存和提供配置信息
    """
    _instance = None
    _config_data: Dict[str, Any] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def load_config(self, config_path: str = "config.json") -> Dict[str, Any]:
        """
        加载配置文件
        :param config_path: 配置文件路径
        :return: 配置数据字典
        """
        if self._config_data is None:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config_data = json.load(f)
            except FileNotFoundError:
                raise FileNotFoundError(f"配置文件 {config_path} 不存在")
            except json.JSONDecodeError:
                raise ValueError(f"配置文件 {config_path} 格式错误")
        return self._config_data

    def get_config(self, key: str = None, default=None):
        """
        获取配置值
        :param key: 配置键名，如果为None则返回整个配置字典
        :param default: 默认值
        :return: 配置值
        """
        if self._config_data is None:
            # 如果还没有加载配置，尝试加载默认配置文件
            self.load_config()
        
        if key is None:
            return self._config_data
        return self._config_data.get(key, default)

    def get_model_path(self) -> str:
        """获取模型路径"""
        return self.get_config("model", "")

    def get_ctx_size(self) -> int:
        """获取上下文大小"""
        return self.get_config("ctx_size", 4096)

    def get_threads(self) -> int:
        """获取线程数"""
        return self.get_config("threads", 8)

    def get_port(self) -> int:
        """获取端口号"""
        return self.get_config("port", 8080)

    def get_api_url(self) -> str:
        """获取API URL"""
        port = self.get_port()
        return f"http://127.0.0.1:{port}/v1/chat/completions"


# 全局配置实例
config_manager = ConfigManager()