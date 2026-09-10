"""Measurement core. Each test here corresponds to a way an early run lied."""
import json, os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import measure

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE = json.load(open(os.path.join(REPO, "lang", "de.json"), encoding="utf-8"))
EN = json.load(open(os.path.join(REPO, "lang", "en.json"), encoding="utf-8"))


class SentenceSplitting(unittest.TestCase):
    def test_abbreviation_does_not_end_a_sentence(self):
        # Without the guard, "z. B." splits and the length statistics collapse.
        s = measure.split_sentences("Wir nehmen z. B. das hier. Und dann weiter.",
                                    DE["sentence_abbreviations"])
        self.assertEqual(len(s), 2)
        self.assertIn("z. B.", s[0])

    def test_blank_line_separates(self):
        self.assertEqual(len(measure.split_sentences("Eins\n\nZwei", DE["sentence_abbreviations"])), 2)

    def test_english_abbreviations(self):
        s = measure.split_sentences("Take e.g. this one. Then the next.",
                                    EN["sentence_abbreviations"])
        self.assertEqual(len(s), 2)


class Markers(unittest.TestCase):
    def test_formal_address_is_case_sensitive(self):
        """German polite "Sie" differs from plural "sie" only by case.

        Matched case-insensitively, informal plural counts as formal address —
        which made a corpus of informal posts look formal.
        """
        informal = measure.analyse(["ihr habt euch das ja selbst ausgesucht"], "t", DE)
        self.assertEqual(informal["markers_per_1000_words"]["formal address"], 0.0)
        self.assertGreater(informal["markers_per_1000_words"]["informal address"], 0)

        formal = measure.analyse(["Haben Sie Ihre Unterlagen dabei"], "t", DE)
        self.assertGreater(formal["markers_per_1000_words"]["formal address"], 0)

    def test_plural_you_counts_as_informal(self):
        # "ihr/euch" must count as informal address, or public posts that
        # address a plural audience report zero informal address.
        r = measure.analyse(["Verbessert ihr eure Arbeit damit"], "t", DE)
        self.assertGreater(r["markers_per_1000_words"]["informal address"], 0)


class Volume(unittest.TestCase):
    def test_counts_and_normalisation(self):
        r = measure.analyse(["Eins zwei drei.", "Vier fuenf."], "t", DE)
        self.assertEqual(r["volume"]["texts"], 2)
        self.assertEqual(r["volume"]["words"], 5)
        self.assertEqual(r["volume"]["sentences"], 2)
        self.assertEqual(r["sentence_length_words"]["median"], 2.5)

    def test_language_is_recorded(self):
        self.assertEqual(measure.analyse(["Hi there."], "t", EN)["language"], "en")


class WordClasses(unittest.TestCase):
    def test_topic_vocabulary_is_labelled_separately(self):
        """Open word classes measure the topic, not the style. An early run
        produced a profile whose defining words were project nouns."""
        r = measure.analyse(["Der Backup Ordner beim Client ist voll. " * 5], "t", DE)
        self.assertIn("topic_vocabulary_not_style", r)
        topic = [w for w, _ in r["topic_vocabulary_not_style"]]
        self.assertIn("backup", topic)
        # ... and those words must not leak into the style inventories.
        self.assertNotIn("backup", [p[0] for p in r["particles"]])

    def test_particles_are_found(self):
        r = measure.analyse(["Das ist halt eben einfach so. " * 4], "t", DE)
        self.assertIn("halt", [p[0] for p in r["particles"]])


class GreetingsAndSignoffs(unittest.TestCase):
    def test_multiline_mail(self):
        r = measure.analyse(["Moin Team,\n\nkurz zum Termin.\n\nBeste Gruesse"], "t", DE)
        self.assertTrue(r["greetings"], "greeting not detected")
        self.assertTrue(r["signoffs"], "sign-off not detected")


if __name__ == "__main__":
    unittest.main()
