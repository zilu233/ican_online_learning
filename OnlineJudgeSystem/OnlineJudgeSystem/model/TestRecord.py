
from OnlineJudgeSystem.model.TestRecordAnswerSelect import TestRecordAnswerSelect
from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
from OnlineJudgeSystem.model.TestRecordAnswer import TestRecordAnswer


class TestRecord(object):
    """description of class"""
    def __init__(self):
        self.Id=0
        self.StudentsId=0
        self.RocordTime=""
        self.SumGrade=0
        self.TestContent = []
        self.TestSelect  = []


class TestRecordServer(object):
    """description of class"""

    def select_sql_all(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_record", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecord = TestRecord() 
                testRecord.Id = row[0]
                testRecord.RocordTime = row[2]
                testRecord.Sum_Grade = row[3]
                test_record_id = row[0]
                testRecord.TestContent=[]
                if test_record_id != None:
                    mysql = MySqlHelper()
                    #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
                    #把它的id 存起来再一次联合查询做题记录和题库表
                    reuslt = mysql.query("select * from test_record_answer_content where Test_Record_Id="+str(test_record_id) +" order by Id asc", "")
                    index = 0
                    for row in mysql.cursor.fetchall():
                        testRecordAnswer = TestRecordAnswer()
                        testRecordAnswer.Id  = row[0]  
                        testRecordAnswer.TestRecordId  = row[1]  
                        testRecordAnswer.TestContentId  = row[2]
                        testRecordAnswer.AnswerContent  = row[3] 
                        testRecordAnswer.Grade  = row[4]
                        testRecord.TestContent.append(testRecordAnswer)
                data.append(testRecord);
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
                testContent = TestContent() 
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
        reuslt = mysql.query("select * from test_record where Id="+str(id), "")
        testRecord = TestRecord()         
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecord.Id = row[0]
                testRecord.RocordTime = row[2]
                testRecord.Sum_Grade = row[3]
                test_record_id = row[0]
                testRecord.TestContent=[]
                if test_record_id != None:
                    mysql = MySqlHelper()
                    #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
                    #把它的id 存起来再一次联合查询做题记录和题库表
                    reuslt = mysql.query("select * from test_record_answer_content where Test_Record_Id="+str(test_record_id) +" order by Id asc", "")
                    index = 0
                    for row in mysql.cursor.fetchall():
                        testRecordAnswer = TestRecordAnswer()
                        testRecordAnswer.Id  = row[0]  
                        testRecordAnswer.TestRecordId  = row[1]  
                        testRecordAnswer.TestContentId  = row[2]
                        testRecordAnswer.AnswerContent  = row[3] 
                        testRecordAnswer.Grade  = row[4]
                        testRecord.TestContent.append(testRecordAnswer)
            mysql.end()
        return testRecord


    def select_sql_by_student_id(self,id):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_record where Students_Id="+str(id), "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testRecord = TestRecord() 
                testRecord.Id = row[0]
                testRecord.RocordTime = row[2]
                testRecord.Sum_Grade = row[3]
                test_record_id = row[0]
                testRecord.TestContent=[]
                if test_record_id != None:
                    mysql = MySqlHelper()
                    #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
                    #把它的id 存起来再一次联合查询做题记录和题库表
                    reuslt = mysql.query("select * from test_record_answer_content where Test_Record_Id="+str(test_record_id) +" order by Id asc", "")
                    index = 0
                    for row in mysql.cursor.fetchall():
                        testRecordAnswer = TestRecordAnswer()
                        testRecordAnswer.Id  = row[0]  
                        testRecordAnswer.TestRecordId   = row[1]  
                        testRecordAnswer.TestContentId  = row[2]
                        testRecordAnswer.AnswerContent  = row[3] 
                        testRecordAnswer.Grade  = row[4]
                        testRecord.TestContent.append(testRecordAnswer)

                testRecord.TestSelect=[]
                if test_record_id != None:
                    mysql = MySqlHelper()
                    #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
                    #把它的id 存起来再一次联合查询做题记录和题库表
                    reuslt = mysql.query("select * from test_record_answer_select where Test_Record_Id="+str(test_record_id) +" order by Id asc", "")
                    index = 0
                    for row in mysql.cursor.fetchall():
                        testRecordAnswerSelect  = TestRecordAnswerSelect()
                        testRecordAnswerSelect.Id  = row[0]  
                        testRecordAnswerSelect.TestRecordId   = row[1]  
                        testRecordAnswerSelect.TestSelectId   = row[2]
                        testRecordAnswerSelect.AnswerSelect   = row[3] 
                        testRecordAnswerSelect.Grade          = row[4]
                        testRecord.TestSelect.append(testRecordAnswer)
                data.append(testRecord);
            mysql.end()
        return data


    def select_sql_all_count(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_record", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                data.append(1);
            mysql.end()
        return len(data)

    def select_sql_get_id(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt  = mysql.query("select Id from test_record ORDER BY Id DESC LIMIT 1;", "")
        last_id = 0
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                last_id = row[0];
            mysql.end()
        return last_id



    def insert_sql(self,testRecord):
        mysql = MySqlHelper()

        mysql.query("insert into test_record (`Students_Id`,`Rocord_Time`,`Sum_Grade`) values("+\
                    str(testRecord.StudentsId)+", \""+str(testRecord.RocordTime)+"\","+str(testRecord.SumGrade)+");", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def update_sql(self,testRecord):
        mysql = MySqlHelper()

        mysql.query("update test_record set Sum_Grade='"+ str(testRecord.SumGrade) +"' where Id="+str(testRecord.Id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def delete_sql(self,id):
        mysql = MySqlHelper()

        mysql.query("delete from test_record WHERE Id="+str(id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end() 


