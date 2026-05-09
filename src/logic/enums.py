from enum import IntEnum

class PieceType(IntEnum):
    PAWN = 100
    KNIGHT = 300
    BISHOP = 350
    ROOK = 500
    QUEEN = 900
    KING = 99999

    NONE = 0


class Player(IntEnum):
    WHITE = 1
    BLACK = -1

    NONE = 0