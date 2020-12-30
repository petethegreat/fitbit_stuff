import os
import json
import logging
import requests
from requests_oauthlib import OAuth2Session
import webbrowser


# with client keys:
#     authorisation code grant flow:
#     https://dev.fitbit.com/build/reference/web-api/oauth2/#authorization-code-grant-flow
#     provides refresh tokens
# without client key:
#     implicit grant flow
#     https://dev.fitbit.com/build/reference/web-api/oauth2/#implicit-grant-flow
#     login/redirect required each time(?)

class FitbitThing(object):
    def __init__(self, token_file="./tokens.json", debug=True):
        self._tokens = None
        self._oauth2_client_key = None
        self._oauth2_client_id = None
        self._client_secret_var = "FITBIT_API_CLIENT_SECRET"
        self._client_id_var = "FITBIT_API_CLIENT_ID"
        self._token_file = token_file
        self._logger = logging.getLogger("fitbit_stuff.FitbitThing")
        self._fitbit_oauth2_authorize = "https://www.fitbit.com/oauth2/authorize"
        self._oauth2_callback_uri = "http://127.0.0.1:8080"

        #logging
        if debug:
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger.setLevel(logging.WARNING)
    ###########################

    def get_client_keys(self):
        print("getting client keys")
        self._oauth2_client_id = os.environ.get(self._client_id_var,None)
        self._oauth2_client_key = os.environ.get(self._client_secret_var,None)
        self.validate_client_keys()
    ###########################

    def validate_client_keys(self):
        if self._oauth2_client_id:
            self._logger.debug("client_id present")
        else:
            self._logger.error("oauth2 client id not found")
            raise ValueError("oauth2 client id not found")

        if self._oauth2_client_key:
            self._logger.debug("client_key present")
        else:
            self._logger.error("oauth2 client key not found")
            raise ValueError("oauth2 client key not found")
    ###########################

    def load_tokens(self):
        pass
    ###########################

    def setup(self):
        """try to load client keys and saved tokens"""
        print("setup")
        print(__name__)
        self._logger.info("setting up...")
        self.get_client_keys()
    ###########################

    def open_authorization_page(self):
        self.validate_client_keys()
        scope = ["activity", "heartrate", "location", "sleep"]

        fitbit_session = OAuth2Session(
            client_id=self._oauth2_client_id,
            scope=scope,
            redirect_uri=self._oauth2_callback_uri,
            state="moose")

        authorization_url, state = fitbit_session.authorization_url(
            self._fitbit_oauth2_authorize)
        # response_type="code"
        self._logger.debug(f"authorization url = {authorization_url}")
        self._logger.debug(f"state = {state}")
        self._logger.debug("opening a browser window")
        webbrowser.open_new(authorization_url)
        self._logger.debug("done opening browser")
        # works
