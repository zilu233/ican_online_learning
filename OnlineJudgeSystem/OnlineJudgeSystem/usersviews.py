"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify, request, session, redirect
from werkzeug.exceptions import RequestURITooLarge
from OnlineJudgeSystem import app
from OnlineJudgeSystem.common.ai_client import get_client, AIClientError
from OnlineJudgeSystem.model.TestContent import TestContentServer, TestContent
from OnlineJudgeSystem.common.CodeExecutor import CodeExecutor
from OnlineJudgeSystem.model.TestCase import TestCaseServer
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
    # Save current test id in session so server-side checks can enforce AI policy even if client omits test_id
    try:
        session['current_test_id'] = test.Id
    except Exception:
        # ignore if session unavailable
        app.logger.debug('Unable to set session current_test_id')

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

    # 1) 编程题按“私有实际用例”逐题评分（没有配置则退回到单一Result对比）
    content_answers = TestRecordAnswerServer().select_sql_all_test_record_id(test_record_id)
    executor = CodeExecutor(timeout=5)
    for item in content_answers:
        # 获取题目信息
        testContent = TestContentServer().select_sql_by_id(item.TestContentId)
        # 获取私有用例
        try:
            private_cases = TestCaseServer().select_private_by_content(item.TestContentId)
        except Exception:
            private_cases = []

        question_grade = 0
        if private_cases and item.AnswerContent:
            total_points = sum([c.Points or 1 for c in private_cases]) or 0
            cases_payload = [
                {
                    'id': c.Id,
                    'input': c.Input or '',
                    'expected': c.ExpectedOutput or '',
                    'points': c.Points or 1,
                } for c in private_cases
            ]
            multi = executor.execute_cases(item.AnswerContent, cases_payload)
            passed_points = sum([cr['points'] for cr in multi.get('case_results', []) if cr.get('success')])
            # 比例分：按题目总分与用例总分比例换算
            if total_points > 0:
                question_grade = int(round((testContent.Grade or 0) * (passed_points / total_points)))
            else:
                question_grade = 0
        else:
            # 兼容旧题：没有配置私有用例，用单一Result比对
            if item.AnswerContent:
                single = executor.execute_code(item.AnswerContent, testContent.Result)
                question_grade = testContent.Grade if single.get('success') else 0
            else:
                question_grade = 0

        # 更新该题得分
        item.Grade = question_grade
        TestRecordAnswerServer().update_sql(item)
        sums += question_grade

    # 2) 选择题按原有记录得分汇总
    datas = TestRecordAnswerSelectServer().select_sql_all_test_record_id(test_record_id)
    for item in datas:
        sums += item.Grade

    # 更新总分
    testRecord = TestRecordServer().select_sql_by_id(test_record_id)
    testRecord.SumGrade = sums
    TestRecordServer().update_sql(testRecord)
    return jsonify({"message": "Answers received successfully", "sum": sums})


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

    # 为每条做题记录补充用户信息（将原先显示手机号的位置改为显示学号，即 UserName）
    for item in data_list:
        item.UserName = temps.UserName
        item.Name = temps.Name
        # 将原先用于显示手机号的字段改为学号：优先使用学生卡号(Card)（学号），若无则回退到 UserName
        item.Phone = getattr(temps, 'Card', '') or getattr(temps, 'UserName', '')
        # 同步在记录对象上设置 Card 字段，便于模板直接读取 {{ item.Card }}
        item.Card = getattr(temps, 'Card', '') or getattr(temps, 'UserName', '')
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

    # 是否为提交评分请求（如果前端发送 submit_for_grade=1，则用私有用例对当前题目评分并保存分数）
    submit_for_grade = request.form.get('submit_for_grade')

    # 优先：如果存在“公开样例用例”，则逐个运行这些用例并返回每例结果，不修改评分（评分在交卷时按私有用例结算）
    try:
        public_cases = TestCaseServer().select_public_by_content(testContentId)
    except Exception:
        public_cases = []

    # 如果是“提交并评分”的请求，优先使用私有用例进行评分（不受公开样例存在与否影响）
    if submit_for_grade and submit_for_grade in ('1', 'true', 'True'):
        # 执行私有用例并更新该题分数（与 /testover 的单题逻辑一致）
        try:
            private_cases = TestCaseServer().select_private_by_content(testContentId)
        except Exception:
            private_cases = []

        question_grade = 0
        case_results = []
        if private_cases and pycode:
            total_points = sum([c.Points or 1 for c in private_cases]) or 0
            cases_payload = [
                {
                    'id': c.Id,
                    'input': c.Input or '',
                    'expected': c.ExpectedOutput or '',
                    'points': c.Points or 1,
                } for c in private_cases
            ]
            multi = executor.execute_cases(pycode, cases_payload)
            passed_points = sum([cr['points'] for cr in multi.get('case_results', []) if cr.get('success')])
            case_results = multi.get('case_results', [])
            if total_points > 0:
                question_grade = int(round((testContent.Grade or 0) * (passed_points / total_points)))
            else:
                question_grade = 0
        else:
            # 退回兼容旧逻辑：单一Result对比
            if pycode:
                single = executor.execute_code(pycode, testContent.Result)
                case_results = [ { 'index': 1, 'input': '', 'expected': testContent.Result, 'output': single.get('output',''), 'success': single.get('success', False), 'msg': single.get('msg','') } ]
                question_grade = testContent.Grade if single.get('success') else 0
            else:
                question_grade = 0

        # 更新数据库中的代码与分数
        try:
            testRecordAnswerServer = TestRecordAnswerServer()
            testRecordAnswer = TestRecordAnswer()
            testRecordAnswer.Id = testAnswerId
            testRecordAnswer.AnswerContent = pycode
            testRecordAnswer.Grade = question_grade
            testRecordAnswerServer.update_sql(testRecordAnswer)
        except Exception:
            app.logger.exception('runcode: failed to save graded answer for testAnswerId %s', testAnswerId)

        return jsonify({
            'success': True,
            'code': 1,
            'msg': f'已提交并按实际用例评分：得分 {question_grade}',
            'grade': question_grade,
            'case_results': case_results,
        })

    # 否则，原有行为：如果存在“公开样例用例”，则逐个运行这些用例并返回每例结果，不修改评分（评分在交卷时按私有用例结算）
    if public_cases:
        cases_payload = [
            {
                'id': c.Id,
                'input': c.Input or '',
                'expected': c.ExpectedOutput or '',
                'points': c.Points or 1
            } for c in public_cases
        ]
        multi = executor.execute_cases(pycode, cases_payload)

        # 更新数据库：仅保存代码，不改分
        testRecordAnswerServer = TestRecordAnswerServer()
        # 读取当前记录，保留原Grade
        current_rec = testRecordAnswerServer.select_sql_by_id(testAnswerId)
        keep_grade = getattr(current_rec, 'Grade', 0) if current_rec else 0
        testRecordAnswer = TestRecordAnswer()
        testRecordAnswer.Id = testAnswerId
        testRecordAnswer.AnswerContent = pycode
        testRecordAnswer.Grade = keep_grade
        # 不改变分数，仅更新代码内容
        testRecordAnswerServer.update_sql(testRecordAnswer)

        overall_msg = f"样例用例通过 {multi['passed']}/{multi['total']}" if multi['total'] else "未配置样例用例"

        # 考试模式：隐藏细节
        try:
            test_id = session.get('current_test_id') or request.form.get('test_id')
            if test_id:
                test_obj = TestServer().select_sql_by_id(test_id)
                test_type = getattr(test_obj, 'TestType', 'homework')
            else:
                test_type = 'homework'
        except Exception:
            test_type = 'homework'

        if test_type == 'exam':
            minimal = {
                'success': multi.get('all_passed', False),
                'code': 1 if multi.get('all_passed') else 0,
                'msg': overall_msg,
            }
            return jsonify(minimal)

        # 作业模式：返回详细的每例结果
        return jsonify({
            'success': multi.get('all_passed', False),
            'code': 1 if multi.get('all_passed') else 0,
            'msg': overall_msg,
            'cases_summary': {
                'passed': multi.get('passed', 0),
                'total': multi.get('total', 0),
            },
            'case_results': multi.get('case_results', []),
        })

    # 兼容：若未配置公开样例，用老逻辑按单一标准输出对比
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
    
    # Based on test type (homework/exam) decide whether to include detailed hints
    try:
        test_id = session.get('current_test_id') or request.form.get('test_id')
        if test_id:
            test_obj = TestServer().select_sql_by_id(test_id)
            test_type = getattr(test_obj, 'TestType', 'homework')
        else:
            test_type = 'homework'
    except Exception:
        # If we cannot determine test type, default to conservative behavior: treat as exam? keep homework for now
        test_type = 'homework'

    # If this is an exam, remove detailed hints from the response to avoid leaking information
    if test_type == 'exam':
        minimal = {
            'success': result.get('success', False),
            'code': result.get('code', 0),
            'msg': result.get('msg', ''),
        }
        # Do not include output or traceback or error details in exam mode
        return jsonify(minimal)

    # For homework (default) return full details
    return jsonify(result)



@app.route('/ask_model', methods=['POST'])
def ask_model():
    """Accepts JSON {question: str, provider: optional} and returns AI provider answer."""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'missing_json_body'}), 400

    question = data.get('question')
    provider = data.get('provider')
    test_id = data.get('test_id')

    if not question or not isinstance(question, str):
        return jsonify({'success': False, 'error': 'invalid_question'}), 400

    try:
        # Determine test id: prefer payload, else fallback to session value saved at test start
        if not test_id:
            test_id = session.get('current_test_id')

        # If a test_id is available, check the test type and forbid AI usage for exams
        if test_id:
            try:
                test_obj = TestServer().select_sql_by_id(test_id)
                if getattr(test_obj, 'TestType', 'homework') == 'exam':
                    return jsonify({'success': False, 'error': 'ai_disabled_for_exam', 'message': '该试卷为考试，禁止使用 AI 助手。'}), 403
            except Exception:
                # If we cannot read test info, log and continue to allow (or you may choose to reject)
                app.logger.warning('ask_model: failed to read test object for id %s', test_id)

        client = get_client(provider)
        success, resp = client.ask(question, metadata={'path': request.path, 'user': session.get('logged_in')})
    except AIClientError as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    if not success:
        # resp is expected to contain an 'error' key and possibly 'error_type'
        error_info = resp if isinstance(resp, dict) else {'error': str(resp)}
        err_type = error_info.get('error_type', '')
        suggestion = ''
        if err_type == 'dns_error':
            suggestion = '请检查服务器 DNS 配置或确认 KIMI_ENDPOINT 环境变量是否正确（可尝试在服务器上使用 `nslookup` 或 `ping` 测试）。'
        elif err_type == 'network_error':
            suggestion = '网络连接失败，请检查服务器网络/代理设置，或确认能访问模型提供商的 host。'
        elif err_type == 'invalid_response':
            suggestion = '模型返回了不可解析的响应。请检查提供商文档或返回的 body 字段。'
        elif err_type == 'provider_error':
            suggestion = '提供商返回 error status，请查看返回的 status_code 和 body 以获取更多信息。'
        else:
            suggestion = '请查看服务器日志获取更多信息。'

        # log for server-side debugging
        app.logger.warning('ask_model failed: %s; suggestion: %s', error_info, suggestion)

        return jsonify({'success': False, 'error': error_info, 'suggestion': suggestion}), 502

    return jsonify({'success': True, 'answer': resp.get('answer'), 'raw': resp.get('raw')})


@app.route('/public_cases', methods=['GET'])
def get_public_cases():
    """学生端获取某题目的公开样例用例。
    入参: test_content_id
    返回: {code:1, data:[{index, input, expected}]}
    """
    try:
        test_content_id = int(request.args.get('test_content_id'))
    except Exception:
        return jsonify({'code': 0, 'error': 'missing_or_invalid_test_content_id'}), 400

    try:
        cases = TestCaseServer().select_public_by_content(test_content_id)
    except Exception:
        cases = []

    data = []
    for idx, c in enumerate(cases, 1):
        data.append({
            'index': idx,
            'input': c.Input or '',
            'expected': c.ExpectedOutput or ''
        })

    return jsonify({'code': 1, 'data': data})




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



