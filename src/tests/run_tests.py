from src.tests.abstract_test import AbstractTest
from src.tests.board_test import ReconstructFenTest, NumberOfLegalMovesTest

import sys

def test():
    test_classes: list[type[AbstractTest]] = [
        ReconstructFenTest,
        NumberOfLegalMovesTest
    ]

    tests: list[AbstractTest] = []
    failed: list[AbstractTest] = []

    for test_class in test_classes:
        tests.extend(test_class.get_tests())


    print(f"Running {str(len(tests))} tests...")
    print()

    for test_id in range(len(tests)):
        print(f"({int(test_id) + 1}/{len(tests)})", end=" ")
        result = tests[test_id].perform()
        if not result:
            failed.append(tests[test_id])

    print()
    print("Done!")
    print(f"{str(len(tests) - len(failed))} passed, {str(len(failed))} failed")
    if failed:
        print()
        print("Failed tests:")
        for failed_test in failed:
            print(failed_test.get_name())
            print(failed_test.get_description())
            print(f" - Expected: {failed_test.get_expected_result()}")
            print(f" - Actual: {failed_test.get_actual_result()}")
            print()
        sys.exit(-1)

if __name__ == "__main__":
    test()
