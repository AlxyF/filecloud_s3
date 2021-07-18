import os
from dotenv import load_dotenv
load_dotenv()
os.getenv('AWS_SHARED_CREDENTIALS_FILE')
volume_path = os.getenv('VOLUME_FILES')
print(os.getenv('AWS_SHARED_CREDENTIALS_FILE'))
import boto3
#import logging
from botocore.exceptions import ClientError


region_name = 'nord1'
api_endpoint = r"https://s3.dtln.ru/"

session = boto3.session.Session(profile_name="dataline")
s3_client = session.client(
    service_name='s3',
    endpoint_url=api_endpoint,
    use_ssl=True,
    verify=False
)


#s = s3_client.list_buckets()
print(os.path.join(volume_path, "my_file.jpg"))

def download_file():
    s3_client.download_file('test_b', 'my_file.jpg', os.path.join(volume_path, "my_file.jpg"))

a = s3_client.download_file('test_b', 'my_file.jpg', os.path.join(volume_path, "my_file.jpg"))
print(a)