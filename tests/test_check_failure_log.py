"""One constructed failure per check, so each check is known to fire.

A gate never observed failing is not known to work. Run from the repository root:

    python -m unittest discover -s tests
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import check_failure_log as c  # noqa: E402

GOOD = (ROOT / "FAILURE_LOG.md").read_text(encoding="utf-8")


def problems(text):
    return c.check(text)


def problems_but_not_the_totals(text):
    """For checks about a field's validity: changing a counted field makes the totals stale,
    which is the totals check doing its job and not what these tests are about."""
    return [p for p in c.check(text) if "totals block" not in p]


def mutate(old, new, text=None):
    text = GOOD if text is None else text
    assert old in text, f"fixture drifted; {old!r} is no longer in the log"
    return text.replace(old, new, 1)


class TheTemplateIsValid(unittest.TestCase):
    def test_the_shipped_log_passes_every_check(self):
        self.assertEqual(problems(GOOD), [])

    def test_the_shipped_totals_match_the_records(self):
        records, _, _, _ = c.parse(GOOD)
        self.assertIn(c.totals(records).strip(), GOOD)

    def test_a_title_after_the_id_is_accepted_and_the_id_is_taken_alone(self):
        records, _, _, _ = c.parse(GOOD)
        self.assertEqual(records[0]["id"], "20260716-ontology-id-from-memory")
        self.assertTrue(records[0]["title"])


class EachCheckFires(unittest.TestCase):
    def fires(self, text, needle):
        found = problems(text)
        self.assertTrue(found, "the check did not fire at all")
        self.assertTrue(
            any(needle in p for p in found),
            f"fired, but not about {needle!r}: {found}",
        )

    def test_duplicate_record_id(self):
        dupe = GOOD + "\n\n### 20260716-ontology-id-from-memory · again\n\n" \
            "- date: 2026-07-16\n- caught_by: human\n- guard: none-yet\n" \
            "- shape: recalled-fact\n- model:\n\n**Failure.** x\n\n**Caught.** y\n"
        self.fires(dupe, "must be unique")

    def test_caught_by_with_free_text(self):
        self.fires(mutate("- caught_by: discipline", "- caught_by: discipline (added a test)"),
                   "nothing else in the cell")

    def test_caught_by_outside_the_enum(self):
        self.fires(mutate("- caught_by: discipline", "- caught_by: reviewer"),
                   "exactly one of")

    def test_guard_absent_from_the_guard_table(self):
        self.fires(mutate("- guard: fetch-verify-identifier", "- guard: a-rule-i-invented"),
                   "not in the guard table")

    def test_guard_cited_before_it_landed(self):
        self.fires(mutate("| `fetch-verify-identifier` | 2026-01-01 |",
                          "| `fetch-verify-identifier` | 2026-09-01 |"),
                   "only exists from")

    def test_shape_absent_from_the_shape_table(self):
        self.fires(mutate("- shape: recalled-fact", "- shape: a-shape-i-invented"),
                   "not in this log's shape table")

    def test_unclassified_shape_is_allowed(self):
        self.assertEqual(
            problems_but_not_the_totals(mutate("- shape: recalled-fact", "- shape: unclassified")),
            [],
        )

    def test_missing_required_field(self):
        self.fires(mutate("- shape: recalled-fact\n", ""), "missing required field")

    def test_blank_model_is_allowed_but_the_key_is_required(self):
        self.assertEqual(
            problems_but_not_the_totals(mutate("- model: claude-opus-4-8[1m]", "- model:")), []
        )
        self.fires(mutate("- model: claude-opus-4-8[1m]\n", ""), "missing required field 'model'")

    def test_non_iso_date(self):
        self.fires(mutate("- date: 2026-07-16", "- date: 16/07/2026"), "is not ISO")

    def test_id_that_disagrees_with_its_own_date(self):
        self.fires(mutate("- date: 2026-07-16", "- date: 2026-07-17"),
                   "does not start with its own date")

    def test_id_in_the_wrong_format(self):
        self.fires(mutate("### 20260716-ontology-id-from-memory", "### record-one"),
                   "id must look like")

    def test_missing_failure_paragraph(self):
        self.fires(mutate("**Failure.**", "Failure:"), "missing the **Failure.** paragraph")

    def test_missing_caught_paragraph(self):
        self.fires(mutate("**Caught.**", "Caught:"), "missing the **Caught.** paragraph")

    def test_stale_totals(self):
        self.fires(mutate("**1 record.**", "**99 records.**"), "does not match the records")

    def test_guard_that_neither_runs_always_nor_on_a_schedule(self):
        self.fires(mutate("| discipline | always | agent instructions",
                          "| discipline | sometimes | agent instructions"),
                   "is not a guard")

    def test_guard_with_an_unknown_kind(self):
        self.fires(mutate("| 2026-01-01 | discipline | always | agent instructions",
                          "| 2026-01-01 | vibes | always | agent instructions"),
                   "not one of")

    def test_duplicate_guard_id(self):
        self.fires(mutate("| `second-os-in-ci` | 2026-01-01 | test | always |",
                          "| `fetch-verify-identifier` | 2026-01-01 | test | always |"),
                   "appears twice in the guard table")

    def test_a_guard_id_without_back_ticks_still_resolves(self):
        self.assertEqual(
            problems(mutate("| `fetch-verify-identifier` |", "| fetch-verify-identifier |")), []
        )

    def test_an_empty_log_says_so(self):
        self.fires(GOOD.split("## Log")[0] + "## Log\n", "no records found")


class TheScrubCheckFires(unittest.TestCase):
    def hard(self, text, denylist=()):
        return c.scrub_check(text, denylist)[0]

    def test_it_finds_an_email_an_ip_a_path_and_a_denylist_name(self):
        text = "asked Someone at /Users/someone, mail a@b.com, host 10.0.0.4, client Acme Corp"
        found = " ".join(self.hard(text, ["Acme Corp"]))
        for needle in ("email", "IPv4", "absolute path", "denylist"):
            self.assertIn(needle, found, f"{needle} not found in: {found}")

    def test_the_shipped_template_has_no_hard_findings(self):
        self.assertEqual(self.hard(GOOD), [])

    def test_a_url_is_soft_not_hard(self):
        text = "see https://example.com/docs"
        self.assertEqual(self.hard(text), [])
        self.assertTrue(c.scrub_check(text)[1])


if __name__ == "__main__":
    unittest.main()
