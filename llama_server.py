import subprocess
import threading
import time
import urllib.request

from config_manager import config_manager


class LlamaServer:
    def __init__(self):
        self.process = None
        self.log_lines = []
        self._reader = None

    def start(self):
        model = config_manager.get_config("model")
        ctx = str(config_manager.get_config("ctx_size"))
        threads = str(config_manager.get_config("threads"))
        port = str(config_manager.get_config("port"))

        cmd = [
            "llama-server.exe",
            "--model",
            model,
            "--ctx-size",
            ctx,
            "--threads",
            threads,
            "--port",
            port,
        ]

        self.log_lines = []
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        self._reader = threading.Thread(target=self._read_output, daemon=True)
        self._reader.start()

        self._wait_ready(port, timeout=180)

    def _read_output(self):
        for line in self.process.stdout:
            self.log_lines.append(line.rstrip())

    def _wait_ready(self, port, timeout=180):
        url = f"http://127.0.0.1:{port}/health"
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.process.poll() is not None:
                tail = "\n".join(self.log_lines[-50:])
                raise RuntimeError(
                    f"llama-server 已退出，returncode={self.process.returncode}\n"
                    f"最近日志:\n{tail}"
                )
            try:
                with urllib.request.urlopen(url, timeout=1) as r:
                    if r.status == 200:
                        return
            except Exception:
                pass
            time.sleep(0.5)
        raise TimeoutError("启动超时，最近日志:\n" + "\n".join(self.log_lines[-50:]))

    def stop(self):
        if self.process is None:
            return

        try:
            print("正在终止llama-server进程...")
            self.process.terminate()
            self.process.wait(timeout=5)
            print("llama-server进程已终止")
        except subprocess.TimeoutExpired:
            print("进程终止超时，强制杀死进程...")
            self.process.kill()
            self.process.wait()
            print("进程已被强制杀死")
        except Exception as e:
            print(f"终止进程时出错: {e}")
