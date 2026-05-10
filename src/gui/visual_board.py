import pygame, pygame.gfxdraw
import sys
from threading import Thread
from queue import Queue, Empty
from time import sleep
from enum import Enum, auto

from src.logic.abstract_board import AbstractBoard, Move
from src.logic.enums import PieceType, Player
from src.logic.bitboard import Bitboard
from src.logic.board_mailbox import BoardMailbox
from src.logic.search import NegaMax


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


class PlayerController(Enum):
    HUMAN = auto()
    MACHINE = auto()


class VisualBoard:
    def __init__(self, board: AbstractBoard=None, highlight_bitboard: Bitboard=None,
                 overlay_bitboard: Bitboard=None, overlay_arrows: list[Move]=[],
                 window_title: str="JacSchack", title: str="", commands: Queue=None, sudo: bool=False,
                 white_controller: PlayerController=PlayerController.HUMAN,
                 black_controller: PlayerController=PlayerController.HUMAN, engine_depth: int=3):

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(window_title)
        self.clock = pygame.time.Clock()
        self.running = False
        self.commands = commands
        self.sudo: bool = sudo
        self.flipped: bool = False

        self.white_controller: PlayerController = white_controller
        self.black_controller: PlayerController = black_controller
        self.engine_depth: int = engine_depth

        self.board: BoardMailbox | None = board
        self.highlight_bitboard: Bitboard | None = highlight_bitboard
        self.overlay_bitboard: Bitboard | None = overlay_bitboard
        self.overlay_arrows: list[Move] | None = overlay_arrows
        self.selected_square: tuple[int, int] | None = None
        self.pickup_x: int | None = None
        self.pickup_y: int | None = None
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
                print("`highlight property <property>`: markerar en egenskap hos brädet")
                print("`highlight clear`: tar bort markeringen")
                print("`overlay bitboard <bitboard: int>`: visualiserar ett bitboard")
                print("`overlay clear`: tar bort visualiseringen")
                print("`overlay property <property>`: visualiserar en egenskap hos brädet")
                print("`moves show`: visar alla möjliga drag som en pil")
                print("`moves clear`: tar bort alla pilar")
                print("`moves property <property>`: visualiserar en samling drag")
                print("`flip`: Vänd på brädet")
                print("`controller <färg> <kontrollerare>`: bestäm vem som kontrollerar ett bräde")
                print("`engine set-depth <djup>`: Sätt sökdjupet på schackmotorn")
                if self.sudo:
                    print("`exec <python>`: kör ett python-kommando")

            case "quit":
                self.stop()
            case "clear":
                self.board = None
                self.highlight_bitboard = None
                self.overlay_bitboard = None
                self.selected_square = None
                self.overlay_arrows = []
            case "fen":
                if args[0].lower().startswith("load"):
                    self.board = BoardMailbox.from_fen(" ".join(args[1:]))
                elif args[0].lower().startswith("dump"):
                    print(self.board.to_fen())
            case "starting-position":
                self.board = BoardMailbox.starting_position()
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
                elif args[0].lower().startswith("show"):
                    self.overlay_arrows = self.board.my_moves
                elif args[0].lower().startswith("property"):
                    self.overlay_arrows = getattr(self.board, args[1])

            case "flip":
                self.flipped = not self.flipped

            case "controller":
                match (args[0].lower(), args[1].lower()):
                    case ("white", "human"):
                        self.white_controller = PlayerController.HUMAN
                    case ("black", "human"):
                        self.black_controller = PlayerController.HUMAN
                    case ("white", "machine"):
                        self.white_controller = PlayerController.MACHINE
                    case ("black", "machine"):
                        self.black_controller = PlayerController.MACHINE

            case "engine":
                if args[0].lower().startswith("set-depth"):
                    self.engine_depth = int(args[1])

            case "exec":
                if self.sudo:
                    exec(" ".join(args))
                else:
                    print("`exec` är avstängt. Slå på det med parametern `VisualBoard(allow_exec=True)`")
            case "":
                pass
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

    def play_move(self, move: Move):
        self.board = self.board.make_move(move)
        self.highlight_bitboard = None
        self.selected_square = None

    def transform_pos(self, x: int, y: int):
        if self.flipped:
            return x, 7 - y
        else:
            return x, y

    def mainloop(self):
        self.running = True
        while self.running:
            if self.board:
                if len(self.board.my_moves) == 0:
                    self.title = "Schack matt!"

                else:
                    if self.board.to_move == Player.WHITE:
                        if self.white_controller == PlayerController.MACHINE:
                            best = NegaMax().make_decision(self.board, self.engine_depth)
                            self.play_move(best)
                    if self.board.to_move == Player.BLACK:
                        if self.black_controller == PlayerController.MACHINE:
                            best = NegaMax().make_decision(self.board, self.engine_depth)
                            self.play_move(best)


            # Event-loop
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        self.running = False
                    case pygame.MOUSEBUTTONDOWN:
                        if pygame.Rect(BOARD_LEFT_X, BOARD_TOP_Y, GRID_SQUARE_SIZE * 8, GRID_SQUARE_SIZE * 8) \
                            .collidepoint(event.pos):
                            x, y = self.transform_pos((event.pos[0] - BOARD_LEFT_X) // GRID_SQUARE_SIZE,
                                                      (event.pos[1] - BOARD_TOP_Y) // GRID_SQUARE_SIZE)
                            if self.selected_square == (x, y):
                                self.selected_square = None
                                self.highlight_bitboard = None
                            else:
                                no_move_made = True
                                self.pickup_x = (event.pos[0] - BOARD_LEFT_X) % GRID_SQUARE_SIZE
                                self.pickup_y = (event.pos[1] - BOARD_TOP_Y) % GRID_SQUARE_SIZE
                                self.highlight_bitboard = Bitboard(0)
                                for move in self.board.my_moves:
                                    if move.from_square == self.selected_square and move.to_square == (x, y):
                                        self.play_move(move)
                                        no_move_made = False
                                        break
                                    elif move.from_square == (x, y):
                                        self.highlight_bitboard = self.highlight_bitboard.set(move.to_square, True)

                                if no_move_made:
                                    self.selected_square = (x, y)

                    case pygame.MOUSEBUTTONUP:
                        self.pickup_x = None
                        self.pickup_y = None
                        x, y = self.transform_pos((event.pos[0] - BOARD_LEFT_X) // GRID_SQUARE_SIZE,
                                                  (event.pos[1] - BOARD_TOP_Y) // GRID_SQUARE_SIZE)
                        if (x, y) == self.selected_square:
                            continue
                        for move in self.board.my_moves:
                            if move.from_square == self.selected_square and move.to_square == (x, y):
                                self.play_move(move)


            self.screen.fill(BACKGROUND_COLOR)

            # Rita rutor
            for xu in range(8):
                for yu in range(8):
                    x, y = self.transform_pos(xu, yu)
                    color: pygame.Color = LIGHT_SQUARE_COLOR if x + y & 1 else DARK_SQUARE_COLOR


                    if self.highlight_bitboard is not None and self.highlight_bitboard[x, y]:
                        color = color.lerp(HIGHLIGHTED_SQUARE_COLOR, 0.6)

                    elif self.overlay_bitboard is not None:
                        color = color.lerp(BITBOARD_INCLUDED_COLOR if self.overlay_bitboard[x, y]
                                   else BITBOARD_NOT_INCLUDED_COLOR, 0.8)

                    if self.selected_square is not None and self.selected_square == (x, y):
                        color += SELECTED_SQUARE_MODIFIER


                    pygame.draw.rect(self.screen, color,
                                     (BOARD_LEFT_X + xu * GRID_SQUARE_SIZE, BOARD_TOP_Y + yu * GRID_SQUARE_SIZE,
                                      GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))

            if self.selected_square is not None:
                x, y = self.transform_pos(*self.selected_square)
                pygame.draw.rect(self.screen, SELECTED_SQUARE_OUTLINE,
                                 (BOARD_LEFT_X + x * GRID_SQUARE_SIZE,
                                      BOARD_TOP_Y + y * GRID_SQUARE_SIZE,
                                      GRID_SQUARE_SIZE, GRID_SQUARE_SIZE), width=OUTLINE)

            # Rita pjäser
            if self.board:
                for x in range(8):
                    for y in range(8):
                        ix, iy = self.transform_pos(x, y)
                        piece = self.board[ix, iy]
                        if piece[0] != PieceType.NONE and piece[1] != Player.NONE:
                            if (ix, iy) == self.selected_square and pygame.mouse.get_pressed()[0]:
                                pos = pygame.Vector2(pygame.mouse.get_pos())
                                pos -= (self.pickup_x, self.pickup_y)
                            else:
                                pos = (BOARD_LEFT_X + x * GRID_SQUARE_SIZE, BOARD_TOP_Y + y * GRID_SQUARE_SIZE)
                            self.screen.blit(self.PIECES[piece], pos)


            # Rita pilar
            for move in self.overlay_arrows:
                fx, fy = self.transform_pos(*move.from_square)
                tx, ty = self.transform_pos(*move.to_square)
                from_pos = pygame.Vector2(BOARD_LEFT_X + GRID_SQUARE_SIZE // 2 + fx * GRID_SQUARE_SIZE,
                                          BOARD_TOP_Y + GRID_SQUARE_SIZE // 2 + fy * GRID_SQUARE_SIZE)
                to_pos = pygame.Vector2(BOARD_LEFT_X + GRID_SQUARE_SIZE // 2 + tx * GRID_SQUARE_SIZE,
                                          BOARD_TOP_Y + GRID_SQUARE_SIZE // 2 + ty * GRID_SQUARE_SIZE)
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
    queue.put("starting-position")
    board = VisualBoard(commands=queue, sudo=True)
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

