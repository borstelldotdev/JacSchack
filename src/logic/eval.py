from src.logic.board_mailbox import BoardMailbox
from src.logic.enums import Player, PieceType

PAWN_TABLE = [
    0, 0, 0, 0, 0, 0
]


def hamming_weight(binary: int) -> int:
    # https://stackoverflow.com/a/843846
    c = 0
    while binary:
        c += 1
        binary &= binary - 1
    return c


def evaluate(board: BoardMailbox):
    # https://www.chessprogramming.org/Evaluation

    sum_accumulator = 0
    for y in range(8):
        for x in range(8):
            piece = board.at_unsafe(x, y)
            # print(piece[0] * piece[1])
            sum_accumulator += piece[0] * piece[1]

    sum_accumulator += 10 * len(board.white_moves)
    sum_accumulator -= 10 * len(board.black_moves)

    # TODO: Bondestruktur
    return sum_accumulator * board.to_move