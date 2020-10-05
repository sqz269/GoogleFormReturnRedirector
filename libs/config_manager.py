import logging
from configparser import ConfigParser
import os
from logging import Logger

from libs.keyboard_command_processor import KeyboardCommandProcessor


class ConfigManager:

    def __init__(self, config_dir_path: str, logger: Logger):
        self.config_dir_path = config_dir_path
        self.config_path = os.path.join(config_dir_path, "form_return_redirector.ini")
        self.config: ConfigParser = ConfigParser()
        self.configuration = {}
        self.logger = logger
        self.logger.info(f"Using {self.config_path} as config file storage")

    @property
    def CredentialJsonPath(self):
        return self.configuration["CREDENTIALS"]["credentials_json_path"]

    @property
    def TokenPicklePath(self):
        return self.configuration["CREDENTIALS"]["token_pickle_path"]

    @property
    def ConfigurationDirectoryPath(self):
        return self.config_dir_path

    def create_config(self):
        if not os.path.isdir(self.config_dir_path):
            self.logger.info(f"Configuration Folder does not exist. Creating a new one at: {self.config_dir_path}")
            os.makedirs(self.config_dir_path)

        self.logger.info(f"Creating a new configuration file at path: {self.config_path}")

        credentials_json_path = KeyboardCommandProcessor.get_next_valid_input("Enter path for credentials.json", target_type=str)
        token_pickle_path = KeyboardCommandProcessor.get_next_valid_input("Enter path where you want to store token.pickle ",
                                                                          default_value=os.path.join(self.config_dir_path, "token.pickle"))

        self.config["CREDENTIALS"] = {"credentials_json_path": credentials_json_path,
                                      "token_pickle_path": token_pickle_path}

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
        for sections in self.config.sections():
            parse_sec = {}
            for k in self.config[sections]:
                parse_sec.update({k: self.config[sections][k]})
            self.configuration.update({sections: parse_sec})

        self.configuration["LOGGING"]["console_level"] = KeyboardCommandProcessor.parse_logger_value(self.configuration["LOGGING"]["console_level"])
        self.configuration["LOGGING"]["file_level"] = KeyboardCommandProcessor.parse_logger_value(self.configuration["LOGGING"]["file_level"])

    def load_config(self) -> bool:
        """
        """
        if os.path.isfile(self.config_path):
            self.config.read(self.config_path)
            self._parse_config()
            self.logger.info("Configuration file loaded.")

            if isinstance(self.logger.handlers[0], logging.FileHandler):
                self.logger.handlers[0].setLevel(self.configuration["LOGGING"]["file_level"])
                self.logger.handlers[1].setLevel(self.configuration["LOGGING"]["console_level"])
            else:
                self.logger.handlers[0].setLevel(self.configuration["LOGGING"]["console_level"])
                self.logger.handlers[1].setLevel(self.configuration["LOGGING"]["file_level"])

            return True
        else:
            return False

    def update_config(self, section_name: str, key: str, new_value: str):
        self.logger.info(f"Updating configuration value for [{section_name}][{key}]")
        self.config[section_name][key] = new_value
        with open(self.config_path, "w") as cfg:
            self.config.write(cfg)
