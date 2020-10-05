from logging import Logger

from googleapiclient.discovery import build
from libs.api_shared.credential_manger import CredentialManager


class ClassroomAPIHandler(CredentialManager):
    def __init__(self, logger: Logger, token_store_path: str = "",
                 app_credential_path: str = "credentials.json") -> None:
        super().__init__(logger, token_store_path, app_credential_path)
        self.service = None
        self.auth_service()

    def auth_service(self) -> None:
        self.service = build('classroom', 'v1', credentials=self.credentials)
