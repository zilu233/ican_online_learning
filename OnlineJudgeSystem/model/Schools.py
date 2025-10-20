# -*- coding: utf-8 -*-
"""
学校模型类
用于处理学校信息的数据访问
"""

from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
import json


class Schools:
    """学校实体类"""
    def __init__(self):
        self.Id = 0
        self.SchoolName = ""
        self.SchoolCode = ""
        self.Province = ""
        self.City = ""
        self.Address = ""
        self.ContactPerson = ""
        self.ContactPhone = ""
        self.Email = ""
        self.Status = 1  # 1-启用, 0-禁用
        self.CreatedAt = ""
        self.UpdatedAt = ""


class SchoolsServer:
    """学校服务类 - 数据访问层"""
    
    @staticmethod
    def select_sql_all(status=None):
        """
        查询所有学校
        :param status: 状态筛选 (1-启用, 0-禁用, None-全部)
        :return: 学校列表
        """
        sql = "SELECT * FROM schools"
        if status is not None:
            sql += f" WHERE status = {status}"
        sql += " ORDER BY created_at DESC"
        
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        
        schools = []
        for item in result:
            school = Schools()
            school.Id = item[0]
            school.SchoolName = item[1]
            school.SchoolCode = item[2]
            school.Province = item[3] if item[3] else ""
            school.City = item[4] if item[4] else ""
            school.Address = item[5] if item[5] else ""
            school.ContactPerson = item[6] if item[6] else ""
            school.ContactPhone = item[7] if item[7] else ""
            school.Email = item[8] if item[8] else ""
            school.Status = item[9]
            school.CreatedAt = str(item[10]) if item[10] else ""
            school.UpdatedAt = str(item[11]) if item[11] else ""
            schools.append(school)
        
        return schools
    
    @staticmethod
    def select_sql_by_id(school_id):
        """
        根据ID查询学校
        :param school_id: 学校ID
        :return: 学校对象或None
        """
        sql = f"SELECT * FROM schools WHERE id = {school_id}"
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        
        if result:
            item = result[0]
            school = Schools()
            school.Id = item[0]
            school.SchoolName = item[1]
            school.SchoolCode = item[2]
            school.Province = item[3] if item[3] else ""
            school.City = item[4] if item[4] else ""
            school.Address = item[5] if item[5] else ""
            school.ContactPerson = item[6] if item[6] else ""
            school.ContactPhone = item[7] if item[7] else ""
            school.Email = item[8] if item[8] else ""
            school.Status = item[9]
            school.CreatedAt = str(item[10]) if item[10] else ""
            school.UpdatedAt = str(item[11]) if item[11] else ""
            return school
        
        return None
    
    @staticmethod
    def select_sql_by_code(school_code):
        """
        根据学校代码查询学校
        :param school_code: 学校代码
        :return: 学校对象或None
        """
        sql = f"SELECT * FROM schools WHERE school_code = '{school_code}'"
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        
        if result:
            item = result[0]
            school = Schools()
            school.Id = item[0]
            school.SchoolName = item[1]
            school.SchoolCode = item[2]
            school.Province = item[3] if item[3] else ""
            school.City = item[4] if item[4] else ""
            school.Address = item[5] if item[5] else ""
            school.ContactPerson = item[6] if item[6] else ""
            school.ContactPhone = item[7] if item[7] else ""
            school.Email = item[8] if item[8] else ""
            school.Status = item[9]
            school.CreatedAt = str(item[10]) if item[10] else ""
            school.UpdatedAt = str(item[11]) if item[11] else ""
            return school
        
        return None
    
    @staticmethod
    def insert_sql(school):
        """
        添加学校
        :param school: 学校对象
        :return: 插入的学校ID
        """
        sql = f"""
        INSERT INTO schools (school_name, school_code, province, city, address, 
                           contact_person, contact_phone, email, status)
        VALUES ('{school.SchoolName}', '{school.SchoolCode}', '{school.Province}', 
                '{school.City}', '{school.Address}', '{school.ContactPerson}', 
                '{school.ContactPhone}', '{school.Email}', {school.Status})
        """
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def update_sql(school):
        """
        更新学校信息
        :param school: 学校对象
        :return: 影响的行数
        """
        sql = f"""
        UPDATE schools 
        SET school_name = '{school.SchoolName}',
            school_code = '{school.SchoolCode}',
            province = '{school.Province}',
            city = '{school.City}',
            address = '{school.Address}',
            contact_person = '{school.ContactPerson}',
            contact_phone = '{school.ContactPhone}',
            email = '{school.Email}',
            status = {school.Status}
        WHERE id = {school.Id}
        """
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def delete_sql(school_id):
        """
        删除学校（物理删除）
        注意：由于外键约束，相关的班级会被级联删除
        :param school_id: 学校ID
        :return: 影响的行数
        """
        sql = f"DELETE FROM schools WHERE id = {school_id}"
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def update_status(school_id, status):
        """
        更新学校状态（软删除）
        :param school_id: 学校ID
        :param status: 状态 (1-启用, 0-禁用)
        :return: 影响的行数
        """
        sql = f"UPDATE schools SET status = {status} WHERE id = {school_id}"
        db = MySqlHelper()
        return db.ExecuteNonQuery(sql)
    
    @staticmethod
    def get_statistics(school_id):
        """
        获取学校统计信息
        :param school_id: 学校ID
        :return: 统计字典
        """
        db = MySqlHelper()
        
        # 教师数量
        teacher_sql = f"SELECT COUNT(*) FROM teacher WHERE school_id = {school_id}"
        teacher_count = db.ExecuteQuery(teacher_sql)[0][0]
        
        # 学生数量
        student_sql = f"SELECT COUNT(*) FROM students WHERE school_id = {school_id}"
        student_count = db.ExecuteQuery(student_sql)[0][0]
        
        # 班级数量
        class_sql = f"SELECT COUNT(*) FROM classes WHERE school_id = {school_id}"
        class_count = db.ExecuteQuery(class_sql)[0][0]
        
        # 待审核教师数量
        pending_teacher_sql = f"""
        SELECT COUNT(*) FROM teacher 
        WHERE school_id = {school_id} AND approval_status = 0
        """
        pending_teacher_count = db.ExecuteQuery(pending_teacher_sql)[0][0]
        
        return {
            'teacher_count': teacher_count,
            'student_count': student_count,
            'class_count': class_count,
            'pending_teacher_count': pending_teacher_count
        }
    
    @staticmethod
    def check_code_exists(school_code, exclude_id=None):
        """
        检查学校代码是否已存在
        :param school_code: 学校代码
        :param exclude_id: 排除的学校ID（用于编辑时）
        :return: True-存在, False-不存在
        """
        sql = f"SELECT COUNT(*) FROM schools WHERE school_code = '{school_code}'"
        if exclude_id:
            sql += f" AND id != {exclude_id}"
        
        db = MySqlHelper()
        result = db.ExecuteQuery(sql)
        return result[0][0] > 0
