"""Regression checks for excerpt fidelity, limits, provenance and advisory scans."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

pack = module("build_context_pack")
prose = module("verify_prose")

class MethodToolsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.md"
        self.spec = self.root / "spec.txt"
        self.out = self.root / "out"

    def prepare(self, source, selector="heading|Target"):
        self.source.write_text(source, encoding="utf-8")
        self.spec.write_text(f"source.md|{selector}|test\n", encoding="utf-8")

    def test_heading_keeps_children_conditions_and_ignores_fences(self):
        self.prepare("# Target\ncondition\n```md\n# Fake\n```\n## Child\nexception\n# Other\nexclude\n")
        parts, manifest = pack.build(self.spec, self.root)
        text = "".join(parts)
        self.assertIn("condition\n```md\n# Fake\n```\n## Child\nexception\n", text)
        self.assertNotIn("exclude", text)
        self.assertEqual(manifest["selections"][0]["end"], 7)

    def test_oversized_section_splits_and_retains_every_line(self):
        body = "# Target\n" + "".join(f"第 {i:04d} 行：" + "雪" * 40 + "\n" for i in range(1000))
        self.prepare(body)
        manifest = pack.write_pack(self.spec, self.out, self.root)
        self.assertGreater(len(manifest["outputs"]), 1)
        text = "".join((self.out / name).read_text(encoding="utf-8") for name in manifest["outputs"])
        for line in body.splitlines():
            self.assertEqual(text.count(line + "\n"), 1)
        for name, info in manifest["outputs"].items():
            self.assertLessEqual((self.out / name).stat().st_size, 40000)
            self.assertEqual((self.out / name).stat().st_size, info["bytes"])
        self.assertEqual(pack.check_pack(self.out, self.root), [])

    def test_source_and_excerpt_changes_detected(self):
        self.prepare("# Target\noriginal\n")
        pack.write_pack(self.spec, self.out, self.root)
        self.source.write_text("# Target\nchanged\n", encoding="utf-8")
        self.assertTrue(any("Changed source" in x for x in pack.check_pack(self.out, self.root)))
        (self.out / "context_pack_1.md").write_text("tampered", encoding="utf-8")
        self.assertTrue(any("changed excerpt" in x for x in pack.check_pack(self.out, self.root)))

    def test_missing_ambiguous_heading_bad_range_and_escape_fail(self):
        for source, selector in [("# Other\n", "heading|Target"),
                                 ("# Target\n# Target\n", "heading|Target"),
                                 ("one\n", "0|1"), ("one\n", "2|1")]:
            with self.subTest(selector=selector, source=source):
                self.prepare(source, selector)
                with self.assertRaises(ValueError):
                    pack.build(self.spec, self.root)
        self.spec.write_text("../outside.md|1|2|bad\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            pack.build(self.spec, self.root)

    def test_legacy_ranges_clamp_eof_and_preserve_blank_lines(self):
        self.prepare("first\n\nlast", "1|9999")
        parts, manifest = pack.build(self.spec, self.root)
        self.assertIn("first\n\nlast", "".join(parts))
        self.assertEqual(manifest["selections"][0]["end"], 3)

    def test_single_line_too_large_and_existing_output_fail_safely(self):
        self.prepare("# Target\n" + "雪" * 14000)
        with self.assertRaises(ValueError):
            pack.write_pack(self.spec, self.out, self.root)
        self.assertFalse(self.out.exists())
        self.prepare("# Target\nokay\n")
        pack.write_pack(self.spec, self.out, self.root)
        before = (self.out / "context_pack_1.md").read_bytes()
        with self.assertRaises(ValueError):
            pack.write_pack(self.spec, self.out, self.root)
        self.assertEqual(before, (self.out / "context_pack_1.md").read_bytes())

    def test_regeneration_removes_only_stale_numbered_packs(self):
        self.prepare("# Target\n" + "line\n" * 1000)
        pack.write_pack(self.spec, self.out, self.root, max_bytes=1000)
        (self.out / "notes.md").write_text("keep", encoding="utf-8")
        self.prepare("# Target\nshort\n")
        pack.write_pack(self.spec, self.out, self.root, overwrite=True)
        self.assertEqual(len(list(self.out.glob("context_pack_*.md"))), 1)
        self.assertEqual((self.out / "notes.md").read_text(), "keep")
        self.assertEqual(pack.check_pack(self.out, self.root), [])

    def test_prose_phrases_are_advisory_and_invalid_encoding_fails(self):
        self.source.write_text("她嘴角微微上揚——那是她的回答。\n", encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(prose.analyze(str(self.source)), 0)
        self.assertIn("閱讀提醒", output.getvalue())
        self.assertNotIn("FAIL", output.getvalue())
        self.source.write_bytes(b"\xff")
        result = subprocess.run([sys.executable, str(HERE / "verify_prose.py"), str(self.source)], capture_output=True)
        self.assertEqual(result.returncode, 2)

if __name__ == "__main__":
    unittest.main()
