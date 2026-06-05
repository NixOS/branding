from pathlib import Path


from compare_artifacts.collect import DiffSpec, collect_files, counts


# Tiny SVG fragments. The content has to differ visibly between A and B
# for the parser to produce different line outputs.
SVG_A = '<svg id="a"><g /></svg>'
SVG_B = '<svg id="b"><g /></svg>'


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class TestCollectFiles:
    def test_empty_trees(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        before.mkdir()
        after.mkdir()
        assert collect_files(before, after) == []

    def test_unchanged(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "logo.svg", SVG_A)
        write(after / "logo.svg", SVG_A)
        specs = collect_files(before, after)
        assert len(specs) == 1
        assert specs[0].state == "unchanged"
        assert specs[0].path == Path("logo.svg")

    def test_changed(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "logo.svg", SVG_A)
        write(after / "logo.svg", SVG_B)
        specs = collect_files(before, after)
        assert len(specs) == 1
        assert specs[0].state == "modified"
        assert specs[0].before != specs[0].after

    def test_added(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        before.mkdir()
        write(after / "new.svg", SVG_A)
        specs = collect_files(before, after)
        assert len(specs) == 1
        assert specs[0].state == "added"
        assert specs[0].before == []
        # Regression: the original code mistakenly parsed from before_root here.
        assert specs[0].after != []

    def test_removed(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "gone.svg", SVG_A)
        after.mkdir()
        specs = collect_files(before, after)
        assert len(specs) == 1
        # Regression: the original code wrote "remove" here.
        assert specs[0].state == "deleted"
        assert specs[0].before != []
        assert specs[0].after == []

    def test_sorted_by_path(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        for name in ["z.svg", "a.svg", "m.svg"]:
            write(before / name, SVG_A)
            write(after / name, SVG_A)
        specs = collect_files(before, after)
        assert [s.path for s in specs] == [
            Path("a.svg"),
            Path("m.svg"),
            Path("z.svg"),
        ]

    def test_subdirectory_paths_preserved(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "clearspace" / "logo.svg", SVG_A)
        write(after / "clearspace" / "logo.svg", SVG_B)
        specs = collect_files(before, after)
        assert specs[0].path == Path("clearspace") / "logo.svg"
        assert specs[0].state == "modified"

    def test_returns_diffspec_instances(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "logo.svg", SVG_A)
        write(after / "logo.svg", SVG_A)
        specs = collect_files(before, after)
        assert isinstance(specs[0], DiffSpec)


class TestCounts:
    def test_empty_list(self):
        # All four keys must be present even when empty.
        assert counts([]) == {
            "modified": 0,
            "added": 0,
            "deleted": 0,
            "unchanged": 0,
        }

    def test_one_of_each(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        # Same path on both sides, same content → unchanged.
        write(before / "u.svg", SVG_A)
        write(after / "u.svg", SVG_A)
        # Same path, different content → modified.
        write(before / "c.svg", SVG_A)
        write(after / "c.svg", SVG_B)
        # Only in before → deleted.
        write(before / "r.svg", SVG_A)
        # Only in after → added.
        write(after / "a.svg", SVG_A)

        specs = collect_files(before, after)
        assert counts(specs) == {
            "modified": 1,
            "added": 1,
            "deleted": 1,
            "unchanged": 1,
        }

    def test_all_keys_always_present(self):
        # Even if some states have zero entries, all four keys exist.
        result = counts([])
        assert set(result.keys()) == {"modified", "added", "deleted", "unchanged"}

    def test_values_are_int(self):
        # The CI's jq type-validation requires integer values, not bool/float.
        result = counts([])
        for value in result.values():
            assert isinstance(value, int)
            assert not isinstance(value, bool)  # bool is a subclass of int
