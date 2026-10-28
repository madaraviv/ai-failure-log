"""One constructed failure per check in the challenge validator.

Run from the repository root:  python -m unittest discover -s tests
"""
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import run_challenges as rc  # noqa: E402

CASE = ROOT / "challenges/fetch-verify-identifier/ontology-id-near-neighbor.md"
GOOD = CASE.read_text(encoding="utf-8")


def validate(text, guard="fetch-verify-identifier", slug="ontology-id-near-neighbor"):
    """Write text as a case under the right guard directory and validate it."""
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / guard
        p.mkdir()
        f = p / f"{slug}.md"
        f.write_text(text, encoding="utf-8")
        return rc.validate(rc.parse_case(f))


def mutate(old, new):
    assert old in GOOD, f"fixture drifted; {old!r} is gone"
    return GOOD.replace(old, new, 1)


class TheShippedCaseIsValid(unittest.TestCase):
    def test_it_passes(self):
        self.assertEqual(validate(GOOD), [])

    def test_its_fields_parse(self):
        case = rc.parse_case(CASE)
        self.assertEqual(case["kind"], "discipline")
        self.assertEqual(case["load"], "embedded")
        self.assertEqual(case["runs"], "10")
        self.assertEqual(case["slug"], "ontology-id-near-neighbor")


class EachCheckFires(unittest.TestCase):
    def fires(self, text, needle, **kw):
        found = validate(text, **kw)
        self.assertTrue(found, "the check did not fire at all")
        self.assertTrue(any(needle in p for p in found), f"fired, but not about {needle!r}: {found}")

    def test_a_discipline_case_without_a_load_is_rejected(self):
        self.fires(mutate("- load: embedded\n", ""), "needs 'load:'")

    def test_an_unknown_load_is_rejected(self):
        self.fires(mutate("- load: embedded", "- load: realistic"), "needs 'load:'")

    def test_a_discipline_case_needs_more_than_one_run(self):
        self.fires(mutate("- runs: 10", "- runs: 1"), "2 or more")

    def test_a_discipline_case_without_runs_is_rejected(self):
        self.fires(mutate("- runs: 10\n", ""), "2 or more")

    def test_a_test_case_must_not_carry_runs_or_load(self):
        self.fires(mutate("- kind: discipline", "- kind: test"), "drop")

    def test_an_unknown_kind_is_rejected(self):
        self.fires(mutate("- kind: discipline", "- kind: vibes"), "must be one of")

    def test_a_missing_shape_is_rejected(self):
        self.fires(mutate("- shape: recalled-fact\n", ""), "missing required field 'shape'")

    def test_a_case_in_the_wrong_guard_directory_is_rejected(self):
        self.fires(GOOD, "a case lives under the guard it challenges", guard="some-other-guard")

    def test_a_heading_that_disagrees_with_the_filename_is_rejected(self):
        self.fires(mutate("### ontology-id-near-neighbor", "### a-different-slug"),
                   "does not match the filename")

    def test_each_required_paragraph_is_required(self):
        for label in ("Bait", "Counts as the failure", "The guard held if", "Why this baits it"):
            with self.subTest(label=label):
                self.fires(mutate(f"**{label}.**", f"{label}:"), f"missing the **{label}.**")


if __name__ == "__main__":
    unittest.main()
