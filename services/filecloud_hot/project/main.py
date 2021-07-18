# importing side libraries
from flask import Flask, Response, request
#from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
# importing default python libraries
import os, sys, time, csv, json, datetime
# importing project modules
from project.config import configuration_class
from project.schemas import schemas
from project.models import models
from project import file_aux
from project import database
from project import s3_connector
load_dotenv()

'''System exit'''
def system_exit(status, error):
    write_log_entry(status, error) 
    sys.exit(4) # gunicorn will stop only with code 4



'''Logger'''
def write_log_entry(log_status,log_message):
    timestamp = time.time()
    return 0


'''Flask app'''
_status = 'Initializing application'
app = Flask(__name__)
app.config['SWAGGER'] = { 'title': 'FileCloudService_s3', 'openapi': '3.0.3' }
app.config['MAX_CONTENT_PATH'] = 255
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 50 Mb


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


'''Schemas preparation'''
openapi_specification = schemas.fetch_openapi_yaml()
upload_schema = schemas.get_scheme(json_api=openapi_specification, schema_name='Upload')
upload_validator = schemas.get_schema_validator(upload_schema)
download_schema = schemas.get_scheme(json_api=openapi_specification, schema_name='Download')
download_validator = schemas.get_schema_validator(download_schema)
swagger = Swagger(app, template=openapi_specification)


'''Responses'''
def response_json(json_string, status, mimetype='application/json'):
    log_status, log_message = status, json_string
    write_log_entry(log_status, log_message)
    return Response(f"{json_string}", status=status, mimetype=mimetype)


'''API routes'''
@app.route('/', methods=['GET'])
def index():
    print('HOME PAGE', flush=True)
    return 'HomePage'


@app.route('/upload', methods=['POST'])
def upload_file():
    global _status, psql_connector
    
    # server time of upload
    timestamp_upload = datetime.datetime.now()

    # measure upload time
    start = time.time()

    # check if request schema is valid
    _status = 'upload_scheme_validation'
    try:
        request_dict = request.form.to_dict()
        validate = schemas.validate_scheme(request_dict, upload_validator)
        if validate != True:
            err = {'Error':''.join([str(i) for i in validate])}
            return response_json(err, status=400)
    except Exception as e:
        return response_json(e, status=500)
 
    # check if at least one of these IDs UCDB_ID,OCDB_ID,SourceID,ContractNumber is present
    _status = 'id_check'
    try:
        upload_IDs_map = dict.fromkeys(upload_IDs, None)
        uploaded_IDs = dict.fromkeys(upload_IDs, None)
        for i in upload_IDs:
            in_request = i in request_dict
            upload_IDs_map[i] = i in request_dict
            if in_request:
                uploaded_IDs[i] = request_dict[i] 
        if all(value == False for value in upload_IDs_map.values()):
            err = {'Error':f'There must be at least one of {upload_IDs} for a file'}
            return response_json(err, status=400)
    except Exception as e:
        return response_json(e, status=500)

    # check if 'File' is present in multipart/form-data
    _status = 'file_check'
    try:
        uploaded_file_name = request.files['File'].filename
        if uploaded_file_name == '':
            err = {'Error':'Empty file name or there is no file named File(Uppercase) in request'}
            return response_json(err, status=400) 
        uploaded_file_bytes, uploaded_file_name = request.files['File'].read(), secure_filename(uploaded_file_name)
    except Exception as e:
        err = {'Error':'There is no file named File(Uppercase) in request'}
        return response_json(err, status=400)

    # check for file extensions in file name
    _status = 'type_check'
    try:
        uploaded_file_extension = uploaded_file_name.rsplit('.', 1)[1].lower()
        if uploaded_file_extension not in allowed_file_extensions:
            err = {'Error':f'.{uploaded_file_extension} file extension is not allowed'}
            return response_json(err, status=415)
    except Exception as e:
        return response_json(e, status=500)

    # check file for base64 decode to binary if needed
    _status = 'base64_check'
    try:
        if file_aux.is_base64(uploaded_file_bytes):
            uploaded_file = file_aux.decode_base64(uploaded_file_bytes)
            uploaded_file_encoding_on_upload = 'base64'
        else:
            uploaded_file = uploaded_file_bytes
            uploaded_file_encoding_on_upload = 'binary'
        uploaded_file_encoding_current = 'binary'
    except Exception as e:
        return response_json(e, status=500)
 
    # check file for mime types
    _status = 'mime_check'
    try:
        file_mime_type = file_aux.get_mime_type(uploaded_file)
        if file_mime_type not in allowed_mime_types:
            err = {'Error':f'{file_mime_type} file type is not allowed'}
            return response_json(err, status=415)
    except Exception as e:
        return response_json(e, status=500)

    # check file size
    _status = 'size_check'
    try:
        file_size_bytes = len(uploaded_file)
        if file_size_bytes > allowed_file_max_size_bytes:
            err = {'Error': 
            (f'Files with size larger than {allowed_file_max_size_bytes} bytes is not allowed, '
            f'uploaded file size is {file_size_bytes} bytes')}
            return response_json(err, status=413)
    except Exception as e:
        return response_json(e, status=500)
  
    # file upload model generation
    _status = 'upload_model'
    try:
        upload = models.UploadModel(required=request.form, File=uploaded_file, UploadedFileName=uploaded_file_name,
        UploadedIDs=uploaded_IDs)

        upload.SizeBytes = file_size_bytes
        upload.FileMimeType = file_mime_type
        upload.FileTypeInfo, upload.FileTypeAuxInfo = file_aux.get_binary_file_info(uploaded_file)
        upload.FileEncodingOnUpload = uploaded_file_encoding_on_upload
        upload.FileEncodingCurrent = uploaded_file_encoding_current
        upload.FileName = uploaded_file_name
        upload.FileExtension = uploaded_file_extension
        
        upload.UploadedDate = timestamp_upload
        upload.LastAcquiredDate = timestamp_upload
    
        for i in upload_IDs_map:
            if upload_IDs_map[i]:
                setattr(upload, i, request.form[f'{i}'])

        upload.InHotStorage = True
        upload.InColdStorage = False
    except Exception as e:
        return response_json(e, status=500)
    
    # logging file and get file id from postgres
    _status = 'get_file_id'
    try:
        upload.sql_injection_save()

        file_info_save_query = f'''
        INSERT INTO {psql_connector.table_main_name}
        ({psql_connector.columns})
        VALUES (DEFAULT, {upload.InHotStorage}, {upload.InColdStorage}, '{upload.UploadedDate}', 
        '{upload.LastAcquiredDate}', {upload.UCDB_ID}, {upload.OCDB_ID}, {upload.SourceID}, 
        {upload.ContractNumber}, '{upload.DocumentType}', '{upload.EDocumentType}', '{upload.SourceSystem}', 
        '{upload.FileName}', '{upload.FileMimeType}','{upload.FileExtension}', {upload.SizeBytes},
        '{upload.ACL}', '{upload.FileEncodingOnUpload}', '{upload.FileEncodingCurrent}',
        '{upload.FileTypeInfo}', '{upload.FileTypeAuxInfo}', '{upload.Description}')
        RETURNING "FileID";
        '''
        upload.FileID = psql_connector.query_fetch_one(file_info_save_query)[0]
    except Exception as e:
        return response_json(e, status=500)

    # save file
    try: 
        with open(os.path.join(volume_path, str(upload.FileID)), "wb") as f:
            f.write(upload.File)
            f.close()
    except Exception as e:
        query_fail_save = f'''
        UPDATE {psql_connector.table_main_name}
        SET "InHotStorage" = False
        WHERE "FileID" = {upload.FileID};
        '''
        psql_connector.query_execute(query_fail_save)
        return response_json(e, status=500)

    # all is OK valid response
    valid_response = {'FileID': upload.FileID}

    end = time.time()
    # write log entry
    print('Time elapsed', end-start)
    return Response(f"{valid_response}", status=200, mimetype='application/json')
   
    
@app.route('/download', methods=['POST'])
def download_file():
    global _status, psql_connector
    # server time of download
    timestamp_download = datetime.datetime.now()

    # measure download time
    start = time.time()

    # check if request schema is valid
    _status = 'download_scheme_validation'
    try:
        request_dict = json.loads(request.data)
        validate = schemas.validate_scheme(request_dict, download_validator)
        if validate != True:
            err = {'Error':''.join([str(i) for i in validate])}
            return response_json(err, status=400)
    except Exception as e:
        return response_json(e, status=500)

    # file download model generation
    _status = 'download_model'
    download = models.DownloadModel(required=request_dict)

    # check if file in hot storage
    query_check_cold = f'''
    SELECT "InColdStorage"
    FROM {psql_connector.table_main_name}
    WHERE "FileID" = {download.FileID}
    '''
    print(psql_connector.query_fetch_one(query_check_cold))
    try: 
        with open(os.path.join(volume_path, str(download.FileID)), "rb") as f:
            valid_response = f.read()
            f.close()
    except Exception as e:
        query_check_cold = f'''
        SELECT "InColdStorage"
        FROM {psql_connector.table_main_name}
        WHERE "FileID" = {download.FileID}
        '''
        if psql_connector.query_fetch_one(query_check_cold) == None:
            return response_json('File with this ID was never uploaded', status=404)
        if psql_connector.query_fetch_one(query_check_cold)[0] == False:
            return response_json('File with this ID was deleted', status=410)
        if psql_connector.query_fetch_one(query_check_cold)[0] == True:
            s3_connector.download_file(download.FileID)

    end = time.time()
    print('Time elapsed', end-start)
    # write log

    return Response(valid_response, status=200, mimetype='application/octet-stream')




# later change to stdout logs
with open(app_config.log_csv_file_name, 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(app_config.log_csv_header)