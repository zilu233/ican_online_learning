# OnlineJudgeSystem/model/TestQuestionRelation.py
from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper

class TestQuestionRelation:
    def __init__(self):
        self.id = 0
        self.test_id = 0
        self.question_id = 0
        self.question_type = ''  # 'select' 或 'content'

class TestQuestionRelationServer:
    def insert(self, relation):
        """插入试卷与题目关联关系"""
        mysql = MySqlHelper()
        try:
            sql = "INSERT INTO TestQuestionRelation (test_id, question_id, question_type) VALUES (%s, %s, %s)"
            params = (relation.test_id, relation.question_id, relation.question_type)
            mysql.query(sql, params)
            
            mysql.connent.commit()  # 提交事务
            return True
        except Exception as e:
            print(f"插入关联关系失败: {e}")
            mysql.connent.rollback()  # 回滚事务
            return False
        finally:
            mysql.end()  # 关闭数据库连接
    
    def get_questions_by_test_id(self, test_id):
        """根据试卷ID获取关联的题目"""
        mysql = MySqlHelper()
        try:
            sql = "SELECT question_id, question_type FROM TestQuestionRelation WHERE test_id = %s"
            params = (test_id,)
            mysql.query(sql, params)
            result = mysql.cursor.fetchall()
            questions = []
            for row in result:
                question_id, question_type = row
                questions.append((question_id, question_type))
            return questions
        except Exception as e:
            print(f"查询关联题目失败: {e}")
            return []
        finally:
            mysql.end()
    def delete_by_test_id(self, test_id):
        """删除指定试卷的所有关联关系"""
        mysql = MySqlHelper()
        try:
            sql = "DELETE FROM TestQuestionRelation WHERE test_id = %s"
            params = (test_id,)
            mysql.query(sql, params)
            mysql.connent.commit()  # 提交事务
            return True
        except Exception as e:
            print(f"删除关联关系失败: {e}")
            mysql.connent.rollback()  # 回滚事务
            return False
        finally:
            mysql.end()        