from typing import Any, List

class Config:
    def __init__(self):
        self.label_code_dict = {}
        self.code_value_dict = {}

    def register(self, label: str, code: str, v: Any):
        """Add mapping from .bel to code, and code to value"""
        self.label_code_dict[label] = code
        self.code_value_dict[code] = v

    def get_by_label(self, target_label: str) -> str:
        """Find code by label"""
        return self.label_code_dict.get(target_label)

    def add_value(self, code: str, value: Any) -> None:
        """Add mapping from .de to object"""
        self.code_value_dict[code] = value

    def get_by_code(self, code: str) -> Any:
        """Get an object by code"""
        return self.code_value_dict.get(code)

    def labels(self) -> List[str]:
        """Return all labels"""
        return list(self.label_code_dict.keys())

    def codes(self) -> List[str]:
        """Return all codes"""
        return list(self.code_value_dict.keys())