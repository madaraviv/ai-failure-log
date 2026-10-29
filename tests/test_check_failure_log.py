"""One constructed failure per check. A gate never observed failing is not known to work.

    python -m unittest discover -s tests
"""
import pathlib
import shutil
import sys
import tempfile
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
        in_template = GOOD.split("## Log\n", 1)[1].strip()
        self.assertEqual(ex.strip(), in_template, "the example and the template record drifted")
        self.assertEqual(c.scrub(ex), [])

    def test_a_bare_record_file_is_format_checked(self):
        ex = (ROOT / "examples/ontology-id-from-memory.md").read_text(encoding="utf-8")
        self.assertEqual(c.check(ex), [], "a contributed record must be checkable on its own")
        self.assertTrue(c.check(ex.replace("- caught_by: discipline", "- caught_by: nobody")))

    def test_the_shipped_example_is_not_reviewed_the_day_it_was_written(self):
        rec = c.parse(GOOD)[0]
        self.assertNotEqual(
            rec["date"], rec["reviewed"],
            "the record every adopter copies must not show same-breath review",
        )


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
        self.fires(mutate("- reviewed: 2026-10-28", "- reviewed: last week"), "not ISO")

    def test_a_blank_reviewed_is_allowed_and_counted(self):
        text = mutate("- reviewed: 2026-10-28", "- reviewed:")
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


class TheCommandLine(unittest.TestCase):
    """--write is the command every adopter runs, so it gets a test."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = pathlib.Path(self.dir) / "FAILURE_LOG.md"
        shutil.copy(ROOT / "FAILURE_LOG.md", self.path)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_write_regenerates_the_tally_after_an_append(self):
        extra = (
            "\n\n### 20261028-a-second-record · another\n\n"
            "- date: 2026-10-28\n- caught_by: human\n- model:\n- class: unclassified\n"
            "- guard:\n- escaped:\n- reviewed:\n\n"
            "**What the model did.** x\n\n**What caught it.** y\n"
        )
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(extra)
        self.assertTrue(c.check(self.path.read_text(encoding="utf-8")), "tally should be stale")
        self.assertEqual(c.main([str(self.path), "--write"]), 0)
        after = self.path.read_text(encoding="utf-8")
        self.assertEqual(c.check(after), [])
        self.assertIn("**2 records.**", after)
        self.assertIn("(not recorded)", after)
        self.assertIn("unreviewed: 1", after)

    def test_scrub_check_exits_nonzero_on_a_leak(self):
        self.path.write_text("### x\n\nmail a@b.com\n", encoding="utf-8")
        self.assertEqual(c.main([str(self.path), "--scrub-check"]), 1)


class TheContextFieldIsShapeChecked(unittest.TestCase):
    """It holds a relative path and a hash. Never a transcript, never an absolute path."""

    GOODS = [
        "- context:",
        "- context: .failure-contexts/20260716-ontology-id-from-memory/",
        "- context: .failure-contexts/20260716-ontology-id-from-memory/ sha256:" + "a1" * 32,
    ]
    BADS = [
        "- context: /Users/someone/.failure-contexts/x/",          # absolute: discloses the user
        "- context: https://example.com/dumps/x.jsonl",            # a URL
        "- context: 3lqvno0nvdhhnggphfbov33388",                   # a session id
        '- context: {"type":"user","message":"..."}',              # the transcript itself
        "- context: .failure-contexts/x/ sha256:tooshort",          # malformed hash
    ]

    def test_the_accepted_shapes_pass(self):
        for good in self.GOODS:
            with self.subTest(value=good):
                self.assertEqual(without_totals(mutate("- context:", good)), [])

    def test_every_rejected_shape_fires(self):
        for bad in self.BADS:
            with self.subTest(value=bad):
                found = c.check(mutate("- context:", bad))
                self.assertTrue(any("context must be a relative path" in p for p in found),
                                f"{bad!r} was accepted: {found}")

    def test_a_hash_on_the_context_line_does_not_trip_the_scrub(self):
        line = "- context: .failure-contexts/x/ sha256:" + "ab" * 32
        self.assertEqual(c.scrub(line), [], "the credential pattern flagged a context hash")
        self.assertTrue(c.scrub("token " + "ab" * 32), "it should still flag one elsewhere")


class TheGitignoreGateFires(unittest.TestCase):
    """An adopter copies two files, not a .gitignore, so this is the only mechanical stop."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.log = pathlib.Path(self.dir) / "FAILURE_LOG.md"
        shutil.copy(ROOT / "FAILURE_LOG.md", self.log)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_no_store_means_nothing_to_check(self):
        self.assertEqual(c.check_store(str(self.log)), [])

    def test_a_store_with_no_gitignore_fires(self):
        (pathlib.Path(self.dir) / ".failure-contexts").mkdir()
        found = c.check_store(str(self.log))
        self.assertTrue(any("not in .gitignore" in p for p in found), found)

    def test_a_store_that_is_ignored_passes(self):
        (pathlib.Path(self.dir) / ".failure-contexts").mkdir()
        (pathlib.Path(self.dir) / ".gitignore").write_text(".failure-contexts/\n")
        self.assertEqual(c.check_store(str(self.log)), [])

    def test_this_repo_ignores_its_own_store(self):
        ignore = (ROOT / ".gitignore").read_text()
        self.assertIn(".failure-contexts/", ignore)


class TheScrubCheckFires(unittest.TestCase):
    def test_it_finds_what_should_not_be_published(self):
        text = ("mail a@b.com, host 10.0.0.4, path /Users/someone/x, s3://bucket/key, "
                "token " + "a1b2c3d4" * 4)
        found = " ".join(c.scrub(text))
        for needle in ("email", "IP address", "path with a username", "cloud resource id",
                       "credential-shaped"):
            self.assertIn(needle, found, f"{needle} missed in: {found}")

    def test_the_template_is_clean(self):
        self.assertEqual(c.scrub(GOOD), [])


if __name__ == "__main__":
    unittest.main()
