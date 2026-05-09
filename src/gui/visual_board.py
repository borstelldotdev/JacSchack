import pygame
import sys
from src.logic.board import Bitboard, PieceType, Player, Board
from multiprocessing import Process
from typing import Callable

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
FONT_COLOR =                    pygame.Color(255, 255, 2)


class VisualBoard:
    def __init__(self, board: Board=None, highlight_bitboard: Bitboard=None, overlay_bitboard: Bitboard=None,
                 window_title: str="JacSchack", title: str=""):

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(window_title)
        self.clock = pygame.time.Clock()
        self.running = False

        self.board: Board | None = board
        self.highlight_bitboard: Bitboard | None = highlight_bitboard
        self.overlay_bitboard: Bitboard | None = overlay_bitboard
        self.selected_square: tuple[int, int] | None = None
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

    def stop(self):
        self.running = False

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


class Backend:
    def __init__(self, board_setter: Callable[[Board | None], None], highlight_setter: Callable[[Bitboard | None], None],
                 overlay_setter: Callable[[Bitboard | None], None], selected_setter: Callable[[tuple[int, int] | None], None],
                 visual_stopper: Callable[[], None],):
        print("JacSchack GUI")
        print("Använd `help` för att visa hjälp")

        self.board_setter = board_setter
        self.highlight_setter = highlight_setter
        self.overlay_setter = overlay_setter
        self.selected_setter = selected_setter
        self.visual_stopper = visual_stopper
        self.running: bool = False

    def mainloop(self):
        self.running = True
        while self.running:
            cmd = input("(JacSchack GUI) > ")
            if isinstance(cmd, str):
                self.process_command(cmd)

    def process_command(self, command: str):
        cmd, args = command.split(" ", maxsplit=2)
        match cmd.lower():
            case "help":
                print("kommandon:")
                print("`help`: visar hjälp")
                print("`quit`: avslutar JacSchack GUI")
                print("`clear`: återställer brädet")
                print("`fen <fen>`: laddar en FEN")
                print("`starting-position`: laddar startpositionen")
                print("`highlight <bitboard: int>`: markerar rutor enligt ett bitboard")
                print("`highlight clear`: tar bort markeringen")
                print("`overlay <bitboard: int>`: visualiserar ett bitboard")
                print("`overlay clear`: tar bort visualiseringen")

            case "quit":
                self.visual_stopper()
                self.running = False
            case "clear":
                self.board_setter(None)
                self.highlight_setter(None)
                self.overlay_setter(None)
                self.selected_setter(None)
            case "fen":
                self.board_setter(Board.from_fen(args))
            case "starting-position":
                self.board_setter(Board.starting_position())
            case "highlight":
                if args.lower().startswith("clear"):
                    self.highlight_setter(None)
                else:
                    self.highlight_setter(Bitboard(int(args, 0)))
            case "overlay":
                if args.lower().startswith("clear"):
                    self.overlay_setter(None)
                else:
                    self.overlay_setter(Bitboard(int(args, 0)))



if __name__ == "__main__":
    board = VisualBoard()
    backend = Backend(board)
    proc = Process(
        target=backend.mainloop,
        args=(lambda x: board.x),
        daemon=True
    )
    proc.start()
    board.mainloop()
    sys.exit(0)

