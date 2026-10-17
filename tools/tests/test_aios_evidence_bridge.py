"""Unit tests for the read-only AIOS field-note adapter."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "aios_evidence_bridge.py"
spec = importlib.util.spec_from_file_location("aios_evidence_bridge", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class EvidenceBridgeTests(unittest.TestCase):
    def test_frontmatter(self):
        result = mod.frontmatter("---\ngame: Elden Ring\nstatus: working\n---\nbody")
        self.assertEqual(result["game"], "Elden Ring")
        self.assertEqual(result["status"], "working")

    def test_missing_frontmatter(self):
        self.assertEqual(mod.frontmatter("# just a heading"), {})

    def test_inventory_and_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root / "knowledge" / "games" / "elden-ring"
            folder.mkdir(parents=True)
            p = folder / "test.md"
            p.write_text("---\ngame: Elden Ring\nstatus: working\n---\nhttps://example.org/test", encoding="utf-8")
            records = mod.inventory(root, "elden ring")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["evidence_state"], "SOURCE_PINNED")
            self.assertFalse(records[0]["runtime_verified"])
            self.assertEqual(len(records[0]["source_sha256"]), 64)
            self.assertEqual(records[0]["cited_urls"], ["https://example.org/test"])
            self.assertEqual(mod.inventory(root, "unrelated"), [])


if __name__ == "__main__":
    unittest.main()
