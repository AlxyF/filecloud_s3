import queue
from flask import Blueprint, request, current_app as app

from queue import Queue

queue = Queue()

filecloud_api_upload = Blueprint('fileCloud', __name__)


class Subject:
    observer = None

    def __init__(self, observer) -> None:
        self.observer = observer
    def notify(self):
        self.observer.update(self, 'UPLOAD_EVENT')


@filecloud_api_upload.route('/upload', methods=['POST', 'GET'])
def upload_file():

    queue.put(request.form["fileName"])

    return str(queue.get())