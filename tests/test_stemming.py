"""Regression tests for two bugs that shipped in the original German version
and were only found when this public port was smoke-tested."""
import json, os, sys, unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import outlier_words

DE = json.load(open(os.path.join(REPO, "lang", "de.json"), encoding="utf-8"))
EN = json.load(open(os.path.join(REPO, "lang", "en.json"), encoding="utf-8"))


class GermanStemming(unittest.TestCase):
    def setUp(self):
        self.stem = outlier_words.make_stem(DE)

    def test_inflected_forms_share_a_stem(self):
        """BUG 1: truncation alone left "tragen" as `tragen` and "trägt" as
        `tragt`. A blocklist entry never matched the inflected form it was
        written for."""
        base = self.stem("tragen")
        for form in ("trägt", "tragen", "getragen", "trage"):
            self.assertEqual(self.stem(form), base, f"{form!r} drifted off the stem")

    def test_ascii_transliteration_matches_umlaut(self):
        """BUG 2: normalising only ä→a missed the ASCII spelling. People write
        both, often in the same corpus."""
        for ascii_form, umlaut in (("traegt", "trägt"), ("fuer", "für"),
                                   ("Gruesse", "Grüße"), ("schoen", "schön")):
            self.assertEqual(self.stem(ascii_form), self.stem(umlaut),
                             f"{ascii_form!r} and {umlaut!r} must share a stem")

    def test_short_words_are_not_stripped_below_the_floor(self):
        # Over-stripping would collapse unrelated words together.
        self.assertEqual(self.stem("Haus"), "haus")
        self.assertNotEqual(self.stem("Haus"), self.stem("Hase"))

    def test_unrelated_words_keep_separate_stems(self):
        self.assertNotEqual(self.stem("tragen"), self.stem("fragen"))


class EnglishStemming(unittest.TestCase):
    def setUp(self):
        self.stem = outlier_words.make_stem(EN)

    def test_common_endings_collapse(self):
        base = self.stem("leverage")
        for form in ("leveraged", "leverages", "leveraging"):
            self.assertEqual(self.stem(form), base, f"{form!r} drifted off the stem")

    def test_unrelated_words_stay_apart(self):
        self.assertNotEqual(self.stem("robust"), self.stem("rubric"))


class LanguagePacks(unittest.TestCase):
    def test_every_pack_is_complete(self):
        required = {"name", "code", "word_pattern", "sentence_abbreviations", "stem",
                    "stopwords", "greeting", "signoff", "markers", "particles",
                    "degree_words", "evaluative", "case_sensitive_markers"}
        for path in sorted(os.listdir(os.path.join(REPO, "lang"))):
            if not path.endswith(".json"):
                continue
            pack = json.load(open(os.path.join(REPO, "lang", path), encoding="utf-8"))
            self.assertTrue(required <= set(pack), f"{path} is missing {required - set(pack)}")
            self.assertEqual(pack["code"], path[:-5], f"{path}: code does not match filename")

    def test_marker_names_match_across_packs(self):
        """Profiles are compared across languages. Diverging marker names would
        make that silently meaningless."""
        packs = [json.load(open(os.path.join(REPO, "lang", f), encoding="utf-8"))
                 for f in os.listdir(os.path.join(REPO, "lang")) if f.endswith(".json")]
        names = [set(p["markers"]) for p in packs]
        self.assertTrue(all(n == names[0] for n in names),
                        "marker names differ between language packs")

    def test_regexes_compile(self):
        import re
        for f in os.listdir(os.path.join(REPO, "lang")):
            if not f.endswith(".json"):
                continue
            pack = json.load(open(os.path.join(REPO, "lang", f), encoding="utf-8"))
            re.compile(pack["word_pattern"]); re.compile(pack["greeting"]); re.compile(pack["signoff"])
            for name, pattern in pack["markers"].items():
                re.compile(pattern)


if __name__ == "__main__":
    unittest.main()
