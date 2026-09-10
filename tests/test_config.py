"""Configuration parsing, including the indented multi-line form."""
import os, sys, tempfile, unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import config


class Parsing(unittest.TestCase):
    def _write(self, text):
        fd, path = tempfile.mkstemp(suffix=".conf")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_simple_key(self):
        v = config._parse(self._write("ROOT=/tmp/x\nLANG=de\n"))
        self.assertEqual(v["ROOT"], "/tmp/x")
        self.assertEqual(v["LANG"], "de")

    def test_comments_and_blank_lines_ignored(self):
        v = config._parse(self._write("# a comment\n\n  # indented comment\nLANG=en\n"))
        self.assertEqual(v["LANG"], "en")
        self.assertEqual(len(v), 1)

    def test_value_may_contain_equals(self):
        v = config._parse(self._write("ROOT=/tmp/a=b\n"))
        self.assertEqual(v["ROOT"], "/tmp/a=b")

    def test_indented_lines_extend_the_previous_key(self):
        path = self._write("SIGNATURE=\n  first anchor\n  second anchor\nLANG=de\n")
        v = config._parse(path)
        self.assertEqual(v["SIGNATURE_LIST"], ["first anchor", "second anchor"])
        self.assertEqual(v["LANG"], "de")

    def test_carriage_returns_do_not_survive(self):
        # A conf file edited on Windows must not yield values ending in \r.
        v = config._parse(self._write("LANG=de\r\nROOT=/tmp/x\r\n"))
        self.assertEqual(v["LANG"], "de")
        self.assertEqual(v["ROOT"], "/tmp/x")


if __name__ == "__main__":
    unittest.main()
