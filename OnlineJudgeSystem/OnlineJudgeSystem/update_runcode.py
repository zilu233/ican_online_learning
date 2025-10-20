"""
脚本用于更新usersviews.py中的runcode函数
"""

import re

# 读取原始文件
with open('usersviews.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 新的runcode函数实现
new_runcode = '''
@app.route('/runcode', methods=['GET', 'POST'])
def runcode():
    \'\'\'
    获取用户提交的py代码和id获取题库，
    把提交的py代码写入到一个文本中，运行它获取结果。
    最后进行对比，并更新数据库中
    增强版：提供详细的错误提示信息
    \'\'\'
    testRecordId = request.form.get("testRecordId")
    testAnswerId = request.form.get("testAnswerId")
    testContentId = request.form.get("testContentId")

    pycode = request.form.get("pycode")
    testContentServer = TestContentServer()
    testContent = testContentServer.select_sql_by_id(testContentId)

    # 使用CodeExecutor执行代码
    executor = CodeExecutor(timeout=5)
    result = executor.execute_code(pycode, testContent.Result)
    
    # 更新数据库中的做题信息
    testRecordAnswerServer = TestRecordAnswerServer()
    testRecordAnswer = TestRecordAnswer()
    testRecordAnswer.Id = testAnswerId
    testRecordAnswer.AnswerContent = pycode
    
    if result["success"]:
        testRecordAnswer.Grade = testContent.Grade
    else:
        testRecordAnswer.Grade = 0
    
    testRecordAnswerServer.update_sql(testRecordAnswer)
    
    # 返回详细的JSON结果
    return jsonify(result)
'''

# 使用正则表达式匹配并替换旧的runcode函数
# 匹配从@app.route('/runcode'开始到下一个@app.route或文件结尾
pattern = r"@app\.route\('/runcode'[^@]*?return jsonify\(jsons\)"

# 执行替换
new_content = re.sub(pattern, new_runcode.strip(), content, flags=re.DOTALL)

# 写入更新后的内容
with open('usersviews.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ runcode函数已成功更新！")
