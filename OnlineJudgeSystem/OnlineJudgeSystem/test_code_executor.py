"""
测试CodeExecutor的错误提示功能
测试各种常见的Python错误场景
"""

import sys
import os

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.CodeExecutor import CodeExecutor

def print_result(test_name, result):
    """打印测试结果"""
    print("\n" + "="*60)
    print(f"测试: {test_name}")
    print("="*60)
    print(f"成功: {result['success']}")
    print(f"代码: {result['code']}")
    print(f"消息: {result['msg']}")
    if result['error_type']:
        print(f"错误类型: {result['error_type']}")
    if result['error_detail']:
        print(f"错误详情: {result['error_detail']}")
    if result['error_line']:
        print(f"错误行号: {result['error_line']}")
    if result['output']:
        print(f"程序输出: {result['output']}")
    if result['traceback']:
        print(f"错误追踪:\n{result['traceback']}")

def test_all_scenarios():
    """测试所有错误场景"""
    executor = CodeExecutor(timeout=5)
    
    # 测试1: 正常执行
    print_result(
        "正常执行 - 打印Hello World",
        executor.execute_code('print("Hello World")', "Hello World")
    )
    
    # 测试2: 语法错误
    print_result(
        "语法错误 - 缺少括号",
        executor.execute_code('print "Hello"', None)
    )
    
    # 测试3: 缩进错误
    print_result(
        "缩进错误",
        executor.execute_code('''
def test():
print("test")
''', None)
    )
    
    # 测试4: 名称错误
    print_result(
        "名称错误 - 使用未定义的变量",
        executor.execute_code('print(undefined_variable)', None)
    )
    
    # 测试5: 类型错误
    print_result(
        "类型错误 - 字符串和整数相加",
        executor.execute_code('result = "5" + 5\nprint(result)', None)
    )
    
    # 测试6: 除零错误
    print_result(
        "除零错误",
        executor.execute_code('result = 10 / 0\nprint(result)', None)
    )
    
    # 测试7: 索引错误
    print_result(
        "索引错误 - 列表索引越界",
        executor.execute_code('lst = [1, 2, 3]\nprint(lst[10])', None)
    )
    
    # 测试8: 键错误
    print_result(
        "键错误 - 字典键不存在",
        executor.execute_code('d = {"a": 1}\nprint(d["b"])', None)
    )
    
    # 测试9: 值错误
    print_result(
        "值错误 - int转换失败",
        executor.execute_code('num = int("abc")\nprint(num)', None)
    )
    
    # 测试10: 属性错误
    print_result(
        "属性错误 - 对象没有该属性",
        executor.execute_code('s = "hello"\nprint(s.undefined_method())', None)
    )
    
    # 测试11: 导入错误
    print_result(
        "导入错误 - 模块不存在",
        executor.execute_code('import nonexistent_module\nprint("done")', None)
    )
    
    # 测试12: 无限循环超时
    print_result(
        "超时错误 - 无限循环",
        executor.execute_code('while True:\n    pass', None)
    )
    
    # 测试13: 输出结果不匹配
    print_result(
        "输出错误 - 结果不匹配",
        executor.execute_code('print("Wrong Answer")', "Correct Answer")
    )
    
    # 测试14: 没有输出
    print_result(
        "无输出 - 代码没有打印",
        executor.execute_code('x = 1 + 1', "2")
    )
    
    # 测试15: 递归错误
    print_result(
        "递归错误 - 递归深度超限",
        executor.execute_code('''
def recurse():
    return recurse()
recurse()
''', None)
    )
    
    # 测试16: 正确答案
    print_result(
        "正确答案 - 简单计算",
        executor.execute_code('''
a = 10
b = 20
print(a + b)
''', "30")
    )

if __name__ == "__main__":
    print("🚀 开始测试CodeExecutor错误提示功能...")
    print("测试各种Python错误场景\n")
    
    try:
        test_all_scenarios()
        print("\n" + "="*60)
        print("✅ 所有测试场景执行完成！")
        print("="*60)
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
