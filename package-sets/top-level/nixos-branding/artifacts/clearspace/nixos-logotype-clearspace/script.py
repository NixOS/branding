from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logotype import Glyph, Logotype

annotations = Annotations.medium(overrides={"construction_lines": {"stroke": "grey"}})
ilc = LogoClearspace(
    logo=Logotype(),
    logo_name="logotype",
    space_object=Glyph(character="N"),
    annotations=annotations,
)
ilc.write_svg()
