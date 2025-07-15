import pymysql
from OnlineJudgeSystem.common.Config import *


class MySqlHelper(object):
    def __init__(self):
        self.__connect_dict = connect_dict_windows_config 
        #self.__connect_dict = Config.connect_dict_linux_config 
        self.connent = pymysql.Connect(**self.__connect_dict)
        self.cursor = self.connent.cursor()


    def query(self,sql,parms):
        if parms:
           return self.cursor.execute(sql, parms)  # 传递参数
        else:
           return self.cursor.execute(sql)


    def end(self):
        self.cursor.close()
        self.connent.close()
