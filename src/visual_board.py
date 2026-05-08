import pygame
from pygame.examples.prevent_display_stretching import BACKGROUNDCOLOR

from board import PieceType, Player, Board
from sys import exit

from src.board import Bitboard

GRID_SQUARE_SIZE = 60
FONT_SIZE = 30
TOP_PADDING = 80
SIDE_PADDING = 20
OUTLINE = 4

HEIGHT = TOP_PADDING + SIDE_PADDING * 2 + GRID_SQUARE_SIZE * 8
WIDTH = SIDE_PADDING * 2 + GRID_SQUARE_SIZE * 8
BOARD_LEFT_X = SIDE_PADDING
BOARD_TOP_Y = TOP_PADDING + SIDE_PADDING


BACKGROUND_COLOR =              pygame.Color(48, 48, 48)
LIGHT_SQUARE_COLOR =            pygame.Color(255, 206, 158)
DARK_SQUARE_COLOR =             pygame.Color(209, 139, 71)
BITBOARD_INCLUDED_COLOR =       pygame.Color(54, 112, 207)
BITBOARD_NOT_INCLUDED_COLOR =   pygame.Color(191, 62, 55)
HIGHLIGHTED_SQUARE_COLOR =      pygame.Color(25, 224, 155)
SELECTED_SQUARE_MODIFIER =      pygame.Color(40, 30, 0)
SELECTED_SQUARE_OUTLINE =       pygame.Color(80, 80, 80)
FONT_COLOR =                    pygame.Color(255, 255, 255)


class VisualBoard:
    def __init__(self, board: Board=None, highlight_bitboard: Bitboard=None, overlay_bitboard: Bitboard=None,
                 target_eval: int=None, title: str=""):

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = False

        self.board: Board = board
        self.highlight_bitboard: Bitboard = highlight_bitboard
        self.overlay_bitboard: Bitboard = overlay_bitboard
        self.selected_square: tuple[int, int] = None
        self.target_eval = target_eval
        self.actual_eval = 0
        self.title = title
        self.font = pygame.font.SysFont(None, FONT_SIZE)

        self.PIECES = {
            (PieceType.PAWN, Player.WHITE): pygame.image.load("assets/pawn-white.png"),
            (PieceType.KNIGHT, Player.WHITE): pygame.image.load("assets/knight-white.png"),
            (PieceType.BISHOP, Player.WHITE): pygame.image.load("assets/bishop-white.png"),
            (PieceType.ROOK, Player.WHITE): pygame.image.load("assets/rook-white.png"),
            (PieceType.QUEEN, Player.WHITE): pygame.image.load("assets/queen-white.png"),
            (PieceType.KING, Player.WHITE): pygame.image.load("assets/king-white.png"),

            (PieceType.PAWN, Player.BLACK): pygame.image.load("assets/pawn-black.png"),
            (PieceType.KNIGHT, Player.BLACK): pygame.image.load("assets/knight-black.png"),
            (PieceType.BISHOP, Player.BLACK): pygame.image.load("assets/bishop-black.png"),
            (PieceType.ROOK, Player.BLACK): pygame.image.load("assets/rook-black.png"),
            (PieceType.QUEEN, Player.BLACK): pygame.image.load("assets/queen-black.png"),
            (PieceType.KING, Player.BLACK): pygame.image.load("assets/king-black.png")
        }

        for piece_key in self.PIECES.keys():
            self.PIECES[piece_key] = pygame.transform.scale(self.PIECES[piece_key].convert_alpha(),
                                                       (GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))

    def mainloop(self):
        self.running = True
        while self.running:
            # Event-loop
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        self.running = False
                    case pygame.MOUSEBUTTONDOWN:
                        if pygame.Rect(BOARD_LEFT_X, BOARD_TOP_Y, GRID_SQUARE_SIZE * 8, GRID_SQUARE_SIZE * 8) \
                            .collidepoint(event.pos):
                            x = (event.pos[0] - BOARD_LEFT_X) // GRID_SQUARE_SIZE
                            y = (event.pos[1] - BOARD_TOP_Y) // GRID_SQUARE_SIZE
                            if self.selected_square is None:
                                self.selected_square = (x, y)
                            elif self.selected_square == (x, y):
                                self.selected_square = None
                            else:
                                self.selected_square = (x, y)


            self.screen.fill(BACKGROUND_COLOR)

            # Rita rutor
            for x in range(8):
                for y in range(8):
                    color: pygame.Color = LIGHT_SQUARE_COLOR if x + y & 1 else DARK_SQUARE_COLOR

                    if self.selected_square is not None and self.selected_square == (x, y):
                        color += SELECTED_SQUARE_MODIFIER
                    elif self.highlight_bitboard is not None and self.highlight_bitboard[x, y]:
                        color = color.lerp(HIGHLIGHTED_SQUARE_COLOR, 0.6)

                    elif self.overlay_bitboard is not None:
                        color = color.lerp(BITBOARD_INCLUDED_COLOR if self.overlay_bitboard[x, y]
                                   else BITBOARD_NOT_INCLUDED_COLOR, 0.8)


                    pygame.draw.rect(self.screen, color,
                                     (BOARD_LEFT_X + x * GRID_SQUARE_SIZE, BOARD_TOP_Y + y * GRID_SQUARE_SIZE,
                                      GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))

            if self.selected_square is not None:
                pygame.draw.rect(self.screen, SELECTED_SQUARE_OUTLINE, (BOARD_LEFT_X + self.selected_square[0] * GRID_SQUARE_SIZE,
                                                      BOARD_TOP_Y + self.selected_square[1] * GRID_SQUARE_SIZE,
                                                      GRID_SQUARE_SIZE, GRID_SQUARE_SIZE), width=OUTLINE)

            # Rita pjäser
            if self.board:
                for x in range(8):
                    for y in range(8):
                        piece = self.board[x, y]
                        if piece[0] != PieceType.NONE and piece[1] != Player.NONE:
                            self.screen.blit(self.PIECES[piece], (BOARD_LEFT_X + x * GRID_SQUARE_SIZE,
                                                                  BOARD_TOP_Y + y * GRID_SQUARE_SIZE))

            # Skriv text
            self.screen.blit(self.font.render(self.title, True, FONT_COLOR), (BOARD_LEFT_X, SIDE_PADDING))

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game_board = Board.from_fen("8/5k1p/1p1pRp2/p2P4/P1P3Pp/1P4bP/6K1/8 w - - 0 49")
    visual_board = VisualBoard(title="JacSchack", board=game_board)
    visual_board.mainloop()
    exit(0)

