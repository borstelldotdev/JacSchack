from typing import Any, Iterator

from src.tests.abstract_test import AbstractTest
from src.tests.board_test import ReconstructFenTest, PerftTest
from concurrent.futures import ProcessPoolExecutor
from time import time

import sys


class Tester:
    def __init__(self, *args):
        self.test_classes: list[type[AbstractTest]] = list(args)
        self.tests: list[AbstractTest] = []

        for test_class in self.test_classes:
            self.tests.extend(test_class.get_tests())

    def perform_idx(self, idx: int):
        try:
            return self.tests[idx].perform(f"({int(idx) + 1}/{len(self.tests)})")
        except Exception as e:
            print(f"{e} thrown while performing {self.tests[idx].get_name()}")
            print(self.tests[idx].get_description())

    def test(self):
        start = time()
        print(f"Running {str(len(self.tests))} tests...")
        print()

        with ProcessPoolExecutor(max_workers=8) as proc:
            results: Iterator[tuple[bool, Any, AbstractTest]] \
                = proc.map(self.perform_idx, range(len(self.tests)))

        stop = time()

        print()
        print("Done!")
        print()
        failed = 0
        for result in results:
            if result[0]: continue

            failed += 1
            print(result[2].get_name())
            print(result[2].get_description())
            print(f" - Expected: {result[2].get_expected_result()}")
            print(f" - Actual: {result[1]}")
            print()


        print(f"{str(len(self.tests) - failed)} passed, {str(failed)} failed")
        print(f"Took {str(int((stop - start) * 1000))} ms")
        sys.exit(-1)

if __name__ == "__main__":
    Tester(
        ReconstructFenTest,
        PerftTest
    ).test()
