class BaseModel:
    def __init__(self, MessageID, MessageDate):
        self.MessageID = MessageID
        self.MessageDate = MessageDate
        
        self.InHotStorage = False
        self.InColdStorage = False


class UploadModel(BaseModel):
    def __init__(self, required, File, UploadedFileName, UploadedIDs):
        super().__init__(required['MessageID'], required['MessageDate'])
        self.SourceSystem = required['SourceSystem']
        self.Description = required['Description']
        self.DocumentType = required['DocumentType']
        self.File = File
        self.UploadedFileName = UploadedFileName
        self.UploadedIDs = UploadedIDs

        self.FileEncodingCurrent = 'NULL'
        self.FileEncodingOnUpload = 'NULL'

        self.FileID = 'NULL'
        self.FileMimeType = 'NULL'
        self.FileTypeInfo = 'NULL'
        self.FileTypeAuxInfo = 'NULL'
        self.FileName = 'NULL'
        self.FileExtension = 'NULL'
        self.SizeBytes = 'NULL'

        self.ACL = {}

        self.UploadedDate = 'NULL'
        self.LastAcquiredDate = 'NULL'

        self.UCDB_ID = 'NULL'
        self.OCDB_ID = 'NULL'
        self.SourceID = 'NULL'
        self.ContractNumber = 'NULL'
        self.EDocumentType = 'NULL'
        self.Description = 'NULL'

        self.EncryptionOnCloud = 'NULL'
    
    def sql_injection_save(self):
        for attribute, value in self.__dict__.items():
            if type(value) == str:
                value = value.replace('"','').replace("'","")


class DownloadModel(BaseModel):
    def __init__(self, required):
        super().__init__(required['MessageID'], required['MessageDate'])
        self.FileID = required['FileID']
        self.Encoding = required['Encoding']
