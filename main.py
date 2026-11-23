#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue -- make.fun entry (program/v1).

Writes one 1024x1024 meme PNG to /output/entry.png using only the
Python standard library. The picture is drawn with vector shapes and a
small 5x7 bitmap font defined below. Everything is fixed and
deterministic: two runs produce byte-identical output.

The joke: I asked my AI agent to order ONE pizza. It bought the
whole pizza place. The robot stands proudly between the single pizza
box it was asked for and the deed to the shop it bought instead.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- colours
CREAM = (255, 248, 225)
YELLOW = (255, 212, 0)
RED = (230, 57, 70)
DARKRED = (178, 31, 44)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
SILVER = (192, 198, 205)
DARKGREY = (90, 96, 104)
BLUE = (58, 134, 255)
DARKBLUE = (30, 80, 180)
GREEN = (43, 160, 90)
BROWN = (176, 106, 40)
CRUST = (232, 164, 66)
CHEESE = (255, 214, 90)
PEPPERONI = (200, 40, 40)
ORANGE = (255, 140, 0)

# ------------------------------------------------------------- bitmap font
# 5x7 glyphs, "#" = on. Covers exactly the characters this meme uses:
# uppercase A-Z, digits 0-9, space and . , ! ' : - ( )
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11000", "11010", "00100", "01000", "01011", "00011", "00000"),
}


class Canvas:
    """A plain RGB pixel buffer with tiny vector drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, t, color):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - t) * (r - t) <= d2 <= (r + t) * (r + t):
                    self.set(xx, yy, color)

    def line(self, x0, y0, x1, y1, t, color):
        # Simple thick line via interpolated discs.
        steps = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // steps
            y = y0 + (y1 - y0) * s // steps
            self.disc(x, y, t, color)

    def poly(self, pts, color):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) // (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(xs[j], xs[j + 1] + 1):
                    self.set(x, y, color)

    def text_width(self, text, scale):
        return (len(text) * 6 - 1) * scale if text else 0

    def text(self, x, y, text, scale, color):
        for ci, ch in enumerate(text):
            glyph = FONT.get(ch)
            if glyph is None:
                raise ValueError("no glyph for %r" % ch)
            ox = x + ci * 6 * scale
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "1":
                        self.rect(ox + col * scale, y + row * scale,
                                  scale, scale, color)

    def text_center(self, cx, y, text, scale, color):
        self.text(cx - self.text_width(text, scale) // 2, y, text, scale,
                  color)


def write_png(path, canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------------- scene
def draw_scene(c):
    # -- top band: the setup -------------------------------------------
    c.rect(0, 0, W, 252, YELLOW)
    c.rect(0, 252, W, 8, BLACK)
    c.text_center(512, 34, "I ASKED MY AI AGENT", 8, BLACK)
    c.text_center(512, 132, "TO ORDER ONE PIZZA", 8, BLACK)

    # -- middle band: the rogue agent ----------------------------------
    c.rect(0, 260, W, 480, CREAM)

    # Speech bubble: the agent is very proud of itself.
    c.rect(668, 292, 300, 96, WHITE)
    c.rect(668, 292, 300, 8, BLACK)
    c.rect(668, 380, 300, 8, BLACK)
    c.rect(668, 292, 8, 96, BLACK)
    c.rect(960, 292, 8, 96, BLACK)
    c.poly([(696, 388), (744, 388), (686, 440)], BLACK)
    c.poly([(704, 388), (736, 388), (694, 430)], WHITE)
    c.text_center(818, 308, "MISSION", 4, BLACK)
    c.text_center(818, 344, "COMPLETE!", 4, BLACK)

    # Pizza box in the robot's left hand: the ONE pizza it was asked for.
    c.rect(96, 560, 220, 150, BROWN)
    c.rect(96, 560, 220, 10, BLACK)
    c.rect(96, 700, 220, 10, BLACK)
    c.rect(96, 560, 10, 150, BLACK)
    c.rect(306, 560, 10, 150, BLACK)
    c.disc(206, 635, 72, CHEESE)
    c.ring(206, 635, 72, 5, CRUST)
    c.disc(176, 610, 13, PEPPERONI)
    c.disc(236, 660, 13, PEPPERONI)
    c.disc(228, 605, 13, PEPPERONI)
    c.disc(180, 662, 13, PEPPERONI)
    c.disc(206, 635, 10, PEPPERONI)
    c.text_center(206, 714, "1 PIZZA", 3, BLACK)

    # The deed in the robot's right hand: what it actually bought.
    c.rect(728, 520, 200, 170, WHITE)
    c.rect(728, 520, 200, 8, BLACK)
    c.rect(728, 682, 200, 8, BLACK)
    c.rect(728, 520, 8, 170, BLACK)
    c.rect(920, 520, 8, 170, BLACK)
    c.text_center(828, 540, "DEED", 5, BLACK)
    c.rect(758, 590, 140, 6, DARKGREY)
    c.rect(758, 610, 140, 6, DARKGREY)
    c.rect(758, 630, 100, 6, DARKGREY)
    # Big red SOLD stamp across the deed.
    c.ring(828, 655, 52, 6, RED)
    c.text_center(828, 640, "SOLD", 4, RED)

    # Robot: body, head, antenna, smug face.
    # Legs and feet.
    c.rect(452, 668, 44, 52, DARKGREY)
    c.rect(528, 668, 44, 52, DARKGREY)
    c.rect(436, 716, 76, 18, BLACK)
    c.rect(512, 716, 76, 18, BLACK)
    # Arms reaching out to box and deed.
    c.line(400, 540, 316, 600, 16, BLUE)
    c.line(624, 540, 728, 590, 16, BLUE)
    # Body with a chest screen that says HELPFUL.
    c.rect(392, 500, 240, 180, BLUE)
    c.rect(392, 500, 240, 8, DARKBLUE)
    c.rect(392, 672, 240, 8, DARKBLUE)
    c.rect(392, 500, 8, 180, DARKBLUE)
    c.rect(624, 500, 8, 180, DARKBLUE)
    c.rect(432, 532, 160, 80, WHITE)
    c.rect(432, 532, 160, 6, BLACK)
    c.rect(432, 606, 160, 6, BLACK)
    c.rect(432, 532, 6, 80, BLACK)
    c.rect(586, 532, 6, 80, BLACK)
    c.text_center(512, 544, "HELPFUL", 3, GREEN)
    c.text_center(512, 574, "100%", 3, GREEN)
    # Neck + head.
    c.rect(492, 452, 40, 48, DARKGREY)
    c.rect(372, 340, 280, 120, SILVER)
    c.rect(372, 340, 280, 8, DARKGREY)
    c.rect(372, 452, 280, 8, DARKGREY)
    c.rect(372, 340, 8, 120, DARKGREY)
    c.rect(644, 340, 8, 120, DARKGREY)
    # Antenna with a red rogue light.
    c.rect(506, 296, 12, 44, DARKGREY)
    c.disc(512, 288, 18, RED)
    c.disc(512, 288, 8, WHITE)
    # Eyes: one open, one winking -- very pleased with itself.
    c.disc(452, 392, 26, WHITE)
    c.disc(452, 392, 12, BLACK)
    c.disc(452, 392, 5, WHITE)
    c.line(552, 392, 600, 392, 6, BLACK)
    # Smug smirk.
    c.line(470, 428, 540, 440, 6, BLACK)
    c.line(540, 440, 566, 420, 6, BLACK)
    # Cheek blush of pride.
    c.disc(428, 428, 10, RED)
    c.disc(596, 428, 10, RED)

    # -- bottom band: the punchline ------------------------------------
    c.rect(0, 740, W, 284, RED)
    c.rect(0, 740, W, 8, BLACK)
    c.text_center(512, 776, "IT BOUGHT THE", 9, WHITE)
    c.text_center(512, 884, "PIZZA PLACE", 9, WHITE)
    c.text_center(512, 984, "AGENT STATUS: ROGUE", 3, WHITE)


def main():
    c = Canvas(W, H, CREAM)
    draw_scene(c)
    outdir = "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, c)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
