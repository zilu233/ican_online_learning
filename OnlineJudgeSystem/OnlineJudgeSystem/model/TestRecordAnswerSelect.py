from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
from OnlineJudgeSystem.model.TestSelect import TestSelect, TestSelectServer

class TestRecordAnswerSelect(object):
    """description of class"""
    def __init__(self):
        self.Id=0
        self.TestRecordId  = 0
        self.TestSelectId  = 0
        self.AnswerSelect = ""
        self.Grade         = 0


class TestRecordAnswerSelectServer(object):
    """description of class"""

    def select_sql_all(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_record tb1 left join test_record_answer_content tb2 on tb1.Id=tb2.Test_Record_Id", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecord = TestRecordAnswerSelect() 
                testRecord.Id = row[0]
                testRecord.TestRecordId = row[1]
                testRecord.TestSelectId = row[2]
                testRecord.AnswerSelect = row[3]
                data.append(testRecord);
            mysql.end()
        return data


    def select_sql_all_test_record_id(self,id):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_record_answer_select where Test_Record_Id=" + str(id), "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent = TestRecordAnswerSelect() 
                testContent.Id = row[0]
                testContent.TestRecordId = row[1]
                testContent.TestSelectId = row[2]
                testContent.TestSelect   = TestSelectServer().select_sql_by_id(row[2])
                testContent.AnswerSelect = row[3]
                testContent.Grade = row[4]
                data.append(testContent);
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
                testContent = TestRecordAnswerSelect() 
                testContent.Id = row[0]
                testContent.Content = row[1]
                testContent.Result = row[2]
                testContent.Grade = row[3]
                data.append(testContent);
            mysql.end()
        return data


    def select_sql_by_id(self,id):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt  = mysql.query("select * from test_record_answer_select where Id="+str(id)+";", "")
        last_id = 0
        data    = None
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecord = TestRecordAnswerSelect() 
                testRecord.Id = row[0]
                testRecord.TestRecordId = row[1]
                testRecord.TestSelectId = row[2]
                testRecord.AnswerSelect = row[3]
                data = testRecord
            mysql.end()
        return data


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
        reuslt = mysql.query("select * from test_record_answer_select", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                data.append(row[0]);
            mysql.end()
        return len(data)


    def select_sql_last_id(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt  = mysql.query("select Id from test_record_answer_select ORDER BY Id DESC LIMIT 1;", "")
        last_id = 0
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                last_id = row[0]
            mysql.end()
        return last_id


    def insert_sql(self,testRecordAnswer):
        mysql = MySqlHelper()

        mysql.query("insert into test_record_answer_select (`Test_Record_Id`,`Test_Select_Id`,`Answer_Select`,`Grade`) values("+\
                    str(testRecordAnswer.TestRecordId)+", "+str(testRecordAnswer.TestSelectId)+",\""+str(testRecordAnswer.AnswerSelect)+"\","+str(testRecordAnswer.Grade)+");", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def update_sql(self,testRecordAnswer):
        mysql = MySqlHelper()

        mysql.query("update test_record_answer_select set Test_Record_Id='"+str(testRecordAnswer.TestRecordId)+"',Test_Select_Id='"+str(testRecordAnswer.TestSelectId)+"',Answer_Select='"+str(testRecordAnswer.Answer_Select)+"',Grade='"+str(testRecordAnswer.Grade)+"' "\
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


