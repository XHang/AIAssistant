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
            print("正在终止llama-server进程...")
            self.process.terminate()
            # 等待进程结束，最多等待5秒
            self.process.wait(timeout=5)
            print("llama-server进程已终止")
        except subprocess.TimeoutExpired:
            print("进程终止超时，强制杀死进程...")
            self.process.kill()
            self.process.wait()
            print("进程已被强制杀死")
        except Exception as e:
            print(f"终止进程时出错: {e}")
            # 即使出错也继续执行
            pass
