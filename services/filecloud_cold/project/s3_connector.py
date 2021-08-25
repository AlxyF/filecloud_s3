import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError


load_dotenv()
os.getenv('AWS_SHARED_CREDENTIALS_FILE')
volume_path = os.getenv('VOLUME_FILES')



class s3_connector:
    def __init__(self, region, endpoint, profile, use_ssl, verify_ssl):
        self.region = region
        self.endpoint = endpoint
        self.profile = profile
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl

    def s3_session(self):
        session = boto3.session.Session(profile_name=self.profile)
        s3_client = session.client(
            service_name='s3',
            endpoint_url=self.endpoint,
            use_ssl=self.use_ssl,
            verify=self.verify_ssl
        )
        return s3_client

    def upload_file(self, bucket, name, file):
        self.s3_session().put_object(Bucket=bucket, Key=name, Body=file)

    def create_bucket(self, bucket_name):
        self.s3_session().create_bucket(Bucket=bucket_name)
    
    def check_bucket(self, bucket_name):  
        try:
            self.s3_session().head_bucket(Bucket=bucket_name)
            print("Bucket Exists!")
            return True
        except ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                print("Private Bucket. Forbidden Access!")
                return True
            elif error_code == 404:
                print("Bucket Does Not Exist!")
                return False
