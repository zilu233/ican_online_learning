from OnlineJudgeSystem.model.TestRecord import TestRecord, TestRecordServer
from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
import json

class Teachers(object):
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
        # 新增字段 - 多学校支持
        self.SchoolId=0
        self.ApprovalStatus=0  # 0-待审核, 1-已通过, 2-已拒绝
        self.ApprovalTime=""
        self.ApprovalAdminId=0
        self.RejectionReason=""
        self.SchoolName=""  # 关联学校名称

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class TeachersServer(object):
    """description of class"""
    def select_sql_login(self,students):
        mysql = MySqlHelper()
        reuslt =  mysql.query("select t.*, s.school_name from teacher t LEFT JOIN schools s ON t.school_id=s.id where t.User_Name='"+students.UserName+"' and t.PWD='"+students.PWD+"' and t.approval_status=1", "")
        students = Teachers()
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
                # 新增字段
                students.SchoolId = row[8] if row[8] else 0
                students.ApprovalStatus = row[9] if row[9] else 0
                students.ApprovalTime = str(row[10]) if row[10] else ""
                students.ApprovalAdminId = row[11] if row[11] else 0
                students.RejectionReason = row[12] if row[12] else ""
                students.SchoolName = row[15] if row[15] else ""
            mysql.end()
        else:
            students = None
        return students


    def select_sql_exist(self,students):
        mysql = MySqlHelper()
        reuslt =  mysql.query("select * from teacher where User_Name='"+students.UserName+"'", "")
        students = Teachers()
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
        reuslt = mysql.query("select * from teacher", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students = Teachers() 
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
        reuslt = mysql.query("select * from teacher tb1 left join test_record tb2 on tb1.Id=tb2.Students_Id ", "")
        data = []
        testRecordServer = TestRecordServer()
        record_Id = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students = Teachers() 
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
        students = Teachers()
        testRecordServer = TestRecordServer() 
        record_Id = []
        reuslt = mysql.query("select * from teacher tb1 left join test_record tb2 on tb1.Id=tb2.Students_Id where tb1.Id="+str(id), "")
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
        reuslt = mysql.query("select * from teacher", "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students = Teachers() 
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
        # 构建插入语句（注册即审核通过）
        school_id_str = str(students.SchoolId) if students.SchoolId else "NULL"
        sql = f"""insert into teacher (`User_Name`,`PWD`,`Classes`,`Name`,`Card`,`Phone`,`Address`,`school_id`,`approval_status`) 
                  values("{students.UserName}", "{students.PWD}", "{students.Classes}", "{students.Name}","{students.Card}","{students.Phone}","{students.Address}",
                  {school_id_str}, 1);"""
        mysql.query(sql, "")
        mysql.connent.commit()
        mysql.end()  


    def update_sql(self,students):
        mysql = MySqlHelper()

        mysql.query("update teacher set User_Name='"+students.UserName+"',PWD='"+students.PWD+"',Classes='"+students.Classes+"',Name='"+students.Name+"',Card='"+students.Card+"',"+"Phone='"+students.Phone+"',"\
                    "Address='"+students.Address+"' where Id="+str(students.Id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def delete_sql(self,id):
        mysql = MySqlHelper()

        mysql.query("delete from teacher WHERE Id="+str(id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end() 


    # ============ 新增方法：教师审核和多学校支持 ============
    
    def select_sql_pending_approval(self, school_id=None):
        """查询待审核教师列表"""
        mysql = MySqlHelper()
        sql = """select t.*, s.school_name from teacher t 
                 LEFT JOIN schools s ON t.school_id=s.id 
                 where t.approval_status=0"""
        if school_id:
            sql += f" AND t.school_id={school_id}"
        sql += " ORDER BY t.created_at DESC"
        
        reuslt = mysql.query(sql, "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                teacher = Teachers()
                teacher.Id = row[0]
                teacher.UserName = row[1]
                teacher.PWD = row[2]
                teacher.Classes = row[3]
                teacher.Name = row[4]
                teacher.Card = row[5]
                teacher.Phone = row[6]
                teacher.Address = row[7]
                teacher.SchoolId = row[8] if row[8] else 0
                teacher.ApprovalStatus = row[9] if row[9] else 0
                teacher.ApprovalTime = str(row[10]) if row[10] else ""
                teacher.ApprovalAdminId = row[11] if row[11] else 0
                teacher.RejectionReason = row[12] if row[12] else ""
                teacher.SchoolName = row[15] if row[15] else ""
                data.append(teacher)
            mysql.end()
        return data
    
    def approve_teacher(self, teacher_id, admin_id, status, reason=""):
        """
        审核教师
        :param teacher_id: 教师ID
        :param admin_id: 管理员ID
        :param status: 审核状态 (1-通过, 2-拒绝)
        :param reason: 拒绝原因（status=2时必填）
        """
        mysql = MySqlHelper()
        sql = f"""update teacher set 
                  approval_status={status}, 
                  approval_time=NOW(), 
                  approval_admin_id={admin_id}, 
                  rejection_reason='{reason}' 
                  where Id={teacher_id};"""
        mysql.query(sql, "")
        mysql.connent.commit()
        mysql.end()
    
    def select_sql_by_school(self, school_id, approval_status=1):
        """根据学校查询教师列表（默认只查已审核通过的）"""
        mysql = MySqlHelper()
        sql = f"""select t.*, s.school_name from teacher t 
                  LEFT JOIN schools s ON t.school_id=s.id 
                  where t.school_id={school_id} AND t.approval_status={approval_status}
                  ORDER BY t.Name"""
        
        reuslt = mysql.query(sql, "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                teacher = Teachers()
                teacher.Id = row[0]
                teacher.UserName = row[1]
                teacher.PWD = row[2]
                teacher.Classes = row[3]
                teacher.Name = row[4]
                teacher.Card = row[5]
                teacher.Phone = row[6]
                teacher.Address = row[7]
                teacher.SchoolId = row[8] if row[8] else 0
                teacher.ApprovalStatus = row[9] if row[9] else 0
                teacher.ApprovalTime = str(row[10]) if row[10] else ""
                teacher.ApprovalAdminId = row[11] if row[11] else 0
                teacher.RejectionReason = row[12] if row[12] else ""
                teacher.SchoolName = row[15] if row[15] else ""
                data.append(teacher)
            mysql.end()
        return data


