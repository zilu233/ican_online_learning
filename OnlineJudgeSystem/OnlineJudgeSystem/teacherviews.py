"""
Routes and views for the flask application.
"""

from datetime import datetime
from io import BytesIO

from flask import render_template,jsonify,request,session,redirect,send_file
from OnlineJudgeSystem import app

from OnlineJudgeSystem.model.Students import StudentsServer
from OnlineJudgeSystem.model.TestSelect import TestSelect,TestSelectServer
from OnlineJudgeSystem.model.TestContent import TestContent, TestContentServer
from OnlineJudgeSystem.model.TestCase import TestCase, TestCaseServer
from OnlineJudgeSystem.model.Test import Test, TestServer
from OnlineJudgeSystem.model.TestRecord import TestRecord, TestRecordServer
from OnlineJudgeSystem.model.TestRecordAnswer import TestRecordAnswerServer
from OnlineJudgeSystem.model.TestRecordAnswerSelect import TestRecordAnswerSelect,TestRecordAnswerSelectServer
from OnlineJudgeSystem.model.TestQuestionRelation import TestQuestionRelation,TestQuestionRelationServer
from OnlineJudgeSystem.model.Classes import ClassesServer
from OnlineJudgeSystem.model.Teachers import TeachersServer
import pandas as pd
import time
from OnlineJudgeSystem.model.PageTool import PageTool
import json


def _get_current_teacher_info():
    try:
        return json.loads(session.get("logged_in", "{}"))
    except Exception:
        return {}


def _refresh_teacher_session(teacher_id, overrides=None):
    if overrides:
        current = _get_current_teacher_info()
        current.update(overrides)
        session['logged_in'] = json.dumps(current, ensure_ascii=False)
        return

    teacher = TeachersServer().select_sql_by_id(teacher_id)
    if teacher:
        session['logged_in'] = teacher.to_json()


def _summarize_teacher_classes(teacher_id):
    classes = ClassesServer.select_sql_by_teacher(teacher_id)
    class_names = ",".join([c.ClassName for c in classes])
    school_id = classes[0].SchoolId if classes else None
    return class_names, school_id, classes


@app.route('/teacher/classes', methods=['GET'])
def teacher_class_management():
    if session.get('logged_type') != 'teacher':
        return redirect('/login')

    teacher_info = _get_current_teacher_info()
    teacher_id = teacher_info.get('Id')
    if not teacher_id:
        return redirect('/login')

    msg = request.args.get('msg')
    classes = ClassesServer.select_sql_all(status=1)

    my_classes = [c for c in classes if c.TeacherId == teacher_id]
    available_classes = [c for c in classes if not c.TeacherId]
    occupied_classes = [c for c in classes if c.TeacherId and c.TeacherId != teacher_id]

    return render_template(
        'teacher/classbinding.html',
        title='班级管理',
        userType=session['logged_type'],
        session=session['logged_type'],
        my_classes=my_classes,
        available_classes=available_classes,
        occupied_classes=occupied_classes,
        teacher_info=teacher_info,
        message=msg,
        school_filter=''
    )


@app.route('/teacher/classes/bind', methods=['POST'])
def teacher_bind_class():
    if session.get('logged_type') != 'teacher':
        return redirect('/login')

    class_id = request.form.get('class_id')
    teacher_info = _get_current_teacher_info()
    teacher_id = teacher_info.get('Id')
    if not class_id or not teacher_id:
        return redirect('/teacher/classes?msg=参数缺失')

    try:
        class_id_int = int(class_id)
    except ValueError:
        return redirect('/teacher/classes?msg=班级编号无效')

    class_info = ClassesServer.select_sql_by_id(class_id_int)
    if class_info is None:
        return redirect('/teacher/classes?msg=班级不存在')
    if class_info.TeacherId and class_info.TeacherId != teacher_id:
        return redirect('/teacher/classes?msg=该班级已由其他老师负责')

    ClassesServer.update_teacher(class_id_int, teacher_id)
    class_names, school_id, bound_classes = _summarize_teacher_classes(teacher_id)
    TeachersServer().update_classes_and_school(teacher_id, class_names, school_id)
    school_name = bound_classes[0].SchoolName if bound_classes else ''
    _refresh_teacher_session(teacher_id, {
        "Classes": class_names,
        "SchoolId": school_id or 0,
        "SchoolName": school_name
    })
    return redirect('/teacher/classes?msg=班级绑定成功')


@app.route('/teacher/classes/unbind', methods=['POST'])
def teacher_unbind_class():
    if session.get('logged_type') != 'teacher':
        return redirect('/login')

    class_id = request.form.get('class_id')
    teacher_info = _get_current_teacher_info()
    teacher_id = teacher_info.get('Id')
    if not class_id or not teacher_id:
        return redirect('/teacher/classes?msg=参数缺失')

    try:
        class_id_int = int(class_id)
    except ValueError:
        return redirect('/teacher/classes?msg=班级编号无效')

    class_info = ClassesServer.select_sql_by_id(class_id_int)
    if class_info is None:
        return redirect('/teacher/classes?msg=班级不存在')
    if class_info.TeacherId != teacher_id:
        return redirect('/teacher/classes?msg=仅能解绑自己负责的班级')

    ClassesServer.update_teacher(class_id_int, None)
    class_names, school_id, bound_classes = _summarize_teacher_classes(teacher_id)
    TeachersServer().update_classes_and_school(teacher_id, class_names, school_id)
    school_name = bound_classes[0].SchoolName if bound_classes else ''
    _refresh_teacher_session(teacher_id, {
        "Classes": class_names,
        "SchoolId": school_id or 0,
        "SchoolName": school_name
    })
    return redirect('/teacher/classes?msg=已解除班级绑定')


'''
编程题库管理
'''
@app.route('/testcontentmanagement',methods=['GET', 'POST'])
def testcontentmanagement():
    """Renders the home page."""
    keyword = request.args.get("seach")
    data_list = []
    seacher  = "555"
    if keyword !=None:
        testContentServer = TestContentServer()
        data_list = testContentServer.select_sql_by_keyword(keyword)
        seacher  ="123"
    else:
        testContentServer = TestContentServer()
        data_list = testContentServer.select_sql_all()

    #上一页下一页
    pre_page  = 0
    next_page = 1
    sum_page  = 0

    #获取请求是上一页还是下一页
    type_page = request.args.get("typePage");
    current_page = request.args.get("currentPage");
    sum      =  len(data_list)
    sum_page =  (sum + 6 - 1) // 6

    '''
        分页机制
       第一页 0: limit 0 ,6
       第二页 1: limit 6 ,6
       第三页 2: limit 12,6
    '''
    if type_page !=None:
        #处理上一页
        if type_page  ==  "pre" and int(current_page) !=0:
            pre_page = int(current_page) - 1
            next_page = int(current_page)
        #处理下一页
        elif type_page == "next" :
            pre_page = int(current_page)
            next_page = int(current_page) + 1
    else:
        current_page = 0

    obj = PageTool(data_list,next_page)
    data_list = obj.show()

    return render_template(
        'teacher/testcontentmanagement.html',
        title='题库管理',
        userType = session['logged_type'],
        session  = session['logged_type'],
        datas = data_list,
        pre   = pre_page,
        next  = next_page,
        sum   = sum,
        sum_page = sum_page,
        seacher  = seacher
    )

@app.route('/teacher/testcases', methods=['GET'])
def teacher_get_testcases():
    """获取某编程题的所有测试用例（公开/私有）。返回JSON。"""
    try:
        test_content_id = int(request.args.get('test_content_id'))
    except Exception:
        return jsonify({'code': 0, 'error': 'missing_or_invalid_test_content_id'}), 400

    server = TestCaseServer()
    cases = server.select_by_content(test_content_id, only_enabled=False)
    data = []
    for c in cases:
        data.append({
            'id': c.Id,
            'test_content_id': c.TestContentId,
            'input': c.Input,
            'expected_output': c.ExpectedOutput,
            'is_public': int(c.IsPublic),
            'points': int(c.Points),
            'case_order': int(c.CaseOrder),
            'enabled': int(c.Enabled),
        })
    return jsonify({'code': 1, 'data': data})

@app.route('/teacher/testcases/save', methods=['POST'])
def teacher_save_testcases():
    """保存某编程题的测试用例（整体替换）。接受JSON: {test_content_id, cases:[...]}
    cases item fields: id(optional), input, expected_output, is_public, points, case_order, enabled
    """
    data = request.get_json(silent=True) or {}
    test_content_id = data.get('test_content_id')
    cases = data.get('cases', [])
    if not test_content_id:
        return jsonify({'code': 0, 'error': 'missing_test_content_id'}), 400

    server = TestCaseServer()
    # 简单策略：清空再插入
    server.delete_by_content(test_content_id)
    order = 0
    for it in cases:
        tc = TestCase()
        tc.TestContentId = int(test_content_id)
        tc.Input = (it.get('input') or '')
        tc.ExpectedOutput = (it.get('expected_output') or '')
        tc.IsPublic = 1 if it.get('is_public') in (1, '1', True, 'true', 'True') else 0
        tc.Points = int(it.get('points') or 1)
        tc.CaseOrder = int(it.get('case_order') if it.get('case_order') is not None else order)
        tc.Enabled = 0 if it.get('enabled') in (0, '0', False, 'false', 'False') else 1
        order += 1
        server.insert_sql(tc)

    return jsonify({'code': 1, 'message': 'saved', 'count': len(cases)})

@app.route('/testcontentmanagementadd',methods=['GET', 'POST'])
def testcontentmanagementadd():
    """Renders the contact page."""

    if request.method == 'POST':
        content    =  request.form.get('content')
        result     =  request.form.get('result')
        grade      =  request.form.get('grade')
        cases_json = request.form.get('cases_json')

        # 放宽校验：允许 result 留空，只要提交了至少一个用例；grade 和 content 必填
        cases_count = 0
        if cases_json:
            try:
                payload = json.loads(cases_json)
                if isinstance(payload, dict):
                    cases_count = len(payload.get('cases', []) or [])
                elif isinstance(payload, list):
                    cases_count = len(payload)
            except Exception:
                cases_count = 0

        if not content or not grade or (not result and cases_count == 0):
            # 返回到添加页，而不是用户管理或登录页
            return redirect("/testcontentmanagementadd")
        else:
            #将用户请求转发给相应的Model
            testContent = TestContent()
            testContent.Content = content
            testContent.Result   = result
            testContent.Grade  = grade
            testContentServer = TestContentServer()
            new_id = testContentServer.insert_sql(testContent)

            # 保存提交的测试用例（若有）
            if cases_json:
                try:
                    payload = json.loads(cases_json)
                    cases = payload.get('cases', []) if isinstance(payload, dict) else (payload if isinstance(payload, list) else [])
                except Exception:
                    cases = []
                if new_id and cases:
                    tcs = TestCaseServer()
                    order = 0
                    for it in cases:
                        try:
                            tc = TestCase()
                            tc.TestContentId = int(new_id)
                            tc.Input = (it.get('input') or '')
                            tc.ExpectedOutput = (it.get('expected_output') or '')
                            tc.IsPublic = 1 if it.get('is_public') in (1, '1', True, 'true', 'True') else 0
                            tc.Points = int(it.get('points') or 1)
                            tc.CaseOrder = int(it.get('case_order') if it.get('case_order') is not None else order)
                            tc.Enabled = 0 if it.get('enabled') in (0, '0', False, 'false', 'False') else 1
                            order += 1
                            tcs.insert_sql(tc)
                        except Exception:
                            continue
            return redirect("/testcontentmanagement")
    else:
        return render_template(
            'teacher/testcontentmanagementadd.html',
            userType = session['logged_type'],
            session  = session['logged_type'],
            title='题库添加',
        )

@app.route('/testcontentmanagementedit',methods=['GET', 'POST'])
def testcontentmanagementedit():
    """Renders the about page."""

    if request.method == 'POST':
        id         =  request.form.get('Id')
        content    =  request.form.get('content')
        result       =  request.form.get('result')
        grade      =  request.form.get('grade')

        if content == '' or result == '' or grade == '':
            return redirect("/usermanagementadd")
        else:
            #将用户请求转发给相应的Model
            testContent = TestContent()
            testContent.Id = id
            testContent.Content = content
            testContent.Result   = result
            testContent.Grade  = grade
            testContentServer = TestContentServer()

            testContentServer.update_sql(testContent)
            return redirect("/testcontentmanagement")
    else:
        id         =  request.args.get('id')
        testContentServer = TestContentServer()
        data = testContentServer.select_sql_by_id(id)

        return render_template(
            'teacher/testcontentmanagementedit.html',
            userType = session['logged_type'],
            session  = session['logged_type'],
            title='题库编辑',
            data = data,
        )

@app.route('/testcontentmanagementdelete',methods=['GET', 'POST'])
def testcontentmanagementdelete():
    """Renders the about page."""
    id         =  request.args.get('id')
    #将用户请求转发给相应的Model
    testContentServer = TestContentServer()
    testContentServer.delete_sql(id)
    testContentServer = TestContentServer()
    testContentServer.delete_sql(id)

    return redirect("/testcontentmanagement")




'''
选择题管理
'''
@app.route('/testselectmanagement',      methods=['GET', 'POST'])
def testselectmanagement():
    """Renders the home page."""
    keyword = request.args.get("seach")
    data_list = []
    seacher  = "555"
    if keyword !=None:
        testContentServer = TestSelectServer()
        data_list = testContentServer.select_sql_by_keyword(keyword)
        seacher  ="123"
    else:
        testContentServer = TestSelectServer()
        data_list = testContentServer.select_sql_all()

    #上一页下一页
    pre_page  = 0
    next_page = 1
    sum_page  = 0

    #获取请求是上一页还是下一页
    type_page = request.args.get("typePage");
    current_page = request.args.get("currentPage");
    sum      =  len(data_list)
    sum_page =  (sum + 6 - 1) // 6

    '''
        分页机制
       第一页 0: limit 0 ,6
       第二页 1: limit 6 ,6
       第三页 2: limit 12,6
    '''
    if type_page !=None:
        #处理上一页
        if type_page  ==  "pre" and int(current_page) !=0:
            pre_page = int(current_page) - 1
            next_page = int(current_page)
        #处理下一页
        elif type_page == "next" :
            pre_page = int(current_page)
            next_page = int(current_page) + 1
    else:
        current_page = 0

    obj = PageTool(data_list,next_page)
    data_list = obj.show()

    return render_template(
        'teacher/testselectmanagement.html',
        title='题库管理',
        userType = session['logged_type'],
        session  = session['logged_type'],
        datas = data_list,
        pre   = pre_page,
        next  = next_page,
        sum   = sum,
        sum_page = sum_page,
        seacher  = seacher
    )

@app.route('/testselectmanagementadd',   methods=['GET', 'POST'])
def testselectmanagementadd():
    """Renders the contact page."""

    if request.method == 'POST':
        content    =  request.form.get('content')
        contentTypes    =  request.form.get('contentTypes')
        answerA    =  request.form.get('answerA')
        answerB    =  request.form.get('answerB')
        answerC    =  request.form.get('answerC')
        answerD    =  request.form.get('answerD')
        result     =  request.form.get('result')
        grade      =  request.form.get('grade')

        if content == '' or result == '' or grade == '' or  answerA == '' or answerB == '' or answerC == '' or answerD == '':
            return "<script>alert('请在空白处填写内容');window.location.href='/testselectmanagementadd'</script>"
        else:
            #将用户请求转发给相应的Model
            testSelect = TestSelect()
            testSelect.Content = content
            testSelect.AnswerA = answerA
            testSelect.AnswerB = answerB
            testSelect.AnswerC = answerC
            testSelect.AnswerD = answerD
            testSelect.Result  = result
            testSelect.Grade   = grade
            testContentServer   = TestSelectServer()

            testContentServer.insert_sql(testSelect);
            return redirect("/testselectmanagement")
    else:
        return render_template(
            'teacher/testselectmanagementadd.html',
            userType = session['logged_type'],
            session  = session['logged_type'],
            title='题库添加',
        )

@app.route('/testselectmanagementedit',  methods=['GET', 'POST'])
def testselectmanagementedit():
    """Renders the about page."""

    if request.method == 'POST':
        id         =  request.form.get('Id')
        content    =  request.form.get('content')
        contentTypes    =  request.form.get('contentTypes')
        answerA    =  request.form.get('answerA')
        answerB    =  request.form.get('answerB')
        answerC    =  request.form.get('answerC')
        answerD    =  request.form.get('answerD')
        result     =  request.form.get('result')
        grade      =  request.form.get('grade')

        if content == '' or result == '' or grade == '' or contentTypes == '' or answerA == '' or answerB == '' or answerC == '' or answerD == '':
            return "<script>alert('请在空白处填写内容');window.location.href='/testselectmanagementadd'</script>"
        else:
            #将用户请求转发给相应的Model
            testSelect = TestSelect()
            testSelect.Content = content
            testSelect.ContentTypes = contentTypes
            testSelect.AnswerA = answerA
            testSelect.AnswerB = answerB
            testSelect.AnswerC = answerC
            testSelect.AnswerD = answerD
            testSelect.Result  = result
            testSelect.Grade   = grade
            testContentServer   = TestSelectServer()

            testContentServer.insert_sql(testSelect);
            return redirect("/testselectmanagement")
    else:
        id         =  request.args.get('id')
        testContentServer = TestSelectServer()
        data = testContentServer.select_sql_by_id(id)

        return render_template(
            'teacher/testselectmanagementedit.html',
            userType = session['logged_type'],
            session  = session['logged_type'],
            title='题库编辑',
            data = data,
        )

@app.route('/testselectmanagementdelete',methods=['GET', 'POST'])
def testselectmanagementdelete():
    """Renders the about page."""
    id         =  request.args.get('id')
    #将用户请求转发给相应的Model
    testSelectServer = TestSelectServer()
    testSelectServer.delete_sql(id)
    return redirect("/testselectmanagement")






'''
试卷管理
'''
@app.route('/testmanagement',      methods=['GET', 'POST'])
def testmanagement():
    """Renders the home page."""
    keyword = request.args.get("seach")
    data_list = []
    seacher  = "555"
    if keyword !=None:
        testContentServer = TestServer()
        data_list = testContentServer.select_sql_by_keyword(keyword)
        seacher  ="123"
    else:
        testContentServer = TestServer()
        data_list = testContentServer.select_sql_all()

    #上一页下一页
    pre_page  = 0
    next_page = 1
    sum_page  = 0

    #获取请求是上一页还是下一页
    type_page = request.args.get("typePage");
    current_page = request.args.get("currentPage");
    sum      =  len(data_list)
    sum_page =  (sum + 6 - 1) // 6

    '''
        分页机制
       第一页 0: limit 0 ,6
       第二页 1: limit 6 ,6
       第三页 2: limit 12,6
    '''
    if type_page !=None:
        #处理上一页
        if type_page  ==  "pre" and int(current_page) !=0:
            pre_page = int(current_page) - 1
            next_page = int(current_page)
        #处理下一页
        elif type_page == "next" :
            pre_page = int(current_page)
            next_page = int(current_page) + 1
    else:
        current_page = 0

    obj = PageTool(data_list,next_page)
    data_list = obj.show()

    return render_template(
        'teacher/testmanagement.html',
        title='试卷管理',
        userType = session['logged_type'],
        session  = session['logged_type'],
        datas = data_list,
        pre   = pre_page,
        next  = next_page,
        sum   = sum,
        sum_page = sum_page,
        seacher  = seacher
    )

@app.route('/testmanagementadd', methods=['GET', 'POST'])
def testmanagementadd():
    if request.method == 'POST':
        # 获取试卷信息
        test_name = request.form.get('testname')
        select_text = request.form.get('selecttext')
        program_text = request.form.get('programetext')
        test_type = request.form.get('testtype') or 'homework'

        # 插入试卷信息到 Test 表
        test = Test()
        test.TestName = test_name
        test.SelectText = select_text
        test.ProgrameText = program_text
        # 保存试卷类型（homework/exam）
        try:
            test.TestType = test_type
        except Exception:
            test.TestType = 'homework'


        test_id = TestServer().insert_sql(test)

        # 获取老师选择的题目 ID
        select_question_ids = request.form.getlist('select_question_ids')
        content_question_ids = request.form.getlist('content_question_ids')

        # 插入选择题关联关系
        relation_server = TestQuestionRelationServer()
        for question_id in select_question_ids:
            relation = TestQuestionRelation()
            relation.test_id = test_id
            relation.question_id = question_id
            relation.question_type = 'select'
            relation_server.insert(relation)

        # 插入编程题关联关系
        for question_id in content_question_ids:
            relation = TestQuestionRelation()
            relation.test_id = test_id
            relation.question_id = question_id
            relation.question_type = 'content'
            relation_server.insert(relation)

        return redirect("/testmanagement")
    else:
        # 获取所有选择题和编程题
        all_select_questions = TestSelectServer().select_sql_all()
        all_content_questions = TestContentServer().select_sql_all()
        return render_template(
            'teacher/testmanagementadd.html',
            title='添加试卷',
            userType=session['logged_type'],
            session=session['logged_type'],
            all_select_questions=all_select_questions,
            all_content_questions=all_content_questions
        )

@app.route('/testmanagementedit',  methods=['GET', 'POST'])
def testmanagementedit():
    """Renders the about page."""

    if request.method == 'POST':
        # 从表单中获取ID
        id = request.form.get('id')  # 注意：这里假设HTML表单中有一个名为'id'的隐藏字段
        
        # 确保ID存在
        if not id:
            return redirect("/testmanagement")  # 直接重定向，不添加错误处理
            
        testname = request.form.get('testname')
        programetext = request.form.get('programetext')
        selecttext = request.form.get('selecttext')
        testtype = request.form.get('testtype') or 'homework'

        if testname == '' or programetext == '' or selecttext == '':
            return redirect("/testmanagement")
        else:
            # 更新试卷信息
            test = Test()
            test.Id = id
            test.TestName = testname
            test.ProgrameText = programetext
            test.SelectText = selecttext
            try:
                test.TestType = testtype
            except Exception:
                test.TestType = 'homework'
            testServer = TestServer()
            testServer.update_sql(test)

            # 删除旧的关联关系
            relation_server = TestQuestionRelationServer()
            relation_server.delete_by_test_id(id)

            # 获取老师选择的题目 ID
            select_question_ids = request.form.getlist('select_question_ids')
            content_question_ids = request.form.getlist('content_question_ids')

            # 插入新的选择题关联关系
            for question_id in select_question_ids:
                relation = TestQuestionRelation()
                relation.test_id = id
                relation.question_id = question_id
                relation.question_type = 'select'
                relation_server.insert(relation)

            # 插入新的编程题关联关系
            for question_id in content_question_ids:
                relation = TestQuestionRelation()
                relation.test_id = id
                relation.question_id = question_id
                relation.question_type = 'content'
                relation_server.insert(relation)

            return redirect("/testmanagement")
    else:
        # 获取URL参数中的ID
        id = request.args.get('id')
        
        # 确保ID存在
        if not id:
            return redirect("/testmanagement")
            
        testContentServer = TestServer()
        data = testContentServer.select_sql_by_id(id)

        # 获取当前试卷关联的选择题和编程题
        relation_server = TestQuestionRelationServer()
        questions = relation_server.get_questions_by_test_id(id)
        selected_select_question_ids = [q[0] for q in questions if q[1] == 'select']
        selected_content_question_ids = [q[0] for q in questions if q[1] == 'content']

        # 获取所有选择题和编程题
        all_select_questions = TestSelectServer().select_sql_all()
        all_content_questions = TestContentServer().select_sql_all()

        return render_template(
            'teacher/testmanagementedit.html',
            title='试卷编辑',
            userType=session['logged_type'],
            session=session['logged_type'],
            data=data,
            all_select_questions=all_select_questions,
            all_content_questions=all_content_questions,
            selected_select_question_ids=selected_select_question_ids,
            selected_content_question_ids=selected_content_question_ids,
            id=id  # 确保ID被传递到模板中
        )

@app.route('/testmanagementdelete',methods=['GET', 'POST'])
def testmanagementdelete():
    """Renders the about page."""
    id         =  request.args.get('id')
    #将用户请求转发给相应的Model
    relation_server = TestQuestionRelationServer()
    relation_server.delete_by_test_id(id)
    testContentServer = TestServer()
    testContentServer.delete_sql(id)
    return redirect("/testmanagement")


@app.route('/getprogramenumber',methods=['GET', 'POST'])
def getprogramenumber():
    """Renders the about page."""
    testCount         =  request.args.get('testCount')
    testSelectServer = TestContentServer()
    count = testSelectServer.select_sql_all()
    flags = "ok"
    if int(testCount)  > len(count):
        flags = "false"


    jsons = {}
    jsons["msg"] = flags
    return jsonify(jsons)

@app.route('/getselectnumber',methods=['GET', 'POST'])
def getselectnumber():
    """Renders the about page."""
    testCount         =  request.args.get('testCount')

    testSelectServer = TestSelectServer()
    count = testSelectServer.select_sql_all()
    flags = "ok"
    if int(testCount)  > len(count):
        flags = "false"


    jsons = {}
    jsons["msg"] = flags
    return jsonify(jsons)








'''
做题记录
'''
@app.route('/testcontentrecordmanagement')
def testcontentrecordmanagement():
    """Renders the home page."""
    selected_class_id = request.args.get("classId") or ""
    selected_test_id = request.args.get("testId") or ""
    teacher_classes = []
    try:
        current_user = json.loads(session.get("logged_in", "{}"))
    except Exception:
        current_user = {}
    user_type = session.get('logged_type', "")
    if user_type == "teacher":
        teacher_id = current_user.get("Id", 0)
        teacher_classes = ClassesServer.select_sql_by_teacher(teacher_id) or []
    else:
            teacher_classes = ClassesServer.select_sql_all() or []

    # 获取试卷列表（供筛选/导出使用）
    tests = []
    debug_matched_ids = []
    all_tests = TestServer().select_sql_all() or []
    # 若选了班级，则仅展示该班级有过作答记录的试卷集合
    if selected_class_id:
        studentsServer = StudentsServer()
        recordServer = TestRecordServer()
        students = studentsServer.select_sql_all_two_table()
        class_students = [s for s in students if str(getattr(s, 'ClassId', '')) == selected_class_id]

        # DEBUG: 输出班级学生数量，便于定位筛选问题
        try:
            print(f"[DEBUG] testcontentrecordmanagement: selected_class_id={selected_class_id}, class_students_count={len(class_students)}")
        except Exception:
            pass

        # 简化并健壮的匹配策略：只要该班级任一学生有作答记录包含本试卷的任一题目（选择或编程），即认为该试卷存在该班级的作答记录
        matched_test_ids = set()
        for t in all_tests:
            try:
                rels = TestQuestionRelationServer().get_questions_by_test_id(t.Id)
                sel_ids = {qid for (qid, tp) in rels if tp == 'select'}
                con_ids = {qid for (qid, tp) in rels if tp == 'content'}
                if not sel_ids and not con_ids:
                    # 如果试卷没有题目关系，跳过
                    continue
            except Exception:
                sel_ids, con_ids = set(), set()

            # 遍历班级学生的作答记录，检查是否有交集
            for stu in class_students:
                try:
                    recs = recordServer.select_sql_by_student_id(stu.Id)
                except Exception:
                    recs = []
                found = False
                for rec in recs:
                    # 检查编程题作答中的 TestContentId
                    for answer in getattr(rec, 'TestContent', []) or []:
                        if getattr(answer, 'TestContentId', None) in con_ids:
                            matched_test_ids.add(t.Id)
                            found = True
                            break
                    if found:
                        break
                    # 检查选择题作答中的 TestSelectId
                    for answer in getattr(rec, 'TestSelect', []) or []:
                        if getattr(answer, 'TestSelectId', None) in sel_ids:
                            matched_test_ids.add(t.Id)
                            found = True
                            break
                    if found:
                        break
                if found:
                    # 不必再检查其他学生
                    continue

        tests = [t for t in all_tests if t.Id in matched_test_ids]
        debug_matched_ids = sorted(list(matched_test_ids))
        try:
            print(f"[DEBUG] testcontentrecordmanagement: matched_test_ids={sorted(list(matched_test_ids))}")
        except Exception:
            pass
    else:
        # 未选班级时，先不提供试卷选项
        tests = []

    studentsServer = StudentsServer()
    temps = studentsServer.select_sql_all_two_table()
    if selected_class_id:
        temps = [stu for stu in temps if str(getattr(stu, 'ClassId', '')) == selected_class_id]

    datas = []
    # If a specific test is selected, filter each student's records to only include answers
    # that belong to that test (by checking TestQuestionRelation). Otherwise keep the first
    # test record as before.
    if selected_test_id:
        try:
            sel_rel = TestQuestionRelationServer().get_questions_by_test_id(int(selected_test_id))
            sel_ids = {qid for (qid, tp) in sel_rel if tp == 'select'}
            con_ids = {qid for (qid, tp) in sel_rel if tp == 'content'}
        except Exception:
            sel_ids, con_ids = set(), set()

        for stu in temps:
            # For each student's test records, find records that include this test's questions
            matched_records = []
            for rec in getattr(stu, 'StudentsTestRecord', []) or []:
                # Sum grades only for matching answers
                matched_sum = 0
                has_match = False
                for answer in getattr(rec, 'TestContent', []) or []:
                    if getattr(answer, 'TestContentId', None) in con_ids:
                        matched_sum += (getattr(answer, 'Grade', 0) or 0)
                        has_match = True
                for answer in getattr(rec, 'TestSelect', []) or []:
                    if getattr(answer, 'TestSelectId', None) in sel_ids:
                        matched_sum += (getattr(answer, 'Grade', 0) or 0)
                        has_match = True
                if has_match:
                    # clone a minimal record object to hold filtered results
                    new_rec = rec
                    try:
                        new_rec.SumGrade = matched_sum
                    except Exception:
                        pass
                    matched_records.append(new_rec)
            if matched_records:
                # attach only the first matched record for display compatibility with template
                stu.StudentsTestRecord = matched_records
                datas.append(stu)
    else:
        for x in temps:
            if len(x.StudentsTestRecord) > 0:
                # ensure SumGrade is accumulated from TestContent entries (backwards compat)
                try:
                    # reset to 0 then accumulate
                    x.StudentsTestRecord[0].SumGrade = 0
                    for item in x.StudentsTestRecord[0].TestContent:
                        x.StudentsTestRecord[0].SumGrade += (getattr(item, 'Grade', 0) or 0)
                except Exception:
                    pass
                datas.append(x)

    #上一页下一页
    pre_page  = 0
    next_page = 1
    sum_page  = 0

    #获取请求是上一页还是下一页
    type_page = request.args.get("typePage");
    current_page = request.args.get("currentPage");
    sum      =  len(datas)
    sum_page =  (sum + 6 - 1) // 6

    '''
        分页机制
       第一页 0: limit 0 ,6
       第二页 1: limit 6 ,6
       第三页 2: limit 12,6
    '''
    if type_page !=None:
        #处理上一页
        if type_page  ==  "pre" and int(current_page) !=0:
            pre_page = int(current_page) - 1
            next_page = int(current_page)
        #处理下一页
        elif type_page == "next" :
            pre_page = int(current_page)
            next_page = int(current_page) + 1
    else:
        current_page = 0

    obj = PageTool(datas,next_page)
    datas = obj.show()

    return render_template(
        'teacher/testcontentrecordmanagement.html',
        userType = session['logged_type'],
        session  = session['logged_type'],
        datas = datas,
        pre   = pre_page,
        next  = next_page,
        sum   = sum,
        sum_page = sum_page,
        classes = teacher_classes,
        selected_class_id = selected_class_id,
        tests = tests,
        debug_matched_ids = debug_matched_ids,
        selected_test_id = selected_test_id
    )


@app.route('/testcontentrecordmanagementseacher',methods=['GET', 'POST'])
def testcontentrecordmanagementseacher():
    """Renders the about page."""
    startTime = request.form.get("startTime")
    endTime   = request.form.get("endTime")
    selected_class_id = request.form.get("classId") or ""
    selected_test_id = request.form.get("testId") or ""

    try:
        current_user = json.loads(session.get("logged_in", "{}"))
    except Exception:
        current_user = {}
    user_type = session.get('logged_type', "")
    if user_type == "teacher":
        teacher_id = current_user.get("Id", 0)
        teacher_classes = ClassesServer.select_sql_by_teacher(teacher_id) or []
    else:
            teacher_classes = ClassesServer.select_sql_all() or []

    # 与列表页一致：根据班级过滤试卷
    tests = []
    debug_matched_ids = []
    all_tests = TestServer().select_sql_all() or []
    if selected_class_id:
        # Use the same lenient matching strategy as the list view: if any student in the class
        # has a record that contains any question from the test (select/content), count the test.
        studentsServer = StudentsServer()
        recordServer = TestRecordServer()
        students = studentsServer.select_sql_all_two_table()
        class_students = [s for s in students if str(getattr(s, 'ClassId', '')) == selected_class_id]

        matched_test_ids = set()
        for t in all_tests:
            try:
                rels = TestQuestionRelationServer().get_questions_by_test_id(t.Id)
                sel_ids = {qid for (qid, tp) in rels if tp == 'select'}
                con_ids = {qid for (qid, tp) in rels if tp == 'content'}
                if not sel_ids and not con_ids:
                    continue
            except Exception:
                sel_ids, con_ids = set(), set()

            for stu in class_students:
                try:
                    recs = recordServer.select_sql_by_student_id(stu.Id)
                except Exception:
                    recs = []
                found = False
                for rec in recs:
                    for answer in getattr(rec, 'TestContent', []) or []:
                        if getattr(answer, 'TestContentId', None) in con_ids:
                            matched_test_ids.add(t.Id)
                            found = True
                            break
                    if found:
                        break
                    for answer in getattr(rec, 'TestSelect', []) or []:
                        if getattr(answer, 'TestSelectId', None) in sel_ids:
                            matched_test_ids.add(t.Id)
                            found = True
                            break
                    if found:
                        break
                if found:
                    continue

        tests = [t for t in all_tests if t.Id in matched_test_ids]
        debug_matched_ids = sorted(list(matched_test_ids))
        try:
            print(f"[DEBUG] testcontentrecordmanagementseacher: selected_class_id={selected_class_id}, matched_test_ids={sorted(list(matched_test_ids))}")
        except Exception:
            pass

    if startTime !='' and endTime!='':
        t  = pd.to_datetime(request.form.get('startTime').split(" ")[0])
        t1  = pd.to_datetime(request.form.get('endTime').split(" ")[0])
        #t1  = pd.to_datetime(times[0]+' '+times[1])
        #datetime is so error, it need match %%%
        #datetime.datetime.strptime(times[0]+' '+times[1], '%Y-%m-%d %H:%M:%S')
        '''
        #year：日
        #month：月
        #week：周
        #day：日
        #hour
        #minute
        #second
        '''
        startTime =  str(t.year) + "-"+ str(t.month) + "-" + str(t.day) + " " + str(t.hour) + ":"+str(t.minute)+":"+str(t.second)
        endTime   =  str(t1.year) + "-"+ str(t1.month) + "-" + str(t1.day) + " " + str(t1.hour) + ":"+str(t1.minute)+":"+str(t1.second)

    studentsServer = StudentsServer()
    temps = studentsServer.select_sql_all_two_table()
    if selected_class_id:
        temps = [stu for stu in temps if str(getattr(stu, 'ClassId', '')) == selected_class_id]
    datas = []
    for x in temps:
        if len(x.StudentsTestRecord) >0 :
            if startTime !='' and endTime!='':
                #时间大小比较
                startTime_s1_1  =  time.strptime(startTime, '%Y-%m-%d %H:%M:%S')
                endTime_s2_1    =  time.strptime(endTime,   '%Y-%m-%d %H:%M:%S')
                temps =  x.StudentsTestRecord[0].RocordTime.strftime('%Y-%m-%d %H:%M:%S')
                print(startTime_s1_1 < time.strptime(temps,'%Y-%m-%d %H:%M:%S'))
                print(endTime_s2_1   < time.strptime(temps,'%Y-%m-%d %H:%M:%S'))
                if (startTime_s1_1 < time.strptime(temps,'%Y-%m-%d %H:%M:%S')) == True and (endTime_s2_1   < time.strptime(temps,'%Y-%m-%d %H:%M:%S')) == False:
                    for item in x.StudentsTestRecord[0].TestContent:
                        x.StudentsTestRecord[0].SumGrade+= item.Grade
                    datas.append(x)
            else:
                for item in x.StudentsTestRecord[0].TestContent:
                    x.StudentsTestRecord[0].SumGrade+= item.Grade
                datas.append(x)


    return render_template(
        'teacher/testcontentrecordmanagement.html',
        userType = session['logged_type'],
        session  = session['logged_type'],
        datas = datas,
        seacher  = "123",
        classes = teacher_classes,
        selected_class_id = selected_class_id,
        tests = tests,
        debug_matched_ids = debug_matched_ids,
        selected_test_id = selected_test_id
    )


@app.route('/testcontentrecordmanagementexport', methods=['GET'])
def testcontentrecordmanagementexport():
    """
    导出规则：
    - 当提供 testId 时，导出该场试卷的全部考生（若为老师账号，则仅限其绑定班级内的学生）。
    - 否则要求提供 classId，仅导出该班级的统计。
    输出为“宽表”：每个学生一行，列为试题成绩与总成绩。
    成绩聚合策略：同一题目取多次作答的最高分。
    """
    test_id = request.args.get("testId")
    class_id = request.args.get("classId")

    if not session.get('logged_in'):
        return redirect("/login")

    try:
        current_user = json.loads(session.get("logged_in", "{}"))
    except Exception:
        current_user = {}
    user_type = session.get('logged_type', "")

    # 老师权限范围：限制在本人绑定的班级
    allowed_class_ids = None
    if user_type == "teacher":
        teacher_id = current_user.get("Id", 0)
        teacher_classes = ClassesServer.select_sql_by_teacher(teacher_id) or []
        allowed_class_ids = {str(cls.Id) for cls in teacher_classes}

    studentsServer = StudentsServer()
    recordServer = TestRecordServer()
    all_students = studentsServer.select_sql_all_two_table()

    # 计算题目列排序规则
    type_order = {"编程": 0, "选择": 1}
    def sort_key(col_name: str):
        try:
            prefix, tail = col_name.split('-', 1)
            num = int(tail)
        except Exception:
            prefix, num = col_name, 1 << 30
        return (type_order.get(prefix, 99), num, col_name)

    # 如果是试卷导出，先取出该试卷的题目集合
    specific_cols = None
    if test_id:
        relations = TestQuestionRelationServer().get_questions_by_test_id(test_id)
        select_ids = {qid for (qid, qtype) in relations if qtype == 'select'}
        content_ids = {qid for (qid, qtype) in relations if qtype == 'content'}
        specific_cols = set()
        for cid in content_ids:
            specific_cols.add(f"编程-{cid}")
        for sid in select_ids:
            specific_cols.add(f"选择-{sid}")

    all_question_cols = set()
    student_rows = []

    def record_matches_test(record, select_ids, content_ids):
        # 判断一次作答记录是否对应于指定试卷（题目集合完全一致即可）
        try:
            r_select = {getattr(a, 'TestSelectId', 0) for a in (getattr(record, 'TestSelect', []) or [])}
            r_content = {getattr(a, 'TestContentId', 0) for a in (getattr(record, 'TestContent', []) or [])}
            return (r_select == select_ids) and (r_content == content_ids)
        except Exception:
            return False

    for stu in all_students:
        # 权限过滤（老师仅导出自己班级的学生）
        if allowed_class_ids is not None:
            if str(getattr(stu, 'ClassId', '')) not in allowed_class_ids:
                continue

        # 若提供了classId，则始终按班级过滤（无论是否选择试卷）
        if class_id and str(getattr(stu, 'ClassId', '')) != class_id:
            continue

        student_no = (stu.Card or "").strip() or stu.UserName
        student_name = (stu.Name or "").strip() or stu.UserName
        records = recordServer.select_sql_by_student_id(stu.Id)

        row = {"学号": student_no, "姓名": student_name}
        filled_any = False

        # 遍历学生所有作答记录
        for record in records:
            # 若为试卷导出：仅统计与该试卷题目集合完全一致的记录
            if test_id:
                if not record_matches_test(record, select_ids, content_ids):
                    continue

            # 编程题
            for answer in getattr(record, 'TestContent', []) or []:
                col = f"编程-{getattr(answer, 'TestContentId', 0)}"
                if specific_cols and col not in specific_cols:
                    continue
                grade = getattr(answer, 'Grade', 0) or 0
                prev = row.get(col)
                row[col] = max(prev, grade) if prev is not None else grade
                all_question_cols.add(col)
                filled_any = True
            # 选择题
            for answer in getattr(record, 'TestSelect', []) or []:
                col = f"选择-{getattr(answer, 'TestSelectId', 0)}"
                if specific_cols and col not in specific_cols:
                    continue
                grade = getattr(answer, 'Grade', 0) or 0
                prev = row.get(col)
                row[col] = max(prev, grade) if prev is not None else grade
                all_question_cols.add(col)
                filled_any = True

        if filled_any:
            student_rows.append(row)

    # 列顺序：若指定试卷，则按试卷的题目集合排序；否则按出现顺序规则排序
    if specific_cols is not None:
        ordered_cols = sorted(specific_cols, key=sort_key)
    else:
        ordered_cols = sorted(all_question_cols, key=sort_key)

    final_cols = ["学号", "姓名"] + ordered_cols + ["总成绩"]
    for r in student_rows:
        r["总成绩"] = sum((r.get(c, 0) or 0) for c in ordered_cols)

    df = pd.DataFrame(student_rows, columns=final_cols)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if test_id:
        xlsx_filename = f"test_{test_id}_statistics_{timestamp}.xlsx"
    else:
        if not class_id:
            return redirect("/testcontentrecordmanagement")
        xlsx_filename = f"class_{class_id}_statistics_{timestamp}.xlsx"

    # 兼容性导出：优先使用 openpyxl → 其次 xlsxwriter → 最后回退 CSV，避免依赖缺失导致 500
    output = BytesIO()
    engine = None
    try:
        import openpyxl  # noqa: F401
        engine = 'openpyxl'
    except Exception:
        try:
            import xlsxwriter  # noqa: F401
            engine = 'xlsxwriter'
        except Exception:
            engine = None

    if engine:
        try:
            with pd.ExcelWriter(output, engine=engine) as writer:
                df.to_excel(writer, index=False, sheet_name='统计结果')
            output.seek(0)
            try:
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=xlsx_filename
                )
            except TypeError:
                # Flask<2.0 兼容参数
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    attachment_filename=xlsx_filename
                )
        except Exception:
            # 写入失败时继续走 CSV 回退
            pass

    # CSV 回退：无需额外依赖，确保不抛 500
    csv_bytes = df.to_csv(index=False).encode('utf-8-sig')
    csv_io = BytesIO(csv_bytes)
    csv_filename = f"class_{class_id}_statistics_{timestamp}.csv"
    try:
        return send_file(
            csv_io,
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            download_name=csv_filename
        )
    except TypeError:
        return send_file(
            csv_io,
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            attachment_filename=csv_filename
        )


@app.route('/gettestcontentrecordanswer',methods=['GET', 'POST'])
def gettestcontentrecordanswer():
    """Renders the about page."""
    testRecordId = request.args.get("testRecordId")

    testRecord             = TestRecordServer().select_sql_by_id(testRecordId)
    testRecordAnswer       = TestRecordAnswerServer().select_sql_all_test_record_id(testRecordId)
    testRecordAnswerSelect = TestRecordAnswerSelectServer().select_sql_all_test_record_id(testRecordId)

    jsons = "["

    jsons+= "{"
    jsons+= "\"times\":\""+  testRecord.RocordTime.strftime('%Y-%m-%d %H:%M:%S')+"\""
    jsons+= "},"

    for item in testRecordAnswer:
        jsons+= "{"
        jsons+= "\"content\":\""+item.TestContent.Content.replace(" ","").replace("\r\n","").replace("\n","")+"\","
        jsons+= "\"grade\":\""+str(item.TestContent.Grade)+"\","
        jsons+= "\"answerContent\":\""+item.AnswerContent.replace(" ","").replace("\r\n","").replace("\n","").replace("\"","")+"\","
        jsons+= "\"AnswerGrade\":\""+str(item.Grade)+"\""
        jsons+= "},"

    for item in testRecordAnswerSelect:
        a = "A:"+item.TestSelect.AnswerA + " "
        b = "B:"+item.TestSelect.AnswerB + " "
        c = "C:"+item.TestSelect.AnswerC + " "
        d = "D:"+item.TestSelect.AnswerD + " "

        jsons+= "{"
        jsons+= "\"contentSelect\":\""+item.TestSelect.Content.replace(" ","").replace("\r\n","").replace("\n","")+"\","
        jsons+= "\"contentOption\":\""+a+b+c+d+"\","
        jsons+= "\"grade\":\""+str(item.Grade)+"\","
        jsons+= "\"answerContent\":\""+item.AnswerSelect.replace(" ","").replace("\r\n","").replace("\n","").replace("\"","")+"\","
        jsons+= "\"AnswerGrade\":\""+str(item.Grade)+"\""
        jsons+= "},"

    jsons = jsons[0:(len(jsons)-1)]
    jsons += "]"
    return jsonify(jsons)



@app.route('/testcontentrecordmanagementdelete',methods=['GET', 'POST'])
def testcontentrecordmanagementdelete():
    """Renders the about page."""
    id = request.args.get("id")
    #先删除test_record_answer_content
    #在删除test_record
    testRecordAnswerServer = TestRecordAnswerServer()
    testRecordAnswerServer.delete_sql_by_testRecordId(id)
    testRecordServer = TestRecordServer()
    testRecordServer.delete_sql(id)
    return redirect("/testcontentrecordmanagement")