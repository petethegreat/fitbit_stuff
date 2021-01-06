#!/usr/bin/env python
import logging


from fitbit_stuff.fitbit_authenticator import FitbitAuthenticator
from fitbit_stuff.data_downloader import DataDownloader

def do_stuff():
    # logging - https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook
    logger = logging.getLogger("")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("./fitbit.log", mode="w")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)
    formatter = logging.Formatter('{asctime} - {name} - {message} ', style='{')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    print(__name__)

    logger.debug("logging test")

    ft = FitbitAuthenticator()
    ft.setup()

    dl = DataDownloader(ft)
    dl.get_heartrate("2021-01-01","2020-01-02")




    # activity_root = "https://api.fitbit.com/1/user/{user_id}/activities/date/{date}.json"
    #
    #
    # # try activit
    # logger.debug("getting activity data")
    # user_id = "7NPJ74"
    #
    # url = activity_root.format(user_id=user_id, date="2021-01-04")
    #
    # response = ft.get_resource(url)
    # print(response.json())
    #
    # activities = [
    #     "activities/tracker/activityCalories",
    #     "activities/tracker/steps",
    #     "activities/tracker/distance"]
    # time_series_root = "https://api.fitbit.com/1/user/{user_id}/{activity}/date/{start_date}/{end_date}.json"
    # start_date = "2020-12-01"
    # end_date = "2020-12-31"
    # for ac in activities:
    #     url = time_series_root.format(
    #         user_id=user_id,
    #         activity=ac,
    #         start_date=start_date,
    #         end_date=end_date)
    #     response = ft.get_resource(url)
    #     print(ac)
    #     print(response.json())



if __name__ == "__main__":
    print("doing stuff")
    do_stuff()
