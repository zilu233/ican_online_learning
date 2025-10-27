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
from OnlineJudgeSystem.model.Classes import ClassesServer, Classes
from OnlineJudgeSystem.model.Schools import SchoolsServer, Schools
from OnlineJudgeSystem.model.TestContent import TestContentServer, TestContent
from OnlineJudgeSystem.model.TestRecord import TestRecord,  TestRecordServer
try:
    from .cacher import cache
except Exception:
    def cache(*args, **kwargs):
        # 缺省空实现，避免因缺少 cacher 导致启动失败
        return None

def _load_active_classes():
    """获取当前可选的班级列表，用于注册页面显示。"""
    try:
        return ClassesServer.select_sql_all(status=1)
    except Exception:
        return []


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

            if data is not None:
                session['logged_in'] = data.to_json()
                session['logged_type'] = "admin"
                return redirect("/adminindex")
            else:
                return render_template('loginAndRegister.html', title='登录', error='登录失败，请重新输入', classes=_load_active_classes())

        elif types == "1":
            teachers = Teachers()
            teachers.UserName = username
            teachers.PWD      = pwd
            teachersServer    = TeachersServer()
            data = teachersServer.select_sql_login(teachers)

            if data is not None:
                session['logged_in'] = data.to_json()
                session['logged_type'] = "teacher"
                return redirect("/home")
            else:
                return render_template('loginAndRegister.html', title='登录', error='登录失败，请重新输入', classes=_load_active_classes())

        elif types == "2":
            students = Students()
            students.UserName = username
            students.PWD   = pwd
            studentsServer = StudentsServer()
            data = studentsServer.select_sql_login(students)

            if data is not None:
                session['logged_in'] = data.to_json()
                session['logged_type'] = "student"
                return redirect("/home")
            else:
                return render_template('loginAndRegister.html', title='登录', error='登录失败，请重新输入', classes=_load_active_classes())

        else:

            return render_template('loginAndRegister.html', title='登录', error='未知用户类型', classes=_load_active_classes())

    else:
        return render_template(
            'loginAndRegister.html',
            title='登录',
            classes=_load_active_classes()
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
        # 学号：兼容旧字段名 card
        card      =  (request.form.get('student_no') or request.form.get('card'))
        phone     =  request.form.get('phone')
        # 兼容旧前端：旧版仍可能提交 address，这里作为班级的别名处理
        if username == '' or pwd == '' or name == '' or card == '' or phone == '':
            return render_template('loginAndRegister.html', title='注册', msg="请完整填写注册信息", classes=_load_active_classes())

        if user_type == "0":
            teachers = Teachers()
            teachers.UserName = username
            teachers.PWD   = pwd
            teachers.Name  = name
            teachers.Card = card
            teachers.Phone = phone
            # 不再采集住址；如果需要显示班级，先写入兼容字段 Classes
            teachers.Classes = ""
            teachersServer = TeachersServer()
            data = teachersServer.select_sql_exist(teachers)

            import sys
            if data is None:
                print("[DEBUG] teachersServer.insert_sql(teachers) called", file=sys.stderr)
                teachersServer.insert_sql(teachers)
                print("[DEBUG] teachersServer.select_sql_login(teachers) called", file=sys.stderr)
                data = teachersServer.select_sql_login(teachers)
                print(f"[DEBUG] select_sql_login result: {data}", file=sys.stderr)
                if data is not None:
                    session['logged_in'] = data.to_json()
                    session['logged_type'] = "teacher"
                    return redirect("/home")
                else:
                    print("[ERROR] 注册后 select_sql_login 返回 None", file=sys.stderr)
                    return render_template('loginAndRegister.html', title="注册", msg="注册失败，数据写入异常，请重试", classes=_load_active_classes())
            else:
                print("[ERROR] 用户名已存在", file=sys.stderr)
                return render_template('loginAndRegister.html', title="注册", msg="用户名已存在，请更换用户名", classes=_load_active_classes())

        else:
            students = Students()
            students.UserName = username
            students.PWD   = pwd
            students.Name  = name
            students.Card = card
            students.Phone = phone
            # 不再采集住址；保存班级到兼容字段 Classes
            class_id = request.form.get('class_id')  # 兼容旧前端
            class_name_input = (request.form.get('class_name') or '').strip()

            class_info = None
            if class_id:
                # 旧逻辑：下拉选择的班级ID
                try:
                    class_id_int = int(class_id)
                except ValueError:
                    return render_template('loginAndRegister.html', title="注册", msg="班级选择无效", classes=_load_active_classes())
                class_info = ClassesServer.select_sql_by_id(class_id_int)
                if class_info is None:
                    return render_template('loginAndRegister.html', title="注册", msg="所选班级不存在", classes=_load_active_classes())
            else:
                # 新逻辑：手动输入班级名称（精确匹配唯一激活班级）
                if not class_name_input:
                    return render_template('loginAndRegister.html', title="注册", msg="学生注册必须填写班级名称", classes=_load_active_classes())
                all_active = ClassesServer.select_sql_all(status=1)
                key = class_name_input.strip().lower()
                candidates = [c for c in all_active if (c.ClassName or '').strip().lower() == key]
                if len(candidates) == 0:
                    # 未找到：自动创建班级（无需管理员或老师审核）
                    # 1) 选择默认学校：优先取第一个启用的学校
                    schools_enabled = SchoolsServer.select_sql_all(status=1)
                    default_school_id = 0
                    if schools_enabled:
                        default_school_id = int(schools_enabled[0].Id)
                    # 若没有启用学校，则自动创建一个“默认学校”并启用
                    if not default_school_id:
                        try:
                            # 若已存在同代码学校则直接复用
                            existing = SchoolsServer.select_sql_by_code('default-auto')
                            if existing:
                                default_school_id = int(existing.Id)
                            else:
                                _sch = Schools()
                                _sch.SchoolName = '默认学校'
                                _sch.SchoolCode = 'default-auto'
                                _sch.Status = 1
                                default_school_id = int(SchoolsServer.insert_sql(_sch))
                        except Exception:
                            default_school_id = 0

                    # 2) 并发去重：若目标学校中已存在同名班级则直接复用
                    try:
                        if default_school_id and ClassesServer.check_name_exists(default_school_id, class_name_input):
                            # 读取该学校启用的同名班级
                            school_classes = ClassesServer.select_sql_all(school_id=default_school_id, status=1)
                            same = [c for c in school_classes if (c.ClassName or '').strip().lower() == key]
                            if same:
                                class_info = same[0]
                            else:
                                class_info = None
                        else:
                            class_info = None
                    except Exception:
                        class_info = None

                    # 3) 真的没有则创建
                    if class_info is None:
                        if not default_school_id:
                            return render_template('loginAndRegister.html', title="注册", msg="系统未配置学校且创建默认学校失败，请联系管理员", classes=_load_active_classes())
                        try:
                            new_cls = Classes()
                            new_cls.SchoolId = default_school_id
                            new_cls.ClassName = class_name_input.strip()
                            new_cls.ClassCode = ''
                            new_cls.Grade = ''
                            new_cls.TeacherId = 0
                            new_cls.Description = '学生注册自动创建'
                            new_cls.Status = 1
                            new_id = ClassesServer.insert_sql(new_cls)
                            # 读取刚创建的班级完整信息
                            class_info = ClassesServer.select_sql_by_id(int(new_id)) if new_id else None
                        except Exception:
                            class_info = None

                    if class_info is None:
                        return render_template('loginAndRegister.html', title="注册", msg="自动创建班级失败，请稍后重试或联系管理员", classes=_load_active_classes())
                if len(candidates) > 1:
                    return render_template('loginAndRegister.html', title="注册", msg="存在多个同名班级，请联系老师提供更准确的班级信息（或稍后由老师在班级管理中绑定）", classes=_load_active_classes())
                # 若之前已创建得到 class_info，则保留；否则使用唯一候选
                if 'class_info' not in locals() or class_info is None:
                    class_info = candidates[0]

            students.Classes = class_info.ClassName
            students.ClassId = class_info.Id
            students.SchoolId = class_info.SchoolId
            studentsServer = StudentsServer()
            data = studentsServer.select_sql_exist(students)

            import sys
            if data is None:
                print("[DEBUG] studentsServer.insert_sql(students) called", file=sys.stderr)
                studentsServer.insert_sql(students)
                try:
                    ClassesServer.update_student_count(class_info.Id)
                except Exception:
                    print("[WARN] 更新班级学生人数失败", file=sys.stderr)
                print("[DEBUG] studentsServer.select_sql_login(students) called", file=sys.stderr)
                data = studentsServer.select_sql_login(students)
                print(f"[DEBUG] select_sql_login result: {data}", file=sys.stderr)
                if data is not None:
                    session['logged_in'] = data.to_json()
                    session['logged_type'] = "student"
                    return redirect("/home")
                else:
                    print("[ERROR] 注册后 select_sql_login 返回 None", file=sys.stderr)
                    return render_template('loginAndRegister.html', title="注册", msg="注册失败，数据写入异常，请重试", classes=_load_active_classes())
            else:
                print("[ERROR] 用户名已存在", file=sys.stderr)
                return render_template('loginAndRegister.html', title="注册", msg="用户名已存在，请更换用户名", classes=_load_active_classes())
    else:
        return render_template(
            'loginAndRegister.html',
            title="注册",   
            classes=_load_active_classes()
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





