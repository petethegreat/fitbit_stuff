"""module for downloading and saving data"""

class DataDownloader(object):
    def __init__(self,authenticator):
        self._authenticator = authenticator
        self.start_date = "2020-09-01"
        self.end_date = None
        self.data_path = "./data"

    def get_max_date(self):
        # get the most recent time series date from data
        # https://stackoverflow.com/a/58121762
        pass


    def get_heartrate(self,date_min,date_max):
        "retrieve data for heartrate in this range"
        heart_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date_min}/{date_max}/1min.json"
        response = self._authenticator.get_resource(heart_url)
        data = response.json()
        print(data)
        
