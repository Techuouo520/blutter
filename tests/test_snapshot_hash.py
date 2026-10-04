"""Snapshot-format diagnostics, independent of downloads or a built Dart VM."""

import contextlib
import hashlib
import io
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from dartvm_fetch_build import DartLibInfo, compute_source_snapshot_hash, verify_snapshot_hash


class SnapshotHashTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "tools").mkdir()
        (self.root / "runtime" / "vm").mkdir(parents=True)
        (self.root / "tools" / "make_version.py").write_text(
            "VM_SNAPSHOT_FILES = ['object.h', 'snapshot.cc']\n", encoding="utf-8"
        )
        (self.root / "runtime" / "vm" / "object.h").write_bytes(b"first\r\n")
        (self.root / "runtime" / "vm" / "snapshot.cc").write_bytes(b"second\n")
        self.expected = hashlib.md5(b"first\r\nsecond\n").hexdigest()

    def output(self, snapshot_hash):
        info = DartLibInfo("3.13.0", "android", "arm64", snapshot_hash=snapshot_hash)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            verify_snapshot_hash(info, str(self.root))
        return stream.getvalue()

    def test_hash_uses_ordered_raw_source_bytes(self):
        self.assertEqual(compute_source_snapshot_hash(str(self.root)), self.expected)

    def test_missing_tools_returns_none(self):
        (self.root / "tools" / "make_version.py").unlink()
        self.assertIsNone(compute_source_snapshot_hash(str(self.root)))

    def test_missing_source_returns_none(self):
        (self.root / "runtime" / "vm" / "object.h").unlink()
        self.assertIsNone(compute_source_snapshot_hash(str(self.root)))

    def test_unrecognized_file_list_returns_none(self):
        (self.root / "tools" / "make_version.py").write_text("OTHER = []\n")
        self.assertIsNone(compute_source_snapshot_hash(str(self.root)))

    def test_empty_file_list_returns_none(self):
        (self.root / "tools" / "make_version.py").write_text("VM_SNAPSHOT_FILES = []\n")
        self.assertIsNone(compute_source_snapshot_hash(str(self.root)))

    def test_matching_hash_is_silent(self):
        self.assertEqual(self.output(self.expected), "")

    def test_absent_app_hash_is_silent(self):
        self.assertEqual(self.output(None), "")

    def test_unknown_source_hash_is_silent(self):
        (self.root / "runtime" / "vm" / "object.h").unlink()
        self.assertEqual(self.output("0" * 32), "")

    def test_mismatch_reports_both_hashes_and_source(self):
        output = self.output("0" * 32)
        self.assertIn("WARNING: Dart snapshot-format hash mismatch", output)
        self.assertIn(self.expected, output)
        self.assertIn("0" * 32, output)
        self.assertIn(str(self.root), output)


if __name__ == "__main__":
    unittest.main()
