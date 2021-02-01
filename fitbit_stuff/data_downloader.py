"""module for downloading and saving data"""

import os
import sys
import datetime
import json
import pandas as pd

# TODO - turn this into an abstract base class,
#  implement it for heartrate
class DataDownloader(object):
    def __init__(self,authenticator, name, start_date = "2021-01-01", data_path="./data", **kwargs):
        self._authenticator = authenticator
        self.start_date = start_date
        self.end_date = kwargs.get("end_date",None)
        self.data_path = data_path
        self.name = name
        # self._out_path_format =
    ###########################


    def download_data(self):
        data_dir = os.path.join(self.data_path, self.name)

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        existing_csv = self.get_existing_files(data_dir)

        start_dt = datetime.datetime.strptime(self.start_date,"%Y-%m-%d")
        end_dt = datetime.datetime.strptime(self.end_date,"%Y-%m-%d") if self.end_date \
            else datetime.datetime.now() +datetime.timedelta(days=-1)

        # print(start_dt)
        # print(end_dt)
        n_days = (end_dt - start_dt).days

        for ii in range(0,n_days):
            the_date = start_dt + datetime.timedelta(days=ii)
            date_str = the_date.strftime("%Y-%m-%d")
            filename = f"{self.name}_{date_str}.csv"
            if filename not in existing_csv:
                print(f"downloading data for {date_str}")
                data = self.get_data_json(date_str)
                self.json_to_csv(data,os.path.join(data_dir,filename))
    ###########################

    def get_existing_files(self,data_dir):
        # get the most recent time series date from data
        # https://stackoverflow.com/a/58121762
        contents =  ( f for f in os.listdir(data_dir) )
        csv_files = [f for f in contents if os.path.isfile(os.path.join(data_dir,f)) and f.endswith(".csv")]
        return csv_files
    ###########################

    def get_data_json(self, date):
        "retrieve data for heartrate in this range"

        # cannot fetch intraday data for multiple days.
        heart_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"
        # heart_url = f"https://api.fitbit.com/1/user/7NPJ74/activities/heart/date/{date_min}/1d/1min/time/00:00/00:10.json"

        # GET https://api.fitbit.com/1/user/-/activities/heart/date/[date]/1d/[detail-level].json`
        # GET https://api.fitbit.com/1/user/-/activities/heart/date/[date]/1d/[detail-level]/time/[start-time]/[end-time].json

        response = self._authenticator.get_resource(heart_url)
        data = response.json()

        # print(data.keys())
        return data
    ###########################

    def json_to_csv(self, data, filepath):

        file_datetime = data["activities-heart"][0]["dateTime"]

        timeseries = data["activities-heart-intraday"]["dataset"]

        df = pd.DataFrame.from_records(timeseries)
        df["datetime"] = file_datetime

        df.to_csv(filepath, columns=["datetime", "time", "value"], header=True, index=False)
    ###########################
