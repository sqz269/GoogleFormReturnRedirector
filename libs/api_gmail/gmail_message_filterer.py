from logging import Logger
from libs.api_gmail.gmail_message_formatter import GmailMessageFormatter
from typing import List, Union, Callable
import re

class GmailMessageFilterRules:
    """All the rules must have a non empty value. If you want to ignore a rule, simple put .
    The rules are in regular expression
    """
    def __init__(self, subject: str, to: str, date: str) -> None:
        self.Subject = subject
        self.To = to
        self.Date = date

class GmailMessageFilterRulesCompiled:
    def __init__(self, subject: Callable[[str], bool], to: Callable[[str], bool], date: Callable[[str], bool]) -> None:
        self.Subject = subject
        self.To = to
        self.Date = date

class GmailMessageFilterer:
    """A helper class to filter gmail messaged based on certain attributes such as To, Subject, Date...

        Why Google, Why? https://webapps.stackexchange.com/questions/85044/gmail-filter-on-partial-words
    """
    def __init__(self, data: List[GmailMessageFormatter], logger: Logger, rules: Union[GmailMessageFilterRules, GmailMessageFilterRulesCompiled]) -> None:
        """Constructor for GmailMessageFilter

        Args:
            data (List[GmailMessageFormatter]): List of message to filter (initially, more can be added later)
            logger (Logger): The logger to log events
            rules (GmailMessageFilterRules): Dictionary of rules to match/filter
        """
        self.logger = logger
        self.filtered_messages: List[GmailMessageFormatter] = []
        self.filter: GmailMessageFilterRulesCompiled = self._compile_rules(rules)
        self.add_message(data)

    @property
    def messages(self):
        return self.filtered_messages

    def set_rules(self, rules: Union[GmailMessageFilterRules, GmailMessageFilterRulesCompiled]):
        self.logger.info("Updating Gmail Message Filter Rules")
        self.filter = self._compile_rules(rules)

    @staticmethod
    def _compile_rules(rules: Union[GmailMessageFilterRules, GmailMessageFilterRulesCompiled]) -> GmailMessageFilterRulesCompiled:
        """Compile GmailMessageFilterRules to callable functions

        Args:
            rules (Union[GmailMessageFilterRules, GmailMessageFilterRulesCompiled]): The rules to compile

        Returns:
            GmailMessageFilterRulesCompiled: The class that contains rules that is callable
        """
        if isinstance(rules, GmailMessageFilterRulesCompiled):
            return rules
        
        # TODO Optimize re.match to re.compile -> match
        return GmailMessageFilterRulesCompiled(lambda s: re.findall(rules.Subject, s) != [], 
                                                lambda s: re.findall(rules.To, s) != [], 
                                                lambda s: re.findall(rules.Date, s) != [])

    def add_message(self, message: Union[List[GmailMessageFormatter], GmailMessageFormatter]):
        if isinstance(message, list):
            for m in message:
                self.filter_messages(m)
        else:
            self.filter_messages(message)

    def filter_messages(self, message: GmailMessageFormatter):
        if (self.filter.Subject(message.Subject) and self.filter.To(message.To) and self.filter.Date(message.Date)):
            self.logger.debug(f"Adding {message} to messages (criteria met)")
            self.filtered_messages.append(message)

    def reset(self):
        self.filtered_messages.clear()
        self.logger.info("Cleared List of already filtered messages")
