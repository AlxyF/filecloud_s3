from datetime import date

class bucket_logic:
    def __init__(self, s3_connector) -> None:
        self.s3_connector = s3_connector
    
 

    def get_bucket(self):
        today = date.today()
        bucket = str(today)
        if self.s3_connector.check_bucket(bucket) == False:
            self.s3_connector.create_bucket(bucket)
        
        return bucket