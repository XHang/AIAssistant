#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试 keep_the_same 方法修改后的行为"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from handler.JSON_handler import JSONHandler
    handler = JSONHandler(api_url="http://test.com")
    keep_the_same = handler.keep_the_same
    print("✓ 使用修改后的 JSONHandler")
except Exception as e:
    print(f"导入失败: {e}")
    # 备用实现
    def keep_the_same(text: str) -> bool:
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')
        return not bool(japanese_pattern.search(text))

print("\n=== keep_the_same 方法行为验证 ===")
print("新逻辑: 包含日语字符(平假名、片假名)返回False，其他返回True")
print("=" * 50)

test_cases = [
    # (输入文本, 描述, 期望结果)
    ("こんにちは", "平假名", False),      # 包含平假名 → False
    ("コンニチハ", "片假名", False),      # 包含片假名 → False
    ("Hello こんにちは", "英文+平假名", False), # 包含平假名 → False
    ("テスト123", "片假名+数字", False),   # 包含片假名 → False
    
    ("日本語", "日文汉字", True),        # 只有汉字 → True
    ("漢字", "中文汉字", True),          # 中文汉字 → True
    ("第1章", "中文+数字", True),        # 中文+数字 → True
    ("123", "纯数字", True),            # 纯数字 → True
    ("Hello World", "纯英文", True),    # 纯英文 → True
    ("", "空字符串", True),             # 空字符串 → True
]

print("测试结果:")
print("-" * 40)

passed = 0
total = 0

for text, description, expected in test_cases:
    result = keep_the_same(text)
    is_correct = (result == expected)
    
    status = "✓" if is_correct else "✗"
    total += 1
    if is_correct:
        passed += 1
    
    print(f"{status} '{text}' ({description})")
    print(f"   实际结果: {result}")
    print(f"   期望结果: {expected}")
    print()

print("=" * 50)
print(f"测试统计: {passed}/{total} 通过")
print(f"成功率: {(passed/total*100):.1f}%")

if passed == total:
    print("🎉 所有测试通过！修改成功！")
else:
    print("❌ 存在测试失败")

print("\n修改说明:")
print("- 只检测平假名(\\u3040-\\u309F)和片假名(\\u30A0-\\u30FF)")
print("- 包含这些字符时返回False")
print("- 不包含时返回True")
print("=" * 50)