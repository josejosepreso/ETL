import oracledb
import re
import Core.config as config
from Core.GUI.MessageDialogWindow import MessageDialogWindow

class DBManager:
    def __init__(self, user, pswd):
        self.user = user
        self.pswd = pswd

        if not isinstance(user, str) and not isinstance(pswd, str):
            self.user = user.get_text()
            self.pswd = pswd.get_text()

    def get_user_tables(self):
        tables = []

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)

            with connection.cursor() as cur:
                cur.execute("SELECT TABLE_NAME FROM USER_TABLES")
                for row in cur:
                    tables.append(str(row[0]))
            
            connection.close()
        except Exception as e:
            print(e)
            return None

        return tables

    def get_columns_names(self, table):
        columns = []

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)

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
            connection = oracledb.connect(user=self.user, password=self.pswd, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)

            with connection.cursor() as cur:
                cur.execute(query)
                for col in cur.description:
                    columns.append(str(col[0]))
            
            connection.close()
        except Exception as e:
            return None

        return columns

    def generate_query(self, source, fields, isQuery):
        selectedFields = []
        for k in fields:
            if not isinstance(fields[k], int):
                selectedFields.append(fields[k])
                continue
            
            if fields[k] == 1:
                selectedFields.append(k)

        if len(selectedFields) == 0:
            return None

        del fields

        fields = ""

        for i, field in enumerate(selectedFields):
            fields += field
            if i+1 < len(selectedFields):
                fields += ","
        
        query = "SELECT %s FROM %s"%(fields, source)

        if isQuery:
            source = re.search('from.*', source, flags=re.IGNORECASE|re.DOTALL).group()
            query= "SELECT %s %s"%(fields, source)

        return query

    def get_data(self, source, fields, isQuery):
        data =[]

        query = self.generate_query(source, fields, isQuery)

        if query is None:
            return None

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)

            with connection.cursor() as cur:
                cur.execute(query)

                for row in cur:
                    data.append(row)
            
            connection.close()
        except Exception as e:
            MessageDialogWindow(e)
            return None        

        return data

    def insert(self, source, fields, isQuery, destination, mappings):
        query = self.generate_query(source, fields, isQuery)

        if query is None:
            return None

        info = []
        data = []
        
        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)

            with connection.cursor() as cur:
                cur.execute(query)

                for row in cur.description:
                    info.append(row)

                for row in cur:
                    data.append(row)
            
            connection.close()
        except Exception as e:
            MessageDialogWindow(e)
            return None        

        tomap = []
        columns = "("
        for i, column in enumerate(mappings):
            if mappings[column].strip() != "":
                columns += mappings[column]
                if i < len(mappings) - 1:
                    columns += ","
                tomap.append(i)
        columns += ")"
            
        values = ""
        for row in data:
            values += "("
            for i in tomap:
                if "TYPE_VARCHAR" in str(info[i][1]):
                    values += "'%s'"%(str(row[i]))
                else:
                    values += str(row[i])                    
                if tomap.index(i) != len(tomap) - 1:
                    values += ","
            values += ") "
                
        dml = "INSERT INTO %s "%(destination) + columns + " VALUES " + values

        print(dml)
