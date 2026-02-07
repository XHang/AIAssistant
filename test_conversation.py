"""
测试改进后的对话系统
"""
import sys
import os
import time
from PySide6.QtWidgets import QApplication
from main import TranslatorGUI


def test_conversation_system():
    """测试对话系统功能"""
    print("=== 开始测试对话系统 ===")
    
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 创建GUI
    gui = TranslatorGUI()
    gui.show()
    
    print("GUI界面已启动")
    print("请在界面中测试以下功能：")
    print("1. 在输入框中输入对话内容，点击'对话'按钮")
    print("2. 观察AI回复是否正确显示")
    print("3. 测试连续对话功能")
    print("4. 测试错误处理机制")
    print("\n按 Ctrl+C 退出测试")
    
    try:
        # 运行应用
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n测试结束")
        gui.close()


if __name__ == "__main__":
    test_conversation_system()