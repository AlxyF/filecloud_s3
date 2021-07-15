class configuration_class:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 5000
        self.volume_path = '/var/filestorage_hot'#'/mnt/c/Users/ALEX/TEST'
    
        #self.volume_path = '/TEST'
        self.allowed_mime_types = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                   'application/pdf',
                                   'image/jpeg'

                                    ]
        self.allowed_file_extensions = ['pdf', 'doc', 'docx', 'png', 'jpeg', 'jpg']
        self.allowed_file_max_size_bytes = 5 * 1024 * 1024 # 5 Mb
        self.upload_IDs = ['UCDB_ID','OCDB_ID','SourceID','ContractNumber']

        self.log_csv_header = ['timestamp', 'method', 'request_dict', 'last_status', 
        'return_status', 'return_message', 'file_id', 'file_encoding', 
        'file_size', 'file_extension', 'file_type']
        self.log_csv_file_name = 'logger_file_cloud_s3_hot.csv'
        
        self.db_host = 'db'#'172.28.16.1' '172.28.19.183'
        self.db_database = 'filecloud_s3'
        self.db_user = 'filecloud'
        self.db_password = 'filecloud'
        

        self.db_table_main_name = 'file_info'
        self.db_table_main_columns = { '"FileID"': 'BIGSERIAL PRIMARY KEY',
                                    '"InHotStorage"': 'BOOLEAN',
                                    '"InColdStorage"': 'BOOLEAN',
                                    '"UploadedDate"': 'TIMESTAMP NOT NULL',
                                    '"LastAcquiredDate"': 'TIMESTAMP NOT NULL',
                                    '"UCDB_ID"': 'BIGINT',
                                    '"OCDB_ID"': 'BIGINT',
                                    '"SourceID"': 'BIGINT',
                                    '"ContractNumber"': 'BIGINT',
                                    '"DocumentType"': 'VARCHAR (50) NOT NULL',
                                    '"EDocumentType"': 'VARCHAR (50)',
                                    '"SourceSystem"': 'VARCHAR (10)',
                                    '"FileName"': 'VARCHAR (50)',
                                    '"MimeType"': 'VARCHAR (50)',
                                    '"FileExtension"': 'VARCHAR (10) NOT NULL',
                                    '"SizeBytes"': 'BIGINT NOT NULL',
                                    '"ACL"': 'JSON NOT NULL',
                                    '"EncodingOnUpload"': 'VARCHAR (10) NOT NULL',
                                    '"EncodingCurrent"': 'VARCHAR (10) NOT NULL',
                                    '"FileTypeInfo"': 'VARCHAR (50) NOT NULL',
                                    '"FileTypeAuxInfo"': 'VARCHAR (255)',
                                    '"Description"': 'VARCHAR (255)', 
                                    }

        #self.db_table_log_file_name = 'filecloud_s3_log'
