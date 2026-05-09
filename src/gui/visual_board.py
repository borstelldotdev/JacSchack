import pygame, pygame.gfxdraw
import sys
from threading import Thread
from queue import Queue, Empty
from time import sleep

from src.logic.abstract_board import AbstractBoard, Move
from src.logic.enums import PieceType, Player
from src.logic.bitboard import Bitboard
from src.logic.board_mailbox import BoardMailbox


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
ARROW_COLOR =                   pygame.Color(255, 0, 0, 192) # RGBA
ARROW_SHAFT_WIDTH = 8
ARROW_HEAD_SIZE = 30


class VisualBoard:
    def __init__(self, impl: type, board: AbstractBoard=None, highlight_bitboard: Bitboard=None,
                 overlay_bitboard: Bitboard=None, overlay_arrows: list[Move]=[],
                 window_title: str="JacSchack", title: str="", commands: Queue=None, sudo: bool=False):

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(window_title)
        self.clock = pygame.time.Clock()
        self.running = False
        self.commands = commands
        self.sudo: bool = sudo

        assert issubclass(impl, AbstractBoard)
        self.impl = impl
        self.board: AbstractBoard | None = board
        self.highlight_bitboard: Bitboard | None = highlight_bitboard
        self.overlay_bitboard: Bitboard | None = overlay_bitboard
        self.overlay_arrows: list[Move] | None = overlay_arrows
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

    def process_command(self, command: str):
        command = command.split(" ", maxsplit=2)
        cmd, args = command[0], command[1:]
        match cmd.lower():
            case "help":
                print("kommandon:")
                print("`help`: visar hjälp")
                print("`quit`: avslutar JacSchack GUI")
                print("`clear`: återställer brädet")
                print("`fen load <fen>`: laddar en FEN")
                print("`fen dump`: skriver ut den nuvarande positionen som en FEN")
                print("`starting-position`: laddar startpositionen")
                print("`move <move>`: gör ett drag")
                print("`highlight bitboard <bitboard: int>`: markerar rutor enligt ett bitboard")
                if self.sudo:
                    print("`highlight property <property>`: markerar en egenskap hos brädet")
                print("`highlight clear`: tar bort markeringen")
                print("`overlay bitboard <bitboard: int>`: visualiserar ett bitboard")
                print("`overlay clear`: tar bort visualiseringen")
                if self.sudo:
                    print("`overlay property <property>`: visualiserar en egenskap hos brädet")
                    print("`exec <python>`: kör ett python-kommando")

            case "quit":
                self.stop()
            case "clear":
                self.board = None
                self.highlight_bitboard = None
                self.overlay_bitboard = None
                self.selected_square = None
            case "fen":
                if args[0].lower().startswith("load"):
                    self.board = self.impl.from_fen(" ".join(args[1:]))
                elif args[0].lower().startswith("dump"):
                    print(self.board.to_fen())
            case "starting-position":
                self.board = self.impl.starting_position()
            case "highlight":
                if args[0].lower().startswith("clear"):
                    self.highlight_bitboard = None
                elif args[0].lower().startswith("property"):
                    self.highlight_bitboard = Bitboard(getattr(self.board, args[1]))
                elif args[0].lower().startswith("bitboard"):
                    self.highlight_bitboard = Bitboard(int(args[0], 0))
            case "overlay":
                if args[0].lower().startswith("clear"):
                    self.overlay_bitboard = None
                elif args[0].lower().startswith("property"):
                    self.overlay_bitboard = Bitboard(getattr(self.board, args[1]))
                elif args[0].lower().startswith("bitboard"):
                    self.overlay_bitboard = Bitboard(int(args[0], 0))
            case "moves":
                if args[0].lower().startswith("clear"):
                    self.overlay_arrows = []
                if args[0].lower().startswith("show"):
                    self.overlay_arrows = self.board.moves

            case "exec":
                if self.sudo:
                    exec(" ".join(args))
                else:
                    print("`exec` är avstängt. Slå på det med parametern `VisualBoard(allow_exec=True)`")
            case _:
                print(f"Okänt kommando: {cmd}")

    def draw_arrow(self, start: pygame.Vector2, end: pygame.Vector2):
        # Riktnings-vektor
        direction = (pygame.math.Vector2(end) - pygame.math.Vector2(start)).normalize()
        ux, uy = direction.x, direction.y

        # Motsatt riktning
        px = -uy
        py = ux

        # Punkt där "huvudet" börjar
        hx = end.x - ux * ARROW_HEAD_SIZE
        hy = end.y - uy * ARROW_HEAD_SIZE

        half_shaft = ARROW_SHAFT_WIDTH / 2
        half_head = ARROW_HEAD_SIZE / 2

        # Punkter i kropps-polygonen
        shaft_points = [
            (start.x + px * half_shaft, start.y + py * half_shaft),
            (start.x - px * half_shaft, start.y - py * half_shaft),
            (hx - px * half_shaft, hy - py * half_shaft),
            (hx + px * half_shaft, hy + py * half_shaft),
        ]

        # Punkter i "huvudets" polygon
        head_points = [
            (end.x, end.y),
            (hx - px * half_head, hy - py * half_head),
            (hx + px * half_head, hy + py * half_head),
        ]

        # Omvandla till heltal
        shaft_points = [(int(x), int(y)) for x, y in shaft_points]
        head_points = [(int(x), int(y)) for x, y in head_points]

        # För att få transparens att funka
        arrow_surf = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

        # Rita kropp
        pygame.gfxdraw.aapolygon(arrow_surf, shaft_points, ARROW_COLOR)
        pygame.gfxdraw.filled_polygon(arrow_surf, shaft_points, ARROW_COLOR)

        # Rita huvud
        pygame.gfxdraw.aapolygon(arrow_surf, head_points, ARROW_COLOR)
        pygame.gfxdraw.filled_polygon(arrow_surf, head_points, ARROW_COLOR)

        # Rita semi-transparent pil på bräde
        self.screen.blit(arrow_surf, (0, 0))

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


                    if self.highlight_bitboard is not None and self.highlight_bitboard[x, y]:
                        color = color.lerp(HIGHLIGHTED_SQUARE_COLOR, 0.6)

                    elif self.overlay_bitboard is not None:
                        color = color.lerp(BITBOARD_INCLUDED_COLOR if self.overlay_bitboard[x, y]
                                   else BITBOARD_NOT_INCLUDED_COLOR, 0.8)

                    if self.selected_square is not None and self.selected_square == (x, y):
                        color += SELECTED_SQUARE_MODIFIER


                    pygame.draw.rect(self.screen, color,
                                     (BOARD_LEFT_X + x * GRID_SQUARE_SIZE, BOARD_TOP_Y + y * GRID_SQUARE_SIZE,
                                      GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))

            if self.selected_square is not None:
                pygame.draw.rect(self.screen, SELECTED_SQUARE_OUTLINE,
                                 (BOARD_LEFT_X + self.selected_square[0] * GRID_SQUARE_SIZE,
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


            # Rita pilar
            for move in self.overlay_arrows:
                from_pos = pygame.Vector2(BOARD_LEFT_X + GRID_SQUARE_SIZE // 2 + move.from_square[0] * GRID_SQUARE_SIZE,
                                          BOARD_TOP_Y + GRID_SQUARE_SIZE // 2 + move.from_square[1] * GRID_SQUARE_SIZE)
                to_pos = pygame.Vector2(BOARD_LEFT_X + GRID_SQUARE_SIZE // 2 + move.to_square[0] * GRID_SQUARE_SIZE,
                                          BOARD_TOP_Y + GRID_SQUARE_SIZE // 2 + move.to_square[1] * GRID_SQUARE_SIZE)
                self.draw_arrow(from_pos, to_pos)


            # Skriv text
            self.screen.blit(self.font.render(self.title, True, FONT_COLOR), (BOARD_LEFT_X, SIDE_PADDING))

            pygame.display.update()
            if self.commands is not None:
                try:
                    cmd = self.commands.get_nowait()
                    self.process_command(cmd)
                except Empty:
                    pass
                except Exception as e:
                    print("An error occurred: ", e)

            self.clock.tick(60)


        pygame.quit()


def run_console(_queue: Queue):
    while True:
        cmd = input("(JacSchack GUI) > ")
        _queue.put(cmd)
        if cmd.lower().startswith("quit"):
            return
        sleep(0.1)


def main():
    queue = Queue()
    board = VisualBoard(impl=BoardMailbox, commands=queue, sudo=True)
    proc = Thread(
        target=run_console,
        args=(queue,),
        daemon=True
    )
    proc.start()
    board.mainloop()
    sys.exit(0)

if __name__ == "__main__":
    main()

