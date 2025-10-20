"""
代码执行器模块
提供代码执行和详细的错误诊断功能
"""

import subprocess
import os
import uuid
import re


class CodeExecutor:
    """代码执行器类，用于执行Python代码并提供详细的错误信息"""
    
    def __init__(self, timeout=5):
        """
        初始化代码执行器
        :param timeout: 代码执行超时时间（秒）
        """
        self.timeout = timeout
    
    def execute_code(self, code, expected_output=None):
        """
        执行Python代码并返回详细的结果信息
        :param code: 要执行的Python代码
        :param expected_output: 期望的输出结果
        :return: 包含执行结果的字典
        """
        result = {
            "success": False,
            "code": 0,
            "msg": "",
            "error_type": "",
            "error_detail": "",
            "error_line": "",
            "output": "",
            "traceback": ""
        }
        
        # 创建临时文件
        current_path = os.getcwd()
        upload_dir = os.path.join(current_path, "OnlineJudgeSystem", "upload")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, str(uuid.uuid1()) + ".py")
        
        try:
            # 写入代码到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 执行代码
            proc = subprocess.Popen(
                f"python {file_path}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            try:
                # 等待执行完成或超时
                stdout, stderr = proc.communicate(timeout=self.timeout)
                stdout_text = stdout.decode('utf-8', errors='ignore').strip()
                stderr_text = stderr.decode('utf-8', errors='ignore').strip()
                
                result["output"] = stdout_text
                
                # 如果有错误输出
                if stderr_text:
                    result["traceback"] = stderr_text
                    error_info = self._parse_error(stderr_text)
                    result.update(error_info)
                    result["success"] = False
                    result["code"] = 0
                
                # 如果没有错误，检查输出
                elif stdout_text:
                    if expected_output and expected_output in stdout_text:
                        result["success"] = True
                        result["code"] = 1
                        result["msg"] = "恭喜你答对了！"
                    elif expected_output:
                        result["success"] = False
                        result["code"] = 0
                        result["msg"] = "代码运行成功，但输出结果不正确"
                        result["error_type"] = "输出错误"
                        result["error_detail"] = f"期望输出: {expected_output}\n实际输出: {stdout_text}"
                    else:
                        result["success"] = True
                        result["code"] = 1
                        result["msg"] = "代码运行成功"
                else:
                    result["success"] = False
                    result["code"] = 0
                    result["msg"] = "代码没有输出结果"
                    result["error_type"] = "无输出"
                    result["error_detail"] = "程序运行完成但没有产生任何输出"
                    
            except subprocess.TimeoutExpired:
                proc.kill()
                result["success"] = False
                result["code"] = 0
                result["msg"] = "代码执行超时"
                result["error_type"] = "TimeoutError"
                result["error_detail"] = f"程序运行时间超过{self.timeout}秒，可能存在无限循环"
                
        except Exception as e:
            result["success"] = False
            result["code"] = 0
            result["msg"] = "系统错误"
            result["error_type"] = type(e).__name__
            result["error_detail"] = str(e)
        
        finally:
            # 清理临时文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        
        return result
    
    def _parse_error(self, error_text):
        """
        解析Python错误信息，提取关键信息
        :param error_text: stderr输出的错误文本
        :return: 包含错误信息的字典
        """
        error_info = {
            "msg": "代码执行出错",
            "error_type": "",
            "error_detail": "",
            "error_line": ""
        }
        
        lines = error_text.strip().split('\n')
        
        if not lines:
            return error_info
        
        # 提取最后一行的错误类型和详细信息
        last_line = lines[-1]
        if ':' in last_line:
            parts = last_line.split(':', 1)
            error_info["error_type"] = parts[0].strip()
            error_info["error_detail"] = parts[1].strip() if len(parts) > 1 else ""
        else:
            error_info["error_type"] = "运行错误"
            error_info["error_detail"] = last_line
        
        # 提取行号信息
        for line in lines:
            if 'line' in line.lower():
                # 使用正则表达式提取行号
                match = re.search(r'line\s+(\d+)', line, re.IGNORECASE)
                if match:
                    line_num = match.group(1)
                    error_info["error_line"] = f"第 {line_num} 行"
                    break
        
        # 生成友好的错误消息
        msg = f"代码执行出错 - {error_info['error_type']}"
        if error_info['error_detail']:
            msg += f": {error_info['error_detail']}"
        if error_info['error_line']:
            msg += f" ({error_info['error_line']})"
        
        error_info["msg"] = msg
        
        # 添加常见错误的中文解释
        error_info["msg"] = self._add_error_explanation(error_info)
        
        return error_info
    
    def _add_error_explanation(self, error_info):
        """
        为常见错误添加中文解释
        :param error_info: 错误信息字典
        :return: 带有解释的错误消息
        """
        error_type = error_info["error_type"]
        msg = error_info["msg"]
        
        explanations = {
            "SyntaxError": "语法错误：代码格式不正确",
            "IndentationError": "缩进错误：代码缩进不正确，请检查空格和Tab",
            "NameError": "名称错误：使用了未定义的变量或函数",
            "TypeError": "类型错误：操作或函数应用于了不适当类型的对象",
            "ValueError": "值错误：操作或函数接收到了正确类型但不适当的值",
            "ZeroDivisionError": "除零错误：尝试除以零",
            "IndexError": "索引错误：序列索引超出范围",
            "KeyError": "键错误：字典中不存在该键",
            "AttributeError": "属性错误：对象没有该属性或方法",
            "ImportError": "导入错误：无法导入模块或包",
            "ModuleNotFoundError": "模块未找到：Python找不到指定的模块",
            "FileNotFoundError": "文件未找到：指定的文件不存在",
            "IOError": "输入输出错误：文件操作失败",
            "RuntimeError": "运行时错误：程序执行时发生的错误",
            "RecursionError": "递归错误：递归深度超过最大限制",
            "MemoryError": "内存错误：内存不足",
        }
        
        if error_type in explanations:
            msg = f"{msg}\n💡 提示：{explanations[error_type]}"
        
        return msg
