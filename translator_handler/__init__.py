# handlers/__init__.py

import pkgutil
import importlib

# 自动扫描当前目录下所有模块并 import
for module_info in pkgutil.iter_modules(__path__):
    module_name = module_info.name
    importlib.import_module(f"{__name__}.{module_name}")

# 暴露 registry
from .registry import HANDLER_REGISTRY
