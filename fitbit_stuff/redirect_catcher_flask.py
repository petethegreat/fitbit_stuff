# some flask stuff to catch the redirect will go here

import flask
import logging
from flask_api import FlaskAPI



def setup_app():
    app = FlaskAPI("flask_oauth2_catcher")

    @app.route("/")
    def hello():
        return "hello, flask app is working"

    return app


def start_catcher():
    app = setup_app()
    app.run(port=8080)


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
