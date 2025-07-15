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
    if request.method == 'POST':
        username    =  request.form.get('username')
        pwd       =  request.form.get('pwd')
        classes    =  request.form.get('classes')
        name    =  request.form.get('name')
        card    =  request.form.get('card')
        phone    =  request.form.get('phone')
        address    =  request.form.get('address')

        if username == '' or pwd == '' or name == '' or card == '' or phone == '' or address =='':
            return redirect("admin/usermanagementadd") 
        else:
            #将用户请求转发给相应的Model
            students = Students()
            students.UserName = username
            students.PWD   = pwd
            students.Classes = classes
            students.Name  = name
            students.Card = card
            students.Phone = phone
            students.Address = address
            studentsServer = StudentsServer()
            data = studentsServer.select_sql_login(students)

            if data == None :           
                studentsServer.insert_sql(students);
                return redirect("/usermanagement")
            return redirect("/usermanagementadd")          
    else:
        return render_template(
            'admin/usermanagementadd.html',
            userType = session['logged_type'],
            session  = session['logged_type'],
            title='学生添加',
        )


@app.route('/usermanagementedit',methods=['GET', 'POST'])
def usermanagementedit():
    """Renders the about page."""
    if request.method == 'POST':
        id         =  request.form.get('Id')
        username    =  request.form.get('username')
        pwd       =  request.form.get('pwd')
        classes    =  request.form.get('classes')
        name    =  request.form.get('name')
        card    =  request.form.get('card')
        phone    =  request.form.get('phone')
        address    =  request.form.get('address')
        
        if username == '' or pwd == '' or name == '' or card == '' or phone == '' or address =='':
            return redirect("/usermanagementedit") 
        else:
            #将用户请求转发给相应的Model
            studentsServer = StudentsServer()
            data = studentsServer.select_sql_by_id(id)
            students = Students()
            students.Id  =   id
            students.UserName = username
            students.PWD = pwd
            students.Classes = classes
            students.Name = name
            students.Card = card
            students.Phone = phone
            students.Address = address
            studentsServer.update_sql(students)

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
        )


@app.route('/usermanagementdelete',methods=['GET', 'POST'])
def usermanagementdelete():
    """Renders the about page."""
    id         =  request.args.get('id')
    #将用户请求转发给相应的Model
    studentsServer = StudentsServer()
    studentsServer.delete_sql(id)

    return redirect("/usermanagement")     