from dotenv import load_dotenv
from pathlib import Path
import json, jsonref, jsonschema, yaml
import os
load_dotenv()
config_path = os.getenv('CONFIG_FILES')
config_file_name = 'filecloud_s3_config.yaml'
config_file_path = Path(config_path).joinpath(config_file_name)
default_config_file_path = Path(__file__).with_name('default_config.yaml')


def fetch_yaml(config_file_path):
    '''Fetching yaml o file and converting it into json.'''
    with open(config_file_path, encoding='utf-8') as f:
        json_ = jsonref.loads(json.dumps(yaml.safe_load(f)))
        return json_

if os.path.isfile(config_file_path) == False:
    with default_config_file_path.open() as infile, config_file_path.open('w') as outfile:
        outfile.write(infile.read())

json_config = fetch_yaml(config_file_path)


class configuration_class:
    def __init__(self):
        global config_file_path
        self.host = '0.0.0.0'
        self.port = 5000
        self.log_csv_header = ['timestamp', 'method', 'request_dict', 'last_status', 
        'return_status', 'return_message', 'file_id']
        self.log_csv_file_name = 'logger_file_cloud_s3_hot.csv'
        
        self.json_config = fetch_yaml(config_file_path)

        self.allowed_mime_types = self.json_config['allowed_mime_types']
        self.allowed_file_extensions = self.json_config['allowed_file_extensions']
        self.allowed_file_max_size_bytes = int(self.json_config['allowed_file_max_size_bytes'])
        self.upload_IDs = self.json_config['upload_IDs']

        self.db_table_main_name = self.json_config['db_table_main_name']
        self.db_host = self.json_config['db_host']
        self.db_database = self.json_config['db_database']
        self.db_user =  self.json_config['db_user']
        self.db_password = self.json_config['db_password']
        
        self.db_table_main_columns = self.json_config['db_table_main_columns']

        self.s3_region_name = self.json_config['s3_region']
        self.s3_endpoint = self.json_config['s3_endpoint']
        self.s3_profile = self.json_config['s3_profile']
        self.s3_use_ssl = self.json_config['s3_use_ssl']
        self.s3_verify_ssl = self.json_config['s3_verify_ssl']
        self.s3_transfer_period_seconds = self.json_config['s3_transfer_period_seconds']

    def reload_config(self):
        self.json_config = fetch_yaml(config_file_path)