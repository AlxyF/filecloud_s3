import psycopg2, time



class psql_connector:
    def __init__(self, host, user, password, database, table_main_name, table_main_columns:dict):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.database = database
        self.table_main_name = table_main_name
        self.table_main_columns = table_main_columns
        self.columns = ''.join([str(item) + ', ' for item in list(self.table_main_columns.keys())]).strip(', ')
        self.time_idle = 0
        self.connection = None

        #if self.is_table_exists(self.table_main_name, self.table_main_columns) == False:
        #    self.create_table(self.table_main_name)
        
    def create_connection(self):
        try:
            connection = psycopg2.connect(dbname=self.database, user=self.user, 
                                password=self.password, host=self.host)
            self.connection = connection
            self.connection.autocommit = False
            return connection
        except (Exception, psycopg2.DatabaseError) as e:
            return e

    def close_connection(self):
        try:
            self.connection.close()
        except (Exception, psycopg2.DatabaseError) as e:
            return e

    def is_db_available(self):
        try:
            conn = psycopg2.connect(dbname=self.database, user=self.user, 
                                password=self.password, host=self.host)
            cursor = conn.cursor()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            return e

    def test_query(self):
        try:
            self.create_connection()
            test_query = 'select 1;'
            cursor = self.connection.cursor()
            cursor.execute(test_query)
            cursor.close()
            self.connection.commit()
            self.close_connection()
            return True
        except (Exception, psycopg2.DatabaseError, AttributeError ) as e:
            return e

    def query_execute(self, query):
        try:
            self.create_connection()
            cursor = self.connection.cursor()
            cursor.execute(query)
            cursor.close()
            self.connection.commit()
            self.close_connection()
            return True
        except (Exception, psycopg2.DatabaseError, AttributeError) as e:
            self.connection.rollback()
            return e

    def query_fetch_all(self, query):
        try:
            self.create_connection()
            cursor = self.connection.cursor()
            cursor.execute(query)
            fetch = cursor.fetchall()
            cursor.close()
            self.connection.commit()
            self.close_connection()
            return fetch
        except (Exception, psycopg2.DatabaseError, AttributeError) as e:
            self.connection.rollback()
            return e

    def query_fetch_one(self, query):
        try:
            self.create_connection()
            cursor = self.connection.cursor()
            cursor.execute(query)
            fetch = cursor.fetchone()
            cursor.close()
            self.connection.commit()
            self.close_connection()
            return fetch
        except (Exception, psycopg2.DatabaseError, AttributeError) as e:
            self.connection.rollback()
            return e

    def create_table(self, table_name, table_columns):
        """ create table in the PostgreSQL database"""
        columns = str(table_columns).replace(':','').replace("'",'').strip('}').strip('{').replace(',',',\n')
        query = f"""
        CREATE TABLE {table_name} (
        {columns}
        );
        """
        q = self.query_execute(query)
        if q == True:
            return True
        else:
            return q

    def is_table_name_exists(self, table_name):
        '''Checks if table name exists'''
        query = f'''
            select * from {table_name};
        '''
        q = self.query_execute(query)
        if q == True:
            return True
        else:
            return q

    def is_table_exists(self, table_name, table_columns):
        '''Checks if table exists'''
        query = f'''
            select {self.columns} from {table_name};
        '''
        if self.query_execute(query) == True:
            return True
        else:
            return False
