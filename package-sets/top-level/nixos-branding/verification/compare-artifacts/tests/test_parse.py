import pytest

from compare_artifacts.parse import pad_min


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
