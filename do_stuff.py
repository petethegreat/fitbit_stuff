#!/usr/bin/env python
import logging


from fitbit_stuff.fitbit_thing import FitbitThing

def do_stuff():
    # logging - https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook
    logger = logging.getLogger("")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("./fitbit.log")
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

    ft = FitbitThing()
    ft.setup()
    ft.get_authorization_code()


if __name__ == "__main__":
    print("doing stuff")
    do_stuff()
