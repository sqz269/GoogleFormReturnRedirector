from logging import Logger
import os.path
import pickle
from typing import List, Union
from google.auth.credentials import Credentials

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build


class CredentialManager:
    API_SCOPES: List[str] = ["https://www.googleapis.com/auth/gmail.modify",
                            #  "https://www.googleapis.com/auth/classroom.courses.readonly",
                            #  "https://www.googleapis.com/auth/classroom.rosters.readonly"
                            ]

    def __init__(self, logger: Logger, token_store_path: str="", app_credential_path: str="credentials.json") -> None:
        self.logger = logger

        self.token_store_path = token_store_path
        self.app_credential_path = app_credential_path
        self.credentials: Credentials = None
        self.token_path = os.path.join(self.token_store_path, "token.pickle")
        self.auth()

    def auth(self):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.logger.info("Authorizing through google services")
        if os.path.exists(self.token_path):
            self.load_old_token()

        # If there are no (valid) credentials available, let the user log in.
        if not self.credentials or not self.credentials.valid:
            self.logger.info("No previous token or they are no longer valid. Requesting a New Token")
            self.grant_authorization()
            self.logger.info("Authorized using refereshed/granted credentials")
        else:
            self.logger.info("Authorized using past credentials")

    def load_old_token(self):
        self.logger.debug(f"Attempting to load old tokens at: {self.token_path}")
        with open('token.pickle', 'rb') as token:
            self.credentials = pickle.load(token)

    def grant_authorization(self):
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            self.logger.info("Previous token expired, refreshing ...")
            self.credentials.refresh(Request())
        else:
            self.logger.info("No previous token exists. Requesting authorization")
            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(self.app_credential_path, self.API_SCOPES)
            self.credentials = flow.run_local_server(port=0)
        with open(self.token_path, 'wb') as token:
            pickle.dump(self.credentials, token)
