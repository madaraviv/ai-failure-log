"""One constructed failure per check. A gate never observed failing is not known to work.

    python -m unittest discover -s tests
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import check_failure_log as c  # noqa: E402

GOOD = (ROOT / "FAILURE_LOG.md").read_text(encoding="utf-8")


def mutate(old, new):
    assert old in GOOD, f"fixture drifted; {old!r} is gone"
    return GOOD.replace(old, new, 1)


def without_totals(text):
    """Changing a counted field makes the tally stale, which is that check working."""
    return [p for p in c.check(text) if "totals" not in p]


class TheTemplateIsValid(unittest.TestCase):
    def test_it_passes(self):
        self.assertEqual(c.check(GOOD), [])

    def test_the_example_file_is_the_same_record(self):
        ex = (ROOT / "examples/ontology-id-from-memory.md").read_text(encoding="utf-8")
        self.assertIn("20260716-ontology-id-from-memory", ex)
        self.assertEqual(c.scrub(ex), [])


class EachCheckFires(unittest.TestCase):
    def fires(self, text, needle):
        found = c.check(text)
        self.assertTrue(found, "the check did not fire")
        self.assertTrue(any(needle in p for p in found), f"not about {needle!r}: {found}")

    def test_duplicate_id(self):
        self.fires(GOOD + "\n" + GOOD.split("## Log\n")[1], "ids are keys")

    def test_caught_by_with_free_text(self):
        self.fires(mutate("- caught_by: discipline", "- caught_by: discipline (a test)"),
                   "nothing else in the cell")

    def test_caught_by_outside_the_three(self):
        self.fires(mutate("- caught_by: discipline", "- caught_by: reviewer"), "exactly one of")

    def test_a_missing_key_line(self):
        self.fires(mutate("- escaped:\n", ""), "missing the 'escaped' line")

    def test_a_blank_date_is_rejected_but_a_blank_model_is_not(self):
        self.fires(mutate("- date: 2026-07-16", "- date:"), "must have a value")
        self.assertEqual(without_totals(mutate("- model: claude-opus-4-8[1m]", "- model:")), [])

    def test_a_non_iso_date(self):
        self.fires(mutate("- date: 2026-07-16", "- date: 16/07/2026"), "not ISO")

    def test_a_non_iso_reviewed_date(self):
        self.fires(mutate("- reviewed: 2026-07-16", "- reviewed: last week"), "not ISO")

    def test_a_blank_reviewed_is_allowed_and_counted(self):
        text = mutate("- reviewed: 2026-07-16", "- reviewed:")
        self.assertIn("unreviewed: 1", c.totals(c.parse(text)))

    def test_an_id_that_disagrees_with_its_date(self):
        self.fires(mutate("- date: 2026-07-16", "- date: 2026-07-17"), "does not start with")

    def test_an_id_in_the_wrong_format(self):
        self.fires(mutate("### 20260716-ontology-id-from-memory", "### record-one"),
                   "id must look like")

    def test_each_paragraph_is_required(self):
        for para in ("What the model did", "What caught it"):
            with self.subTest(para=para):
                self.fires(mutate(f"**{para}.**", f"{para}:"), f"missing the **{para}.**")

    def test_a_stale_tally(self):
        self.fires(mutate("**1 record.**", "**99 records.**"), "do not match the records")

    def test_an_empty_log(self):
        self.fires(GOOD.split("## Log")[0] + "## Log\n", "no records found")


class TheScrubCheckFires(unittest.TestCase):
    def test_it_finds_what_should_not_be_published(self):
        text = "mail a@b.com, host 10.0.0.4, path /Users/someone/x, s3://bucket/key"
        found = " ".join(c.scrub(text))
        for needle in ("email", "IP address", "path with a username", "cloud resource id"):
            self.assertIn(needle, found, f"{needle} missed in: {found}")

    def test_the_template_is_clean(self):
        self.assertEqual(c.scrub(GOOD), [])


if __name__ == "__main__":
    unittest.main()
