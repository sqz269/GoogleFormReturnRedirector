import logging
from configparser import ConfigParser
import os
from logging import Logger

from libs.keyboard_command_processor import KeyboardCommandProcessor


class ConfigManager:

    def __init__(self, config_path, logger: Logger):
        self.config_path = config_path
        self.config: ConfigParser = ConfigParser()
        self.logger = logger
        self.logger.info(f"Using {config_path} as config file storage")

    def create_config(self) -> bool:
        self.logger.info(f"Creating a new configuration file at path: {self.config_path}")

        credentials_json_path = KeyboardCommandProcessor.get_next_valid_input("Enter path for credentials.json", target_type=str)
        token_pickle_path = KeyboardCommandProcessor.get_next_valid_input("Enter path where you want to store token.pickle ", default_value="./")

        self.config["CREDENTIALS"] = {"credentials_json_path": credentials_json_path,
                                      "token_pickle_path": os.path.join(token_pickle_path, "token.pickle")}

        level_std_out = KeyboardCommandProcessor.get_next_valid_input("Enter the logger level for console output",
                                                      default_value="INFO",
                                                      expected_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        level_std_out = KeyboardCommandProcessor.parse_logger_value(level_std_out)

        level_file_out = KeyboardCommandProcessor.get_next_valid_input("Enter the logger level for file output",
                                                          default_value="WARNING",
                                                          expected_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        level_file_out = KeyboardCommandProcessor.parse_logger_value(level_file_out)
        self.config["LOGGING"] = {"console_level": str(level_std_out),
                                  "file_level": str(level_file_out)}

        with open(self.config_path, "w") as cfg:
            self.config.write(cfg)

    def _parse_config(self):
        self.config["LOGGING"]["console_level"] = KeyboardCommandProcessor.parse_logger_value(self.config["LOGGING"]["console_level"])
        self.config["LOGGING"]["file_level"] = KeyboardCommandProcessor.parse_logger_value(self.config["LOGGING"]["file_level"])

    def load_config(self) -> bool:
        """
        """
        if os.path.isfile(self.config_path):
            self.config.read(self.config_path)
            self._parse_config()
            self.logger.info("Configuration file loaded.")

            if isinstance(self.logger.handlers[0], logging.FileHandler):
                self.logger.handlers[0].setLevel(self.config["LOGGING"]["file_level"])
                self.logger.handlers[1].setLevel(self.config["LOGGING"]["console_level"])
            else:
                self.logger.handlers[0].setLevel(self.config["LOGGING"]["console_level"])
                self.logger.handlers[1].setLevel(self.config["LOGGING"]["file_level"])

            return True
        else:
            return False
