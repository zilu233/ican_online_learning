"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template,jsonify,request,session,redirect
from OnlineJudgeSystem import app
from OnlineJudgeSystem.model.Students import StudentsServer,Students
from OnlineJudgeSystem.model.PageTool import PageTool
import json
from OnlineJudgeSystem.model.Admins import Admins,AdminsServer
from OnlineJudgeSystem.model.Students import Students, StudentsServer
from OnlineJudgeSystem.model.Teachers import Teachers, TeachersServer
from OnlineJudgeSystem.model.Schools import SchoolsServer
from OnlineJudgeSystem.model.Classes import ClassesServer

from OnlineJudgeSystem.model.TestContent import TestContentServer, TestContent
from OnlineJudgeSystem.model.TestSelect import TestSelect, TestSelectServer

from OnlineJudgeSystem.model.TestRecord import TestRecord,  TestRecordServer
from OnlineJudgeSystem.model.TestRecordAnswerSelect import TestRecordAnswerSelect,  TestRecordAnswerSelectServer

@app.route('/adminindex')
def adminindex():

    users = json.loads(session["logged_in"])
    user_type = session['logged_type']

    echart_json = ""
    datas_student = []
    datas_test    = []
    datas_count   = ""

    studentsServer    = StudentsServer()
    datas_student     = studentsServer.select_sql_all()
    teachersServer    = TeachersServer()
    testContentServer = TestContentServer()
    testSelectServer  = TestSelectServer()
    datas_test        = testContentServer.select_sql_all()
    testRecordServer  = TestRecordServer()
    testRecordAnswerSelect  = TestRecordAnswerSelectServer()
    test_record_datas = testRecordServer.select_sql_all()
    #正确率和错误率
    right_result = 0
    error_result = 0

    if user_type == 'admin':

        datas_count += "["
        datas_count += str(studentsServer.select_sql_all_count())
        datas_count += ","
        datas_count += str(testContentServer.select_sql_all_count() + testSelectServer.select_sql_all_count())
        datas_count += ","
        datas_count += str(testRecordServer.select_sql_all_count()  + testRecordAnswerSelect.select_sql_all_count())
        datas_count += ","
        datas_count += str(teachersServer.select_sql_all_count())
        datas_count += ","
        for item in test_record_datas:
            for x in item.TestContent:
                if x.Grade != 0:
                    right_result = right_result+1
                else:
                    error_result = error_result+1
        datas_count += str(right_result)
        datas_count += ","
        datas_count += str(error_result)
        datas_count += "]"
        pass
    else:

        datas_count += "["
        datas_count += str(studentsServer.select_sql_all_count())
        datas_count += ","
        datas_count += str(testContentServer.select_sql_all_count() + testSelectServer.select_sql_all_count())
        datas_count += ","
        datas_count += str(testRecordServer.select_sql_all_count()  + testRecordAnswerSelect.select_sql_all_count())
        datas_count += ","
        datas_count += str(teachersServer.select_sql_all_count())
        datas_count += ","
        for item in test_record_datas:
            for x in item.TestContent:
                if x.Grade != 0:
                    right_result = right_result+1
                else:
                    error_result = error_result+1
        datas_count += str(right_result)
        datas_count += ","
        datas_count += str(error_result)
        datas_count += "]"

    return render_template(
        'admin/adminIndex.html',
        title='首页',
        userType = user_type,
        session  = user_type,
        datas_student = datas_student,
        datas_test = datas_test,
        datas_count = datas_count
    )

    return render_template(
        'admin/adminIndex.html',
        userType = session['logged_type'],
        session  = session['logged_type'],
    )



@app.route('/usermanagement')
def usermanagement():
    """Renders the home page."""
    if session.get('logged_type') != 'admin':
        return redirect('/login')
    studentsServer = StudentsServer()
    data_list = studentsServer.select_sql_all()

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
        'admin/usermanagement.html',
        userType = session['logged_type'],
        session  = session['logged_type'],
        datas = data_list,
        pre   = pre_page,
        next  = next_page,
        sum   = sum,
        sum_page = sum_page
    )



@app.route('/usermanagementadd',methods=['GET', 'POST'])
def usermanagementadd():
    """Renders the contact page."""
    if session.get('logged_type') != 'admin':
        return redirect('/login')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        pwd = request.form.get('pwd', '').strip()
        name = request.form.get('name', '').strip()
        # 学号：兼容旧字段名 card
        card = (request.form.get('student_no', '') or request.form.get('card', '')).strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        school_id = request.form.get('school_id', '').strip()
        class_id = request.form.get('class_id', '').strip()
        status = request.form.get('status', '1').strip()
        classes = request.form.get('classes', '').strip()
        # 新增：支持手动输入学校/班级名称
        school_name = request.form.get('school_name', '').strip()
        class_name = request.form.get('class_name', '').strip()

        if not (username and pwd and name and card and phone and (school_id or school_name) and (class_id or class_name)):
            return redirect("/usermanagementadd")

        students = Students()
        students.UserName = username
        students.PWD = pwd
        students.Name = name
        students.Card = card
        students.Phone = phone
        students.Address = address
        students.Status = int(status) if status else 1

        try:
            students.SchoolId = int(school_id)
        except (TypeError, ValueError):
            students.SchoolId = 0
        try:
            students.ClassId = int(class_id)
        except (TypeError, ValueError):
            students.ClassId = 0

        # 若未提供ID则根据名称解析
        if students.SchoolId == 0 and school_name:
            try:
                for s in SchoolsServer.select_sql_all(status=1):
                    if str(s.SchoolName).strip() == school_name:
                        students.SchoolId = s.Id
                        break
            except Exception:
                pass
        if students.ClassId == 0 and class_name and students.SchoolId:
            try:
                for c in ClassesServer.select_sql_all(school_id=students.SchoolId, status=1):
                    if str(c.ClassName).strip() == class_name:
                        students.ClassId = c.Id
                        break
            except Exception:
                pass

        # classes 文本优先使用手工输入
        if not classes and class_name:
            classes = class_name
        if not classes and students.ClassId:
            cls_info = ClassesServer.select_sql_by_id(students.ClassId)
            classes = cls_info.ClassName if cls_info else ""
        students.Classes = classes

        studentsServer = StudentsServer()
        data = studentsServer.select_sql_login(students)

        # 校验：必须解析到有效的学校与班级ID
        if not students.SchoolId or not students.ClassId:
            return redirect("/usermanagementadd")

        if data is None:
            studentsServer.insert_sql(students)
            if students.ClassId:
                ClassesServer.update_student_count(students.ClassId)
            return redirect("/usermanagement")
        return redirect("/usermanagementadd")
    else:
        return render_template(
            'admin/usermanagementadd.html',
            userType = session['logged_type'],
            session  = session['logged_type'],
            title='学生添加',
            schools = SchoolsServer.select_sql_all(status=1)
        )


@app.route('/usermanagementedit',methods=['GET', 'POST'])
def usermanagementedit():
    """Renders the about page."""
    if session.get('logged_type') != 'admin':
        return redirect('/login')
    if request.method == 'POST':
        id         =  request.form.get('Id')
        try:
            student_id = int(id)
        except (TypeError, ValueError):
            return redirect("/usermanagement")
        username    =  request.form.get('username', '').strip()
        pwd       =  request.form.get('pwd', '').strip()
        classes    =  request.form.get('classes', '').strip()
        name    =  request.form.get('name', '').strip()
        # 学号：兼容旧字段名 card
        card    =  (request.form.get('student_no', '') or request.form.get('card', '')).strip()
        phone    =  request.form.get('phone', '').strip()
        address    =  request.form.get('address', '').strip()
        school_id = request.form.get('school_id', '').strip()
        class_id = request.form.get('class_id', '').strip()
        status = request.form.get('status', '1').strip()
        # 新增：支持手工输入学校/班级名称
        school_name = request.form.get('school_name', '').strip()
        class_name = request.form.get('class_name', '').strip()

        # 仅要求提供学校；班级可选（可留空）
        if not (username and pwd and name and card and phone and (school_id or school_name)):
            return redirect("/usermanagementedit?id=" + str(id)) 
        studentsServer = StudentsServer()
        existing = studentsServer.select_sql_by_id(student_id)

        students = Students()
        students.Id  =   student_id
        students.UserName = username
        students.PWD = pwd
        students.Classes = classes
        students.Name = name
        students.Card = card
        students.Phone = phone
        students.Address = address
        students.Status = int(status) if status else 1

        try:
            students.SchoolId = int(school_id)
        except (TypeError, ValueError):
            students.SchoolId = 0
        try:
            students.ClassId = int(class_id)
        except (TypeError, ValueError):
            students.ClassId = 0

        # 优先按名称解析（不区分大小写，去前后空格）；若解析成功则覆盖传入的ID
        try:
            if school_name:
                key = str(school_name).strip().lower()
                for s in SchoolsServer.select_sql_all(status=1):
                    if str(getattr(s, 'SchoolName', '')).strip().lower() == key:
                        students.SchoolId = s.Id
                        break
        except Exception:
            pass
        try:
            if class_name and students.SchoolId:
                keyc = str(class_name).strip().lower()
                for c in ClassesServer.select_sql_all(school_id=students.SchoolId, status=1):
                    if str(getattr(c, 'ClassName', '')).strip().lower() == keyc:
                        students.ClassId = c.Id
                        break
        except Exception:
            pass

        # 学校变更后，若现有班级不属于该学校，则清空班级
        try:
            if students.ClassId:
                cls_info_chk = ClassesServer.select_sql_by_id(students.ClassId)
                if (not cls_info_chk) or getattr(cls_info_chk, 'SchoolId', 0) != students.SchoolId:
                    students.ClassId = 0
        except Exception:
            pass

        # classes 文本优先使用手工输入
        if not classes and class_name:
            classes = class_name
        students.Classes = classes

        if not students.Classes and students.ClassId:
            cls_info = ClassesServer.select_sql_by_id(students.ClassId)
            students.Classes = cls_info.ClassName if cls_info else ""

        try:
            old_class_id = getattr(existing, 'ClassId', 0)
        except Exception:
            old_class_id = 0
        # 校验：允许不选择班级，但必须解析到有效学校
        if not students.SchoolId:
            return redirect("/usermanagementedit?id=" + str(id))
        # 保存更新
        studentsServer.update_sql(students)
        if old_class_id and old_class_id != students.ClassId:
            ClassesServer.update_student_count(old_class_id)
        if students.ClassId:
            ClassesServer.update_student_count(students.ClassId)

        return redirect("/usermanagement")      
        
    else:
        id = request.args.get("id")
        studentsServer = StudentsServer()
        data = studentsServer.select_sql_by_id(id)

        return render_template(
            'admin/usermanagementedit.html',
            title='About',
            userType = session['logged_type'],
            session  = session['logged_type'],
            data = data,
            schools = SchoolsServer.select_sql_all(status=1),
            available_classes = ClassesServer.select_sql_by_school(data.SchoolId, status=1) if data.SchoolId else [],
        )


@app.route('/usermanagementdelete',methods=['GET', 'POST'])
def usermanagementdelete():
    """Renders the about page."""
    if session.get('logged_type') != 'admin':
        return redirect('/login')
    id         =  request.args.get('id')
    #将用户请求转发给相应的Model
    studentsServer = StudentsServer()
    studentsServer.delete_sql(id)

    return redirect("/usermanagement")     