import oracledb

class DBManager:
    def __init__(self, user, pswd, url):
        self.user = user
        self.pswd = pswd
        self.url = url

    def get_user_tables(self):
        # connection = oracledb.connect(user="C##BD_BICICLETAS", password="oracle", host="localhost", port=1521, service_name="xe")

        tables = []

        try:

            connection = oracledb.connect(user=self.user, password=self.pswd, host="localhost", port=1521, service_name="xe")

            with connection.cursor() as cur:
                cur.execute("SELECT TABLE_NAME FROM USER_TABLES")
                for row in cur:
                    tables.append(str(row).replace("('", "").replace("',)", ""))
            
            connection.close()
        except Exception:

            print("Error conectando a base de datos")
            return []

        return tables
