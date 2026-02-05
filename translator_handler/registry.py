# registry.py

HANDLER_REGISTRY = []

def register_handler(cls):
    HANDLER_REGISTRY.append(cls)
    return cls
