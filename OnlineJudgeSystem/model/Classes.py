# -*- coding: utf-8 -*-
"""
班级模型类
用于处理班级信息的数据访问
"""

from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
import json


class Classes:
    """班级实体类"""
    def __init__(self):
        self.Id = 0
        self.SchoolId = 0
        self.ClassName = ""
        self.ClassCode = ""
        self.Grade = ""
        self.TeacherId = 0
        self.StudentCount = 0
        self.Description = ""
        self.Status = 1  # 1-启用, 0-禁用
        self.CreatedAt = ""
        self.UpdatedAt = ""
        # 关联信息
        self.SchoolName = ""
        self.TeacherName = ""


class ClassesServer:
    """班级服务类 - 数据访问层"""
    
    @staticmethod
    def select_sql_all(school_id=None, status=None):
        """
        查询班级列表
        :param school_id: 学校ID筛选
        :param status: 状态筛选 (1-启用, 0-禁用, None-全部)
        :return: 班级列表
        """
        sql = """
        SELECT c.*, s.school_name, t.Name as teacher_name
        FROM classes c
        LEFT JOIN schools s ON c.school_id = s.id
        LEFT JOIN teacher t ON c.teacher_id = t.Id
        WHERE 1=1
        """
        
        if school_id:
            sql += f" AND c.school_id = {school_id}"
        if status is not None:
            sql += f" AND c.status = {status}"
        
        sql += " ORDER BY c.school_id, c.grade, c.class_name"
        
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        
        classes_list = []
        for item in result:
            cls = Classes()
            cls.Id = item[0]
            cls.SchoolId = item[1]
            cls.ClassName = item[2]
            cls.ClassCode = item[3] if item[3] else ""
            cls.Grade = item[4] if item[4] else ""
            cls.TeacherId = item[5] if item[5] else 0
            cls.StudentCount = item[6] if item[6] else 0
            cls.Description = item[7] if item[7] else ""
            cls.Status = item[8]
            cls.CreatedAt = str(item[9]) if item[9] else ""
            cls.UpdatedAt = str(item[10]) if item[10] else ""
            cls.SchoolName = item[11] if item[11] else ""
            cls.TeacherName = item[12] if item[12] else ""
            classes_list.append(cls)
        
        return classes_list
    
    @staticmethod
    def select_sql_by_id(class_id):
        """
        根据ID查询班级
        :param class_id: 班级ID
        :return: 班级对象或None
        """
        sql = f"""
        SELECT c.*, s.school_name, t.Name as teacher_name
        FROM classes c
        LEFT JOIN schools s ON c.school_id = s.id
        LEFT JOIN teacher t ON c.teacher_id = t.Id
        WHERE c.id = {class_id}
        """
        
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        
        if result:
            item = result[0]
            cls = Classes()
            cls.Id = item[0]
            cls.SchoolId = item[1]
            cls.ClassName = item[2]
            cls.ClassCode = item[3] if item[3] else ""
            cls.Grade = item[4] if item[4] else ""
            cls.TeacherId = item[5] if item[5] else 0
            cls.StudentCount = item[6] if item[6] else 0
            cls.Description = item[7] if item[7] else ""
            cls.Status = item[8]
            cls.CreatedAt = str(item[9]) if item[9] else ""
            cls.UpdatedAt = str(item[10]) if item[10] else ""
            cls.SchoolName = item[11] if item[11] else ""
            cls.TeacherName = item[12] if item[12] else ""
            return cls
        
        return None
    
    @staticmethod
    def select_sql_by_school(school_id, status=1):
        """
        根据学校查询班级列表
        :param school_id: 学校ID
        :param status: 状态 (1-启用, 0-禁用, None-全部)
        :return: 班级列表
        """
        return ClassesServer.select_sql_all(school_id=school_id, status=status)
    
    @staticmethod
    def select_sql_by_teacher(teacher_id):
        """
        根据班主任查询班级列表
        :param teacher_id: 教师ID
        :return: 班级列表
        """
        sql = f"""
        SELECT c.*, s.school_name, t.Name as teacher_name
        FROM classes c
        LEFT JOIN schools s ON c.school_id = s.id
        LEFT JOIN teacher t ON c.teacher_id = t.Id
        WHERE c.teacher_id = {teacher_id} AND c.status = 1
        ORDER BY c.grade, c.class_name
        """
        
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        
        classes_list = []
        for item in result:
            cls = Classes()
            cls.Id = item[0]
            cls.SchoolId = item[1]
            cls.ClassName = item[2]
            cls.ClassCode = item[3] if item[3] else ""
            cls.Grade = item[4] if item[4] else ""
            cls.TeacherId = item[5] if item[5] else 0
            cls.StudentCount = item[6] if item[6] else 0
            cls.Description = item[7] if item[7] else ""
            cls.Status = item[8]
            cls.CreatedAt = str(item[9]) if item[9] else ""
            cls.UpdatedAt = str(item[10]) if item[10] else ""
            cls.SchoolName = item[11] if item[11] else ""
            cls.TeacherName = item[12] if item[12] else ""
            classes_list.append(cls)
        
        return classes_list
    
    @staticmethod
    def insert_sql(cls):
        """
        添加班级
        :param cls: 班级对象
        :return: 插入的班级ID
        """
        teacher_id_str = str(cls.TeacherId) if cls.TeacherId else "NULL"
        
        sql = f"""
        INSERT INTO classes (school_id, class_name, class_code, grade, 
                           teacher_id, description, status)
        VALUES ({cls.SchoolId}, '{cls.ClassName}', '{cls.ClassCode}', 
                '{cls.Grade}', {teacher_id_str}, '{cls.Description}', {cls.Status})
        """
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def update_sql(cls):
        """
        更新班级信息
        :param cls: 班级对象
        :return: 影响的行数
        """
        teacher_id_str = str(cls.TeacherId) if cls.TeacherId else "NULL"
        
        sql = f"""
        UPDATE classes 
        SET school_id = {cls.SchoolId},
            class_name = '{cls.ClassName}',
            class_code = '{cls.ClassCode}',
            grade = '{cls.Grade}',
            teacher_id = {teacher_id_str},
            description = '{cls.Description}',
            status = {cls.Status}
        WHERE id = {cls.Id}
        """
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def delete_sql(class_id):
        """
        删除班级（物理删除）
        注意：会影响关联的学生
        :param class_id: 班级ID
        :return: 影响的行数
        """
        sql = f"DELETE FROM classes WHERE id = {class_id}"
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def update_status(class_id, status):
        """
        更新班级状态（软删除）
        :param class_id: 班级ID
        :param status: 状态 (1-启用, 0-禁用)
        :return: 影响的行数
        """
        sql = f"UPDATE classes SET status = {status} WHERE id = {class_id}"
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def update_teacher(class_id, teacher_id):
        """
        更新班主任
        :param class_id: 班级ID
        :param teacher_id: 教师ID (0或None表示移除班主任)
        :return: 影响的行数
        """
        teacher_id_str = str(teacher_id) if teacher_id else "NULL"
        sql = f"UPDATE classes SET teacher_id = {teacher_id_str} WHERE id = {class_id}"
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def update_student_count(class_id):
        """
        更新班级学生人数（从students表统计）
        :param class_id: 班级ID
        :return: 影响的行数
        """
        sql = f"""
        UPDATE classes 
        SET student_count = (
            SELECT COUNT(*) FROM students WHERE class_id = {class_id}
        )
        WHERE id = {class_id}
        """
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def get_students(class_id):
        """
        获取班级的学生列表
        :param class_id: 班级ID
        :return: 学生列表
        """
        sql = f"""
        SELECT Id, User_Name, Name, Card, Phone, Address
        FROM students 
        WHERE class_id = {class_id} AND status = 1
        ORDER BY Name
        """
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        
        students = []
        for item in result:
            student = {
                'id': item[0],
                'username': item[1],
                'name': item[2],
                'card': item[3] if item[3] else "",
                'phone': item[4] if item[4] else "",
                'address': item[5] if item[5] else ""
            }
            students.append(student)
        
        return students
    
    @staticmethod
    def check_name_exists(school_id, class_name, exclude_id=None):
        """
        检查班级名称在该学校是否已存在
        :param school_id: 学校ID
        :param class_name: 班级名称
        :param exclude_id: 排除的班级ID（用于编辑时）
        :return: True-存在, False-不存在
        """
        sql = f"""
        SELECT COUNT(*) FROM classes 
        WHERE school_id = {school_id} AND class_name = '{class_name}'
        """
        if exclude_id:
            sql += f" AND id != {exclude_id}"
        
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        return result[0][0] > 0
