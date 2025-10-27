from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper

class TestCase(object):
    def __init__(self):
        self.Id = 0
        self.TestContentId = 0
        self.Input = ''
        self.ExpectedOutput = ''
        self.IsPublic = 0  # 1=public sample, 0=private
        self.Points = 1
        self.CaseOrder = 0
        self.Enabled = 1

class TestCaseServer(object):
    table = 'test_cases'

    def _ensure_table(self, mysql: MySqlHelper):
        """Ensure test_cases table exists to avoid runtime errors on fresh setups."""
        sql = (
            "CREATE TABLE IF NOT EXISTS `test_cases` ("
            "  `Id` INT(11) NOT NULL AUTO_INCREMENT,"
            "  `Test_Content_Id` INT(11) NOT NULL,"
            "  `Input` LONGTEXT NOT NULL,"
            "  `Expected_Output` LONGTEXT NOT NULL,"
            "  `Is_Public` TINYINT(1) NOT NULL DEFAULT 0,"
            "  `Points` INT(11) NOT NULL DEFAULT 1,"
            "  `Case_Order` INT(11) NOT NULL DEFAULT 0,"
            "  `Enabled` TINYINT(1) NOT NULL DEFAULT 1,"
            "  PRIMARY KEY (`Id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        )
        try:
            mysql.query(sql, "")
            mysql.connent.commit()
        except Exception:
            # If creation fails, let later queries raise actual error
            pass

    def _row_to_obj(self, row):
        tc = TestCase()
        tc.Id = row[0]
        tc.TestContentId = row[1]
        tc.Input = row[2] or ''
        tc.ExpectedOutput = row[3] or ''
        tc.IsPublic = row[4] or 0
        tc.Points = row[5] or 1
        tc.CaseOrder = row[6] or 0
        tc.Enabled = row[7] or 1
        return tc

    def select_by_content(self, test_content_id, only_enabled=True):
        mysql = MySqlHelper()
        self._ensure_table(mysql)
        sql = f"SELECT Id, Test_Content_Id, Input, Expected_Output, Is_Public, Points, Case_Order, Enabled FROM {self.table} WHERE Test_Content_Id={int(test_content_id)}"
        if only_enabled:
            sql += " AND Enabled=1"
        sql += " ORDER BY Case_Order ASC, Id ASC"
        res = mysql.query(sql, "")
        data = []
        if res > 0:
            for row in mysql.cursor.fetchall():
                data.append(self._row_to_obj(row))
            mysql.end()
        return data

    def select_public_by_content(self, test_content_id, only_enabled=True):
        mysql = MySqlHelper()
        self._ensure_table(mysql)
        sql = f"SELECT Id, Test_Content_Id, Input, Expected_Output, Is_Public, Points, Case_Order, Enabled FROM {self.table} WHERE Test_Content_Id={int(test_content_id)} AND Is_Public=1"
        if only_enabled:
            sql += " AND Enabled=1"
        sql += " ORDER BY Case_Order ASC, Id ASC"
        res = mysql.query(sql, "")
        data = []
        if res > 0:
            for row in mysql.cursor.fetchall():
                data.append(self._row_to_obj(row))
            mysql.end()
        return data

    def select_private_by_content(self, test_content_id, only_enabled=True):
        mysql = MySqlHelper()
        self._ensure_table(mysql)
        sql = f"SELECT Id, Test_Content_Id, Input, Expected_Output, Is_Public, Points, Case_Order, Enabled FROM {self.table} WHERE Test_Content_Id={int(test_content_id)} AND Is_Public=0"
        if only_enabled:
            sql += " AND Enabled=1"
        sql += " ORDER BY Case_Order ASC, Id ASC"
        res = mysql.query(sql, "")
        data = []
        if res > 0:
            for row in mysql.cursor.fetchall():
                data.append(self._row_to_obj(row))
            mysql.end()
        return data

    def insert_sql(self, tc: TestCase):
        mysql = MySqlHelper()
        self._ensure_table(mysql)
        sql = (
            f"INSERT INTO {self.table} (Test_Content_Id, Input, Expected_Output, Is_Public, Points, Case_Order, Enabled) "
            f"VALUES ({int(tc.TestContentId)}, '{self._e(tc.Input)}', '{self._e(tc.ExpectedOutput)}', {int(tc.IsPublic)}, {int(tc.Points)}, {int(tc.CaseOrder)}, {int(tc.Enabled)})"
        )
        mysql.query(sql, "")
        mysql.connent.commit()
        mysql.end()

    def update_sql(self, tc: TestCase):
        mysql = MySqlHelper()
        self._ensure_table(mysql)
        sql = (
            f"UPDATE {self.table} SET "
            f"Input='{self._e(tc.Input)}', Expected_Output='{self._e(tc.ExpectedOutput)}', "
            f"Is_Public={int(tc.IsPublic)}, Points={int(tc.Points)}, Case_Order={int(tc.CaseOrder)}, Enabled={int(tc.Enabled)} "
            f"WHERE Id={int(tc.Id)}"
        )
        mysql.query(sql, "")
        mysql.connent.commit()
        mysql.end()

    def delete_sql(self, id):
        mysql = MySqlHelper()
        self._ensure_table(mysql)
        mysql.query(f"DELETE FROM {self.table} WHERE Id={int(id)}", "")
        mysql.connent.commit()
        mysql.end()

    def delete_by_content(self, test_content_id):
        mysql = MySqlHelper()
        self._ensure_table(mysql)
        mysql.query(f"DELETE FROM {self.table} WHERE Test_Content_Id={int(test_content_id)}", "")
        mysql.connent.commit()
        mysql.end()

    @staticmethod
    def _e(s: str) -> str:
        if s is None:
            return ''
        return s.replace("'", "''").replace("\\", "\\\\")
