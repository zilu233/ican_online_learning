"""
这个文件包含了新的runcode函数实现
用于替换usersviews.py中的旧版本
"""

# 新的runcode函数
# 复制以下代码替换 usersviews.py 中第323行开始的原有runcode函数

@app.route('/runcode', methods=['GET', 'POST'])
def runcode():
    '''
    获取用户提交的py代码和id获取题库，
    把提交的py代码写入到一个文本中，运行它获取结果。
    最后进行对比，并更新数据库中
    增强版：提供详细的错误提示信息
    '''
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
