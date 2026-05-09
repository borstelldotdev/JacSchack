from enum import IntEnum
from typing import Self


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


class Bitboard(int):
    # Bitboard order:
    #
    # (rank 8): 0 . . . 7
    #           .       .
    # (rank 1)  56 . . .63

    BITBOARD_SIZE = 0xFF_FF_FF_FF_FF_FF_FF_FF

    def __new__(cls, data: int) -> Self:
        return int.__new__(cls, data)

    def shift_vertical(self, y: int):
        if y > 0:
            return (self << y * 8) & self.BITBOARD_SIZE
        else:
            return self >> y * 8

    def at(self, x: int, y: int) -> bool:
        mask = 1 << (y * 8 + x)
        return (self & mask) != 0

    def __getitem__(self, value: tuple[int, int]):
        return self.at(value[0], value[1])

    def __repr__(self) -> str:
        lines = [
            "  A B C D E F G H"
        ]

        for y in range(8):
            lines.append(str(8 - y) + " ")
            for x in range(8):
                lines[-1] = lines[-1] + ("X " if self[x, y] else ". ")

        return "\n".join(lines)


class Board:
    piece_table = {
        (PieceType.NONE, Player.NONE): ".",

        (PieceType.PAWN, Player.WHITE): "P",
        (PieceType.KNIGHT, Player.WHITE): "N",
        (PieceType.BISHOP, Player.WHITE): "B",
        (PieceType.ROOK, Player.WHITE): "R",
        (PieceType.QUEEN, Player.WHITE): "Q",
        (PieceType.KING, Player.WHITE): "K",

        (PieceType.PAWN, Player.BLACK): "p",
        (PieceType.KNIGHT, Player.BLACK): "n",
        (PieceType.BISHOP, Player.BLACK): "b",
        (PieceType.ROOK, Player.BLACK): "r",
        (PieceType.QUEEN, Player.BLACK): "q",
        (PieceType.KING, Player.BLACK): "k",
    }

    def __init__(self, to_move: Player, white_castle_queenside: bool, black_castle_queenside: bool,
                 white_castle_kingside: bool, black_castle_kingside: bool, en_passant_square: tuple[int, int],
                 halfmove: int, fullmove: int,

                 white_bitboard: Bitboard, black_bitboard: Bitboard,
                 kings_bitboard: Bitboard, queen_bitboard: Bitboard, rook_bitboard: Bitboard,
                 bishop_bitboard: Bitboard, knight_bitboard: Bitboard, pawn_bitboard: Bitboard) -> None:

        self.to_move: Player = to_move

        self.white_castle_queenside: bool = white_castle_queenside
        self.black_castle_queenside: bool = black_castle_queenside
        self.white_castle_kingside: bool = white_castle_kingside
        self.black_castle_kingside: bool = black_castle_kingside

        self.en_passant_square: tuple[int, int] = en_passant_square
        self.halfmove = halfmove
        self.fullmove = fullmove

        self.white: Bitboard = white_bitboard
        self.black: Bitboard = black_bitboard

        self.kings: Bitboard = kings_bitboard
        self.queens: Bitboard = queen_bitboard
        self.rooks: Bitboard = rook_bitboard
        self.bishops: Bitboard = bishop_bitboard
        self.knights: Bitboard = knight_bitboard
        self.pawns: Bitboard = pawn_bitboard

    def at(self, x: int, y: int) -> tuple[PieceType, Player]:
        mask = 1 << (y * 8 + x)
        if self.kings & mask:
            piece_type = PieceType.KING
        elif self.queens & mask:
            piece_type = PieceType.QUEEN
        elif self.rooks & mask:
            piece_type = PieceType.ROOK
        elif self.bishops & mask:
            piece_type = PieceType.BISHOP
        elif self.knights & mask:
            piece_type = PieceType.KNIGHT
        elif self.pawns & mask:
            piece_type = PieceType.PAWN
        else:
            piece_type = PieceType.NONE

        if self.white & mask:
            player = Player.WHITE
        elif self.black & mask:
            player = Player.BLACK
        else:
            player = Player.NONE

        return piece_type, player

    def __getitem__(self, value: tuple[int, int]):
        return self.at(value[0], value[1])

    @staticmethod
    def square_to_cords(square: str) -> tuple[int, int]:
        return "abcdefgh".index(square[0].lower()), 8 - int(square[1])

    @classmethod
    def starting_position(cls):
        return cls.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    @classmethod
    def from_fen(cls, fen: str) -> Self:
        board, to_move, castle, en_passant, halfmove, fullmove = fen.split(" ")

        if to_move == "w":
            player_to_move = Player.WHITE
        elif to_move == "b":
            player_to_move = Player.BLACK
        else:
            player_to_move = Player.NONE

        new = Board(to_move=player_to_move,
                    white_castle_kingside="K" in castle, white_castle_queenside="Q" in castle,
                    black_castle_kingside="k" in castle, black_castle_queenside="q" in castle,
                    en_passant_square=cls.square_to_cords(en_passant) if en_passant != "-" else None,
                    halfmove=int(halfmove),
                    fullmove=int(fullmove),
                    white_bitboard=Bitboard(0), black_bitboard=Bitboard(0), kings_bitboard=Bitboard(0),
                    queen_bitboard=Bitboard(0), rook_bitboard=Bitboard(0), bishop_bitboard=Bitboard(0),
                    knight_bitboard=Bitboard(0), pawn_bitboard=Bitboard(0),
                    )

        ranks = board.split("/")
        for rank in range(8):
            file = 0
            for char in list(ranks[rank]):
                if char.isdigit():
                    file += int(char)
                else:
                    match char:
                        case "P":
                            new.white |= 1 << rank * 8 + file
                            new.pawns |= 1 << rank * 8 + file
                        case "N":
                            new.white |= 1 << rank * 8 + file
                            new.knights |= 1 << rank * 8 + file
                        case "B":
                            new.white |= 1 << rank * 8 + file
                            new.bishops |= 1 << rank * 8 + file
                        case "R":
                            new.white |= 1 << rank * 8 + file
                            new.rooks |= 1 << rank * 8 + file
                        case "Q":
                            new.white |= 1 << rank * 8 + file
                            new.queens |= 1 << rank * 8 + file
                        case "K":
                            new.white |= 1 << rank * 8 + file
                            new.kings |= 1 << rank * 8 + file

                        case "p":
                            new.black |= 1 << rank * 8 + file
                            new.pawns |= 1 << rank * 8 + file
                        case "n":
                            new.black |= 1 << rank * 8 + file
                            new.knights |= 1 << rank * 8 + file
                        case "b":
                            new.black |= 1 << rank * 8 + file
                            new.bishops |= 1 << rank * 8 + file
                        case "r":
                            new.black |= 1 << rank * 8 + file
                            new.rooks |= 1 << rank * 8 + file
                        case "q":
                            new.black |= 1 << rank * 8 + file
                            new.queens |= 1 << rank * 8 + file
                        case "k":
                            new.black |= 1 << rank * 8 + file
                            new.kings |= 1 << rank * 8 + file
                        case _:
                            raise ValueError("No such piece: " + char)
                    file += 1

        return new


    def to_fen(self) -> str:
        pass

    def __repr__(self) -> str:
        lines = [
            "  A B C D E F G H"
        ]

        for y in range(8):
            lines.append(str(8 - y) + " ")
            for x in range(8):
                lines[-1] = lines[-1] + self.piece_table[self[x, y]]

        return "\n".join(lines)

    @property
    def all_pieces(self) -> Bitboard:
        return self.white | self.black

    @property
    def white_kings(self) -> Bitboard:
        return self.white & self.kings

    @property
    def white_queens(self) -> Bitboard:
        return self.white & self.queens

    @property
    def white_knight(self) -> Bitboard:
        return self.white & self.knights

    @property
    def white_bishop(self) -> Bitboard:
        return self.white & self.bishops

    @property
    def white_rooks(self) -> Bitboard:
        return self.white & self.rooks

    @property
    def white_pawns(self) -> Bitboard:
        return self.white & self.pawns

    @property
    def black_kings(self) -> Bitboard:
        return self.black & self.kings

    @property
    def black_queens(self) -> Bitboard:
        return self.black & self.queens

    @property
    def black_knight(self) -> Bitboard:
        return self.black & self.knights

    @property
    def black_bishop(self) -> Bitboard:
        return self.black & self.bishops

    @property
    def black_rooks(self) -> Bitboard:
        return self.black & self.rooks

    @property
    def black_pawns(self) -> Bitboard:
        return self.black & self.pawns
