import subprocess
import time
from config_manager import config_manager


class LlamaServer:
    def __init__(self):
        self.process = None

    def start(self):
        model = config_manager.get_config("model")
        ctx = str(config_manager.get_config("ctx_size"))
        threads = str(config_manager.get_config("threads"))
        port = str(config_manager.get_config("port"))

        cmd = [
            "llama-server.exe",
            "--model", model,
            "--ctx-size", ctx,
            "--threads", threads,
            "--port", port
        ]

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        time.sleep(2)

    def stop(self):
        if self.process is None:
            return

        try:
            self.process.terminate()
        except Exception as e:
            raise RuntimeError(f"终止进程失败: {e}") from e

