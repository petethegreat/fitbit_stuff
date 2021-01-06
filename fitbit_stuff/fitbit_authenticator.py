"""fitbit_authenticator - Class for authenticating and making requests through fitbit api"""

import os
import json
import logging
import webbrowser
from typing import Tuple, Dict
import time
import math

import requests
from requests_oauthlib import OAuth2Session
from .redirect_catcher_flask import start_catcher
from oauthlib.oauth2 import WebApplicationClient
from requests.auth import HTTPBasicAuth

# with client keys:
#     authorisation code grant flow:
#     https://dev.fitbit.com/build/reference/web-api/oauth2/#authorization-code-grant-flow
#     provides refresh tokens
# without client key:
#     implicit grant flow
#     https://dev.fitbit.com/build/reference/web-api/oauth2/#implicit-grant-flow
#     login/redirect required each time(?)


class FitbitAuthenticator(object):
    """Class for authenticating and making requests through fitbit api"""
    def __init__(self, token_file: str="./tokens.json", debug: bool=True):
        """Short summary.

        Parameters
        ----------
        token_file : str
            json file in which token info will be stored (the default is "./tokens.json").
        debug : bool
            If true, log level will be set to debug, else warning

        Returns
        -------
        FitbitAuthenticator
            instance of class.

        """

        self._tokens = None
        self._oauth2_client_secret = None
        self._oauth2_client_id = None
        self._client_secret_var = "FITBIT_API_CLIENT_SECRET"
        self._client_id_var = "FITBIT_API_CLIENT_ID"
        self._token_file = token_file
        self._logger = logging.getLogger("fitbit_stuff.FitbitAuthenticator")
        self._fitbit_oauth2_authorize = "https://www.fitbit.com/oauth2/authorize"
        self._fitbit_oauth2_token_url = "https://api.fitbit.com/oauth2/token"
        self._oauth2_callback_uri = "http://127.0.0.1:8080"
        self._oauth2_session = None

        #logging
        if debug:
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger.setLevel(logging.WARNING)
    ###########################

    def setup(self):
        """load keys and tokens, authenticate if needed"""

        print("setup")
        print(__name__)
        self._logger.info("setting up...")
        self.load_tokens()

        self.get_client_keys()
        self.setup_oauth2_session()

        # acode = self.get_authorization_code()
        # token = self.get_access_refresh_token(acode)

        # refresh if needed force a refresh
        if self._tokens:
            # expires_in should be current
            if self._tokens.get("expires_in",0) < 10:
                self._logger.debug("manual token refresh")
                self.refresh_token()
        else:
            # no tokens, obtain authorisation
            acode = self.get_authorization_code()
            token = self.get_access_refresh_token(acode)
        # at this point, we should be authorised

        msg = f"session authorized: {self._oauth2_session.authorized}"
        self._logger.debug(msg)

    ###########################

    def setup_oauth2_session(self):
        """Sets up the oauth2 session object
        """

        self._oauth2_session = OAuth2Session(
            client_id=self._oauth2_client_id,
            redirect_uri=self._oauth2_callback_uri,
            token_updater=self.save_tokens,
            auto_refresh_url=self._fitbit_oauth2_token_url,
            token=self._tokens
            )

        msg = f"session authorised: {self._oauth2_session.authorized}"
        self._logger.debug(msg)
        msg = f"current time: {time.time()}"
        self._logger.debug(msg)
        print(self._tokens)

#         client = OAuth2Session(client_id, token=token, auto_refresh_url=refresh_url,
# ...     auto_refresh_kwargs=extra, token_updater=token_saver)

    ###########################

    def get_client_keys(self):
        """look up client id and secret from environment.

        client secret and id are expected to be found in environment variables
        FITBIT_API_CLIENT_SECRET and FITBIT_API_CLIENT_ID, respectively.

        Raises
        ------
        ValueError
            ValueError is raised if either environment variable cannot be found

        """
        print("getting client keys")
        self._oauth2_client_id = os.environ.get(self._client_id_var,None)
        self._oauth2_client_secret = os.environ.get(self._client_secret_var,None)
        self.validate_client_keys()
    ###########################

    def validate_client_keys(self):
        """Checks that client id and secret are present

        Raises
        ------
        ValueError
            ValueError is raised if either environment variable cannot be found

        """
        if self._oauth2_client_id:
            self._logger.debug("client_id present")
        else:
            self._logger.error("oauth2 client id not found")
            raise ValueError("oauth2 client id not found")

        if self._oauth2_client_secret:
            self._logger.debug("client_key present")
        else:
            self._logger.error("oauth2 client key not found")
            raise ValueError("oauth2 client key not found")
    ###########################

    def load_tokens(self):
        """load tokens, if token file is present

        Raises
        ------
        json.JSONDecodeError
            raised if token file contains invalid json

        """

        try:
            with open(self._token_file, "r") as tfile:
                tokens = json.load(tfile)
                # requests_oauthlib needs expires_in
                # update this, based on __expires_at

                if "__expires_at" not in tokens:
                    self._logger.debug("__expires_at not in tokens")
                if "__expires_at" in tokens and "expires_in" in tokens:
                    expiry = tokens.pop("__expires_at")
                    tokens["expires_in"] = math.floor(expiry - time.time())
                self._tokens = tokens
                self._logger.debug(tokens)

        except IOError:
            self._logger.debug("token file not found")
    ###########################

    def save_tokens(self, tokens):
        """save tokens"""
        out_dict = tokens.copy()

        if "expires_at" in out_dict:
            self._logger.debug("saving token, contains 'expires_at'")
            out_dict["__expires_at"] = out_dict["expires_at"]
        elif "expires_in" in out_dict:
            out_dict["__expires_at"] = math.floor(time.time() + out_dict["expires_in"])
            self._logger.debug("saving token, using expires_in")

        try:
            with open(self._token_file, "w") as tfile:
                json.dump(out_dict,tfile)
        except IOError as e:
            self._logger.debug("could not write to token file")
            raise e
    ###########################

    def refresh_token(self):
        """ manually refresh """
        auth_tuple = HTTPBasicAuth(self._oauth2_client_id, self._oauth2_client_secret)
        new_tokens = self._oauth2_session.refresh_token(self._fitbit_oauth2_token_url, auth=auth_tuple)
        self.save_tokens(new_tokens)
        self._tokens = new_tokens
    ###########################



    def get_resource(self, endpoint_url):
        """try to get data"""
        response = self._oauth2_session.get(endpoint_url)
        return response
    ###########################

    def get_authorization_code(self) -> Tuple[str, str]:
        """Authenticates with fitbit api

        If a current access or refresh token are not available, Authenticates
        with fitbit to retrieve an authorisation code, through
        authorisation code grant flow
        https://dev.fitbit.com/build/reference/web-api/oauth2/#authorization-code-grant-flow

        Returns
        -------
        acode_state: Tuple[str,str]
            Tuple in which first element is the authorisation code, second is the session state

        Raises
        ------
        RuntimeError
            Raised if authorisation code can not be retrieved, or if the
            returned state does not match that suplied.

        """
        self.validate_client_keys()
        if not self._oauth2_session.scope:
            self._oauth2_session.scope = ['heartrate', 'sleep', 'location', 'activity']

        authorization_url, state = self._oauth2_session.authorization_url(
            self._fitbit_oauth2_authorize)
        # response_type="code"
        msg = f"authorization url = {authorization_url}, state = {state}"
        self._logger.debug(msg)
        self._logger.debug("opening a browser window")
        webbrowser.open_new(authorization_url)
        self._logger.debug("done opening browser")
        acode_state = start_catcher(timeout=12.0)
        msg = "a_code obtained" if acode_state else "did not get a_code"
        self._logger.debug(msg)
        if not acode_state:
            raise RuntimeError("could not retrieve authorisation code")
        if acode_state[1] != state:
            raise RuntimeError(f"supplied state {state} does not match returned state {acode_state[1]}")
        return acode_state
    ###########################

    def get_access_refresh_token(self, acode_state: Tuple[str,str]) ->Dict[str, str]:
        """gets access and refresh token from fitbit

        Parameters
        ----------
        acode_state : Tuple(str,str)) ->Dict(str
            first element contains authorisation code

        Returns
        -------
        Dict(str,str)
            dictionary containing access and refresh tokens, and time duration info

        Raises
        ------
        ExceptionName
            Why the exception is raised.

        """
        msg = f"fetching token from {self._fitbit_oauth2_token_url}"
        self._logger.debug(msg)
        t_dict = self._oauth2_session.fetch_token(
            self._fitbit_oauth2_token_url,
            code=acode_state[0],
            state=acode_state[1],
            client_secret=self._oauth2_client_secret)
        # save this
        self.save_tokens(t_dict)

        return t_dict
# {"errors":[{"errorType":"invalid_client","message":"Invalid authorization header format. The client id was not provided in proper format inside Authorization Header. Received authorization header = Basic MjJCWUs5Og==,  received client encoded id = null. Visit https://dev.fitbit.com/docs/oauth2 for more information on the Fitbit Web API authorization process."}],"success":false}.





  # - other pep8
        # works
