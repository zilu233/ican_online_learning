from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
import json

class Admins(object):
    """description of class"""
    def __init__(self):
        self.Id=""
        self.UserName=""
        self.PWD=""

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class AdminsServer(object):
    """description of class"""
    def select_sql_login(self,adminModel):
        mysql = MySqlHelper()
        reuslt =  mysql.query("select * from admins where User_Name='"+adminModel.UserName+"' and PWD='"+adminModel.PWD+"'", "")
        adminModel = Admins()
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                adminModel.Id = row[0]
                adminModel.Access = row[1]
                adminModel.PWD = row[2]
            mysql.end()
        else:
            adminModel = None
        return adminModel
