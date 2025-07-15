


from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper

import json

class Test(object):
    """description of class"""
    def __init__(self):
        self.Id=0
        self.TestName=""
        self.ProgrameText=0
        self.SelectText=0

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    

class TestServer(object):
    """description of class"""

    def select_sql_all(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from test", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent = Test() 
                testContent.Id           = row[0]
                testContent.TestName     = row[1]
                testContent.ProgrameText = row[2]
                testContent.SelectText   = row[3]
                data.append(testContent);
            mysql.end()
        return data


    def select_sql_by_id(self,id):
        mysql = MySqlHelper()
        testContent = Test()         
        reuslt = mysql.query("select * from test where Id="+str(id), "")
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent.Id           = row[0]
                testContent.TestName     = row[1]
                testContent.ProgrameText = row[2]
                testContent.SelectText   = row[3]
            mysql.end()
        return testContent

    def select_sql_by_keyword(self,keyword):
        mysql = MySqlHelper()
        data = []        
        reuslt = mysql.query("select * from test where Content like '%"+str(keyword) +"%'", "")
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent = Test()
                testContent.Id           = row[0]
                testContent.TestName     = row[1]
                testContent.ProgrameText = row[2]
                testContent.SelectText   = row[3]
                data.append(testContent);
            mysql.end()
        return data


    def select_sql_all_count(self):
        mysql = MySqlHelper()
        reuslt = mysql.query("select * from test", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent = Test() 
                testContent.Id           = row[0]
                testContent.TestName     = row[1]
                testContent.ProgrameText = row[2]
                testContent.SelectText   = row[3]
                data.append(testContent);
            mysql.end()
        return len(data)


    def insert_sql(self,testContent):
        mysql = MySqlHelper()

        mysql.query("insert into test (`testname`,`programetext`,`selecttext`) values(\""+\
                    testContent.TestName+"\", \""+testContent.ProgrameText+"\", \""+testContent.SelectText+"\");", "")
        #Must user commit in crud

        mysql.cursor.execute("SELECT LAST_INSERT_ID()")
        insert_id = mysql.cursor.fetchone()[0]
        mysql.connent.commit()
        mysql.end() 
        return insert_id 



    def update_sql(self,testContent):
        mysql = MySqlHelper()

        mysql.query("update test set testname='"+testContent.TestName+"',programetext='"+testContent.ProgrameText+"',selecttext='"+testContent.SelectText+"' "\
                    " where Id="+str(testContent.Id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def delete_sql(self,id):
        mysql = MySqlHelper()

        mysql.query("delete from test WHERE Id="+str(id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end() 

