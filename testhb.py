# import sys
import os
from pathlib import Path

import uharfbuzz as hb
from nixoslogo.core import BaseRenderable
from nixoslogo.logotype import FontLoader, Glyph

# # fontfile = sys.argv[1]
# # text = sys.argv[2]
#
# fontfile = Path(os.getenv("NIXOS_LOGOTYPE_FONT_FILE"))
# text = "office fleas L· l· NIXOS"
# text = "y! y. AY"
# text = "NixOS"
#
# blob = hb.Blob.from_file_path(fontfile)
# face = hb.Face(blob)
# font = hb.Font(face)
#
# buf = hb.Buffer()
# buf.add_str(text)
# buf.guess_segment_properties()
#
# features = {"kern": True, "liga": True, "cpsp": True}
# # features = {"kern": True, "liga": True}
# # features = {"kern": False}
# # features = {}
# hb.shape(font, buf, features)
#
# infos = buf.glyph_infos
# positions = buf.glyph_positions
#
# for info, pos in zip(infos, positions):
#     gid = info.codepoint
#     glyph_name = font.glyph_to_string(gid)
#     cluster = info.cluster
#     x_advance = pos.x_advance
#     x_offset = pos.x_offset
#     y_offset = pos.y_offset
#     print(f"{glyph_name} gid{gid}={cluster}@{x_advance},{y_offset}+{x_advance}")


class HBFont(BaseRenderable):
    fontfile = Path(os.getenv("NIXOS_LOGOTYPE_FONT_FILE"))
    text = "Hamburgefonstiv"
    text = "fleas"
    text = "NIXOS"
    text = "r, v, w,"
    text = "AY F, FJ P,"
    text = "v,f,f?y."
    text = "v•f•f?y•"

    def __init__(self, **kwargs):
        self.loader = FontLoader()
        self.get_hb_info()
        self._load_glyphs()
        self._set_spacings()

        super().__init__(**kwargs)

    def get_hb_info(self):
        blob = hb.Blob.from_file_path(self.fontfile)
        face = hb.Face(blob)
        font = hb.Font(face)
        # font.scale = (self.loader.capHeight,) * 2
        font.scale = (1150,) * 2

        buf = hb.Buffer()
        buf.add_str(self.text)
        buf.guess_segment_properties()

        # features = {"kern": True, "liga": True, "cpsp": True}
        # features = {"kern": True, "liga": True, "cpsp": False}
        # features = {"kern": False, "liga": False, "cpsp": False}
        features = {}
        hb.shape(font, buf, features)

        self.blob = blob
        self.face = face
        self.font = font
        self.buf = buf
        self.infos = buf.glyph_infos
        self.positions = buf.glyph_positions
        self.characters = [font.glyph_to_string(info.codepoint) for info in self.infos]
        print(self.characters)

    def _load_glyphs(self):
        self.glyphs = tuple(
            Glyph(
                loader=self.loader,
                character=character,
            )
            for character in self.characters
        )

    def _set_spacings(self):
        advance = 0
        for character, position in zip(self.glyphs, self.positions):
            character.layer.transform((1, 0, 0, 1, advance, 0))
            advance += position.x_advance
            print(position.x_advance)

    def _get_clearspace(self):
        return 0

    @property
    def elements_bounding_box(self):
        characters_box = tuple(
            f(elem)
            for f, elem in zip(
                (min, min, max, max),
                list(zip(*(elem.elements_bounding_box for elem in self.glyphs))),
            )
        )
        with_lead_spacing = characters_box
        return with_lead_spacing

    def make_svg_elements(self):
        return tuple(elem.make_svg_element() for elem in self.glyphs)

    def make_filename(self, extras: tuple[str] = ()):
        return "test-harfbuzz"


logo = HBFont()
logo.write_svg()

# glyphs = tuple(Glyph(loader=loader, character=character) for character in text)
# # print(glyphs[-1].make_svg_elements())

# advance = 0
# for character, position in zip(glyphs, positions):
#     character.layer.transform((1, 0, 0, 1, advance, 0))
#     advance += position.x_advance
# # print(glyphs[-1].make_svg_elements())


# def elements_bounding_box(glyphs):
#     characters_box = tuple(
#         f(elem)
#         for f, elem in zip(
#             (min, min, max, max),
#             list(zip(*(elem.elements_bounding_box for elem in glyphs))),
#         )
#     )
#     # with_lead_spacing = (characters_box[0] - self.spacings[0],) + characters_box[1:]
#     with_lead_spacing = characters_box
#     return with_lead_spacing
