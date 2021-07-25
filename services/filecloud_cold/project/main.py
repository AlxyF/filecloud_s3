from dotenv import load_dotenv
# importing default python libraries
import os, sys, time, csv, json, datetime, threading
# importing project modules
from project.config import configuration_class
from project import database
from project import s3_connector
from project import bucket_logic
load_dotenv()


'''System exit'''
def system_exit(status, error):
    write_log_entry(status, error, 'ERROR') 
    sys.exit(error) # gunicorn will stop only with code 4


'''Logger'''
logs_path = os.getenv('LOG_FILES')
def write_log_entry(log_status, log_message, log_level):
    timestamp = str(datetime.datetime.now())
    today = datetime.date.today()

    log_message = str(log_message)[0:str(log_message).find(r'\n')] + '"}'

    log_entry = 'filecloud_hot ' + f'{timestamp}, {log_level}, {log_status}: {log_message}'

    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
    with open(os.path.join(logs_path, f"{today}"), 'w+', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow([log_entry]) 

    print(log_entry)
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
    global _status, app_config, allowed_file_extensions, \
    allowed_mime_types, allowed_file_max_size_bytes, upload_IDs, \
    s3_region, s3_endpoint, s3_profile, s3_use_ssl, s3_verify_ssl, s3_transfer_period_seconds
    #if __name__ == '__main__':
    _status = 'configuration'
    # configuration
    #try:
    app_config = configuration_class()
    # restrictions
    allowed_file_extensions = app_config.allowed_file_extensions
    allowed_mime_types = app_config.allowed_mime_types
    allowed_file_max_size_bytes = app_config.allowed_file_max_size_bytes
    upload_IDs = app_config.upload_IDs
    #s3
    s3_region = app_config.s3_region_name
    s3_endpoint = app_config.s3_endpoint
    s3_profile = app_config.s3_profile
    s3_use_ssl = app_config.s3_use_ssl
    s3_verify_ssl = app_config.s3_verify_ssl

    s3_transfer_period_seconds = app_config.s3_transfer_period_seconds
    #except Exception as e:
    #    system_exit(_status, e)
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


class FileCloudColdThread(threading.Thread):
    def __init__(self, s3, bucket_logic_, period, event):
        threading.Thread.__init__(self)
        self.s3 = s3
        self.stopped = event
        self.bucket_logic_ = bucket_logic_
        self.period = period

    def run(self):
        while not self.stopped.wait(self.period):

            is_in_cloud_query = f'''
            SELECT "FileID"
            FROM {app_config.db_table_main_name}
            WHERE "InColdStorage" = False
            '''
            files_to_cloud = psql_connector.query_fetch_all(is_in_cloud_query)

            for result in files_to_cloud:
                file_id = result[0]
                with open(os.path.join(volume_path, str(file_id)), "rb") as f:
                    file = f.read()
                    f.close()  
                #except Exception as e:
                #    print(e)
                bucket = self.bucket_logic_.get_bucket()
                self.s3.upload_file(bucket=bucket, name=str(file_id), file=file)
                
def filecloud_cold_start():
    s3 = s3_connector.s3_connector(region=s3_region, endpoint=s3_endpoint, profile=s3_profile,
    use_ssl=s3_use_ssl, verify_ssl=s3_verify_ssl)

    bucket_logic_ = bucket_logic.bucket_logic(s3_connector=s3)

    stopFlag = threading.Event()
    thread = FileCloudColdThread(s3, bucket_logic_, s3_transfer_period_seconds, stopFlag)
    thread.start()