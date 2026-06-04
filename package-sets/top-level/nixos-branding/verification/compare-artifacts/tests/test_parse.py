import pytest

from compare_artifacts.parse import pad_min


class TestPadMin:
    def test_empty_sequence_returns_minimum(self):
        # Regression: log10(0) used to crash.
        assert pad_min([]) == 4

    @pytest.mark.parametrize(
        "length,expected",
        [
            (1, 4),  # min wins
            (9999, 4),  # log10(9999) ~ 4
            (10000, 5),  # crosses the boundary
            (99999, 5),
            (100000, 6),
        ],
    )
    def test_length_drives_padding_above_min(self, length, expected):
        assert pad_min([0] * length) == expected

    def test_custom_minimum(self):
        assert pad_min([], min=2) == 2
        assert pad_min([0] * 1000, min=2) == 4  # length wins
