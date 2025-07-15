

"""
Routes and views for the flask application.
"""

from datetime import datetime

from flask import render_template,jsonify,request,session,redirect
from OnlineJudgeSystem import app

from OnlineJudgeSystem.model.Students import StudentsServer, Students
from OnlineJudgeSystem.model.TestSelect import TestSelect,TestSelectServer
from OnlineJudgeSystem.model.TestContent import TestContent, TestContentServer
from OnlineJudgeSystem.model.Test import Test, TestServer
from OnlineJudgeSystem.model.TestRecord import TestRecord, TestRecordServer
from OnlineJudgeSystem.model.TestRecordAnswer import TestRecordAnswerServer
from OnlineJudgeSystem.model.TestRecordAnswerSelect import TestRecordAnswerSelect,TestRecordAnswerSelectServer
from OnlineJudgeSystem.model.TestQuestionRelation import TestQuestionRelation,TestQuestionRelationServer
import pandas as pd
import time
from OnlineJudgeSystem.model.PageTool import PageTool


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

@app.route('/testcontentmanagementadd',methods=['GET', 'POST'])
def testcontentmanagementadd():
    """Renders the contact page."""

    if request.method == 'POST':
        content    =  request.form.get('content')
        result       =  request.form.get('result')
        grade      =  request.form.get('grade')

        if content == '' or result == '' or grade == '':
            return redirect("/usermanagementadd")
        else:
            #将用户请求转发给相应的Model
            testContent = TestContent()
            testContent.Content = content
            testContent.Result   = result
            testContent.Grade  = grade
            testContentServer = TestContentServer()

            testContentServer.insert_sql(testContent);
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

        # 插入试卷信息到 Test 表
        test = Test()
        test.TestName = test_name
        test.SelectText = select_text
        test.ProgrameText = program_text


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

        if testname == '' or programetext == '' or selecttext == '':
            return redirect("/testmanagement")
        else:
            # 更新试卷信息
            test = Test()
            test.Id = id
            test.TestName = testname
            test.ProgrameText = programetext
            test.SelectText = selecttext
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
    studentsServer = StudentsServer()
    temps = studentsServer.select_sql_all_two_table()
    datas = []
    for x in temps:
        if len(x.StudentsTestRecord) >0 :
            for item in x.StudentsTestRecord[0].TestContent:
                x.StudentsTestRecord[0].SumGrade+= item.Grade
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
        sum_page = sum_page
    )


@app.route('/testcontentrecordmanagementseacher',methods=['GET', 'POST'])
def testcontentrecordmanagementseacher():
    """Renders the about page."""
    startTime = request.form.get("startTime")
    endTime   = request.form.get("endTime")

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
        seacher  = "123"
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