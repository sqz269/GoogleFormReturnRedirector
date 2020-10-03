import logging
from logging import Logger

from libs.gmail_api.gmail_api_handler import COMMON_LABELS, EMAIL_DETAIL_FORMATS, GmailAPIHandler
from libs.gmail_api.gmail_message_filterer import (GmailMessageFilterer,
                                                   GmailMessageFilterRules)
from libs.gmail_api.gmail_message_formatter import GmailMessageFormatter
from libs.logger import init_logging


class GoogleFormRetrunRedirector(object):

    def __init__(self) -> None:
        self.logger: Logger = init_logging(name="REDIRECTOR", level_stdout=logging.DEBUG)
        self.gmail_api = GmailAPIHandler(self.logger)
        
        filter_rules = GmailMessageFilterRules("Score released:", "@gmail", ".")
        self.message_filterer = GmailMessageFilterer([], self.logger, filter_rules)

    def redirector(self):
        pass

    def test(self):
        messages = self.gmail_api.fetch_email(limit=1, label=COMMON_LABELS.sent)["messages"]
        for i in messages:
            data = GmailMessageFormatter(self.gmail_api.get_email_details(i["id"], fmt=EMAIL_DETAIL_FORMATS.full))
            self.message_filterer.add_message(data)
            self.gmail_api.forward_email(self.message_filterer.messages[0], "******@gmail.com")

redirector = GoogleFormRetrunRedirector()
redirector.test()
