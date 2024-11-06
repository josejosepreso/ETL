import oracledb

class DBManager:
    def __init__(self, user, pswd):
        self.user = user.get_text()
        self.pswd = pswd.get_text()

    def get_user_tables(self):
        tables = []

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host="localhost", port=1521, service_name="xe")

            with connection.cursor() as cur:
                cur.execute("SELECT TABLE_NAME FROM USER_TABLES")
                for row in cur:
                    tables.append(str(row).replace("('", "").replace("',)", ""))
            
            connection.close()
        except Exception as e:
            return None

        return tables

    def get_columns_names(self, table):
        columns = []

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host="localhost", port=1521, service_name="xe")

            with connection.cursor() as cur:
                cur.execute("SELECT COLUMN_NAME FROM USER_TAB_COLUMNS WHERE TABLE_NAME = '{table_name}'".format(table_name=table))
                for row in cur:
                    columns.append(str(row).replace("('", "").replace("',)", ""))
            
            connection.close()
        except Exception as e:
            print(e)
            return None

        return columns

    def get_query_columns(self, query):
        columns = []

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host="localhost", port=1521, service_name="xe")

            with connection.cursor() as cur:
                cur.execute(query)
                for col in cur.description:
                    columns.append(str(col[0]))
            
            connection.close()
        except Exception as e:
            return None

        return columns

