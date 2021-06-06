from flask import Flask, Blueprint, app, request, current_app, jsonify
from datetime import datetime
from flask.globals import request
import os
# later remove as naming is done by ID preparation
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

from flasgger import Swagger

from jsonschema import validate 
#from schema import Schema, And, Use, Optional, SchemaError


from filecloud_api.schemas import schemas 

#upload_schema = schemas.upload.json

upload_schema = schemas.get_scheme('upload')
download_schema = schemas.get_scheme('download')


filecloud_app = None
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
    #from argparse import ArgumentParser
    #parser = ArgumentParser()
    #parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    #args = parser.parse_args()
    #port = args.port

    filecloud_app.run(debug=True, host=HOST, port=PORT, threaded=True)



        



    
    
    