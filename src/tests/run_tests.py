from typing import Any

from src.tests.abstract_test import AbstractTest
from src.tests.board_test import ReconstructFenTest, PerftTest

import sys

def test():
    test_classes: list[type[AbstractTest]] = [
        ReconstructFenTest,
        PerftTest
    ]

    tests: list[AbstractTest] = []
    failed: list[tuple[AbstractTest, Any]] = []

    for test_class in test_classes:
        tests.extend(test_class.get_tests())


    print(f"Running {str(len(tests))} tests...")
    print()

    for test_id in range(len(tests)):
        print(f"({int(test_id) + 1}/{len(tests)})", end=" ")
        result = tests[test_id].perform()
        if not result[0]:
            failed.append((tests[test_id], result[1]))

    print()
    print("Done!")
    print(f"{str(len(tests) - len(failed))} passed, {str(len(failed))} failed")
    if failed:
        print()
        print("Failed tests:")
        for failed_test in failed:
            print(failed_test[0].get_name())
            print(failed_test[0].get_description())
            print(f" - Expected: {failed_test[0].get_expected_result()}")
            print(f" - Actual: {failed_test[1]}")
            print()
        sys.exit(-1)

if __name__ == "__main__":
    test()
