"""module for downloading and saving data"""

import os
import sys
import datetime
import json
import pandas as pd
import logging
from .fitbit_authenticator import FitbitAuthenticator
from typing import List, Dict

from abc import ABC, abstractmethod
# TODO - turn this into an abstract base class,
#  implement it for heartrate
class DataDownloader(ABC):
    """Short summary.

    Parameters
    ----------
    authenticator : FitbitAuthenticator
        authenticator instance, for authenticating with fitbit api
    name : str
        name - determines name/location of the saved data
    start_date : str
        start date for which data should be retrieved, in format "YYYY-MM-DD" (the default is "2021-01-01").
    data_path : type
        directory under which data will be saved (the default is "./data").
    **kwargs : type
        Description of parameter `**kwargs`.

    Attributes
    ----------
    _authenticator : type
        Description of attribute `_authenticator`.
    end_date : type
        Description of attribute `end_date`.
    _logger : type
        Description of attribute `_logger`.
    start_date
    data_path
    name

    """
    def __init__(
        self,
        authenticator: FitbitAuthenticator,
        name: str,
        start_date: str = "2021-01-01",
        data_path="./data",
        **kwargs
    ):
        self._authenticator = authenticator
        self.start_date = start_date
        self.end_date = kwargs.get("end_date",None)
        self.data_path = data_path
        self.name = name
        self._logger = logging.getLogger("fitbit_stuff.data_downloader")
    ###########################

    def download_data(self):
        """Downloads data

        checks that data directory exists, if not then it is created.
        gets the json data, parses and saves it as csv
        Returns
        -------
        type
            Description of returned object.

        Raises
        ------
        ExceptionName
            Why the exception is raised.

        """
        data_dir = os.path.join(self.data_path, self.name)
        self._logger.debug(data_dir)

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # start_dt = datetime.datetime.strptime(self.start_date,"%Y-%m-%d")
        # end_dt = datetime.datetime.strptime(self.end_date,"%Y-%m-%d") if self.end_date \
        #     else (datetime.datetime.now() +datetime.timedelta(days=-1))

        # n_days = (end_dt - start_dt).days

        filename = os.path.join(data_dir, f"{self.name}_{self.start_date}_{self.end_date}.csv")

        data = self.get_data_json(self.start_date,self.end_date)
        self.json_to_csv(data,filename)
    ###########################
    @abstractmethod
    def get_data_json(self, date, date2=None):
        pass


    ###########################
    @abstractmethod
    def json_to_csv(self, data, filepath):
        pass
    ###########################
###########################

class DataDownloaderTS(DataDownloader):
    """Abstract class for downloading time series (intra-day) data

    inherits from DataDownloader. One file is written for each day in the specified date range
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    ###########################

    def download_data(self):
        """Download time series data

        Returns
        -------
        type
            Description of returned object.

        Raises
        ------
        ExceptionName
            Why the exception is raised.

        """
        self._logger.debug(self.data_path)
        self._logger.debug(self.name)
        data_dir = os.path.join(self.data_path, self.name)

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        existing_csv = self.get_existing_files(data_dir)

        start_dt = datetime.datetime.strptime(self.start_date,"%Y-%m-%d")
        end_dt = datetime.datetime.strptime(self.end_date,"%Y-%m-%d") if self.end_date \
            else datetime.datetime.now() +datetime.timedelta(days=-1)

        # self._logger.debug(start_dt)
        # self._logger.debug(end_dt)
        n_days = (end_dt - start_dt).days

        for ii in range(0,n_days):
            the_date = start_dt + datetime.timedelta(days=ii)
            date_str = the_date.strftime("%Y-%m-%d")
            filename = f"{self.name}_{date_str}.csv"
            if filename not in existing_csv:
                self._logger.info(f"downloading data for {date_str}")
                data = self.get_data_json(date_str)
                self.json_to_csv(data,os.path.join(data_dir,filename))
    ###########################

    def get_existing_files(self,data_dir: str) -> List[str]:
        """Gets a list of csv files currently existing in the given directory.

        Parameters
        ----------
        data_dir : str
            name of the directory to check

        Returns
        -------
        List[str]
            list of found filenames

        Raises
        ------
        ExceptionName
            Why the exception is raised.

        """

        # get the most recent time series date from data
        # https://stackoverflow.com/a/58121762
        contents =  ( f for f in os.listdir(data_dir) )
        csv_files = [f for f in contents if os.path.isfile(os.path.join(data_dir,f)) and f.endswith(".csv")]
        return csv_files
    ###########################
###########################

class SleepDataDownloader(DataDownloader):
    """Class for downloading sleep data"""
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
    ###########################

    def get_data_json(self, start_date: str, end_date: str) -> Dict:
        """gets json data for sleep stats.

        Parameters
        ----------
        start_date : str
            start date
        end_date : str
            end date

        Returns
        -------
        Dict
            nested dictionary containing the json data retrieved from fitbit

        Raises
        ------
        ExceptionName
            Why the exception is raised.

        """

        # cannot fetch intraday data for multiple days.
        sleep_url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{start_date}/{end_date}.json"
        # heart_url = f"https://api.fitbit.com/1/user/7NPJ74/activities/heart/date/{date_min}/1d/1min/time/00:00/00:10.json"

        response = self._authenticator.get_resource(sleep_url)
        data = response.json()
        # self._logger.debug(response.text)

        return data
    ###########################

    def json_to_csv(self, data: Dict, filepath: str):
        """Short summary.

        Parameters
        ----------
        data : Dict
            Data, to be saved in csv form
        filepath : str
            where the data should be written

        Returns
        -------
        type
            Description of returned object.

        Raises
        ------
        ExceptionName
            Why the exception is raised.

        """
        self._logger.debug(data.keys())

        records = [ {
            "date" : x["dateOfSleep"],
            "duration_total_ms": x["duration"],
            "efficiency": x["efficiency"],
            "isMainSleep": x["isMainSleep"],
            "light_periods": x["levels"]["summary"]["light"]["count"] if x["levels"]["summary"].get("light") else 0,
            "light_minutes": x["levels"]["summary"]["light"]["minutes"] if x["levels"]["summary"].get("light") else 0,
            "deep_periods": x["levels"]["summary"]["deep"]["count"] if x["levels"]["summary"].get("deep") else 0,
            "deep_minutes": x["levels"]["summary"]["deep"]["minutes"] if x["levels"]["summary"].get("deep") else 0,
            "rem_periods": x["levels"]["summary"]["rem"]["count"] if x["levels"]["summary"].get("rem") else 0,
            "rem_minutes": x["levels"]["summary"]["rem"]["minutes"] if x["levels"]["summary"].get("rem") else 0,
            "wake_periods": x["levels"]["summary"]["wake"]["count"] if x["levels"]["summary"].get("wake") else 0,
            "wake_minutes": x["levels"]["summary"]["wake"]["minutes"] if x["levels"]["summary"].get("wake") else 0}
            for x in data["sleep"] ]
        df = pd.DataFrame.from_records(records)
        df.to_csv(filepath, header=True, index=False)
    ###########################
###########################

class HeartRateTSDownloader(DataDownloaderTS):
    """downloads heart rate intra-day time series"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    ###########################

    def get_data_json(self, date):
        """Gets json data from the heartrate endpoint, for a particular day

        Parameters
        ----------
        date : type
            Description of parameter `date`.

        Returns
        -------
        type
            Description of returned object.

        Raises
        ------
        ExceptionName
            Why the exception is raised.

        """

        # cannot fetch intraday data for multiple days.
        heart_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"
        # heart_url = f"https://api.fitbit.com/1/user/7NPJ74/activities/heart/date/{date_min}/1d/1min/time/00:00/00:10.json"

        response = self._authenticator.get_resource(heart_url)
        data = response.json()

        return data
    ###########################

    def json_to_csv(self, data: Dict, filepath: str):
        """saves data as csv

        Parameters
        ----------
        data : Dict
            Data, to be saved in csv form
        filepath : str
            where the data should be written

        Returns
        -------
        type
            Description of returned object.

        Raises
        ------
        ExceptionName
            Why the exception is raised.

        """

        file_datetime = data["activities-heart"][0]["dateTime"]
        timeseries = data["activities-heart-intraday"]["dataset"]

        df = pd.DataFrame.from_records(timeseries)
        df["datetime"] = file_datetime

        df.to_csv(filepath, columns=["datetime", "time", "value"], header=True, index=False)
    ###########################
###########################
