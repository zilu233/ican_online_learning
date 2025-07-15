from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper

from OnlineJudgeSystem.model.TestContent import TestContent, TestContentServer

class TestRecordAnswer(object):
    """description of class"""
    def __init__(self):
        self.Id=0
        self.TestRecordId=0
        self.TestContentId=0
        self.AnswerContent=""
        self.Grade=0


class TestRecordAnswerServer(object):
    """description of class"""

    def select_sql_all(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_record tb1 left join test_record_answer_content tb2 on tb1.Id=tb2.Test_Record_Id", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecord = TestRecord() 
                testRecord.Id = row[0]
                testRecord.RocordTime = row[2]
                testRecord.Sum_Grade = row[3]
                test_content_id = row[6]
                if record_Id != None:
                    pass
                data.append(students);
            mysql.end()
        return data


    def select_sql_all_test_record_id(self,id):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_record_answer_content where Test_Record_Id=" + str(id), "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecordAnswer = TestRecordAnswer() 
                testRecordAnswer.Id = row[0]
                testRecordAnswer.TestRecordId  = row[1]
                testRecordAnswer.TestContentId = row[2]
                testRecordAnswer.TestContent   = TestContentServer().select_sql_by_id(row[2])
                testRecordAnswer.AnswerContent = row[3]
                testRecordAnswer.Grade = row[4]
                data.append(testRecordAnswer);
            mysql.end()
        return data

    def select_sql_all_Test_Content(self,id):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_content where Id=" + str(id), "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecordAnswer = TestRecordAnswer() 
                testRecordAnswer.Id = row[0]
                testRecordAnswer.TestRecordId = row[1]
                testRecordAnswer.TestContentId = row[2]
                testRecordAnswer.AnswerContent = row[3]
                testRecordAnswer.Grade = row[4]
                data.append(testRecordAnswer);
            mysql.end()
        return data


    def select_sql_by_id(self,id):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        testRecordAnswer = None       
        reuslt = mysql.query("select * from test_record_answer_content where Id="+str(id), "")
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecordAnswer = TestRecordAnswer() 
                testRecordAnswer.Id = row[0]
                testRecordAnswer.TestRecordId = row[1]
                testRecordAnswer.TestContentId = row[2]
                testRecordAnswer.AnswerContent = row[3]
                testRecordAnswer.Grade = row[4]
            mysql.end()
        return testRecordAnswer




    def select_sql_by_student_id(self,id):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        testRecord = TestRecord()
        data = []
        reuslt = mysql.query("select * from test_record where Students_Id="+str(id), "")
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecord.Id = row[0]
                testRecord.StudentsId = row[1]
                testRecord.RocordTime = row[2]
                testRecord.SumGrade = row[3]
                data.append(testRecord)
            mysql.end()
        return data


    def select_sql_all_count(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from students", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students = Students() 
                students.Id = row[0]
                students.UserName = row[1]
                students.PWD = row[2]
                students.Name = row[3]
                students.Card = row[4]
                students.Phone = row[5]
                students.Address = row[6]
                data.append(students);
            mysql.end()
        return len(data)


    def select_sql_last_id(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt  = mysql.query("select Id from test_record_answer_content ORDER BY Id DESC LIMIT 1;", "")
        last_id = 0
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                last_id = row[0]
            mysql.end()
        return last_id

    def insert_sql(self,testRecordAnswer):
        mysql = MySqlHelper()

        mysql.query("insert into test_record_answer_content (`Test_Record_Id`,`Test_Content_Id`,`Answer_Content`,`Grade`) values("+\
                    str(testRecordAnswer.TestRecordId)+", "+str(testRecordAnswer.TestContentId)+",\""+str(testRecordAnswer.AnswerContent)+"\","+str(testRecordAnswer.Grade)+");", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def update_sql(self,testRecordAnswer):
        mysql = MySqlHelper()

        mysql.query("update test_record_answer_content set Answer_Content='"+testRecordAnswer.AnswerContent+"',Grade='"+str(testRecordAnswer.Grade)+"' "\
                    " where Id="+str(testRecordAnswer.Id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def delete_sql_by_testRecordId(self,id):
        mysql = MySqlHelper()
        mysql.query("delete from test_record_answer_content WHERE Test_Record_Id="+str(id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end() 


