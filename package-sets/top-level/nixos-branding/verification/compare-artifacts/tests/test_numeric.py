from compare_artifacts.numeric import NumericResult, compare_numeric


def test_shifted_depth_tags_are_not_deltas():
    before = ["<g @0>", "  <rect @0/0>", "    @x: 5", "</g @0>"]
    after = [
        "<g @0>",
        "  <circle @0/0>",
        "    @r: 1",
        "  <rect @0/1>",
        "    @x: 5",
        "</g @0>",
    ]
    result = compare_numeric(before, after)
    assert result.unmatched_after == 2
    assert (
        result.compared == 1
    )  # the rect's x; the renumbered depth tag is not a number
    assert result.changed == 0
    assert result.max_delta == 0.0


def test_numeric_drift_is_measured_on_matched_lines():
    before = ["<path @0/1>", "  @d:", "    [0000] M 100.0 200.0"]
    after = ["<path @0/1>", "  @d:", "    [0000] M 100.5 199.0"]
    assert compare_numeric(before, after) == NumericResult(3, 0, 0, 2, 2, 1.0)


def test_inserted_element_is_unmatched_not_a_huge_delta():
    before = ["<g @0>", "  <path @0/0>", "    @d: M 1 1", "</g @0>"]
    after = [
        "<g @0>",
        "  <path @0/0>",
        "    @d: M 1 1",
        "  <path @0/1>",
        "    @d: M 900 900",
        "</g @0>",
    ]
    result = compare_numeric(before, after)
    assert result.unmatched_before == 0
    assert result.unmatched_after == 2
    assert result.compared == 2  # the matched path's M 1 1
    assert result.changed == 0
    assert result.max_delta == 0.0
