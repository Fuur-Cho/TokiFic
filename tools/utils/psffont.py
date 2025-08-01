"""
反序列化实现参考：
https://github.com/matteosandrin/online-pixel-font-creator/blob/main/src/convert.js#L50
"""

from __future__ import annotations

import base64
from io import StringIO
from os import PathLike
from typing import TextIO, Iterator


def _create_lines_iterator(stream: TextIO) -> Iterator[str]:
    for line in stream:
        line = line.strip()
        if line == '':
            continue
        yield line


class PsfGlyph:
    @staticmethod
    def parse_line(font: PsfFont, line: str) -> tuple[int, PsfGlyph]:
        attrs = line.split(':')
        code_point = int(attrs[0])
        bitmap_data = base64.b64decode(attrs[1])
        width = int(attrs[2]) if len(attrs) >= 5 else font.width
        height = int(attrs[3]) if len(attrs) >= 5 else font.height
        baseline = int(attrs[4]) if len(attrs) >= 5 else font.baseline
        left_offset = int(attrs[5]) if len(attrs) >= 6 else font.left_offset

        pixels = []
        for b in bitmap_data:
            binary = [int(c) for c in f'{b:08b}']
            pixels.extend(binary)

        bitmap = []
        for y in range(height):
            bitmap.append(pixels[y * width:(y + 1) * width])

        glyph = PsfGlyph(
            width,
            height,
            baseline,
            left_offset,
            bitmap,
        )
        return code_point, glyph

    width: int
    height: int
    baseline: int
    left_offset: int
    bitmap: list[list[int]]

    def __init__(
            self,
            width: int,
            height: int,
            baseline: int,
            left_offset: int = 0,
            bitmap: list[list[int]] | None = None,
    ):
        self.width = width
        self.height = height
        self.baseline = baseline
        self.left_offset = left_offset
        self.bitmap = [] if bitmap is None else bitmap


class PsfFont:
    @staticmethod
    def parse(stream: str | TextIO) -> PsfFont:
        if isinstance(stream, str):
            stream = StringIO(stream)
        lines = _create_lines_iterator(stream)

        name = next(lines)
        author = next(lines)
        style = next(lines)

        attrs = next(lines).split(':')
        width = int(attrs[0])
        height = int(attrs[1])
        baseline = int(attrs[2])
        ascend = int(attrs[3])
        descend = int(attrs[4])
        spacing = int(attrs[5])
        em_size = int(attrs[6])
        left_offset = int(attrs[7]) if len(attrs) >= 8 else 0

        font = PsfFont(
            name,
            author,
            style,
            width,
            height,
            baseline,
            ascend,
            descend,
            spacing,
            em_size,
            left_offset,
        )

        for line in lines:
            code_point, glyph = PsfGlyph.parse_line(font, line)
            font.glyphs[code_point] = glyph

        return font

    @staticmethod
    def load(file_path: str | PathLike[str]) -> PsfFont:
        with open(file_path, 'r', encoding='utf-8') as file:
            return PsfFont.parse(file)

    name: str
    author: str
    style: str
    width: int
    height: int
    baseline: int
    ascend: int
    descend: int
    spacing: int
    em_size: int
    left_offset: int
    glyphs: dict[int, PsfGlyph]

    def __init__(
            self,
            name: str = 'My Amazing Font',
            author: str = 'Anonymous',
            style: str = 'Medium',
            width: int = 8,
            height: int = 10,
            baseline: int = 8,
            ascend: int = 7,
            descend: int = -1,
            spacing: int = 1,
            em_size: int = 8,
            left_offset: int = 0,
            glyphs: dict[int, PsfGlyph] | None = None,
    ):
        self.name = name
        self.author = author
        self.style = style
        self.width = width
        self.height = height
        self.baseline = baseline
        self.ascend = ascend
        self.descend = descend
        self.spacing = spacing
        self.em_size = em_size
        self.left_offset = left_offset
        self.glyphs = {} if glyphs is None else glyphs
