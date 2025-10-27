# -*- coding: utf-8 -*-
"""
班级模型类（内层包）
用于处理班级信息的数据访问
"""

from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper


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
        self.Status = 1
        self.CreatedAt = ""
        self.UpdatedAt = ""
        self.SchoolName = ""
        self.TeacherName = ""


class ClassesServer:
    """班级服务类 - 数据访问层"""

    @staticmethod
    def _escape(value: str) -> str:
        return (value or "").replace("'", "''")

    @staticmethod
    def _row_to_class(row):
        cls = Classes()
        cls.Id = row[0]
        cls.SchoolId = row[1]
        cls.ClassName = row[2]
        cls.ClassCode = row[3] or ""
        cls.Grade = row[4] or ""
        cls.TeacherId = row[5] or 0
        cls.StudentCount = row[6] or 0
        cls.Description = row[7] or ""
        cls.Status = row[8]
        cls.CreatedAt = row[9]
        cls.UpdatedAt = row[10]
        # 连接列
        if len(row) > 11:
            cls.SchoolName = row[11] or ""
        if len(row) > 12:
            cls.TeacherName = row[12] or ""
        return cls

    @staticmethod
    def select_sql_all(school_id=None, status=None):
        sql = (
            "SELECT c.*, s.school_name, t.Name as teacher_name "
            "FROM classes c "
            "LEFT JOIN schools s ON c.school_id = s.id "
            "LEFT JOIN teacher t ON c.teacher_id = t.Id "
            "WHERE 1=1"
        )
        if school_id:
            sql += f" AND c.school_id = {int(school_id)}"
        if status is not None:
            sql += f" AND c.status = {int(status)}"
        sql += " ORDER BY c.school_id, c.grade, c.class_name"

        db = MySqlHelper()
        db.query(sql, "")
        classes_list = [ClassesServer._row_to_class(r) for r in db.cursor.fetchall()]
        db.end()
        return classes_list

    @staticmethod
    def select_sql_by_id(class_id: int):
        sql = (
            "SELECT c.*, s.school_name, t.Name as teacher_name "
            "FROM classes c "
            "LEFT JOIN schools s ON c.school_id = s.id "
            "LEFT JOIN teacher t ON c.teacher_id = t.Id "
            f"WHERE c.id = {int(class_id)}"
        )
        db = MySqlHelper()
        db.query(sql, "")
        row = db.cursor.fetchone()
        db.end()
        return ClassesServer._row_to_class(row) if row else None

    @staticmethod
    def select_sql_by_school(school_id: int, status: int = 1):
        return ClassesServer.select_sql_all(school_id=school_id, status=status)

    @staticmethod
    def select_sql_by_teacher(teacher_id: int):
        sql = (
            "SELECT c.*, s.school_name, t.Name as teacher_name "
            "FROM classes c "
            "LEFT JOIN schools s ON c.school_id = s.id "
            "LEFT JOIN teacher t ON c.teacher_id = t.Id "
            f"WHERE c.teacher_id = {int(teacher_id)} AND c.status = 1 "
            "ORDER BY c.grade, c.class_name"
        )
        db = MySqlHelper()
        db.query(sql, "")
        classes_list = [ClassesServer._row_to_class(r) for r in db.cursor.fetchall()]
        db.end()
        return classes_list

    @staticmethod
    def insert_sql(cls: 'Classes') -> int:
        teacher_id_str = str(cls.TeacherId) if cls.TeacherId else "NULL"
        sql = f"""
        INSERT INTO classes (school_id, class_name, class_code, grade,
                             teacher_id, description, status)
        VALUES ({int(cls.SchoolId)}, '{ClassesServer._escape(cls.ClassName)}', '{ClassesServer._escape(cls.ClassCode)}',
                '{ClassesServer._escape(cls.Grade)}', {teacher_id_str}, '{ClassesServer._escape(cls.Description)}', {int(cls.Status)})
        """
        db = MySqlHelper()
        db.query(sql, "")
        db.connent.commit()
        new_id = db.cursor.lastrowid if hasattr(db.cursor, 'lastrowid') else 0
        db.end()
        return new_id

    @staticmethod
    def update_sql(cls: 'Classes') -> int:
        teacher_id_str = str(cls.TeacherId) if cls.TeacherId else "NULL"
        sql = f"""
        UPDATE classes
        SET school_id = {int(cls.SchoolId)},
            class_name = '{ClassesServer._escape(cls.ClassName)}',
            class_code = '{ClassesServer._escape(cls.ClassCode)}',
            grade = '{ClassesServer._escape(cls.Grade)}',
            teacher_id = {teacher_id_str},
            description = '{ClassesServer._escape(cls.Description)}',
            status = {int(cls.Status)}
        WHERE id = {int(cls.Id)}
        """
        db = MySqlHelper()
        cnt = db.query(sql, "")
        db.connent.commit()
        db.end()
        return cnt

    @staticmethod
    def delete_sql(class_id: int) -> int:
        sql = f"DELETE FROM classes WHERE id = {int(class_id)}"
        db = MySqlHelper()
        cnt = db.query(sql, "")
        db.connent.commit()
        db.end()
        return cnt

    @staticmethod
    def update_status(class_id: int, status: int) -> int:
        sql = f"UPDATE classes SET status = {int(status)} WHERE id = {int(class_id)}"
        db = MySqlHelper()
        cnt = db.query(sql, "")
        db.connent.commit()
        db.end()
        return cnt

    @staticmethod
    def update_teacher(class_id: int, teacher_id: int) -> int:
        teacher_id_str = str(teacher_id) if teacher_id else "NULL"
        sql = f"UPDATE classes SET teacher_id = {teacher_id_str} WHERE id = {int(class_id)}"
        db = MySqlHelper()
        cnt = db.query(sql, "")
        db.connent.commit()
        db.end()
        return cnt

    @staticmethod
    def update_student_count(class_id: int) -> int:
        sql = f"""
        UPDATE classes
        SET student_count = (
            SELECT COUNT(*) FROM students WHERE class_id = {int(class_id)}
        )
        WHERE id = {int(class_id)}
        """
        db = MySqlHelper()
        cnt = db.query(sql, "")
        db.connent.commit()
        db.end()
        return cnt

    @staticmethod
    def get_students(class_id: int):
        sql = f"""
        SELECT Id, User_Name, Name, Card, Phone, Address
        FROM students
        WHERE class_id = {int(class_id)} AND status = 1
        ORDER BY Name
        """
        db = MySqlHelper()
        db.query(sql, "")
        students = []
        for item in db.cursor.fetchall():
            student = {
                'id': item[0],
                'username': item[1],
                'name': item[2],
                'card': item[3] or "",
                'phone': item[4] or "",
                'address': item[5] or ""
            }
            students.append(student)
        db.end()
        return students

    @staticmethod
    def check_name_exists(school_id: int, class_name: str, exclude_id: int = None) -> bool:
        sql = (
            f"SELECT COUNT(*) FROM classes WHERE school_id = {int(school_id)} "
            f"AND class_name = '{class_name}'"
        )
        if exclude_id:
            sql += f" AND id != {int(exclude_id)}"
        db = MySqlHelper()
        db.query(sql, "")
        row = db.cursor.fetchone()
        db.end()
        return (row[0] if row else 0) > 0
