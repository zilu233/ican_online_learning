from OnlineJudgeSystem.model.TestRecord import TestRecord, TestRecordServer
from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
import json

class Students(object):
    """description of class"""
    def __init__(self):
        self.Id=0
        self.UserName=""
        self.PWD=""
        self.Classes=""  # 保留向后兼容
        self.Name=""
        self.Card=""
        self.Phone=""
        self.Address=""  # 字段保留但不再使用
        self.StudentsTestRecord=[]
        # 新增字段 - 多学校支持
        self.SchoolId=0
        self.ClassId=0
        self.EnrollmentDate=""
        self.Status=1  # 1-在读, 0-毕业/退学
        self.SchoolName=""  # 关联学校名称
        self.ClassName=""   # 关联班级名称

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class StudentsServer(object):
    """description of class"""
    def select_sql_login(self,students):
        mysql = MySqlHelper()
        sql = (
            "SELECT s.Id, s.User_Name, s.PWD, s.Classes, s.Name, s.Card, s.Phone, s.Address, "
            "s.school_id, s.class_id, s.enrollment_date, s.status, sc.school_name, c.class_name "
            "FROM students s "
            "LEFT JOIN schools sc ON s.school_id=sc.id "
            "LEFT JOIN classes c ON s.class_id=c.id "
            f"WHERE s.User_Name='{students.UserName}' AND s.PWD='{students.PWD}'"
        )
        reuslt = mysql.query(sql, "")
        result = None
        if reuslt > 0:
            row = mysql.cursor.fetchone()
            if row:
                stu = Students()
                stu.Id = row[0]
                stu.UserName = row[1] or ""
                stu.PWD = row[2] or ""
                stu.Classes = row[3] or ""
                stu.Name = row[4] or ""
                stu.Card = row[5] or ""
                stu.Phone = row[6] or ""
                stu.Address = row[7] or ""
                stu.SchoolId = row[8] or 0
                stu.ClassId = row[9] or 0
                stu.EnrollmentDate = str(row[10]) if row[10] else ""
                stu.Status = row[11] or 1
                # join 列
                stu.SchoolName = row[12] or ""
                stu.ClassName = row[13] or ""
                result = stu
        mysql.end()
        return result


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
        # 联表获取班级名称，兼容老字段 Classes
        sql = (
            "SELECT s.Id, s.User_Name, s.PWD, s.Classes, s.Name, s.Card, s.Phone, s.Address, "
            "s.school_id, s.class_id, s.enrollment_date, s.status, c.class_name "
            "FROM students s LEFT JOIN classes c ON s.class_id=c.id ORDER BY s.Id"
        )
        reuslt = mysql.query(sql, "")
        data = []
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                students = Students()
                students.Id = row[0]
                students.UserName = row[1] or ""
                students.PWD = row[2] or ""
                students.Classes = row[3] or ""
                students.Name = row[4] or ""
                students.Card = row[5] or ""
                students.Phone = row[6] or ""
                students.Address = row[7] or ""
                students.SchoolId = row[8] or 0
                students.ClassId = row[9] or 0
                students.EnrollmentDate = str(row[10]) if row[10] else ""
                students.Status = row[11] or 1
                students.ClassName = row[12] or ""
                data.append(students)
        mysql.end()
        return data


    def select_sql_all_two_table(self):
        mysql = MySqlHelper()
        # 显式列选择，避免 select * 导致的列错位；联表拿到班级名称
        sql = (
            "SELECT s.Id, s.User_Name, s.PWD, s.Classes, s.Name, s.Card, s.Phone, s.Address, "
            "s.school_id, s.class_id, s.enrollment_date, s.status, tr.Id AS tr_id, c.class_name "
            "FROM students s "
            "LEFT JOIN test_record tr ON s.Id=tr.Students_Id "
            "LEFT JOIN classes c ON s.class_id=c.id "
            "ORDER BY s.Id, tr.Id"
        )
        reuslt = mysql.query(sql, "")
        data = []
        testRecordServer = TestRecordServer()
        if reuslt > 0:
            for row in mysql.cursor.fetchall():
                stu = Students()
                stu.Id = row[0]
                stu.UserName = row[1] or ""
                stu.PWD = row[2] or ""
                stu.Classes = row[3] or ""
                stu.Name = row[4] or ""
                stu.Card = row[5] or ""
                stu.Phone = row[6] or ""
                stu.Address = row[7] or ""
                stu.SchoolId = row[8] or 0
                stu.ClassId = row[9] or 0
                stu.EnrollmentDate = str(row[10]) if row[10] else ""
                stu.Status = row[11] or 1
                stu.ClassName = row[13] or ""

                tr_id = row[12]
                if tr_id is not None:
                    record = testRecordServer.select_sql_by_id(tr_id)
                    stu.StudentsTestRecord.append(record)

                data.append(stu)
        mysql.end()
        return data


    def select_sql_by_id(self,id):
        mysql = MySqlHelper()
        # 精确列选择，避免 * 导致的列错位
        sql = (
            "SELECT s.Id, s.User_Name, s.PWD, s.Classes, s.Name, s.Card, s.Phone, s.Address, "
            "s.school_id, s.class_id, s.enrollment_date, s.status, sc.school_name, c.class_name "
            "FROM students s "
            "LEFT JOIN schools sc ON s.school_id=sc.id "
            "LEFT JOIN classes c ON s.class_id=c.id "
            "WHERE s.Id=" + str(id)
        )
        students = Students()
        reuslt = mysql.query(sql, "")
        if reuslt > 0:
            row = mysql.cursor.fetchone()
            if row:
                students.Id = row[0]
                students.UserName = row[1] or ""
                students.PWD = row[2] or ""
                students.Classes = row[3] or ""
                students.Name = row[4] or ""
                students.Card = row[5] or ""
                students.Phone = row[6] or ""
                students.Address = row[7] or ""
                students.SchoolId = row[8] or 0
                students.ClassId = row[9] or 0
                students.EnrollmentDate = str(row[10]) if row[10] else ""
                students.Status = row[11] or 1
                students.SchoolName = row[12] or ""
                students.ClassName = row[13] or ""
        mysql.end()

        # 加载学生的测试记录（保持原有逻辑）
        try:
            testRecordServer = TestRecordServer()
            datas = testRecordServer.select_sql_by_student_id(students.Id)
            for item in datas:
                students.StudentsTestRecord.append(item)
        except Exception:
            pass
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
        
        # 构建插入语句（支持新字段）
        school_id_str = str(students.SchoolId) if students.SchoolId else "NULL"
        class_id_str = str(students.ClassId) if students.ClassId else "NULL"
        enrollment_date_str = f"'{students.EnrollmentDate}'" if students.EnrollmentDate else "NULL"
        
        sql = f"""insert into students (`User_Name`,`PWD`,`Classes`,`Name`,`Card`,`Phone`,`Address`,`school_id`,`class_id`,`enrollment_date`,`status`) 
                  values("{students.UserName}", "{students.PWD}", "{students.Classes}", "{students.Name}","{students.Card}","{students.Phone}","{students.Address}",
                  {school_id_str}, {class_id_str}, {enrollment_date_str}, {students.Status});"""
        
        mysql.query(sql, "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def update_sql(self,students):
        mysql = MySqlHelper()
        
        # 构建更新语句（支持新字段）
        school_id_str = str(students.SchoolId) if students.SchoolId else "NULL"
        class_id_str = str(students.ClassId) if students.ClassId else "NULL"
        
        sql = f"""update students set User_Name='{students.UserName}',PWD='{students.PWD}',Classes='{students.Classes}',Name='{students.Name}',Card='{students.Card}',
                  Phone='{students.Phone}',Address='{students.Address}',school_id={school_id_str},class_id={class_id_str},status={students.Status} 
                  where Id={students.Id};"""
        
        mysql.query(sql, "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end()  


    def delete_sql(self,id):
        mysql = MySqlHelper()

        mysql.query("delete from students WHERE Id="+str(id)+";", "")
        #Must user commit in crud
        mysql.connent.commit()
        mysql.end() 


    # ============ 新增方法：多学校支持 ============
    
    def select_sql_by_school(self, school_id):
        """根据学校查询学生列表"""
        mysql = MySqlHelper()
        reuslt = mysql.query(f"""
            select s.*, sc.school_name, c.class_name 
            from students s 
            LEFT JOIN schools sc ON s.school_id=sc.id 
            LEFT JOIN classes c ON s.class_id=c.id 
            where s.school_id={school_id} AND s.status=1
            ORDER BY s.class_id, s.Name
        """, "")
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
                students.SchoolId = row[8] if row[8] else 0
                students.ClassId = row[9] if row[9] else 0
                students.EnrollmentDate = str(row[10]) if row[10] else ""
                students.Status = row[11] if row[11] else 1
                students.SchoolName = row[14] if row[14] else ""
                students.ClassName = row[15] if row[15] else ""
                data.append(students)
            mysql.end()
        return data
    
    def select_sql_by_class(self, class_id):
        """根据班级查询学生列表"""
        mysql = MySqlHelper()
        reuslt = mysql.query(f"""
            select s.*, sc.school_name, c.class_name 
            from students s 
            LEFT JOIN schools sc ON s.school_id=sc.id 
            LEFT JOIN classes c ON s.class_id=c.id 
            where s.class_id={class_id} AND s.status=1
            ORDER BY s.Name
        """, "")
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
                students.SchoolId = row[8] if row[8] else 0
                students.ClassId = row[9] if row[9] else 0
                students.EnrollmentDate = str(row[10]) if row[10] else ""
                students.Status = row[11] if row[11] else 1
                students.SchoolName = row[14] if row[14] else ""
                students.ClassName = row[15] if row[15] else ""
                data.append(students)
            mysql.end()
        return data
    
    def update_class(self, student_id, new_class_id):
        """更新学生班级"""
        mysql = MySqlHelper()
        class_id_str = str(new_class_id) if new_class_id else "NULL"
        mysql.query(f"update students set class_id={class_id_str} where Id={student_id};", "")
        mysql.connent.commit()
        mysql.end()


