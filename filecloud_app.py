#importing side libraries
from flask import Flask, request
from jsonschema import validate
from werkzeug.utils import secure_filename # later remove as naming is done by ID preparation
from werkzeug.datastructures import FileStorage 
from flasgger import Swagger
#importing default python libraries
from datetime import datetime
import os
#importing project modules
from config import configuration
from filecloud_api.schemas import schemas
from filecloud_api.models import upload_model


upload_schema = schemas.get_scheme('upload')
download_schema = schemas.get_scheme('download')


PORT = 5000
HOST = '0.0.0.0'
#os.chmod('/var/', 0o777)
#if not os.path.exists('/var/TEST'):
#    os.makedirs('/var/TEST')
#uploads_dir = '/TEST/'
uploads_dir = '/mnt/c/Users/ALEX/TEST'


filecloud_app = Flask(__name__)

swagger = Swagger(filecloud_app)
#filecloud_app.config['UPLOAD_FOLDER'] = '/mnt/c/Users/ALEX/var'
filecloud_app.config['MAX_CONTENT_PATH'] = 255
filecloud_app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
filecloud_app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
#app config
#swagger
#app.register_blueprint(upload.filecloud_api_upload, url_prefix='/fileCloud')


@filecloud_app.route('/', methods=['POST', 'GET'])
def index():
    return 'HomePage'

@filecloud_app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['File']
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(uploads_dir, secure_filename(uploaded_file.filename)))
    #validate(instance=)
    #print(request.json)
    #print(request.headers)
    print(validate(instance=request.form.to_dict(), schema=upload_schema))
    #print(request.form.to_dict())
    return 'Hi'



#@filecloud_app.route('/upload', methods=['GET'])
def download_file():
    return request.data





if __name__ == '__main__':
    filecloud_s3_hot

    filecloud_app.run(debug=True, host=HOST, port=PORT, threaded=True)



        



    
    
    