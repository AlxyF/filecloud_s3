# importing side libraries
from flask import Flask, Response, request
from flasgger import Swagger
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
# importing default python libraries
from datetime import datetime
import os, sys, time, csv
# importing project modules
from config import configuration_class
from filecloud_api.schemas import schemas
from filecloud_api.models import models
from filecloud_api import file_aux
from filecloud_api import database


'''Flask app'''
_status = 'Initializing application'
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'FileCloudService_s3',
    'openapi': '3.0.3'
}
# hardcode flas restrictions
app.config['MAX_CONTENT_PATH'] = 255
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 50 Mb


'''Schemas preparation'''
openapi_specification = schemas.fetch_openapi_yaml()
upload_schema = schemas.get_scheme(json_api=openapi_specification, schema_name='Upload')
upload_validator = schemas.get_schema_validator(upload_schema)

#download_schema = schemas.get_scheme('Download')


swagger = Swagger(app, template=openapi_specification)
#filecloud_app.config['UPLOAD_FOLDER'] = '/mnt/c/Users/ALEX/var'

'''Logger'''
def write_log_entry(log_status,log_message):
    timestamp = time.time()
    return 0

'''Responses'''
def response_json(json_string, status, mimetype='application/json'):
    log_status, log_message = status, json_string
    write_log_entry(log_status, log_message)
    return Response(f"{json_string}", status=status, mimetype=mimetype)

'''API routes'''
@app.route('/', methods=['GET'])
def index():
    return 'HomePage'


@app.route('/upload', methods=['POST'])
def upload_file():
    global _status
    # measure upload time
    start = time.time()
    
    # check if request schema is valid
    _status = 'scheme_validation'
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
    try:
        _status = 'base64_check'
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
    try:
        _status = 'mime_check'
        file_mime_type = file_aux.get_mime_type(uploaded_file)
        if file_mime_type not in allowed_mime_types:
            err = {'Error':f'{file_mime_type} file type is not allowed'}
            return response_json(err, status=415)
    except Exception as e:
        return response_json(e, status=500)

    # check file size
    try:
        _status = 'size_check'
        if len(uploaded_file) > allowed_file_max_size_bytes:
            err = {'Error': 
            (f'Files with size larger than {allowed_file_max_size_bytes} bytes is not allowed, '
            f'uploaded file size is {len(uploaded_file)} bytes')}
            return response_json(err, status=413)
    except Exception as e:
        return response_json(e, status=500)
  
    # file id and model generation
    upload = models.UploadModel(required=request.form, File=uploaded_file, UploadedFileName=uploaded_file_name,
    UploadedIDs=uploaded_IDs)

    upload.FileMimeType = file_mime_type
    upload.FileTypeInfo, upload.FileTypeAuxInfo = file_aux.get_binary_file_info(uploaded_file)
    upload.FileEncodingOnUpload = uploaded_file_encoding_on_upload
    upload.FileEncodingCurrent = uploaded_file_encoding_current

    upload.set_file_id()

    print(upload.FileID)
    
    # save file 
    with open(os.path.join(volume_path, upload.FileID), "wb") as f:
        f.write(upload.File)
        f.close()

    # post file info into database
    #database.create_table()

    # all is great valid response
    valid_response = {'FileID': upload.FileID}

    # logging file in database
    

    
    # logging filecloud_logs
    end = time.time()
    #print(uploaded_file)
    print('Time elapsed', end-start)
    return Response(f"{valid_response}", status=200, mimetype='application/json')
   
    
    

    


@app.route('/download', methods=['GET'])
def download_file():
    return request.data


def system_exit(status, error):
    write_log_entry(status, error) 
    sys.exit(error)


if __name__ == '__main__':
    _status = 'configuration'
    # configuration
    try:
        app_config = configuration_class()

        # volume path
        volume_path = app_config.volume_path

        # restrictions
        allowed_file_extensions = app_config.allowed_file_extensions
        allowed_mime_types = app_config.allowed_mime_types
        allowed_file_max_size_bytes = app_config.allowed_file_max_size_bytes

        # upload id
        upload_IDs = app_config.upload_IDs
    except Exception as e:
        system_exit(_status, e)

    # later change to stdout logs
    with open(app_config.log_csv_file_name, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(app_config.log_csv_header)

    # database session
    _status = 'postgresql_session_initialization'
    try:
        psql_connector = database.psql_connector(host=app_config.db_host, user=app_config.db_user, 
        password=app_config.db_password, database=app_config.db_database, table_main_name=app_config.db_table_main_name,
        table_main_columns=app_config.db_table_main_columns)
        psql_connection = psql_connector.create_connection()
        if type(psql_connection) == database.psycopg2.OperationalError:
            system_exit(_status, psql_connection)
        test_query = psql_connector.test_query()
        if type(test_query) == database.psycopg2.OperationalError or type(test_query) == AttributeError:
            system_exit(_status, test_query)
    except Exception as e:
        system_exit(_status, e)
    
    # database checks
    _status = 'postgresql_table_check'
    try:
        table_name_exists = psql_connector.is_table_name_exists(table_name=psql_connector.table_main_name)
    except:
        system_exit(_status, table_name_exists)
    try:
        # if table name does not exists create one
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
                    break
            psql_connector.table_main_name = check_table
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

    app.run(debug=True, host=app_config.host, port=app_config.port, threaded=True)



        




    
    
    