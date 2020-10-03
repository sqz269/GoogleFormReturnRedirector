from typing import Any, Dict, List

class GmailMessageFormatter:

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

        # Fields that must present in the message
        self.id: str = data['id']
        self.payload: Dict[str, List[Dict[str, str]]] = data['payload']
        self.headers: List[Dict[str, str]] = self.payload['headers']
        self.size_estimate = data['sizeEstimate']

    def search_header_value(self, header_key: str, raise_exc: bool=True):
        """Search for a certain header and return it's value

        Args:
            header_key (str): The header to search for
            raise_exc (bool, optional): Raises exception if the header can't be found?. Defaults to True.

        Raises:
            AttributeError: Raised when the header can not be found

        Returns:
            str: The value associated with the header, returns empty string if header_key can't be found and raise_exc is false
        """
        for item in self.headers:
            if item['name'].lower() == header_key.lower():
                return item['value']

        for item in self.payload["headers"]:
            if item['name'].lower() == header_key.lower():
                return item['value']

        if raise_exc:
            raise AttributeError(f"There is no such field in the header named: {header_key}")
        return ""

    @property
    def From(self):
        return self.search_header_value("From")

    @property
    def To(self):
        return self.search_header_value("To")

    @property
    def Subject(self):
        return self.search_header_value("Subject")

    @property
    def Date(self):
        return self.search_header_value("Date")

    @property
    def MainPayload(self):
        return self.data["payload"]["parts"]

    def __str__(self) -> str:
        return f"{self.From} -> {self.To}"
