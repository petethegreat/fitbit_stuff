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

        # cannot fetch intraday data for multiple days.
        heart_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date_min}/1d/1min.json"
        # heart_url = f"https://api.fitbit.com/1/user/7NPJ74/activities/heart/date/{date_min}/1d/1min/time/00:00/00:10.json"

        # GET https://api.fitbit.com/1/user/-/activities/heart/date/[date]/1d/[detail-level].json`
        # GET https://api.fitbit.com/1/user/-/activities/heart/date/[date]/1d/[detail-level]/time/[start-time]/[end-time].json


        response = self._authenticator.get_resource(heart_url)
        data = response.json()

        print(data.keys())

        print(data["activities-heart-intraday"]["dataset"][0:10])
        # print(len(data["activities-heart"]))
        # print(data["activities-heart"][index])
        # for index in range(len(data["activities-heart"])):
        #     # dt = ["datetime"]
        #     # val = data["activities-heart"][index]["value"]
        #     print(data["activities-heart"][index])
        # print(data)
