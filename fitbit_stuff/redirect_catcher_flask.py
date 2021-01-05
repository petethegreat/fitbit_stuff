# some flask stuff to catch the redirect will go here

import flask
from flask import request
import logging
from flask_api import FlaskAPI
from threading import Thread
import time
import requests

logger = logging.getLogger(__name__)

acode_state = None

def setup_app(route, shutdown_route):
    "defaults to '/'"
    app = FlaskAPI("fitbit_stuff")
    logger.debug("setting up app")

    @app.route(route)
    def get_auth_code():
        global acode_state
        logger.debug("request received")
        the_auth_code = request.args.get("code", None)
        the_state = request.args.get("state", None)
        if the_auth_code:
            acode_state = (the_auth_code, the_state)
            logger.debug("auth code parsed")
            shutdown()
            return f"Authorization code retrieved, you may close this window."
        else:
            logger.debug("auth code not retrieved")
            shutdown()
            return "could not parse authorisation code"

    @app.route(shutdown_route)
    def shutdown():
        "stop the flask dev server"
        # https://werkzeug.palletsprojects.com/en/1.0.x/serving/
        # https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        logger.debug("shutting down werkzeug server")
        func()
        return "shutting down"
    return app





def await_callback(app,port):
    app.run(port=port)


def start_catcher(*args,**kwargs):
    # this function is run by the main thread
    # spawns a child thread, in which the server runs
    route = kwargs.get("route","/")
    shutdown_route = kwargs.get("shutdown_route","/shutdown")
    port = kwargs.get("port",8080)
    check_interval = kwargs.get("check_interval", 0.2)
    log_interval = kwargs.get("log_interval", 5.0)
    timeout = kwargs.get("timeout", 30.0)


    app = setup_app(route, shutdown_route)
    # app.run should happen in a thread
    # the interval/logging stuff can happen here ("main thread")
    logger.debug("start_catcher - starting thread")

    server_thread = Thread(target=await_callback,args=(app,port))
    begin = time.time()
    server_thread.setDaemon(True)
    server_thread.start()
    time_since_log = 9000
    while not acode_state:
        now = time.time()
        if (now - begin) > timeout:
            logger.warning(
                f"elapsed = {now - begin}, timeout = {timeout}, shutting down")
            r = requests.get(f"http://127.0.0.1:{port}{shutdown_route}")
            break
        if time_since_log > log_interval:
            logger.debug(f"elapsed = {now - begin} - waiting")
            logger.debug(f"acode_state = {acode_state}")
            time_since_log = 0
        time.sleep(check_interval)
    # end while loop
    # should exit when timeout is hit or acode_state is updated

    # join the thread
    # server_thread.join()

    return acode_state

# def await_callback(*args,**kwargs):
#     logger = logging.getLogger("fitbit_stuff.await_callback")
#     logger.debug("await_callback - starting")
#     check_interval = kwargs.get("check_interval", 0.2)
#     log_interval = kwargs.get("log_interval", 5.0)
#     timeout = kwargs.get("timeout", 120.0)
#     redirect_uri = kwargs.get("redirect_uri","blah")

    # begin = time.clock()
    # elapsed = 0
    # while elapsed < timeout:

    # spin up flask here, app.run
    # this function returns either when a request is made to the callback
    # or when timeout is reached.

    # this function may run in a thread.
    # Or maybe the timing/waiting goes in the main thread.

# TODO:
  # - add docstrings
  # - consolidate logging
  # - other pep8

if __name__ == "__main__":
    start_catcher()
