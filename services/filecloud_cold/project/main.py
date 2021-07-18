from dotenv import load_dotenv
# importing default python libraries
import os, sys, time, csv, json, datetime, threading
# importing project modules
from project.config import configuration_class
from project import database
from project import s3_connector
load_dotenv()


'''System exit'''
def system_exit(status, error):
    write_log_entry(status, error) 
    sys.exit(error) # gunicorn will stop only with code 4


'''Logger'''
def write_log_entry(log_status,log_message):
    timestamp = time.time()
    return 0


'''File volume'''
volume_path = os.getenv('VOLUME_FILES')
try:
    _status = 'Checking volume availability'
    with open(os.path.join(volume_path, "test_file"), "wb") as f:
        f.write(b'\xd0\x91\xd0\xb0\xd0\xb9\xd1\x82\xd1\x8b')
        f.close()
except Exception as e:
    system_exit(_status, e)


'''Configuration'''
def configuration():
    global _status, app_config, allowed_file_extensions, allowed_mime_types, allowed_file_max_size_bytes, upload_IDs
    #if __name__ == '__main__':
    _status = 'configuration'
    # configuration
    try:
        app_config = configuration_class()

        # volume path
        #volume_path = app_config.volume_path

        # restrictions
        allowed_file_extensions = app_config.allowed_file_extensions
        allowed_mime_types = app_config.allowed_mime_types
        allowed_file_max_size_bytes = app_config.allowed_file_max_size_bytes

        # upload id
        upload_IDs = app_config.upload_IDs
    except Exception as e:
        system_exit(_status, e)
configuration()


'''Database connector and checks'''
def database_connector_and_checks():
    global _status, app_config, psql_connector
    # database session
    _status = 'postgresql_session_initialization'
    try:
        psql_connector = database.psql_connector(host=app_config.db_host, user=app_config.db_user, 
        password=app_config.db_password, database=app_config.db_database, table_main_name=app_config.db_table_main_name,
        table_main_columns=app_config.db_table_main_columns)
        psql_connection = psql_connector.create_connection()
        if type(psql_connection) == database.psycopg2.OperationalError:
            system_exit(_status, psql_connection)
        psql_connection = psql_connector.close_connection()
        test_query = psql_connector.test_query()
        if type(test_query) == database.psycopg2.OperationalError or type(test_query) == AttributeError:
            system_exit(_status, test_query)
    except Exception as e:
        system_exit(_status, e)
    # database checks
    _status = 'postgresql_table_check'
    try:
        table_name_exists = None
        table_name_exists = psql_connector.is_table_name_exists(table_name=psql_connector.table_main_name)
    except:
        system_exit(_status, table_name_exists)
    try:
        # if table name does not exists create one
        create_table = None
        if table_name_exists != True:
            create_table = psql_connector.create_table(table_name=psql_connector.table_main_name,
            table_columns=psql_connector.table_main_columns)
    except:
        system_exit(_status, create_table)

    try:
        # if table name exists but not all columns are present create new table _{i} version
        table_exists = psql_connector.is_table_exists(table_name=psql_connector.table_main_name,
        table_columns=psql_connector.table_main_columns)
        if table_exists != True:
            for i in range(1,20):
                check_table = psql_connector.table_main_name + f'_{i}'
                table_exists = psql_connector.is_table_exists(table_name=check_table,
                table_columns=psql_connector.table_main_columns)
                if table_exists:
                    psql_connector.table_main_name = check_table
                    break
        if table_exists != True:
            for i in range(1,20):
                check_name = psql_connector.table_main_name + f'_{i}'
                table_name_exists_aux = psql_connector.is_table_name_exists(table_name=check_name)
                if table_name_exists_aux != True:
                    break
            create_table = psql_connector.create_table(table_name=check_name,
        table_columns=psql_connector.table_main_columns)
            psql_connector.table_main_name = check_name
    except Exception as e:
        system_exit(_status, create_table)
database_connector_and_checks()

check_period = 1
cloud_transfer_timer_s = 30

#def filecloud_cold_start():
#    while True:
#        pass

s3 = s3_connector.s3_client

class FileCloudColdThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(cloud_transfer_timer_s):

            is_in_cloud_query = '''
            SELECT "FileID"
            FROM file_info
            WHERE "InColdStorage" = False
            '''
            print("my thread")
            files_to_cloud = psql_connector.query_fetch_all(is_in_cloud_query)
            print(files_to_cloud)

            for result in files_to_cloud:
                file_id = result[0]
                with open(os.path.join(volume_path, str(file_id)), "rb") as f:
                    file = f.read()
                    f.close()
                #except Exception as e:
                #    print(e)

                s3.put_object(Bucket='test_b', Key=str(file_id), Body=file)
            # call a function


stopFlag = threading.Event()
thread = FileCloudColdThread(stopFlag)
thread.start()
# this will stop the timer
#stopFlag.set()