"""
AI对话工作线程
负责处理用户输入并与LlamaServer进行对话
"""
import json
import requests
import threading
import time
from typing import Optional, Dict, Any
from message_queue import MessageQueue, QueueProcessor, MessageType


class AIConversationWorker(QueueProcessor):
    """AI对话工作线程"""
    
    def __init__(self, message_queue: MessageQueue, api_url: str):
        super().__init__(message_queue)
        self.api_url = api_url
        self.session_history = []  # 对话历史记录
        self.max_history_length = 10  # 最大历史记录长度
        
    def _run(self):
        """主运行循环"""
        print("AI对话工作线程已启动")
        
        # 发送系统启动消息
        self.message_queue.put_system_message("AI助手已准备就绪，可以开始对话了")
        
        while not self._stop_event.is_set():
            try:
                # 从输入队列获取用户消息，使用更短的超时时间以便更快响应停止信号
                user_message = self.message_queue.get_user_message(timeout=0.05)
                
                if user_message:
                    self._process_user_message(user_message)
                    
            except Exception as e:
                if not self._stop_event.is_set():  # 只在非停止状态下报告错误
                    error_msg = f"处理用户消息时出错: {str(e)}"
                    print(error_msg)
                    self.message_queue.put_error_message(error_msg)
                
        print("AI对话工作线程已停止")
        
    def _process_user_message(self, message):
        """处理用户消息"""
        try:
            user_input = message.content
            
            # 添加到对话历史
            self.session_history.append({"role": "user", "content": user_input})
            
            # 保持历史记录在合理范围内
            if len(self.session_history) > self.max_history_length:
                # 保留系统消息和最近的几条对话
                self.session_history = self.session_history[-self.max_history_length:]
                
            # 构造API请求
            payload = {
                "model": "qwen3-4b",
                "messages": self.session_history,
                "stream": True  # 启用流式输出
            }
            
            # 发送请求到LlamaServer
            response = requests.post(
                self.api_url,
                json=payload,
                stream=True,
                timeout=(5, 30)  # 连接超时5秒，读取超时30秒
            )
            response.raise_for_status()
            
            # 处理流式响应
            ai_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        # 解析流式响应
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            data_str = decoded_line[6:]  # 移除 'data: ' 前缀
                            if data_str.strip() == '[DONE]':
                                break
                                
                            chunk_data = json.loads(data_str)
                            
                            # 提取回复内容
                            if 'choices' in chunk_data and chunk_data['choices']:
                                delta = chunk_data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    ai_response += content
                                    # 实时发送部分回复到输出队列
                                    self.message_queue.put_ai_message(content, {"partial": True})
                                    
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"解析流式响应出错: {e}")
                        continue
            
            # 完整回复完成后，添加到历史记录
            if ai_response:
                self.session_history.append({"role": "assistant", "content": ai_response})
                # 发送完整回复结束标记
                self.message_queue.put_ai_message("", {"partial": False, "complete": True})
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            print(error_msg)
            self.message_queue.put_error_message(error_msg)
        except Exception as e:
            error_msg = f"处理对话时出错: {str(e)}"
            print(error_msg)
            self.message_queue.put_error_message(error_msg)

    def clear_history(self):
        """清空对话历史"""
        self.session_history.clear()
        # 重新添加系统提示
        self.session_history.append({
            "role": "system", 
            "content": "你是一个智能AI助手，能够进行自然对话。"
        })
        
    def get_history_summary(self) -> str:
        """获取对话历史摘要"""
        return f"当前对话轮次: {len(self.session_history) // 2}"


class ConversationManager:
    """对话管理器"""
    
    def __init__(self, api_url: str):
        self.message_queue = MessageQueue()
        self.worker = AIConversationWorker(self.message_queue, api_url)
        self._gui_update_callback = None
        
    def start(self):
        """启动对话系统"""
        self.worker.start()
        
    def stop(self):
        """停止对话系统"""
        try:
            # 先停止工作线程
            self.worker.stop()
            # 再停止消息队列
            self.message_queue.stop()
        except Exception as e:
            print(f"停止对话系统时出错: {e}")
        
    def send_message(self, content: str):
        """发送用户消息"""
        self.message_queue.put_user_message(content)
        
    def set_gui_update_callback(self, callback):
        """设置GUI更新回调函数"""
        self._gui_update_callback = callback
        
    def process_output_messages(self):
        """处理输出队列中的消息并更新GUI"""
        if not self._gui_update_callback:
            return
            
        while True:
            message = self.message_queue.get_ai_message(timeout=0.01)
            if not message:
                break
                
            # 调用GUI更新回调
            self._gui_update_callback(message.type.value, message.content, message.metadata or {})

    def is_running(self) -> bool:
        """检查对话系统是否运行中"""
        return self.worker.is_running()
        
    def clear_conversation(self):
        """清空当前对话"""
        self.worker.clear_history()
        self.message_queue.clear_queues()
        
    def get_status(self) -> Dict[str, Any]:
        """获取对话系统状态"""
        return {
            "running": self.is_running(),
            "input_queue_size": self.message_queue.input_queue_size,
            "output_queue_size": self.message_queue.output_queue_size,
            "history_summary": self.worker.get_history_summary()
        }


# 使用示例
if __name__ == "__main__":
    # 测试代码
    manager = ConversationManager("http://127.0.0.1:8080/v1/chat/completions")
    
    def test_callback(msg_type, content, metadata):
        print(f"[{msg_type}] {content} (meta: {metadata})")
    
    manager.set_gui_update_callback(test_callback)
    manager.start()
    
    # 发送测试消息
    manager.send_message("你好，这是一个测试")
    
    # 等待一段时间让消息处理
    time.sleep(5)
    
    manager.stop()