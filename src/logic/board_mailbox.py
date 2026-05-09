from typing import Self

from src.logic.abstract_board import AbstractBoard
from src.logic.enums import Player, PieceType

class BoardMailbox(AbstractBoard):
    def __init__(self, data: list[tuple[PieceType, Player]], to_move: Player,
                 white_castle_queenside: bool, black_castle_queenside: bool,
                 white_castle_kingside: bool, black_castle_kingside: bool,
                 en_passant_square: tuple[int, int] | None=None, halfmove: int=0, fullmove: int=1) -> None:

        self.data: list[tuple[PieceType, Player]] = data

        self.to_move = to_move
        self.white_castle_queenside: bool = white_castle_queenside
        self.black_castle_queenside: bool = black_castle_queenside
        self.white_castle_kingside: bool = white_castle_kingside
        self.black_castle_kingside: bool = black_castle_kingside
        self.en_passant_square: tuple[int, int] | None = en_passant_square
        self.halfmove, self.fullmove = halfmove, fullmove

    @classmethod
    def from_fen(cls, fen: str) -> Self:
        board, to_move, castle, en_passant, halfmove, fullmove = fen.split(" ")

        if to_move == "w":
            player_to_move = Player.WHITE
        elif to_move == "b":
            player_to_move = Player.BLACK
        else:
            player_to_move = Player.NONE

        new = cls(data=[], to_move=player_to_move,
                  white_castle_kingside="K" in castle, white_castle_queenside="Q" in castle,
                  black_castle_kingside="k" in castle, black_castle_queenside="q" in castle,
                  en_passant_square=cls.square_to_cords(en_passant) if en_passant != "-" else None,
                  halfmove=int(halfmove),
                  fullmove=int(fullmove))

        ranks = board.split("/")
        for rank in range(8):
            file = 0
            for char in list(ranks[rank]):
                if char.isdigit():
                    file += int(char)
                    new.data.extend([(PieceType.NONE, Player.NONE)] * int(char))
                else:
                    new.data.append(cls.reverse_piece_table[char])
        return new

    def at(self, x, y) -> tuple[PieceType, Player]:
        return self.data[y * 8 + x]