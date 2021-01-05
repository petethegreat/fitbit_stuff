"""module for downloading and saving data"""

class DataDownloader(object):
    def __init__(self,authenticator):
        self._authenticator = authenticator
        self.start_date = "2019-09-01"
        self.end_date = None
        self.data_path = "./data"

    def get_dates(self,root)

    def get_heartrate(self):
