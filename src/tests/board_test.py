from typing import Any

from src.tests.abstract_test import AbstractTest
from src.logic.abstract_board import AbstractBoard
from src.logic.board_mailbox import BoardMailbox

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



class PerftTest(AbstractTest):
    def get_name(self) -> str:
        return "Perft"

    def get_description(self) -> str:
        return "Performance test, Move path enumeration" + \
               "\nTests if the correct number of legal moves from a given position is found" + \
                f"\ndepth: {self.depth}, fen: {self.test_fen}"

    def get_expected_result(self) -> Any:
        return self.legal_moves

    def get_actual_result(self) -> Any:
        board = BoardMailbox.from_fen(self.test_fen)
        return board.count_moves(self.depth)

    def __init__(self, test_fen: str, depth: int, legal_moves: int) -> None:
        self.test_fen = test_fen
        self.depth = depth
        self.legal_moves = legal_moves



    @staticmethod
    def get_tests() -> list['AbstractTest']:
        return [
            # Startposition
            PerftTest("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 1, 20),
            PerftTest("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 2, 400),
            PerftTest("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 3, 8902),
            #PerftTest("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 4, 197281)

            # https://gist.github.com/peterellisjones/8c46c28141c162d1d8a0f0badbc9cff9
            PerftTest("r6r/1b2k1bq/8/8/7B/8/8/R3K2R b KQ - 3 2", 1, 8),
            PerftTest("8/8/8/2k5/2pP4/8/B7/4K3 b - d3 0 3", 1, 8),
            PerftTest("r1bqkbnr/pppppppp/n7/8/8/P7/1PPPPPPP/RNBQKBNR w KQkq - 2 2", 1, 19),
            PerftTest("r3k2r/p1pp1pb1/bn2Qnp1/2qPN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQkq - 3 2", 1, 5),
            PerftTest("2kr3r/p1ppqpb1/bn2Qnp1/3PN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQ - 3 2", 1, 44),
            PerftTest("rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R w KQ - 3 9", 1, 39),
            PerftTest("2r5/3pk3/8/2P5/8/2K5/8/8 w - - 5 4", 1, 9),
            PerftTest("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 3, 62379),
            PerftTest("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", 3, 89890),
            #PerftTest("3k4/3p4/8/K1P4r/8/8/8/8 b - - 0 1", 6, 1134888),
            #PerftTest("8/8/4k3/8/2p5/8/B2P2K1/8 w - - 0 1", 6, 1015133),
            #PerftTest("8/8/1k6/2b5/2pP4/8/5K2/8 b - d3 0 1", 6, 1440467),
            #PerftTest("5k2/8/8/8/8/8/8/4K2R w K - 0 1", 6, 661072),
            #PerftTest("3k4/8/8/8/8/8/8/R3K3 w Q - 0 1", 6, 803711),
            #PerftTest("r3k2r/1b4bq/8/8/8/8/7B/R3K2R w KQkq - 0 1", 4, 1274206),
            #PerftTest("r3k2r/8/3Q4/8/8/5q2/8/R3K2R b KQkq - 0 1", 4, 1720476),
            #PerftTest("2K2r2/4P3/8/8/8/8/8/3k4 w - - 0 1", 6, 3821001),
            #PerftTest("8/8/1P2K3/8/2n5/1q6/8/5k2 b - - 0 1", 5, 1004658),
            #PerftTest("4k3/1P6/8/8/8/8/K7/8 w - - 0 1", 6, 217342),
            PerftTest("8/P1k5/K7/8/8/8/8/8 w - - 0 1", 6, 92683),
            PerftTest("K1k5/8/P7/8/8/8/8/8 w - - 0 1", 6, 2217),
            #PerftTest("8/k1P5/8/1K6/8/8/8/8 w - - 0 1", 7, 567584),
            PerftTest("8/8/2k5/5q2/5n2/8/5K2/8 b - - 0 1", 4, 23527),

            # https://www.chessprogramming.org/Perft_Results
            PerftTest("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 1, 48),
            PerftTest("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 2, 2039),
            PerftTest("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 3, 97862),

            PerftTest("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1 ", 1, 14),
            PerftTest("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1 ", 2, 191),
            PerftTest("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1 ", 3, 2812),
            PerftTest("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1 ", 4, 43238),

            PerftTest("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1", 1, 6),
            PerftTest("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1", 2, 264),
            PerftTest("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1", 3, 9467),

            PerftTest("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 1, 44),
            PerftTest("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 2, 1486),
            PerftTest("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 3, 62379),
        ]
