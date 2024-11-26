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

        # TODO
        fields = [str(field).lstrip().replace("\n","") for field in re.search(r"(?<=SELECT)(.*?)(?=FROM(?![^()]*\)).*)", query, flags=re.IGNORECASE|re.DOTALL).group().split(",\n")]

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)
            # TODO
            with connection.cursor() as cur:
                cur.execute(query)
                #for col in cur.description:
                #    column = re.compile(re.escape("FROM"), re.IGNORECASE)
                #    columns.append(column.sub(" FROM ", str(col[0])))
                columns = fields

            connection.close()
        except Exception as e:
            print(e)
            return None

        if len(columns) == 0:
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
            source = re.search(r"FROM(?![^()]*\)).*", source, flags=re.IGNORECASE|re.DOTALL).group()
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

    # ugly
    def insert(self, source, fields, isQuery, destination, mappings, destinUser, destinPass):
        query = self.generate_query(source, fields, isQuery)

        if query is None:
            return

        metaData = []
        data = []
        
        connection = None
        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)

            with connection.cursor() as cur:
                cur.execute(query)

                for row in cur.description:
                    metaData.append(row)

                for row in cur:
                    data.append(row)

            connection.close()
        except Exception as e:
            MessageDialogWindow(e)
            return

        connection = None
        
        # store fields to map positions
        tomap = []
        compareColumn = ""

        columns = "("
        for column in mappings:
            if mappings[column].strip() != "": # if this source field is mapped to a destination field

                index = list(mappings).index(column)

                if index == 0:
                    compareColumn = mappings[column]

                columns += mappings[column]

                if index != len(mappings) - 1:
                    columns += ","

                tomap.append(index)
        columns += ")"

        if len(tomap) == 0:
            return

        try:
            connection = oracledb.connect(user=destinUser, password=destinPass, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)
        except Exception as e:
            return

        compareValue = ""
            
        values = ""
        for row in data:
            for i in tomap:
                ##
                if i == 0:
                    compareValue = str(row[i])
                
                dataType = metaData[i][1]
    
                if "TYPE_VARCHAR" in str(dataType):
                    values += "'%s'"%(str(row[i]))
                else:
                    values += str(row[i])                    
                if tomap.index(i) != len(tomap) - 1:
                    values += ","
                
            dml = """
            INSERT INTO %s %s
            SELECT %s FROM DUAL
            WHERE NOT EXISTS (SELECT 1 FROM %s WHERE %s = %s)
            """%(destination, columns, values, destination, compareColumn, compareValue)

            try:
                with connection.cursor() as cur:
                    cur.execute(dml)
                    cur.execute("COMMIT")        
            except Exception as e:
                MessageDialogWindow(str(e) + "\nCarga de datos interrumpida.")
                return

            values = ""

        connection.close()
        MessageDialogWindow("Carga de datos realizada con exito")
