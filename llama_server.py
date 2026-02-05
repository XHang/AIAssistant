import json
import subprocess
import time


class LlamaServer:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.process = None

    def start(self):
        model = self.config["model"]
        ctx = str(self.config["ctx_size"])
        threads = str(self.config["threads"])
        port = str(self.config["port"])

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

