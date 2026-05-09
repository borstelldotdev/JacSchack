from abc import ABC, abstractmethod
from typing import Any

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

    def perform(self) -> bool:
        print(f"Performing test `{self.get_name()}`... ", end="")
        expected = self.get_expected_result()
        actual = self.get_actual_result()
        if expected == actual:
            print("passed")
            return True
        else:
            print("failed")
            print(f" - Expected: {expected}")
            print(f" - Actual: {actual}")
            return False

    @staticmethod
    @abstractmethod
    def get_tests() -> list['AbstractTest']:
        pass
