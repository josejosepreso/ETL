import oracledb
import re

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
                for col in cur:
                    columns.append(str(col[0]))
            
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

    def get_data(self, source, fields, isQuery):
        data =[]

        selectedFields = []
        for k in fields:
            if fields[k] == 1:
                selectedFields.append(k)

        del fields

        fields = str(selectedFields).replace("[","").replace("]","").replace("'","")
        
        query = "SELECT %s FROM %s"%(fields, source)

        if isQuery:
            query = source

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host="localhost", port=1521, service_name="xe")

            with connection.cursor() as cur:
                cur.execute(query)

                for row in cur:
                    data.append(row)
            
            connection.close()
        except Exception as e:
            return None        

        return data
