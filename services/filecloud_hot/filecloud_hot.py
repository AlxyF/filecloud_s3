# importing side libraries
from flask import Flask, Response, request
from flasgger import Swagger
from werkzeug.datastructures import FileStorage 
# importing default python libraries
from datetime import datetime
import os, time
# importing project modules
from config import configuration
from filecloud_api.schemas import schemas
from filecloud_api.models import upload_model


'''Flask app'''
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'FileCloudService_s3',
    'openapi': '3.0.3'
}
app.config['MAX_CONTENT_PATH'] = 255
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024


''' Schemas preparation'''
openapi_specification = schemas.fetch_openapi_yaml()
upload_schema = schemas.get_scheme(json_api=openapi_specification, schema_name='Upload')
upload_validator = schemas.get_schema_validator(upload_schema)

#download_schema = schemas.get_scheme('Download')


swagger = Swagger(app, template=openapi_specification)
#filecloud_app.config['UPLOAD_FOLDER'] = '/mnt/c/Users/ALEX/var'



@app.route('/', methods=['POST', 'GET'])
def index():
    return 'HomePage'


@app.route('/upload', methods=['POST'])
def upload_file():
    start = time.time()
    # validate schema 
    validate = schemas.validate_scheme(request.form.to_dict(), upload_validator)
    if validate != True:
        err = {'Error':''.join([str(i) for i in validate])}
        return Response(f"{err}", status=400, mimetype='application/json')
    # check if 'File' is present
    try:
        uploaded_file = request.files['File']
    except:
        err = {'Error':'Where is no file named File(Uppercase) in request'}
        return Response(f"{err}", status=400, mimetype='application/json')

    
    
    # check file for base64

    # check decoded version of file for formats

    # file id generation
    file_id = 999


    # all is great valid response
    valid_response = {'FileID':file_id}

    # logging file in database

    # logging filecloud_logs
    end = time.time()
    print('Time elapsed', end-start)
    return Response(f"{valid_response}", status=200, mimetype='application/json')
    #if uploaded_file.filename != '':
    #    uploaded_file.save(os.path.join(volume_path, secure_filename(uploaded_file.filename)))
    
    
    #validate(instance=)
    #print(request.headers)
    #ry:
    #    validator.is_valid(request.form.to_dict())
    #    #jsonschema.validate(instance=request.form.to_dict(), schema=upload_schema)
    #except jsonschema.exceptions.ValidationError as e:
    #    print(e)

    #print(request.form.to_dict())
    


@app.route('/download', methods=['GET'])
def download_file():
    return request.data


if __name__ == '__main__':
    app_config = configuration()
    volume_path = app_config.volume_path
    app.run(debug=True, host=app_config.host, port=app_config.port, threaded=True)



        




    
    
    