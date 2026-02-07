"""
消息队列系统
用于GUI和后台工作线程之间的异步通信
"""
import queue
import threading
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """消息类型枚举"""
    USER_INPUT = "user_input"      # 用户输入
    AI_RESPONSE = "ai_response"    # AI回复
    SYSTEM_MESSAGE = "system"      # 系统消息
    ERROR = "error"                # 错误消息


@dataclass
class Message:
    """消息数据结构"""
    type: MessageType
    content: str
    metadata: Optional[dict] = None


class MessageQueue:
    """消息队列管理器"""
    
    def __init__(self):
        self._input_queue = queue.Queue()      # 用户输入队列
        self._output_queue = queue.Queue()     # AI输出队列
        self._lock = threading.Lock()
        self._running = True
        
    def put_user_message(self, content: str, metadata: Optional[dict] = None):
        """添加用户消息到输入队列"""
        message = Message(
            type=MessageType.USER_INPUT,
            content=content,
            metadata=metadata
        )
        with self._lock:
            if self._running:
                self._input_queue.put(message)
                
    def get_user_message(self, timeout: float = 0.1) -> Optional[Message]:
        """从输入队列获取用户消息"""
        try:
            return self._input_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def put_ai_message(self, content: str, metadata: Optional[dict] = None):
        """添加AI消息到输出队列"""
        message = Message(
            type=MessageType.AI_RESPONSE,
            content=content,
            metadata=metadata
        )
        with self._lock:
            if self._running:
                self._output_queue.put(message)
                
    def get_ai_message(self, timeout: float = 0.1) -> Optional[Message]:
        """从输出队列获取AI消息"""
        try:
            return self._output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def put_system_message(self, content: str, metadata: Optional[dict] = None):
        """添加系统消息"""
        message = Message(
            type=MessageType.SYSTEM_MESSAGE,
            content=content,
            metadata=metadata
        )
        with self._lock:
            if self._running:
                self._output_queue.put(message)
                
    def put_error_message(self, content: str, metadata: Optional[dict] = None):
        """添加错误消息"""
        message = Message(
            type=MessageType.ERROR,
            content=content,
            metadata=metadata
        )
        with self._lock:
            if self._running:
                self._output_queue.put(message)
                
    def clear_queues(self):
        """清空所有队列"""
        with self._lock:
            # 清空输入队列
            while not self._input_queue.empty():
                try:
                    self._input_queue.get_nowait()
                except queue.Empty:
                    break
                    
            # 清空输出队列
            while not self._output_queue.empty():
                try:
                    self._output_queue.get_nowait()
                except queue.Empty:
                    break
                    
    def stop(self):
        """停止消息队列"""
        print("正在停止消息队列...")
        with self._lock:
            self._running = False
            # 不再清空队列，避免与其他线程竞争锁
            # self.clear_queues()  # 移除这行
        print("消息队列已停止")
            
    def is_running(self) -> bool:
        """检查队列是否运行中"""
        with self._lock:
            return self._running
            
    @property
    def input_queue_size(self) -> int:
        """获取输入队列大小"""
        return self._input_queue.qsize()
        
    @property
    def output_queue_size(self) -> int:
        """获取输出队列大小"""
        return self._output_queue.qsize()


class QueueProcessor:
    """队列处理器基类"""
    
    def __init__(self, message_queue: MessageQueue):
        self.message_queue = message_queue
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        
    def start(self):
        """启动处理器"""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            
    def stop(self):
        """停止处理器"""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            # 等待线程正常退出
            self._thread.join(timeout=3)
            # 如果线程仍未退出，强制终止
            if self._thread.is_alive():
                print(f"警告: {self.__class__.__name__} 线程未能正常退出，可能存在阻塞操作")
            
    def _run(self):
        """运行循环 - 子类需要实现"""
        raise NotImplementedError("子类必须实现 _run 方法")
        
    def is_running(self) -> bool:
        """检查处理器是否运行中"""
        return self._thread is not None and self._thread.is_alive() and not self._stop_event.is_set()


# 全局消息队列实例
global_message_queue = MessageQueue()