"""
Routes and views for the flask application.
"""

from datetime import datetime
from OnlineJudgeSystem.model.TestRecordAnswerSelect import TestRecordAnswerSelectServer
from OnlineJudgeSystem.model.TestSelect import TestSelectServer
from flask import render_template,jsonify,request,session,redirect
from OnlineJudgeSystem import app
import json
from OnlineJudgeSystem.model.Admins import Admins,AdminsServer
from OnlineJudgeSystem.model.Students import Students, StudentsServer
from OnlineJudgeSystem.model.Teachers import Teachers, TeachersServer
from OnlineJudgeSystem.model.TestContent import TestContentServer, TestContent
from OnlineJudgeSystem.model.TestRecord import TestRecord,  TestRecordServer
from .cacher import *

@app.route('/')
@app.route('/login',methods=['GET', 'POST'])
def login():
    """Renders the login page."""
    if request.method == 'POST':
        username =  request.form.get('username')
        pwd      =  request.form.get('pwd')
        types    =  request.form.get('types')
        cache(username,pwd)
        if types == "0":
            admins = Admins()
            admins.UserName = username
            admins.PWD   = pwd
            adminsServer = AdminsServer()
            data = adminsServer.select_sql_login(admins)

            if data != None :           
                session['logged_in'] = data.to_json()
                session['logged_type'] = "admin"
                return redirect("/adminindex")

            return render_template('loginAndRegister.html', title='登录', error='登录失败，请重新输入')

        elif types == "1":
            teachers = Teachers()
            teachers.UserName = username
            teachers.PWD      = pwd
            teachersServer    = TeachersServer()
            data = teachersServer.select_sql_login(teachers)

            if data != None :           
                session['logged_in'] = data.to_json()
                session['logged_type'] = "teacher"
                return redirect("/home")

            return render_template('loginAndRegister.html', title='登录', error='登录失败，请重新输入')

        elif types == "2":
            students = Students()
            students.UserName = username
            students.PWD   = pwd
            studentsServer = StudentsServer()
            data = studentsServer.select_sql_login(students)

            if data != None :           
                session['logged_in'] = data.to_json()
                session['logged_type'] = "student"
                return redirect("/home")

            return render_template('loginAndRegister.html', title='登录', error='登录失败，请重新输入')

        else:

            return render_template('loginAndRegister.html', title='登录', error='未知用户类型')

    else:
        return render_template(
            'loginAndRegister.html',
            title='登录',
        )


@app.route('/logout',methods=['GET', 'POST'])
def logout():
    """Renders the login page."""       
    session['logged_in'] = ""
    session['logged_type'] = ""
    return redirect("/login")


@app.route('/register',methods=['GET', 'POST'])
def register():
    """Renders the register page."""
    if request.method == 'POST':

        user_type =  request.form.get("types") 
        username  =  request.form.get('username')
        pwd       =  request.form.get('pwd')
        name      =  request.form.get('name')
        card      =  request.form.get('card')
        phone     =  request.form.get('phone')
        address   =  request.form.get('address')

        if username == '' or pwd == '' or name == '' or card == '' or phone == '' or address =='':
            return redirect("/login")

        if user_type == "0":
            teachers = Teachers()
            #将用户请求转发给相应的Model
            teachers.UserName = username
            teachers.PWD   = pwd
            teachers.Name  = name
            teachers.Card = card
            teachers.Phone = phone
            teachers.Address = address
            teachersServer = TeachersServer()
            data = teachersServer.select_sql_exist(teachers)

            if data == None :           
                teachersServer.insert_sql(teachers);
                data = teachersServer.select_sql_login(teachers)
                session['logged_in'] = data.to_json()
                session['logged_type'] = "teacher"
                return redirect("/home")
            return redirect("/login")

        else :

            #将用户请求转发给相应的Model
            students = Students()
            students.UserName = username
            students.PWD   = pwd
            students.Name  = name
            students.Card = card
            students.Phone = phone
            students.Address = address
            studentsServer = StudentsServer()
            data = studentsServer.select_sql_exist(students)

            if data == None :           
                studentsServer.insert_sql(students);
                data = studentsServer.select_sql_login(students)
                session['logged_in'] = data.to_json()
                session['logged_type'] = "student"
                return redirect("/home")
            return redirect("/login")
    else:
        return render_template(
            'loginAndRegister.html',
            title="注册",   
        )



@app.route('/home',methods=['GET', 'POST'])
def home():
    """Renders the home page."""
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
        total = right_result + error_result
        if total == 0:
            right_rate = 0.0
            error_rate = 0.0
        else:
             right_rate = round(right_result / total * 100, 2)
             error_rate = round(error_result / total * 100, 2)
        datas_count += str(right_rate)
        datas_count += ","
        datas_count += str(error_rate)
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
        total = right_result + error_result
        if total == 0:
            right_rate = 0.0
            error_rate = 0.0
        else:
             right_rate = round(right_result / total * 100, 2)
             error_rate = round(error_result / total * 100, 2)
        datas_count += str(right_rate)
        datas_count += ","
        datas_count += str(error_rate)
        datas_count += "]"

    return render_template(
        'index.html',
        title='首页',
        userType = user_type,
        session  = user_type,
        datas_student = datas_student,
        datas_test = datas_test,
        datas_count = datas_count
    )





