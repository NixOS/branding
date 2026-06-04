import pytest

from compare_artifacts.parse import pad_min, no_name_space, parse_misc, parse_viewbox


class TestPadMin:
    def test_empty_sequence_returns_minimum(self):
        # Regression: log10(0) used to crash.
        assert pad_min([]) == 4

    @pytest.mark.parametrize(
        "length,expected",
        [
            (1, 4),  # log10(1)=0, min wins
            (9999, 4),  # log10(9999)~3.99, ceil=4, min ties
            (10000, 4),  # log10(10000)=4.0 exactly, ceil=4
            (10001, 5),  # log10(10001)~4.00004, ceil=5 — crosses
            (99999, 5),  # log10(99999)~4.99996, ceil=5
            (100000, 5),  # log10(100000)=5.0 exactly, ceil=5
            (100001, 6),  # log10(100001)~5.00000043, ceil=6 — crosses
        ],
    )
    def test_length_drives_padding_above_min(self, length, expected):
        assert pad_min([0] * length) == expected

    def test_custom_minimum(self):
        assert pad_min([], min=2) == 2
        # log10(1000) = 3.0 exactly, ceil = 3; length wins over min=2
        assert pad_min([0] * 1000, min=2) == 3


class TestNoNameSpace:
    def test_bare_tag(self):
        assert no_name_space("svg") == "svg"

    def test_namespaced_tag(self):
        assert no_name_space("{http://www.w3.org/2000/svg}svg") == "svg"

    def test_empty_string(self):
        assert no_name_space("") == ""


class TestParseMisc:
    def test_basic_round_trip(self):
        assert parse_misc("  ", "fill", "#abcdef") == "  @fill: #abcdef"

    def test_no_indent(self):
        assert parse_misc("", "id", "foo") == "@id: foo"

    def test_empty_value(self):
        assert parse_misc("", "class", "") == "@class: "


class TestParseViewbox:
    def test_four_values(self):
        result = parse_viewbox("", "viewBox", "0 0 100 100")
        assert result == [
            "@viewBox:",
            "  [0000] 0",
            "  [0001] 0",
            "  [0002] 100",
            "  [0003] 100",
        ]

    def test_with_indent(self):
        result = parse_viewbox("  ", "viewBox", "0 0 10 20")
        # parse_viewbox adds INDENT (two spaces) to indent for the value lines.
        assert result[0] == "  @viewBox:"
        assert result[1] == "    [0000] 0"
