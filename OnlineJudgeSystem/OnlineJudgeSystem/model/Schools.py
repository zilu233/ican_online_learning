# -*- coding: utf-8 -*-
"""
学校模型类（内层包）
用于处理学校信息的数据访问
"""

from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper


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
    def _row_to_school(row):
        s = Schools()
        s.Id = row[0]
        s.SchoolName = row[1]
        s.SchoolCode = row[2]
        s.Province = row[3] or ""
        s.City = row[4] or ""
        s.Address = row[5] or ""
        s.ContactPerson = row[6] or ""
        s.ContactPhone = row[7] or ""
        s.Email = row[8] or ""
        s.Status = row[9]
        s.CreatedAt = row[10]
        s.UpdatedAt = row[11]
        return s

    @staticmethod
    def select_sql_all(status=None):
        sql = "SELECT * FROM schools"
        if status is not None:
            sql += f" WHERE status = {int(status)}"
        sql += " ORDER BY created_at DESC"

        db = MySqlHelper()
        db.query(sql, "")
        schools = [SchoolsServer._row_to_school(r) for r in db.cursor.fetchall()]
        db.end()
        return schools

    @staticmethod
    def select_sql_by_id(school_id: int):
        sql = f"SELECT * FROM schools WHERE id = {int(school_id)}"
        db = MySqlHelper()
        db.query(sql, "")
        row = db.cursor.fetchone()
        db.end()
        return SchoolsServer._row_to_school(row) if row else None

    @staticmethod
    def select_sql_by_code(school_code: str):
        sql = f"SELECT * FROM schools WHERE school_code = '{school_code}'"
        db = MySqlHelper()
        db.query(sql, "")
        row = db.cursor.fetchone()
        db.end()
        return SchoolsServer._row_to_school(row) if row else None

    @staticmethod
    def insert_sql(school: 'Schools') -> int:
        sql = f"""
        INSERT INTO schools (school_name, school_code, province, city, address,
                             contact_person, contact_phone, email, status)
        VALUES ('{school.SchoolName}', '{school.SchoolCode}', '{school.Province}',
                '{school.City}', '{school.Address}', '{school.ContactPerson}',
                '{school.ContactPhone}', '{school.Email}', {int(school.Status)})
        """
        db = MySqlHelper()
        db.query(sql, "")
        db.connent.commit()
        new_id = db.cursor.lastrowid if hasattr(db.cursor, 'lastrowid') else 0
        db.end()
        return new_id

    @staticmethod
    def update_sql(school: 'Schools') -> int:
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
            status = {int(school.Status)}
        WHERE id = {int(school.Id)}
        """
        db = MySqlHelper()
        cnt = db.query(sql, "")
        db.connent.commit()
        db.end()
        return cnt

    @staticmethod
    def delete_sql(school_id: int) -> int:
        sql = f"DELETE FROM schools WHERE id = {int(school_id)}"
        db = MySqlHelper()
        cnt = db.query(sql, "")
        db.connent.commit()
        db.end()
        return cnt

    @staticmethod
    def update_status(school_id: int, status: int) -> int:
        sql = f"UPDATE schools SET status = {int(status)} WHERE id = {int(school_id)}"
        db = MySqlHelper()
        cnt = db.query(sql, "")
        db.connent.commit()
        db.end()
        return cnt

    @staticmethod
    def get_statistics(school_id: int):
        db = MySqlHelper()

        def scalar(sql: str) -> int:
            db.query(sql, "")
            row = db.cursor.fetchone()
            return int(row[0]) if row and len(row) > 0 else 0

        t_count = scalar(f"SELECT COUNT(*) FROM teacher WHERE school_id = {int(school_id)}")
        s_count = scalar(f"SELECT COUNT(*) FROM students WHERE school_id = {int(school_id)}")
        c_count = scalar(f"SELECT COUNT(*) FROM classes WHERE school_id = {int(school_id)}")
        p_count = scalar(f"SELECT COUNT(*) FROM teacher WHERE school_id = {int(school_id)} AND approval_status = 0")

        db.end()
        return {
            'teacher_count': t_count,
            'student_count': s_count,
            'class_count': c_count,
            'pending_teacher_count': p_count
        }

    @staticmethod
    def check_code_exists(school_code: str, exclude_id: int = None) -> bool:
        sql = f"SELECT COUNT(*) FROM schools WHERE school_code = '{school_code}'"
        if exclude_id:
            sql += f" AND id != {int(exclude_id)}"

        db = MySqlHelper()
        db.query(sql, "")
        row = db.cursor.fetchone()
        db.end()
        return (row[0] if row else 0) > 0
