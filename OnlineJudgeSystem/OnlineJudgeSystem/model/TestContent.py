


from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper

import json

class TestContent(object):
    """description of class"""
    def __init__(self):
        self.Id=0
        self.Content=""
        self.Result=""
        self.Grade=""

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    

class TestContentServer(object):
    """description of class"""

    def select_sql_all(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from Test_Content", "")
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
        testContent = TestContent()         
        reuslt = mysql.query("select * from Test_Content where Id="+str(id), "")
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                testContent.Id = row[0]
                testContent.Content = row[1]
                testContent.Result = row[2]
                testContent.Grade = row[3]
            mysql.end()
        return testContent

    def select_sql_by_keyword(self,keyword):
        mysql = MySqlHelper()
        data = []        
        reuslt = mysql.query("select * from Test_Content where Content like '%"+str(keyword) +"%'", "")
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


    def select_sql_all_count(self):
        mysql = MySqlHelper()
        reuslt = mysql.query("select * from Test_Content", "")
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
        return len(data)


    def insert_sql(self,testContent):
        mysql = MySqlHelper()

        mysql.query("insert into Test_Content (`Content`,`Result`,`Grade`) values(\""+\
                    testContent.Content+"\", \""+testContent.Result+"\", \""+testContent.Grade+"\");", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def update_sql(self,testContent):
        mysql = MySqlHelper()

        mysql.query("update Test_Content set Content='"+testContent.Content+"',Result='"+testContent.Result+"',Grade='"+testContent.Grade+"' "\
                    " where Id="+str(testContent.Id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def delete_sql(self,id):
        mysql = MySqlHelper()

        mysql.query("delete from Test_Content WHERE Id="+str(id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end() 

