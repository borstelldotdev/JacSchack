from typing import Self
from copy import deepcopy

from src.logic.abstract_board import AbstractBoard, Move, SpecialMoveType
from src.logic.bitboard import Bitboard
from src.logic.enums import Player, PieceType

class BoardMailbox(AbstractBoard):
    KNIGHT_MOVES = [(1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1)]
    PERPENDICULAR_MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    DIAGONAL_MOVES = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    KING_QUEEN_MOVES = PERPENDICULAR_MOVES + DIAGONAL_MOVES


    def __init__(self, data: list[tuple[PieceType, Player]], to_move: Player,
                 white_castle_queenside: bool, black_castle_queenside: bool,
                 white_castle_kingside: bool, black_castle_kingside: bool,
                 en_passant_square: tuple[int, int] | None=None, halfmove: int=0, fullmove: int=1,
                 white_attacking: Bitboard | None=None, black_attacking: Bitboard | None=None) -> None:

        self.data: list[tuple[PieceType, Player]] = data

        self.to_move = to_move
        self.white_castle_queenside: bool = white_castle_queenside
        self.black_castle_queenside: bool = black_castle_queenside
        self.white_castle_kingside: bool = white_castle_kingside
        self.black_castle_kingside: bool = black_castle_kingside
        self.en_passant_square: tuple[int, int] | None = en_passant_square
        self.halfmove, self.fullmove = halfmove, fullmove

        self._white_moves: list[Move] | None = None
        self._black_moves: list[Move] | None = None
        self.white_attacking = white_attacking
        self.black_attacking = black_attacking

    def gen_attackers(self):
        pass

    def __setitem__(self, key: tuple[int, int], value: tuple[PieceType, Player]) -> None:
        if 0 <= key[0] < 8 and 0 <= key[1] < 8:
            self.data[key[1] * 8 + key[0]] = value


    @classmethod
    def from_fen(cls, fen: str) -> Self:
        try:
            board, to_move, castle, en_passant, halfmove, fullmove = fen.strip().split(" ")
        except ValueError:
            print("Malformed fen:", fen)
            return cls.empty()

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
                    new.data.extend([cls.empty_square] * int(char))
                else:
                    new.data.append(cls.reverse_piece_table[char])
        return new

    def at_unsafe(self, x, y) -> tuple[PieceType, Player]:
        return self.data[y * 8 + x]

    def at(self, x, y) -> tuple[PieceType, Player]:
        if 0 <= x < 8 and 0 <= y < 8:
            return self.data[y * 8 + x]
        return self.empty_square

    @property
    def me_attacking(self) -> Bitboard:
        return self.white_attacking if self.to_move == Player.WHITE else self.black_attacking

    @me_attacking.setter
    def me_attacking(self, value: Bitboard) -> None:
        if self.to_move == Player.WHITE:
            self.white_attacking = value
        else:
            self.black_attacking = value

    @property
    def opponent_attacking(self) -> Bitboard:
        return self.black_attacking if self.to_move == Player.WHITE else self.white_attacking

    @opponent_attacking.setter
    def opponent_attacking(self, value: Bitboard) -> None:
        if self.to_move == Player.WHITE:
            self.black_attacking = value
        else:
            self.white_attacking = value

    @property
    def opponent(self):
        return self.to_move * -1

    def relative_moves(self, player: int, from_square: tuple[int, int], patterns: list[tuple[int, int]],
                       multimove: bool=False) -> list[Move]:

        moves: list[Move] = []
        for pattern in patterns:
            cx, cy = from_square
            cx += pattern[0]
            cy += pattern[1]
            if multimove:
                while 0 <= cx < 8 and 0 <= cy < 8:
                    owner = self[cx, cy][1]
                    if owner != player:
                        moves.append(Move(from_square, (cx, cy)))
                    if owner != Player.NONE:
                        break
                    cx += pattern[0]
                    cy += pattern[1]
            else:
                if self[cx, cy][1] != player and 0 <= cx < 8 and 0 <= cy < 8:
                    moves.append(Move(from_square, (cx, cy)))
        return moves

    @property
    def white_moves(self) -> list[Move]:
        if not self._white_moves:
            self.gen_moves()
        return self._white_moves

    @property
    def black_moves(self) -> list[Move]:
        if not self._black_moves:
            self.gen_moves()
        return self._black_moves

    @property
    def my_moves(self) -> list[Move]:
        return self.white_moves if self.to_move == Player.WHITE else self.black_moves

    @property
    def opponent_moves(self) -> list[Move]:
        return self.black_moves if self.to_move == Player.BLACK else self.white_moves

    def gen_moves_at_square(self, x: int, y: int) -> None:
        piece = self.at_unsafe(x, y)  # index kan aldrig komma utanför

        # Ignorera tomma rutor och motståndares pjäser
        if piece == self.empty_square:
            return

        me = piece[1]
        opponent = me * -1
        _moves = self._white_moves if me == Player.WHITE else self._black_moves

        match piece[0]:
            case PieceType.PAWN:
                # Opponent = riktning bonden går åt
                if self[x, y + opponent] == self.empty_square:
                    _moves.append(Move((x, y), (x, y + opponent)))

                    # Flytta två steg från startposition
                    if y == (6 if me == Player.WHITE else 1) \
                            and self[x, y + (opponent * 2)] == self.empty_square:
                        _moves.append(Move((x, y), (x, y + (opponent * 2))))

                # slå andra pjäser + en passant
                if self[x + 1, y + opponent][1] == opponent:
                    _moves.append(Move((x, y), (x + 1, y + opponent)))
                elif self.en_passant_square == (x + 1, y + opponent):
                    _moves.append(Move((x, y), (x + 1, y + opponent),
                                       special_move=SpecialMoveType.EN_PASSANT))

                if self[x - 1, y + opponent][1] == opponent:
                    _moves.append(Move((x, y), (x - 1, y + opponent)))
                elif self.en_passant_square == (x - 1, y + opponent):
                    _moves.append(Move((x, y), (x - 1, y + opponent),
                                       special_move=SpecialMoveType.EN_PASSANT))

            case PieceType.KNIGHT:
                _moves.extend(self.relative_moves(me, (x, y), self.KNIGHT_MOVES))

            case PieceType.BISHOP:
                _moves.extend(self.relative_moves(me, (x, y), self.DIAGONAL_MOVES, multimove=True))

            case PieceType.ROOK:
                _moves.extend(self.relative_moves(me, (x, y), self.PERPENDICULAR_MOVES, multimove=True))

            case PieceType.QUEEN:
                _moves.extend(self.relative_moves(me, (x, y), self.KING_QUEEN_MOVES, multimove=True))

            case PieceType.KING:
                _moves.extend(self.relative_moves(me, (x, y), self.KING_QUEEN_MOVES))

        for move in _moves:
            self.me_attacking = self.me_attacking.set(move.from_square, True)

    def gen_moves(self) -> None:
        self._white_moves = []
        self._black_moves = []
        self.white_attacking = Bitboard(0)
        self.black_attacking = Bitboard(0)
        for x in range(8):
            for y in range(8):
                self.gen_moves_at_square(x, y)

    def make_move(self, move) -> Self:
        new = deepcopy(self)
        piece_to_move: tuple[PieceType, Player] = new[move.from_square]
        new[move.to_square] = piece_to_move
        new[move.from_square] = new.empty_square

        # En passant
        new.en_passant_square = None
        if piece_to_move[0] == PieceType.PAWN:
            new.halfmove = -1
            if move.special_move == SpecialMoveType.EN_PASSANT:
                new[move.to_square[0], move.to_square[1] + new.to_move] = new.empty_square
            if abs(move.from_square[1] - move.to_square[1]) == 2:
                # Tillåt en passant nästa drag
                new.en_passant_square = (move.from_square[0], (move.from_square[1] + move.to_square[1]) // 2)

        # TODO: Rockad
        new.fullmove += 1
        new.halfmove += 1
        new.to_move = new.to_move * -1
        new._white_moves = None
        new._black_moves = None
        return new

    def count_moves(self, depth: int) -> int:
        if depth == 1:
            return len(self.my_moves)
        return sum([self.make_move(x).count_moves(depth - 1) for x in self.my_moves])
