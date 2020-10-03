from typing import List, Any


class KeyboardCommandProcessor:

    @staticmethod
    def get_next_valid_input(message, default_value=None, target_type=str, expected_values: List[str]=None, case_sensitive=False) -> Any:
        if expected_values and not case_sensitive:
            expected_values = [i.lower() for i in expected_values]

        if default_value:
            message = message + f" (Default: {default_value})"
        if expected_values:
            message = message + f" (Available values: {expected_values})"
        if message[-1] != ":" or message[len(message) - 2] == ":":
            message = message + ": "
        while True:
            user_input = input(message)
            if default_value:
                if user_input.strip() == "":
                    print(f"No values entered. Using default value: {default_value}")
                    return default_value

            if not case_sensitive:
                user_input = user_input.lower()

            if expected_values and user_input not in expected_values:
                print(f"Invalid input. Input should only be: {expected_values} but found {user_input}")
                continue
            if expected_values:
                return user_input

            try:
                return target_type(user_input)
            except ValueError:
                print(f"Invalid input. Expected input to be a(n) {target_type}.")

    @staticmethod
    def parse_logger_value(value: str) -> int:
        logger_values = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "FATAL": 50
        }
        return logger_values[value.upper()]
