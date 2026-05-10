from abc import ABC, abstractmethod
from typing import Any, Self

class AbstractTest(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_expected_result(self) -> Any:
        pass

    @abstractmethod
    def get_actual_result(self) -> Any:
        pass

    def perform(self, idx: str) -> tuple[bool, Any, Self]:
        expected = self.get_expected_result()
        actual = self.get_actual_result()
        if expected == actual:
            print(f"{idx} {self.get_name()} passed")
            return True, actual, self
        else:
            print(f"{idx} {self.get_name()} failed")
            return False, actual, self

    @staticmethod
    @abstractmethod
    def get_tests() -> list['AbstractTest']:
        pass
