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

        filter_rules = GmailMessageFilterRules("Score released:", "@ebrschools.org", ".")
        self.message_filterer = GmailMessageFilterer([], self.logger, filter_rules)

        self.cmd_to_description = {
            "1": "Run Redirector (Resend emails based on Email receiver and Subject)"
        }

        self.cmd_to_function = {
            "1": self.redirector
        }

    def print_options(self):
        print()
        for i in range(1, len(self.cmd_to_function) + 1):
            print(f"{i}: {self.cmd_to_description[str(i)]}")

    def get_input_cmd(self):
        while True:
            self.print_options()
            user_input = KeyboardCommandProcessor.get_next_valid_input("Chose an option",
                                                                       expected_values=[str(i) for i in range(1, len(self.cmd_to_description)+1)])
            self.cmd_to_function[user_input]()

    def redirector(self):
        self.logger.info("CSV Based email searching/replacing coming soon")
        print()
        fetch_limit = KeyboardCommandProcessor.get_next_valid_input("How many email to fetch per request",
                                                                    default_value=50, target_type=int)
        email_subject = KeyboardCommandProcessor.get_next_valid_input("What's the email's subject should be (Regex is used here)",
                                                                      default_value="Score released:")
        to = KeyboardCommandProcessor.get_next_valid_input("What's the Email To should be (Domain)",
                                                           default_value="@ebrschools.org")
        print("\nNext two questions will asks about the date range of those emails")
        date_before = KeyboardCommandProcessor.get_next_valid_input("What's the before date (YYYY/MM/DD)", default_value="")
        date_after = KeyboardCommandProcessor.get_next_valid_input("What's the after date (YYYY/MM/DD)", default_value="")

        original_domain = KeyboardCommandProcessor.get_next_valid_input(f"What's the domain to be replaced",
                                                                        default_value="@ebrschools.org")
        replace_with = KeyboardCommandProcessor.get_next_valid_input(f"What should the original domain be replaced with",
                                                                     default_value="@ebrstudents.org")

        q = ""
        if date_after and date_before:
            q = f"after:{date_after} before:{date_before}"
        elif date_after:
            q = f"after:{date_after}"
        elif date_before:
            q = f"before:{date_before}"

        self.logger.info("Operation Parameter Fulfilled")
        self.logger.warning("Please confirm the parameters")
        print(f"\nFetching {fetch_limit} emails per request.")
        print(f"Only fetching emails with subject lines match \"{email_subject}\". To lines match: \"{to}\"")
        print(f"Additional email filters (Standard Query): {q}")
        print(f"Domain {replace_with} will be replacing {original_domain}. Example: JohnDoe{original_domain} -> JohnDoe{replace_with}\n")
        confirm_op = KeyboardCommandProcessor.get_next_valid_input("Is Above Information Correct?", expected_values=["yes", "no", "y", "n"])

        self.fetch_and_redirect(fetch_limit, q, email_subject, to, replace_with)

    def fetch_and_redirect(self, fetch_lim, fetch_query, rule_subject, rule_to, replace_email_domain):
        self.message_filterer.set_rules(GmailMessageFilterRules(rule_subject, rule_to, "."))
        messages = self.gmail_api.fetch_email(limit=fetch_lim, label=COMMON_LABELS.sent, q=fetch_query)["messages"]
        for m in messages:
            data = GmailMessageFormatter(self.gmail_api.get_email_details(m["id"], fmt=EMAIL_DETAIL_FORMATS.full))
            self.message_filterer.add_message(data)

        self.logger.info(f"Found {len(self.message_filterer.messages)} messages that matches given criteria")
        print_all = KeyboardCommandProcessor.get_next_valid_input("Display all matched email addresses",
                                                                  expected_values=["yes", "no", "y", "n"])
        if print_all in ["yes", "y"]:
            for filtered_msg in self.message_filterer.messages:
                print(f"Email: {filtered_msg.To} | Subject: {filtered_msg.Subject}")

    def test(self):
        messages = self.gmail_api.fetch_email(limit=1, label=COMMON_LABELS.sent)["messages"]
        for i in messages:
            data = GmailMessageFormatter(self.gmail_api.get_email_details(i["id"], fmt=EMAIL_DETAIL_FORMATS.full))
            self.message_filterer.add_message(data)
            self.gmail_api.forward_email(self.message_filterer.messages[0], "******@gmail.com")

redirector = GoogleFormRetrunRedirector()
redirector.get_input_cmd()
# redirector.test()
