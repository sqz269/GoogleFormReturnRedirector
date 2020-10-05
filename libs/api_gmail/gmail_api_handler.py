import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

from libs.api_gmail.gmail_message_formatter import GmailMessageFormatter
from logging import Logger
from typing import Any, Dict, List

from googleapiclient.discovery import build
from libs.api_shared.credential_manger import CredentialManager

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class COMMON_LABELS:
    chat="CHAT"
    sent="SENT"
    inbox="INBOX"
    important="IMPORTANT"

class EMAIL_DETAIL_FORMATS:
    """Returns only email message ID and labels; does not return the email headers, body, or payload."""
    minimum="minimal"

    """Returns the full email message data with body content parsed in the payload field; the raw field is not used. 
    Format cannot be used when accessing the api using the gmail.metadata scope.
    """
    full="full"

    """Returns the full email message data with body content in the raw field as a base64url encoded string; the payload field is not used. 
    Format cannot be used when accessing the api using the gmail.metadata scope.
    """
    raw="raw"

    """Returns only email message ID, labels, and email headers"""
    metadata="metadata"

class GmailAPIHandler(CredentialManager):

    def __init__(self, logger: Logger, token_store_path: str = "", app_credential_path: str = "credentials.json") -> None:
        super().__init__(logger, token_store_path, app_credential_path)
        self.service = None
        self.auth_service()

    def auth_service(self) -> None:
        self.service = build('gmail', 'v1', credentials=self.credentials)

    def fetch_email(self, limit: int, label: str, userId: str="me", q: str="") -> Dict[str, List[Dict[str, str]]]:
        """Fetches email from your gmail account

        Args:
            limit (int): The maximum number of email to fetch
            label (str): Only return messages with labels that match all of the specified label IDs.
            userId (str, optional): The user's email address. The special value me can be used to indicate the authenticated user. Defaults to "me".
            q (str, optional): Only return messages matching the specified query. Supports the same query format as the Gmail search box. Defaults to "".

        Returns:
            Dict[str, List[Dict[str, str]]]: A list of message object. each message resource contains only an id and a threadId.

        SeeAlso:
            https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
        """
        return self.service.users().messages().list(userId=userId, maxResults=limit, labelIds=label, q=q).execute()

    def get_email_details(self, id: str, userId: str="me", fmt: str=EMAIL_DETAIL_FORMATS.metadata):
        """Gets the specified email

        Args:
            id (str): The ID of the email to retrieve.
            userId (str, optional): The user's email address. The special value me can be used to indicate the authenticated user. Defaults to "me".
            fmt (str, optional): The format to return the message in. Defaults to EMAIL_DETAIL_FORMATS.metadata.

        Returns:
            Dict: An instance of message. (Details can be found here: https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message)

        SeeAlso:
            https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get
        """
        return self.service.users().messages().get(userId=userId, id=id, format=fmt).execute()

    def make_payload(self, mime_type: str, sub_type: str, data: Any):
        if mime_type == 'text':
            msg = MIMEText(data, _subtype=sub_type)
        elif mime_type == 'image':
            msg = MIMEImage(data, _subtype=sub_type)
        elif mime_type == 'audio':
            msg = MIMEAudio(data, _subtype=sub_type)
        else:
            msg = MIMEBase(mime_type, sub_type)
            msg.set_payload(data)
        return msg

    def move_to_trash(self, id: str, userId: str="me"):
        return self.service.users().messages().trash(userId=userId, id=id).execute()

    def forward_email(self, original: GmailMessageFormatter, to: str):
        """Forward email to an alternative address.

        Note: This function is not necessarily a forward implementation as it does not forward threads
            And currently, the compatibility is limited

        Args:
            original (GmailMessageFormatter): The original message
            to (str): The email to forward to
        """
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = original.From
        message['subject'] = original.Subject

        message_body = original.MainPayload
        for msg_part in message_body:
            mime_type, sub_type = msg_part["mimeType"].split("/", 1)
            payload = self.make_payload(mime_type, sub_type, base64.urlsafe_b64decode(msg_part['body']["data"]).decode())
            message.attach(payload)

        data = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

        return self.send_message(data)

    def send_message(self, message: Dict[str, str], user_id: str='me'):
        message = self.service.users().messages().send(userId=user_id, body=message).execute()
        return message

    def get_labels(self) -> List[str]:
        results: Dict[str, List[str]] = self.service.users().labels().list(userId='me').execute()
        return results.get('labels', [])
