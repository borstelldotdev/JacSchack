from typing import Self
from copy import deepcopy

from src.logic.abstract_board import AbstractBoard, Move, SpecialMoveType
from src.logic.bitboard import Bitboard
from src.logic.enums import Player, PieceType

class BoardMailbox(AbstractBoard):
    KNIGHT_MOVES = [(1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1)]
    ORTHOGONAL_MOVES= [(1, 0), (-1, 0), (0, 1), (0, -1)]
    DIAGONAL_MOVES = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    KING_QUEEN_MOVES = ORTHOGONAL_MOVES + DIAGONAL_MOVES


    def __init__(self, data: list[tuple[PieceType, Player]], to_move: Player,
                 white_castle_queenside: bool, black_castle_queenside: bool,
                 white_castle_kingside: bool, black_castle_kingside: bool,
                 en_passant_square: tuple[int, int] | None=None, halfmove: int=0, fullmove: int=1,
                 white_attacking: Bitboard | None=None, black_attacking: Bitboard | None=None,
                 white_king: tuple[int, int]=None, black_king: tuple[int, int]=None) -> None:

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
        self.white_king: tuple[int, int] = white_king
        self.black_king: tuple[int, int] = black_king

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
                    if char == "k":
                        new.black_king = (file, rank)
                    elif char == "K":
                        new.white_king = (file, rank)
                    file += 1
        new.gen_moves(Player.BOTH)
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
                    owner = self.at_unsafe(cx, cy)[1]
                    if owner != player:
                        moves.append(Move(from_square, (cx, cy)))
                    if owner != Player.NONE:
                        break
                    cx += pattern[0]
                    cy += pattern[1]
            else:
                # Kan hamna utanför
                if self[cx, cy][1] != player and 0 <= cx < 8 and 0 <= cy < 8:
                    moves.append(Move(from_square, (cx, cy)))
        return moves

    @property
    def white_moves(self) -> list[Move]:
        if not self._white_moves:
            self.gen_moves(Player.BOTH)
        return self._white_moves

    @property
    def black_moves(self) -> list[Move]:
        if not self._black_moves:
            self.gen_moves(Player.BOTH)
        return self._black_moves

    def is_legal(self, player_to_move: Player) -> bool:
        king_start = self.white_king if player_to_move == Player.BLACK else self.black_king  # Motståndarens kung
        for direction in self.ORTHOGONAL_MOVES:
            king_x, king_y = king_start
            king_x += direction[0]
            king_y += direction[1]
            steps = 0
            while 0 <= king_x < 8 and 0 <= king_y < 8:
                steps += 1
                piece = self.at_unsafe(king_x, king_y)
                if piece != self.empty_square:
                    if piece[1] == player_to_move and (piece[0] == PieceType.ROOK or piece[0] == PieceType.QUEEN
                                                        or (piece[0] == PieceType.KING and steps == 1)):
                        return False
                    break
                king_x += direction[0]
                king_y += direction[1]

        for direction in self.DIAGONAL_MOVES:
            king_x, king_y = king_start
            king_x += direction[0]
            king_y += direction[1]
            steps = 0
            while 0 <= king_x < 8 and 0 <= king_y < 8:
                steps += 1
                piece = self[king_x, king_y]
                if piece != self.empty_square:
                    if piece[1] == player_to_move and (piece[0] == PieceType.BISHOP or piece[0] == PieceType.QUEEN or (
                                piece[0] == PieceType.PAWN and ((king_x + 1, king_y - player_to_move) == king_start
                                                         or (king_x - 1, king_y - player_to_move) == king_start))
                                or (piece[0] == PieceType.KING and steps == 1)):
                        return False
                    break
                king_x += direction[0]
                king_y += direction[1]

        for direction in self.KNIGHT_MOVES:
            if self[king_start[0] + direction[0], king_start[1] + direction[1]] == (PieceType.KNIGHT, player_to_move):
                return False

        return True


    def is_legal_move(self, move: Move, to_move: Player) -> bool:
        msk = move.from_square[0] + (move.from_square[1] * 8)
        if move.special_move == SpecialMoveType.KINGSIDE_CASTLE and (
                self.opponent_attacking & (3 << msk)):
            return False
        elif move.special_move == SpecialMoveType.QUEENSIDE_CASTLE and (
                self.opponent_attacking & (3 << (msk - 1))):
            return False


        new = self.make_move(move)
        new.to_move = to_move * -1
        return new.is_legal(to_move * -1)

    def is_in_check(self, player: Player) -> bool:
        return self.is_legal(player * -1)


    def is_empty(self, x: int, y: int) -> bool:
        return self[x, y] == self.empty_square


    def gen_moves_at_square(self, x: int, y: int) -> tuple[list[Move], Player]:
        piece = self.at_unsafe(x, y)  # index kan aldrig komma utanför

        # Ignorera tomma rutor och motståndares pjäser
        if piece == self.empty_square:
            return [], Player.NONE

        me = piece[1]
        opponent = me * -1
        _moves = []

        match piece[0]:
            case PieceType.PAWN:
                # Opponent = riktning bonden går åt
                if self[x, y + opponent] == self.empty_square:
                    if (y + opponent == 0) or (y + opponent == 7):
                        for t in [SpecialMoveType.PROMOTE_QUEEN, SpecialMoveType.PROMOTE_BISHOP,
                                  SpecialMoveType.PROMOTE_KNIGHT, SpecialMoveType.PROMOTE_ROOK]:
                            _moves.append(Move((x, y), (x, y + opponent), special_move=t))
                    else:
                        _moves.append(Move((x, y), (x, y + opponent)))

                    # Flytta två steg från startposition
                    if y == (6 if me == Player.WHITE else 1) \
                            and self[x, y + (opponent * 2)] == self.empty_square:
                        _moves.append(Move((x, y), (x, y + (opponent * 2))))

                # slå andra pjäser + en passant
                if self[x + 1, y + opponent][1] == opponent:
                    if (y + opponent == 0) or (y + opponent == 7):
                        for t in [SpecialMoveType.PROMOTE_QUEEN, SpecialMoveType.PROMOTE_BISHOP,
                                  SpecialMoveType.PROMOTE_KNIGHT, SpecialMoveType.PROMOTE_ROOK]:
                            _moves.append(Move((x, y), (x + 1, y + opponent), special_move=t))
                    else:
                        _moves.append(Move((x, y), (x + 1, y + opponent)))
                elif self.en_passant_square == (x + 1, y + opponent):
                    _moves.append(Move((x, y), (x + 1, y + opponent),
                                       special_move=SpecialMoveType.EN_PASSANT))


                if self[x - 1, y + opponent][1] == opponent:
                    if (y + opponent == 0) or (y + opponent == 7):
                        for t in [SpecialMoveType.PROMOTE_QUEEN, SpecialMoveType.PROMOTE_BISHOP,
                                  SpecialMoveType.PROMOTE_KNIGHT, SpecialMoveType.PROMOTE_ROOK]:
                            _moves.append(Move((x, y), (x - 1, y + opponent), special_move=t))
                    else:
                        _moves.append(Move((x, y), (x - 1, y + opponent)))
                elif self.en_passant_square == (x - 1, y + opponent):
                    _moves.append(Move((x, y), (x - 1, y + opponent),
                                       special_move=SpecialMoveType.EN_PASSANT))

            case PieceType.KNIGHT:
                _moves.extend(self.relative_moves(me, (x, y), self.KNIGHT_MOVES))

            case PieceType.BISHOP:
                _moves.extend(self.relative_moves(me, (x, y), self.DIAGONAL_MOVES, multimove=True))

            case PieceType.ROOK:
                _moves.extend(self.relative_moves(me, (x, y), self.ORTHOGONAL_MOVES, multimove=True))

            case PieceType.QUEEN:
                _moves.extend(self.relative_moves(me, (x, y), self.KING_QUEEN_MOVES, multimove=True))

            case PieceType.KING:
                _moves.extend(self.relative_moves(me, (x, y), self.KING_QUEEN_MOVES))
                if me == Player.WHITE:
                    if self.white_castle_kingside and self.is_empty(5, 7) and self.is_empty(6, 7):
                        _moves.append(Move((4, 7), (6, 7), special_move=SpecialMoveType.KINGSIDE_CASTLE))
                    if (self.white_castle_queenside and self.is_empty(1, 7) and
                            self.is_empty(2, 7) and self.is_empty(3, 7)):
                        _moves.append(Move((4, 7), (2, 7), special_move=SpecialMoveType.QUEENSIDE_CASTLE))

                elif me == Player.BLACK:
                    if self.black_castle_kingside and self.is_empty(5, 0) and self.is_empty(6, 0):
                        _moves.append(Move((4, 0), (6, 0), special_move=SpecialMoveType.KINGSIDE_CASTLE))
                    if (self.black_castle_queenside and self.is_empty(1, 0) and
                            self.is_empty(2, 0) and self.is_empty(3, 0)):
                        _moves.append(Move((4, 0), (2, 0), special_move=SpecialMoveType.QUEENSIDE_CASTLE))

        return _moves, me

    def gen_moves(self, remove_illegal_players: Player) -> None:
        self._white_moves = []
        self._black_moves = []
        self.white_attacking = Bitboard(0)
        self.black_attacking = Bitboard(0)
        for x in range(8):
            for y in range(8):
                moves, player = self.gen_moves_at_square(x, y)
                if player == Player.WHITE:
                    self._white_moves.extend(moves)
                elif player == Player.BLACK:
                    self._black_moves.extend(moves)

        for move in self._white_moves:
            self.white_attacking = self.white_attacking.set(move.to_square, True)
        for move in self._black_moves:
            self.black_attacking = self.black_attacking.set(move.to_square, True)

        if remove_illegal_players == Player.WHITE or remove_illegal_players == Player.BOTH:
            self.remove_illegal_moves_white()
        if remove_illegal_players == Player.BLACK or remove_illegal_players == Player.BOTH:
            self.remove_illegal_moves_black()

    def remove_illegal_moves_white(self):
        i = 0
        while i < len(self._white_moves):
            if self.is_legal_move(self._white_moves[i], Player.WHITE):
                i += 1
            else:
                self._white_moves.pop(i)

    def remove_illegal_moves_black(self):
        i = 0
        while i < len(self._black_moves):
            if self.is_legal_move(self._black_moves[i], Player.BLACK):
                i += 1
            else:
                self._black_moves.pop(i)

    def make_move(self, move, gen_moves: bool=False) -> Self:
        # TODO: in-place moves !!!
        new = BoardMailbox(self.data[:], self.to_move * -1, self.white_castle_queenside, self.black_castle_queenside,
                           self.white_castle_kingside, self.black_castle_kingside, halfmove=self.halfmove + 1,
                           fullmove=self.fullmove + 1, white_king=self.white_king, black_king=self.black_king)
        piece_to_move: tuple[PieceType, Player] = new[move.from_square]
        new[move.to_square] = piece_to_move
        new[move.from_square] = new.empty_square

        # Bonde-saker
        if piece_to_move[0] == PieceType.PAWN:
            new.halfmove = 0
            if abs(move.from_square[1] - move.to_square[1]) == 2:
                # Tillåt en passant nästa drag
                new.en_passant_square = (move.from_square[0], (move.from_square[1] + move.to_square[1]) // 2)

        elif piece_to_move[0] == PieceType.KING:
            if piece_to_move[1] == Player.WHITE:
                new.white_king = move.to_square
                new.white_castle_kingside = False
                new.white_castle_queenside = False
            elif piece_to_move[1] == Player.BLACK:
                new.black_king = move.to_square
                new.black_castle_kingside = False
                new.black_castle_queenside = False

        elif piece_to_move[0] == PieceType.ROOK:
            match move.from_square:
                case (0, 0):
                    new.black_castle_queenside = False
                case (7, 0):
                    new.black_castle_kingside = False
                case (0, 7):
                    new.white_castle_queenside = False
                case (7, 7):
                    new.white_castle_kingside = False

        match move.to_square:
            case (0, 0):
                new.black_castle_queenside = False
            case (7, 0):
                new.black_castle_kingside = False
            case (0, 7):
                new.white_castle_queenside = False
            case (7, 7):
                new.white_castle_kingside = False

        match move.special_move:
            case SpecialMoveType.NONE:
                pass
            case SpecialMoveType.PROMOTE_KNIGHT:
                new[move.to_square] = (PieceType.KNIGHT, piece_to_move[1])
            case SpecialMoveType.PROMOTE_BISHOP:
                new[move.to_square] = (PieceType.BISHOP, piece_to_move[1])
            case SpecialMoveType.PROMOTE_ROOK:
                new[move.to_square] = (PieceType.ROOK, piece_to_move[1])
            case SpecialMoveType.PROMOTE_QUEEN:
                new[move.to_square] = (PieceType.QUEEN, piece_to_move[1])
            case SpecialMoveType.EN_PASSANT:
                new[move.to_square[0], move.to_square[1] - new.to_move] = new.empty_square
            case SpecialMoveType.KINGSIDE_CASTLE:
                # Tornet hamnar på höger sida
                new[5, move.to_square[1]] = new[7, move.to_square[1]]
                new[7, move.to_square[1]] = new.empty_square
            case SpecialMoveType.QUEENSIDE_CASTLE:
                # Tornet hamnar på vänster sida
                new[3, move.to_square[1]] = new[0, move.to_square[1]]
                new[0, move.to_square[1]] = new.empty_square

        new._white_moves = None
        new._black_moves = None
        new.white_attacking = None
        new.black_attacking = None
        if gen_moves:
            new.gen_moves(Player.BOTH)
        return new

    def count_moves(self, depth: int) -> int:
        if depth == 1:
            return len(self.my_moves)
        return sum(self.make_move(x).count_moves(depth - 1) for x in self.my_moves)
