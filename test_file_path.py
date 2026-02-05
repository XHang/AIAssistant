#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试文件路径处理功能"""

import os

def test_output_path_generation():
    """测试输出文件路径生成逻辑"""
    
    test_cases = [
        # (输入文件路径, 期望的输出文件名)
        (r"C:\Users\Test\Documents\test.txt", "test_translated.txt"),
        (r"/home/user/documents/hello.txt", "hello_translated.txt"),
        (r"D:\Projects\sample.txt", "sample_translated.txt"),
        (r"file_without_extension", "file_without_extension_translated.txt"),
    ]
    
    print("=== 输出文件路径生成测试 ===")
    print()
    
    for input_path, expected_filename in test_cases:
        # 模拟实际的路径处理逻辑
        input_dir = os.path.dirname(input_path)
        input_filename = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{input_filename}_translated.txt"
        output_path = os.path.join(input_dir, output_filename)
        
        actual_filename = os.path.basename(output_path)
        
        status = "✓" if actual_filename == expected_filename else "✗"
        print(f"{status} 输入: {input_path}")
        print(f"   输出: {output_path}")
        print(f"   文件名: {actual_filename}")
        if actual_filename != expected_filename:
            print(f"   期望: {expected_filename}")
        print()

if __name__ == "__main__":
    test_output_path_generation()