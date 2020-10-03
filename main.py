import logging
import sys
import os
from logging import Logger

from libs.config_manager import ConfigManager
from libs.gmail_api.gmail_api_handler import COMMON_LABELS, EMAIL_DETAIL_FORMATS, GmailAPIHandler
from libs.gmail_api.gmail_message_filterer import (GmailMessageFilterer,
                                                   GmailMessageFilterRules)
from libs.gmail_api.gmail_message_formatter import GmailMessageFormatter
from libs.keyboard_command_processor import KeyboardCommandProcessor
from libs.logger import init_logging


def global_exception_hook(exctype, value, tb):
    if exctype == KeyboardInterrupt:
        print("Ctrl + C Received. Press Enter to exit")
        input()
        sys.exit(0)
    else:
        sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_exception_hook

class GoogleFormRetrunRedirector(object):

    def __init__(self) -> None:
        self.logger: Logger = init_logging(name="REDIRECTOR", level_stdout=logging.DEBUG)
        self.config_mgr = ConfigManager(os.path.join(os.getenv('LOCALAPPDATA'), 'form_return_redirector.ini'), self.logger)

        if not self.config_mgr.load_config():
            self.logger.info("It looks like this is the first time this program ran on this computer. We need a few configurations to get things started")
            self.config_mgr.create_config()
            self.config_mgr.load_config()

        self.gmail_api = GmailAPIHandler(self.logger)

        filter_rules = GmailMessageFilterRules("Score released:", "@gmail", ".")
        self.message_filterer = GmailMessageFilterer([], self.logger, filter_rules)

        self.cmd_to_description = {
            "1": "Run Redirector (Resend emails based on Email receiver and Subject)"
        }

        self.cmd_to_function = {
            "1": self.redirector
        }

    def print_options(self):
        print()
        for i in range(1, len(self.cmd_to_function)):
            print(f"{i}: {self.cmd_to_description[str(i)]}")

    def get_input_cmd(self):
        while True:
            user_input = KeyboardCommandProcessor.get_next_valid_input("Chose an option",
                                                                       expected_values=[str(i) for i in range(1,len(self.cmd_to_description))])
            self.cmd_to_function[user_input]()

    def redirector(self):
        pass

    def test(self):
        messages = self.gmail_api.fetch_email(limit=1, label=COMMON_LABELS.sent)["messages"]
        for i in messages:
            data = GmailMessageFormatter(self.gmail_api.get_email_details(i["id"], fmt=EMAIL_DETAIL_FORMATS.full))
            self.message_filterer.add_message(data)
            self.gmail_api.forward_email(self.message_filterer.messages[0], "******@gmail.com")

redirector = GoogleFormRetrunRedirector()
# redirector.test()
