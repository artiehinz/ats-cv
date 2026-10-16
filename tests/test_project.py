"""No-network tests for generic template composition and PDF diagnostics."""
import copy
import importlib.util
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

    def test_master_has_generic_placeholder_inventory(self):
        sections = self.master["cv"]["sections"]
        self.assertEqual(self.master["cv"]["name"], "Your Name")
        self.assertEqual(len(sections), 9)
        self.assertEqual(len(sections["Professional Experience"]), 2)
        self.assertEqual(len(sections["Selected Projects"]), 3)

    def test_composition_does_not_mutate_master(self):
        before = copy.deepcopy(self.master)
        cv.assemble(self.master, self.variant, self.style)
        self.assertEqual(self.master, before)

    def test_focused_order_and_selection(self):
        payload = cv.assemble(self.master, self.variant, self.style)
        sections = payload["cv"]["sections"]
        self.assertEqual(list(sections)[:2], ["Summary", "Professional Experience"])
        self.assertEqual(len(sections["Selected Projects"]), 2)
        self.assertEqual(payload["cv"]["social_networks"], [])
        self.assertEqual(
            [item["placeholder"] for item in payload["cv"]["custom_connections"]],
            ["linkedin.com/in/your-profile", "github.com/your-handle"],
        )
        self.assertEqual(
            [item["url"] for item in payload["cv"]["custom_connections"]],
            ["https://www.linkedin.com/in/your-profile", "https://github.com/your-handle"],
        )

    def test_invalid_selection_rejected(self):
        self.variant["section_selections"]["Selected Projects"]["indices"] = [-1]
        with self.assertRaises(ValueError):
            cv.assemble(self.master, self.variant, self.style)

    def test_unknown_section_rejected(self):
        self.variant["section_order"].append("Invented section")
        with self.assertRaises(ValueError):
            cv.assemble(self.master, self.variant, self.style)

    def test_invisible_content_rejected(self):
        self.master["cv"]["name"] += "\u200b"
        with self.assertRaises(ValueError):
            cv.assemble(self.master, self.variant, self.style)

    def test_expected_fields_cover_generic_payload(self):
        payload = cv.assemble(self.master, self.variant, self.style)
        fields = cv.expected_fields(payload)
        self.assertIn("Your Name", fields)
        self.assertIn("Professional Experience", fields)


if __name__ == "__main__":
    unittest.main()
