# some flask stuff to catch the redirect will go here

import flask
from flask import request
import logging
from flask_api import FlaskAPI

logger = logging.getLogger(__name__)

def stop_app():
    pass

def setup_app():
    app = FlaskAPI("flask_oauth2_catcher")
    logger.debug("setting up app")

    @app.route("/")
    def get_auth_code():
        logger.debug("request received")
        the_auth_code = request.args.get("code", None)
        the_state = request.args.get("state", None)
        if the_auth_code:
            auth_code = the_auth_code
            logger.debug("auth code parsed")
            return f"the auth code = \"{the_auth_code}\""
        else:
            logger.debug("auth code not retrieved")
            return "could not parse authorisation code"
    return app


def start_catcher():
    auth_code = None
    app = setup_app()
    # app.run should happen in a thread
    # the interval/logging stuff can happen here ("main thread")
    app.run(port=8080)
    return auth_code

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

if __name__ == "__main__":
    start_catcher()
