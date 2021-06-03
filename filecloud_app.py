from flask import Flask, Blueprint, app, request, current_app

from datetime import datetime

from flask.globals import request

from filecloud_api.methods import upload as upload
import threading

class observer:
    def update(self, arg):
        print(arg) 


obs1 = observer()
upload_sub = upload.Subject(observer=obs1)


PORT = 5000
HOST = '0.0.0.0'


#@filecloud_app.route('/', methods=['POST', 'GET'])
def index():
    return 'HomePage'




#@filecloud_app.route('/upload', methods=['DELETE', 'GET'])
def delete_file():
    return request.data

#@filecloud_app.route('/upload', methods=['GET'])
def download_file():
    return request.data


def create_app():
    app = Flask(__name__)
    #app config
    #swagger
    app.register_blueprint(upload.filecloud_api_upload, url_prefix='/fileCloud')
    return app


if __name__ == '__main__':
    #from argparse import ArgumentParser

    #parser = ArgumentParser()
    #parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    #args = parser.parse_args()
    #port = args.port
    

    filecloud_app = create_app()

    filecloud_app.run(debug=True, host=HOST, port=PORT, threaded=True)



        



    
    
    