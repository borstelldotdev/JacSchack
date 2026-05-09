from abc import ABC, abstractmethod
from typing import Self

from src.logic.enums import PieceType, Player

class Move:
    def __init__(self, from_square: tuple[int, int], to_square: tuple[int, int]) -> None:
        self.from_square = from_square
        self.to_square = to_square

class AbstractBoard(ABC):
    empty_square = (PieceType.NONE, Player.NONE)

    piece_table = {
        empty_square: ".",

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

    reverse_piece_table = {v: k for k, v in piece_table.items()}

    @abstractmethod
    def __init__(self):
        self.to_move: Player = Player.NONE
        self.white_castle_queenside: bool = False
        self.black_castle_queenside: bool = False
        self.white_castle_kingside: bool = False
        self.black_castle_kingside: bool = False
        self.en_passant_square: tuple[int, int] | None = None
        self.halfmove: int = 0
        self.fullmove: int = 1


    @abstractmethod
    def at(self, x, y) -> tuple[PieceType, Player]:
        pass

    def __getitem__(self, value: tuple[int, int]):
        return self.at(value[0], value[1])

    def __repr__(self) -> str:
        lines = [
            "  A B C D E F G H"
        ]

        for y in range(8):
            lines.append(str(8 - y) + " ")
            for x in range(8):
                lines[-1] = lines[-1] + self.piece_table[self[x, y]]

        return "\n".join(lines)

    @abstractmethod
    def __setitem__(self, key: tuple[int, int], value: tuple[PieceType, Player]):
        pass

    @classmethod
    @abstractmethod
    def from_fen(cls, fen: str) -> Self:
        pass

    def to_fen(self) -> str:
        fen = ""
        for y in range(8):
            for x in range(8):
                if self[x, y] == self.empty_square:
                    if fen and fen[-1].isdigit():
                        fen = fen[:-1] + str(int(fen[-1]) + 1)
                    else:
                        fen += "1"
                else:
                    fen += self.piece_table[self[x, y]]
            fen += "/"

        fen = fen[:-1] + " "
        fen += {Player.WHITE: "w", Player.BLACK: "b"}[self.to_move]

        fen += " "
        if self.white_castle_kingside:
            fen += "K"
        if self.white_castle_queenside:
            fen += "Q"
        if self.black_castle_kingside:
            fen += "k"
        if self.black_castle_queenside:
            fen += "q"
        if fen.endswith(" "):
            fen += "-"

        fen += " "
        if self.en_passant_square:
            fen += "abcdefgh"[self.en_passant_square[0]]
            fen += "87654321"[self.en_passant_square[1]]
        else:
            fen += "-"

        fen += " "
        fen += str(self.halfmove)
        fen += " "
        fen += str(self.fullmove)

        return fen

    @classmethod
    def starting_position(cls):
        return cls.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    @classmethod
    def empty(cls):
        return cls.from_fen("8/8/8/8/8/8/8/8 w - - 0 1")

    @staticmethod
    def square_to_cords(square: str) -> tuple[int, int]:
        return "abcdefgh".index(square[0].lower()), 8 - int(square[1])

    @property
    @abstractmethod
    def moves(self) -> list[Move]:
        pass

    @abstractmethod
    def make_move(self, move: Move) -> Self:
        pass