


from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper

import json

class TestSelect(object):
    """description of class"""
    def __init__(self):
        self.Id = 0
        self.Content      = ""
        self.AnswerA      = ""
        self.AnswerB      = ""
        self.AnswerC      = ""
        self.AnswerD      = ""
        self.Result       = ""
        self.Grade        = ""

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    

class TestSelectServer(object):
    """description of class"""

    def select_sql_all(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test_select", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent = TestSelect() 
                testContent.Id = row[0]
                testContent.Content = row[1]
                testContent.AnswerA = row[2]
                testContent.AnswerB = row[3]
                testContent.AnswerC = row[4]
                testContent.AnswerD = row[5]
                testContent.Result = row[6]
                testContent.Grade = row[7]
                data.append(testContent);
            mysql.end()
        return data


    def select_sql_by_id(self,id):
        mysql = MySqlHelper()
        testContent = TestSelect()         
        reuslt = mysql.query("select * from test_select where Id="+str(id), "")
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent.Id = row[0]
                testContent.Content = row[1]
                testContent.AnswerA = row[2]
                testContent.AnswerB = row[3]
                testContent.AnswerC = row[4]
                testContent.AnswerD = row[5]
                testContent.Result = row[6]
                testContent.Grade = row[7]
            mysql.end()
        return testContent

    def select_sql_by_keyword(self,keyword):
        mysql = MySqlHelper()
        data = []        
        reuslt = mysql.query("select * from test_select where Content like '%"+str(keyword) +"%'", "")
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent = TestSelect()
                testContent.Id = row[0]
                testContent.Content = row[1]
                testContent.AnswerA = row[2]
                testContent.AnswerB = row[3]
                testContent.AnswerC = row[4]
                testContent.AnswerD = row[5]
                testContent.Result = row[6]
                testContent.Grade = row[7]
                data.append(testContent);
            mysql.end()
        return data


    def select_sql_all_count(self):
        mysql = MySqlHelper()
        reuslt = mysql.query("select * from test_select", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent = TestSelect() 
                testContent.Id = row[0]
                testContent.Content = row[1]
                testContent.AnswerA = row[2]
                testContent.AnswerB = row[3]
                testContent.AnswerC = row[4]
                testContent.AnswerD = row[5]
                testContent.Result = row[6]
                testContent.Grade = row[7]
                data.append(testContent);
            mysql.end()
        return len(data)


    def insert_sql(self,testContent):
        mysql = MySqlHelper()

        mysql.query("insert into test_select (`Content`,`AnswerA`,`AnswerB`,`AnswerC`,`AnswerD`,`Result`,`Grade`) values(\""+\
                    testContent.Content+"\", \""+testContent.AnswerA+"\", \""+testContent.AnswerB+"\", \""+testContent.AnswerC+"\", \""+testContent.AnswerD+"\", \""+testContent.Result+"\", \""+testContent.Grade+"\");", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def update_sql(self,testContent):
        mysql = MySqlHelper()

        mysql.query("update test_select set Content='"+testContent.Content+"',AnswerA='"+testContent.AnswerA+"',AnswerB='"+testContent.AnswerB+"',AnswerC='"+testContent.AnswerC+"',AnswerD='"+testContent.AnswerD+"',Result='"+testContent.Result+"',Grade='"+testContent.Grade+"' "\
                    " where Id="+str(testContent.Id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def delete_sql(self,id):
        mysql = MySqlHelper()

        mysql.query("delete from test_select WHERE Id="+str(id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end() 

