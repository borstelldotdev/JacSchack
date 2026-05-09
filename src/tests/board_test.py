from typing import Any

from src.tests.abstract_test import AbstractTest
from src.logic.abstract_board import AbstractBoard
from src.logic.board_mailbox import BoardMailbox
from src.logic.board_bitboard_old import BoardBitboard

class ReconstructFenTest(AbstractTest):
    def get_name(self) -> str:
        return "Reconstruct FEN"

    def get_description(self) -> str:
        return "Tests if a board representation yields the same FEN from self.to_fen()," + \
            " compared to the one that was used to create it."

    def get_expected_result(self) -> Any:
        return self.test_fen

    def get_actual_result(self) -> Any:
        board = self.board_impl.from_fen(self.test_fen)
        return board.to_fen()

    def __init__(self, board_impl: type[AbstractBoard], test_fen: str) -> None:
        self.board_impl = board_impl
        self.test_fen = test_fen


    # https://gist.github.com/peterellisjones/8c46c28141c162d1d8a0f0badbc9cff9
    @staticmethod
    def get_tests() -> list['AbstractTest']:
        return [
            ReconstructFenTest(BoardMailbox, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
            ReconstructFenTest(BoardMailbox, "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"),
            ReconstructFenTest(BoardMailbox, "r6r/1b2k1bq/8/8/7B/8/8/R3K2R b KQ - 3 2"),
            ReconstructFenTest(BoardMailbox, "rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R w KQ - 3 9"),
            ReconstructFenTest(BoardMailbox, "3k4/3p4/8/K1P4r/8/8/8/8 b - - 0 1"),
            ReconstructFenTest(BoardMailbox, "8/8/8/2k5/2pP4/8/B7/4K3 b - d3 0 3"),
        ]



class NumberOfLegalMovesTest(AbstractTest):
    def get_name(self) -> str:
        return "Number of legal moves"

    def get_description(self) -> str:
        return "Tests if the correct number of legal moves from a given position is found"

    def get_expected_result(self) -> Any:
        return self.legal_moves

    def get_actual_result(self) -> Any:
        board = self.board_impl.from_fen(self.test_fen)
        return board.to_fen()

    def __init__(self, test_fen: str, legal_moves: int) -> None:
        self.test_fen = test_fen
        self.legal_moves = legal_moves


    # https://gist.github.com/peterellisjones/8c46c28141c162d1d8a0f0badbc9cff9
    @staticmethod
    def get_tests() -> list['AbstractTest']:
        return [

        ]
