from src.gui.visual_board import main as visual_main
from src.tests.run_tests import test

import sys

def main():
    match sys.argv[1]:
        case "test":
            test()
        case "visual":
            visual_main()

if __name__ == "__main__":
    main()


