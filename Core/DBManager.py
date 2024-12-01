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
            return None

        return columns

    def get_query_columns(self, query):
        columns = []

        try:
            connection = oracledb.connect(user=self.user, password=self.pswd, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)
            with connection.cursor() as cur:
                cur.execute(query)
                for col in cur.description:
                    column = re.compile(re.escape("FROM"), re.IGNORECASE)
                    columns.append(column.sub(" FROM ", str(col[0])))

            connection.close()
        except Exception as e:
            return None

        if len(columns) == 0:
            return None

        for i in range(0, len(columns)):
            m = re.search(r"[A-Za-z]+\." + columns[i], query)
            if m is not None and m.group() != "": columns[i] = m.group()

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
            return 1

        connection = None
        
        tomap = [] # store fields to map positions
        compareColumns = []

        columns = "("
        for column in mappings:
            if mappings[column].strip() != "": # if this source field is mapped to a destination field

                index = list(mappings).index(column)

                compareColumns.append(mappings[column])

                columns += mappings[column]

                if index != len(mappings) - 1:
                    columns += ","

                tomap.append(index)
        columns += ")"

        if len(tomap) == 0:
            return 1

        try:
            connection = oracledb.connect(user=destinUser, password=destinPass, host=config.HOST, port=config.PORT, service_name=config.SERVICE_NAME)
        except Exception as e:
            return 1

        compareValues = []
            
        values = ""
        for row in data:
            for i in tomap:
                value = str(row[i])

                if value == "None":
                    value = "NULL"
                ##
                compareValues.append(value)
                
                dataType = metaData[i][1]

                if "TYPE_VARCHAR" in str(dataType):
                    values += "'%s'"%(value)
                else:
                    values += value
                if tomap.index(i) != len(tomap) - 1:
                    values += ","
                
            dml = """
            INSERT INTO %s %s
            SELECT %s
            FROM DUAL
            WHERE NOT EXISTS (SELECT 1 FROM %s WHERE %s = %s
            """%(destination, columns, values, destination, compareColumns[0], compareValues[0])

            factsTable = re.search("HECHOS", destination, flags=re.IGNORECASE)
            if factsTable is not None and factsTable.group() != "":
                dml += " AND"
                for i in range(1, len(compareValues)):
                    dml += " %s = %s "%(compareColumns[i], compareValues[i])
                    if i < len(compareValues) - 1:
                        dml += "AND"

            dml += ")"

            ######
            redate = re.search(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}", dml)
            if redate is not None and redate.group() != "":
                dml = dml.replace(redate.group(), "TO_DATE('%s','YYYY-MM-DD')"%(redate.group().replace(" 00:00:00", "")))
            ######

            print(dml)

            try:
                with connection.cursor() as cur:
                    cur.execute(dml)
                    connection.commit()
            except Exception as e:
                MessageDialogWindow(str(e) + "\n\nCarga de datos interrumpida.")
                return 1

            values = ""
            compareValues = []

        connection.close()
        return 0
