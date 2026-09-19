"""Keep product and Autopoiesis agent instructions linked without duplicating them."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRODUCT_AGENTS = ROOT / "AGENTS.md"
HARNESS_AGENTS = ROOT / ".autopoiesis" / "AGENTS.md"


class InstructionContractTests(unittest.TestCase):
    def test_both_instruction_files_exist(self):
        self.assertTrue(PRODUCT_AGENTS.is_file())
        self.assertTrue(HARNESS_AGENTS.is_file())

    def test_product_instructions_delegate_to_harness(self):
        text = PRODUCT_AGENTS.read_text(encoding="utf-8")
        self.assertIn(".autopoiesis/AGENTS.md", text)

    def test_harness_instructions_require_product_context(self):
        text = HARNESS_AGENTS.read_text(encoding="utf-8")
        self.assertIn("/projects/app/AGENTS.md", text)
        self.assertIn("/projects/app/.autopoiesis/AGENTS.md", text)

    def test_responsibilities_stay_separated(self):
        product = PRODUCT_AGENTS.read_text(encoding="utf-8")
        harness = HARNESS_AGENTS.read_text(encoding="utf-8")
        self.assertNotIn("gh pr create", product)
        self.assertIn("gh pr create", harness)


if __name__ == "__main__":
    unittest.main()
