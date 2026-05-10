from src.logic.board_mailbox import BoardMailbox
from src.logic.enums import Player, PieceType

PAWN_TABLE = [
    0, 0, 0, 0, 0, 0
]




def evaluate(board: BoardMailbox):
    for x in range(8):
        for y in range(8):
            piece = board[x, y]
