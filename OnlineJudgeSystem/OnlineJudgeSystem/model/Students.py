from OnlineJudgeSystem.model.TestRecord import TestRecord, TestRecordServer
from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
import json

class Students(object):
    """description of class"""
    def __init__(self):
        self.Id=0
        self.UserName=""
        self.PWD=""
        self.Classes=""
        self.Name=""
        self.Card=""
        self.Phone=""
        self.Address=""
        self.StudentsTestRecord=[]

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class StudentsServer(object):
    """description of class"""
    def select_sql_login(self,students):
        mysql = MySqlHelper()
        reuslt =  mysql.query("select * from students where User_Name='"+students.UserName+"' and PWD='"+students.PWD+"'", "")
        students = Students()
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students.Id = row[0]
                students.UserName = row[1]
                students.PWD = row[2]
                students.Classes = row[3]
                students.Name = row[4]
                students.Card = row[5]
                students.Phone = row[6]
                students.Address = row[7]
            mysql.end()
        else:
            students = None
        return students


    def select_sql_exist(self,students):
        mysql = MySqlHelper()
        reuslt =  mysql.query("select * from students where User_Name='"+students.UserName+"'", "")
        students = Students()
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students.Id = row[0]
                students.UserName = row[1]
                students.PWD = row[2]
                students.Classes = row[3]
                students.Name = row[4]
                students.Card = row[5]
                students.Phone = row[6]
                students.Address = row[7]
            mysql.end()
        else:
            students = None
        return students


    def select_sql_all(self):
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
                students.Classes = row[3]
                students.Name = row[4]
                students.Card = row[5]
                students.Phone = row[6]
                students.Address = row[7]
                data.append(students);
            mysql.end()
        return data


    def select_sql_all_two_table(self):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        reuslt = mysql.query("select * from students tb1 left join test_record tb2 on tb1.Id=tb2.Students_Id ", "")
        data = []
        testRecordServer = TestRecordServer()
        record_Id = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students = Students() 
                students.Id = row[0]
                students.UserName = row[1]
                students.PWD = row[2]
                students.Classes = row[3]
                students.Name = row[4]
                students.Card = row[5]
                students.Phone = row[6]
                students.Address = row[7]
                if row[8] != None:
                    #record_Id.append(row[7])
                    datas =  testRecordServer.select_sql_by_id(row[8])
                    students.StudentsTestRecord.append(datas)  
                data.append(students);
            mysql.end()
        return data


    def select_sql_by_id(self,id):
        mysql = MySqlHelper()
        #左右联合查询获取两个表的数据，如果当前用户中有做题记录，
        #把它的id 存起来再一次联合查询做题记录和题库表
        students = Students()
        testRecordServer = TestRecordServer() 
        record_Id = []
        reuslt = mysql.query("select * from students tb1 left join test_record tb2 on tb1.Id=tb2.Students_Id where tb1.Id="+str(id), "")
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students.Id = row[0]
                students.UserName = row[1]
                students.PWD      = row[2]
                students.Classes  = row[3]
                students.Name = row[4]
                students.Card = row[5]
                students.Phone = row[6]
                students.Address = row[7]
                if row[8] != None or row[8] !='':
                    record_Id.append(row[8])
            mysql.end()

            datas =  testRecordServer.select_sql_by_student_id(students.Id)
            for item in datas:
                students.StudentsTestRecord.append(item)                    
        return students


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


    def insert_sql(self,students):
        mysql = MySqlHelper()

        mysql.query("insert into students (`User_Name`,`PWD`,`Classes`,`Name`,`Card`,`Phone`,`Address`) values(\""+\
                    students.UserName+"\", \""+students.PWD+"\", \""+students.Classes+"\", \""+students.Name+"\",\""+students.Card+"\",\""+students.Phone+"\",\""+students.Address+"\");", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def update_sql(self,students):
        mysql = MySqlHelper()

        mysql.query("update students set User_Name='"+students.UserName+"',PWD='"+students.PWD+"',Classes='"+students.Classes+"',Name='"+students.Name+"',Card='"+students.Card+"',"+"Phone='"+students.Phone+"',"\
                    "Address='"+students.Address+"' where Id="+str(students.Id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def delete_sql(self,id):
        mysql = MySqlHelper()

        mysql.query("delete from students WHERE Id="+str(id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end() 

