"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify, request, session, redirect
from werkzeug.exceptions import RequestURITooLarge
from OnlineJudgeSystem import app
from OnlineJudgeSystem.model.TestContent import TestContentServer, TestContent
from OnlineJudgeSystem.common.CodeExecutor import CodeExecutor
import json
import random
import math 
import os
import uuid
import subprocess

from OnlineJudgeSystem.model.Students import Students, StudentsServer
from OnlineJudgeSystem.model.TestRecord import TestRecord, TestRecordServer
from OnlineJudgeSystem.model.TestSelect import TestSelect, TestSelectServer
from OnlineJudgeSystem.model.Test import Test, TestServer
from OnlineJudgeSystem.model.TestRecordAnswer import TestRecordAnswer, TestRecordAnswerServer
from OnlineJudgeSystem.model.TestRecordAnswerSelect import TestRecordAnswerSelect, TestRecordAnswerSelectServer
from OnlineJudgeSystem.model.PageTool import PageTool
from OnlineJudgeSystem.model.TestQuestionRelation import TestQuestionRelation
from OnlineJudgeSystem.model.TestQuestionRelation import TestQuestionRelationServer
'''
在线考试
'''


@app.route('/myonlinetest', methods=['GET', 'POST'])
def myonlinetest():
    """Renders the home page."""

    datas = TestServer().select_sql_all()

    return render_template(
        'users/myonlinetest.html',
        userType=session['logged_type'],
        session=session['logged_type'],
        datas=datas,
    )


'''
开始考试
'''


@app.route('/myonlineanswer', methods=['GET', 'POST'])
def myonlineanswer():
    """Renders the home page."""
    users = json.loads(session["logged_in"])
    test_id = request.args.get("id")

    test = TestServer().select_sql_by_id(test_id)

    # 根据试卷 ID 获取关联的题目
    test_question_relation_server = TestQuestionRelationServer()
    questions = test_question_relation_server.get_questions_by_test_id(test_id)

    test_select = []
    test_content = []
    for question_id, question_type in questions:
        if question_type == 'select':
            test_select_item = TestSelectServer().select_sql_by_id(question_id)
            if test_select_item:
                test_select.append(test_select_item)
        elif question_type == 'content':
            test_content_item = TestContentServer().select_sql_by_id(question_id)
            if test_content_item:
                test_content.append(test_content_item)

    test_select_len = len(test_select)
    test_content_len = len(test_content)

    testRecord = TestRecord()
    testRecordAnswer = TestRecordAnswer()
    testRecordServer = TestRecordServer()
    testRecordAnswerServer = TestRecordAnswerServer()

    testRecordAnswerSelect = TestRecordAnswerSelect()
    testRecordAnswerSelectServer = TestRecordAnswerSelectServer()

    # 把这题的数据插入到数据库中
    # 提前把题插入到数据库中，如果用户中途退出不做了，这 5 题根据用户做题情况计分。
    # 先把 test_record 插入数据
    testRecord.StudentsId = users['Id']
    testRecord.RocordTime = str(datetime.now())
    testRecord.SumGrade = 0
    testRecordServer.insert_sql(testRecord)

    last_id = testRecordServer.select_sql_get_id()

    test_select_record = []
    for item in test_select:
        # 再把 test_record_answer_content 插入到数据库中
        testRecordAnswerSelect.TestRecordId = last_id
        testRecordAnswerSelect.TestSelectId = item.Id
        testRecordAnswerSelect.AnswerSelect = ""
        testRecordAnswerSelect.Grade = 0
        testRecordAnswerSelectServer.insert_sql(testRecordAnswerSelect)
        ids = testRecordAnswerSelectServer.select_sql_last_id()
        test_select_record.append(ids)

    test_content_record = []
    for item in test_content:
        # 再把 test_record_answer_content 插入到数据库中
        testRecordAnswer.TestRecordId = last_id
        testRecordAnswer.TestContentId = item.Id
        testRecordAnswer.AnswerContent = ""
        testRecordAnswer.Grade = 0
        testRecordAnswerServer.insert_sql(testRecordAnswer)
        ids = testRecordAnswerServer.select_sql_last_id()
        test_content_record.append(ids)

    return render_template(
        'users/myonlinetestanswer.html',
        userType=session['logged_type'],
        session=session['logged_type'],
        test=test,
        test_select=test_select,
        test_content=test_content,
        test_select_len=test_select_len,
        test_content_len=test_content_len,
        test_select_record=test_select_record,
        test_content_record=test_content_record,
        test_record_id=last_id,
    )


'''
选择题提交
'''


@app.route('/selectanswers', methods=['POST'])
def selectanswers():
    users = session['logged_in']

    data = request.get_json()
    test_record_answer_select_id_temp = data['select_id']
    test_select_id = []
    for item in test_record_answer_select_id_temp:
        test_record_answer_select_id = TestRecordAnswerSelectServer().select_sql_by_id(item)
        test_select_id.append(test_record_answer_select_id)

    for key, value in data.items():
        for item in test_select_id:
            if key == str(item.TestSelectId):
                testSelect = TestSelectServer().select_sql_by_id(key)

                if testSelect.Result == value:
                    item.Answer_Select = value
                    item.Grade = testSelect.Grade
                    TestRecordAnswerSelectServer().update_sql(item)

                else:
                    item.Answer_Select = value
                    TestRecordAnswerSelectServer().update_sql(item)

    # 在这里处理接收到的答案
    print("Received answers:", data)
    return jsonify({"message": "Answers received successfully"})


'''
做题结束
'''


@app.route('/testover', methods=['POST', 'GET'])
def testover():
    test_record_id = request.args.get("test_record_id")

    # 计算结果
    sums = 0

    datas = TestRecordAnswerServer().select_sql_all_test_record_id(test_record_id)
    for item in datas:
        sums += item.Grade

    datas = TestRecordAnswerSelectServer().select_sql_all_test_record_id(test_record_id)
    for item in datas:
        sums += item.Grade

    testRecord = TestRecordServer().select_sql_by_id(test_record_id)
    testRecord.SumGrade = sums
    TestRecordServer().update_sql(testRecord)
    return jsonify({"message": "Answers received successfully"})


'''
当前用户的做题情况
'''


@app.route('/mytestcontentrecordmanagement', methods=['GET', 'POST'])
def mytestcontentrecordmanagement():
    """Renders the home page."""
    users = json.loads(session["logged_in"])

    studentsServer = StudentsServer()
    temps = studentsServer.select_sql_by_id(users["Id"])
    datas = []
    if len(temps.StudentsTestRecord) > 0:
        datas = temps.StudentsTestRecord

    # 分页参数
    current_page = int(request.args.get("currentPage", 1))
    per_page = 6
    obj = PageTool(datas, current_page, per_page)
    data_list = obj.show()
    sum_page = math.ceil(len(datas) / per_page)

    # 为每条做题记录补充用户信息
    for item in data_list:
        item.UserName = temps.UserName
        item.Name = temps.Name
        item.Phone = temps.Phone
        # 展示班级，不再展示住址
        item.ClassName = getattr(temps, 'ClassName', '')
        item.Classes = getattr(temps, 'Classes', '')

    return render_template(
        'users/mytestcontentrecordmanagement.html',
        datas=data_list,
        sum=len(datas),
        sum_page=sum_page,
        pre=current_page - 1 if current_page > 1 else 1,
        next=current_page + 1 if current_page < sum_page else sum_page,
        userType=session['logged_type'],
        session=session['logged_type']
    )


@app.route('/getmytestcontentrecordanswer', methods=['GET', 'POST'])
def getmytestcontentrecordanswer():
    """Renders the about page."""
    testRecordId = request.args.get("testRecordId")

    testRecord = TestRecordServer().select_sql_by_id(testRecordId)
    testRecordAnswer = TestRecordAnswerServer().select_sql_all_test_record_id(testRecordId)
    testRecordAnswerSelect = TestRecordAnswerSelectServer().select_sql_all_test_record_id(testRecordId)

    jsons = "["

    jsons += "{"
    jsons += "\"times\":\"" + testRecord.RocordTime.strftime('%Y-%m-%d %H:%M:%S') + "\""
    jsons += "},"

    for item in testRecordAnswer:
        jsons += "{"
        jsons += "\"content\":\"" + item.TestContent.Content.replace(" ", "").replace("\r\n", "").replace("\n",
                                                                                                          "") + "\","
        jsons += "\"grade\":\"" + str(item.TestContent.Grade) + "\","
        jsons += "\"answerContent\":\"" + item.AnswerContent.replace(" ", "").replace("\r\n", "").replace("\n",
                                                                                                          "").replace(
            "\"", "") + "\","
        jsons += "\"AnswerGrade\":\"" + str(item.Grade) + "\""
        jsons += "},"

    for item in testRecordAnswerSelect:
        a = "A:" + item.TestSelect.AnswerA + " "
        b = "B:" + item.TestSelect.AnswerB + " "
        c = "C:" + item.TestSelect.AnswerC + " "
        d = "D:" + item.TestSelect.AnswerD + " "

        jsons += "{"
        jsons += "\"contentSelect\":\"" + item.TestSelect.Content.replace(" ", "").replace("\r\n", "").replace("\n",
                                                                                                               "") + "\","
        jsons += "\"contentOption\":\"" + a + b + c + d + "\","
        jsons += "\"grade\":\"" + str(item.TestSelect.Grade) + "\","
        jsons += "\"answerContent\":\"" + item.AnswerSelect.replace(" ", "").replace("\r\n", "").replace("\n",
                                                                                                         "").replace(
            "\"", "") + "\","
        jsons += "\"AnswerGrade\":\"" + str(item.Grade) + "\""
        jsons += "},"

    jsons = jsons[0:(len(jsons) - 1)]
    jsons += "]"
    return jsonify(jsons)





@app.route('/getTestContent', methods=['GET', 'POST'])
def getTestContent():
    '''
    根据id获取题库，然后获取session 中的学信息并查询此学生的所有记录id获取最后一个id，最后json发给前端
    '''
    users = json.loads(session["logged_in"])
    # 编程题目id
    id = request.args.get("id")
    # 编程题的回答id
    test_record_answer_content_temp = request.args.get('contentId')
    test_record_answer_content_id = test_record_answer_content_temp.replace("[", "").replace("]", "").split(",")
    testContentServer = TestContentServer()
    temps = testContentServer.select_sql_by_id(id)
    datas = []
    datas.append(temps)

    jsons = "["
    for item in test_record_answer_content_id:

        testRecordAnswerServer = TestRecordAnswerServer().select_sql_by_id(item)
        if str(testRecordAnswerServer.TestContentId) == id:
            jsons += "{"
            jsons += "\"testRecordId\":\"" + str(testRecordAnswerServer.TestRecordId) + "\","
            jsons += "\"testAnswerId\":\"" + str(testRecordAnswerServer.Id) + "\","
            jsons += "\"testContentId\":\"" + str(testRecordAnswerServer.TestContentId) + "\","
            jsons += "\"content\":\"" + temps.Content.replace(" ", "").replace("\r\n", "").replace("\n", "") + "\","
            jsons += "\"grade\":\"" + str(temps.Grade) + "\""
            jsons += "},"

    jsons = jsons[0:(len(jsons) - 1)]
    jsons += "]"

    return jsons


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




@app.route('/myprofile', methods=['GET'])
def myprofile():
    users = json.loads(session["logged_in"])
    studentsServer = StudentsServer()
    user = studentsServer.select_sql_by_id(users["Id"])
    # 容错与自愈：如库里存在空字段，回填 session 并尝试写回数据库（不再处理 Address）
    try:
        from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
        need_update = False
        # 以 session 为可信源
        sess_username = users.get("UserName") or users.get("User_Name")
        sess_name = users.get("Name")
        sess_phone = users.get("Phone")
    # 地址字段已废弃

        if user:
            if not getattr(user, 'UserName', None) and sess_username:
                user.UserName = sess_username
                need_update = True
            if (not getattr(user, 'Name', None)) and sess_name:
                user.Name = sess_name
                need_update = True
            if (not getattr(user, 'Phone', None)) and sess_phone:
                user.Phone = sess_phone
                need_update = True
            # 不再处理 Address 字段

            if need_update:
                helper = MySqlHelper()
                # 仅更新非空字段，避免覆盖已有信息
                sets = []
                if user.UserName:
                    sets.append(f"User_Name='{user.UserName}'")
                if user.Name:
                    sets.append(f"Name='{user.Name}'")
                if user.Phone:
                    sets.append(f"Phone='{user.Phone}'")
                # 不再更新 Address 字段
                if sets:
                    sql = f"UPDATE students SET {', '.join(sets)} WHERE Id={int(users['Id'])}"
                    helper.query(sql, "")
                    helper.connent.commit()
                    helper.end()
    except Exception as _:
        # 自愈不应影响页面渲染，忽略更新失败
        pass
    return render_template(
        'users/myprofile.html',
        user=user,
        userType=session.get('logged_type'),
        session=session
    )



