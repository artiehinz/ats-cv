"""No-network tests for source preservation, composition, and PDF diagnostics."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cv", ROOT / "scripts/cv.py")
cv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cv)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.master = cv.load_yaml(ROOT / "content/master.yaml")
        self.variant = cv.load_yaml(ROOT / "variants/motion.yaml")
        self.style = cv.load_yaml(ROOT / "design/blue.yaml")

    def test_original_pdf_unchanged(self):
        manifest = json.loads((ROOT / "source/manifest.json").read_text())
        self.assertEqual(hashlib.sha256((ROOT / "source/original.pdf").read_bytes()).hexdigest(), manifest["sha256"])

    def test_master_keeps_inventory(self):
        sections = self.master["cv"]["sections"]
        self.assertEqual(len(sections), 10)
        self.assertEqual(len(sections["Professional Experience"]), 5)
        self.assertEqual(len(sections["Selected Projects"]), 6)
        self.assertEqual(len(sections["AI & Pipeline Contributions"]), 5)
        self.assertEqual(len(sections["Awards & Recognition"]), 4)
        self.assertEqual(len(sections["Education"]), 3)
        self.assertEqual(sections["Languages"], [{"bullet": "English: IELTS B2"}, {"bullet": "Russian"}, {"bullet": "Ukrainian"}])

    def test_composition_does_not_mutate_master(self):
        before = copy.deepcopy(self.master)
        cv.assemble(self.master, self.variant, self.style)
        self.assertEqual(self.master, before)

    def test_motion_order_and_selection(self):
        payload = cv.assemble(self.master, self.variant, self.style)
        sections = payload["cv"]["sections"]
        self.assertEqual(list(sections)[:2], ["Summary", "Professional Experience"])
        self.assertNotIn("AI & Pipeline Contributions", sections)
        self.assertEqual(len(sections["Selected Projects"]), 4)
        self.assertEqual(sections["Languages"], [{"bullet": "English: IELTS B2"}, {"bullet": "Russian"}, {"bullet": "Ukrainian"}])
        self.assertEqual(payload["cv"]["social_networks"], [])
        self.assertEqual([item["placeholder"] for item in payload["cv"]["custom_connections"]], ["LinkedIn", "GitHub"])

    def test_employment_and_dates_not_invented(self):
        payload = cv.assemble(self.master, self.variant, self.style)
        original = self.master["cv"]["sections"]["Professional Experience"]
        self.assertEqual(payload["cv"]["sections"]["Professional Experience"], original)
        self.assertEqual(original[-1]["company"], "New Cave Media, Blackbox, Art. Lebedev Studio")
        self.assertEqual(original[-1]["date"], "2017 – 2020")

    def test_unknown_section_rejected(self):
        self.variant["section_order"].append("Invented section")
        with self.assertRaises(ValueError):
            cv.assemble(self.master, self.variant, self.style)

    def test_invalid_selection_rejected(self):
        self.variant["section_selections"]["Selected Projects"]["indices"] = [-1]
        with self.assertRaises(ValueError):
            cv.assemble(self.master, self.variant, self.style)

    def test_invisible_content_rejected(self):
        self.master["cv"]["name"] += "\u200b"
        with self.assertRaises(ValueError):
            cv.assemble(self.master, self.variant, self.style)

    def test_source_hyperlinks_retained(self):
        links = json.loads((ROOT / "source/links.json").read_text())
        self.assertEqual(len(links), 14)
        self.assertIn("https://www.linkedin.com/in/artie-hinz/", [i["uri"] for i in links])
        self.assertIn("https://artiehinz.com/arcore", [i["uri"] for i in links])

    def test_pdf_checker_on_original_not_rebuilt_output(self):
        # This tests the checker, NOT RenderCV or the proposed template.
        with tempfile.TemporaryDirectory() as tmp:
            source_master = copy.deepcopy(self.master)
            del source_master["cv"]["sections"]["Languages"]
            result = cv.inspect_pdf(ROOT / "source/original.pdf", source_master, Path(tmp), previews=False)
            self.assertEqual(result["pages"], 2)
            self.assertFalse(result["missing_fields"], result)
            self.assertTrue(any("below 9.5 pt" in w for w in result["warnings"]))
            self.assertTrue((Path(tmp) / "report.json").is_file())


if __name__ == "__main__":
    unittest.main()
