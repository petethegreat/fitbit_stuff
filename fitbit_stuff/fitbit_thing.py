import os
import json
import logging
import requests
import requests_oauthlib


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
        self.tokens = None
        self._oauth2_client_key = None
        self._oauth2_client_id = None
        self._client_secret_var = "FITBIT_API_CLIENT_SECRET"
        self._client_id_var = "FITBIT_API_CLIENT_ID"
        self._token_file = token_file
        self._logger = logging.getLogger("fitbit_stuff.FitbitThing")

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
        if self._oauth2_client_id:
            self._logger.debug("client_id retrieved")
        else:
            self._logger.debug("unable to load client id from envorinoment")

        if self._oauth2_client_key:
            self._logger.debug("client_key retrieved")
        else:
            self._logger.debug("unable to load client key from envorinoment")
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
