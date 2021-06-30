

class BaseModel:
    def __init__(self, MessageID, MessageDate):
        self.MessageID = MessageID
        self.MessageDate = MessageDate



class UploadModel(BaseModel):
    def __init__(self, required, File, UploadedFileName, UploadedIDs):
        super().__init__(required['MessageID'], required['MessageDate'])
        self.SourceSystem = required['SourceSystem']
        self.Description = required['Description']
        self.DocumentType = required['DocumentType']
        self.File = File
        self.UploadedFileName = UploadedFileName
        self.UploadedIDs = UploadedIDs

        self.FileEncodingCurrent = None
        self.FileEncodingOnUpload = None

        self.FileID = None
        self.FileMimeType = None
        self.FileTypeInfo = None
        self.FileTypeAuxInfo = None

        

    def set_file_id(self):
        file_id = ''
        for ID in self.UploadedIDs:
            if self.UploadedIDs[ID] != None:
                file_id = file_id + '_' + str(self.UploadedIDs[ID])
        self.FileID = file_id.strip('_')