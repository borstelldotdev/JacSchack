from typing import Self

class Bitboard(int):
    # Bitboard order:
    #
    # (rank 8): 0 . . . 7
    #           .       .
    # (rank 1)  56 . . .63

    BITBOARD_SIZE = 0xFF_FF_FF_FF_FF_FF_FF_FF
    FILE = 0x01_01_01_01_01_01_01_01

    def __new__(cls, data: int) -> Self:
        return int.__new__(cls, data)

    def shift_vertical(self, y: int):
        if y > 0:
            return Bitboard(self << y * 8)
        else:
            return Bitboard((self >> y * -8) & self.BITBOARD_SIZE)

    @classmethod
    def left_files(cls, n: int):
        return cls(~(cls.FILE * ((1 << n) - 1)))

    @classmethod
    def right_files(cls, n: int):
        return cls(cls.FILE * ((1 << (8 - n)) - 1))

    def shift_horisontal(self, x: int):
        if x > 0:
            return Bitboard(((self & self.right_files(x)) << x) & self.BITBOARD_SIZE)
        else:
            return Bitboard((self & self.left_files(-x)) >> -x)

    def shift(self, x: int, y: int):
        return self.shift_horisontal(x).shift_vertical(y)

    def at(self, x: int, y: int) -> bool:
        mask = 1 << (y * 8 + x)
        return (self & mask) != 0

    def __getitem__(self, key: tuple[int, int]):
        return self.at(key[0], key[1])

    def set(self, key: tuple[int, int], value: bool):
        if not (0 <= key[0] < 8 and 0 <= key[1] < 8): return self
        mask = 1 << (key[1] * 8 + key[0])
        return Bitboard((self & ~mask) | (mask * int(value)))

    def __repr__(self) -> str:
        lines = [
            "  A B C D E F G H"
        ]

        for y in range(8):
            lines.append(str(8 - y) + " ")
            for x in range(8):
                lines[-1] = lines[-1] + ("X " if self[x, y] else ". ")

        return "\n".join(lines)