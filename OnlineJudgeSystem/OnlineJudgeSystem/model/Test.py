


from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper

import json

class Test(object):
    """description of class"""
    def __init__(self):
        self.Id=0
        self.TestName=""
        self.ProgrameText=0
        self.SelectText=0
        self.TestType='homework'  # 'homework' or 'exam'

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    

class TestServer(object):
    """description of class"""

    def _has_column(self, mysql, column_name):
        try:
            # Use information_schema to check for column existence in current database
            sql = "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='test' AND COLUMN_NAME=%s"
            # MySqlHelper.query supports parms
            mysql.query(sql, (column_name,))
            row = mysql.cursor.fetchone()
            if row and row[0] > 0:
                return True
        except Exception:
            # If any error occurs, fallback conservatively to False
            try:
                import traceback
                traceback.print_exc()
            except Exception:
                pass
        return False

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
                try:
                    testContent.TestType = row[4]
                except Exception:
                    testContent.TestType = 'homework'
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
                try:
                    testContent.TestType = row[4]
                except Exception:
                    testContent.TestType = 'homework'
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
                try:
                    testContent.TestType = row[4]
                except Exception:
                    testContent.TestType = 'homework'
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
        # Insert using testtype if the column exists; otherwise use legacy insert
        if self._has_column(mysql, 'testtype'):
            mysql.query("insert into test (`testname`,`programetext`,`selecttext`,`testtype`) values(\""+\
                        testContent.TestName+"\", \""+str(testContent.ProgrameText)+"\", \""+str(testContent.SelectText)+"\", \""+testContent.TestType+"\");", "")
        else:
            mysql.query("insert into test (`testname`,`programetext`,`selecttext`) values(\""+\
                        testContent.TestName+"\", \""+str(testContent.ProgrameText)+"\", \""+str(testContent.SelectText)+"\");", "")
        #Must user commit in crud

        mysql.cursor.execute("SELECT LAST_INSERT_ID()")
        insert_id = mysql.cursor.fetchone()[0]
        mysql.connent.commit()
        mysql.end() 
        return insert_id 



    def update_sql(self,testContent):
        mysql = MySqlHelper()

        # Update using testtype if the column exists; otherwise use legacy update
        if self._has_column(mysql, 'testtype'):
            mysql.query("update test set testname='"+testContent.TestName+"',programetext='"+str(testContent.ProgrameText)+"',selecttext='"+str(testContent.SelectText)+"', testtype='"+str(getattr(testContent, 'TestType', 'homework'))+"' "\
                        " where Id="+str(testContent.Id)+";", "")
        else:
            mysql.query("update test set testname='"+testContent.TestName+"',programetext='"+str(testContent.ProgrameText)+"',selecttext='"+str(testContent.SelectText)+"' "\
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

