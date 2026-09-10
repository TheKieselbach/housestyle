"""Mail cleaning. Every case here is a way the corpus got polluted."""
import os, re, sys, unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import collect_mail

SIGNOFF = re.compile(r"^\s*((Mit freundlichen|Viele|Beste)\s+Gr(ue|ü)(ss|ß)e[n]?|LG|VG)\b[^\n]{0,40}",
                     re.I | re.M)
SIGNATURE = re.compile(r"(?im)^[ \t]*(Beste Gruesse aus Springfield|Jane Doe|Example Ltd|--[ \t]*$).*$")


def clean(text):
    return collect_mail.own_text(text, SIGNATURE, SIGNOFF)


class Quoting(unittest.TestCase):
    def test_german_reply_header_cuts(self):
        out = clean("Passt so.\n\nVon: Someone\nGesendet: Montag\n\nIhr Text hier.")
        self.assertIn("Passt so.", out)
        self.assertNotIn("Ihr Text hier", out)

    def test_english_reply_header_cuts(self):
        out = clean("Sounds good.\n\nOn Monday, someone wrote:\n> their words")
        self.assertIn("Sounds good.", out)
        self.assertNotIn("their words", out)

    def test_angle_quote_cuts(self):
        self.assertNotIn("quoted", clean("Mine.\n\n> quoted line"))


class Signature(unittest.TestCase):
    def test_block_is_removed(self):
        out = clean("Kurz zum Termin.\n\nBeste Gruesse aus Springfield,\nJane Doe\nExample Ltd")
        self.assertIn("Kurz zum Termin.", out)
        self.assertNotIn("Jane Doe", out)
        self.assertNotIn("Springfield", out)

    def test_canned_signoff_above_the_block_is_removed_too(self):
        """The automatic sign-off sits just above the signature and is not
        typed. Counting it produced a farewell formula the author never uses."""
        out = clean("Das passt.\n\nBeste Gruesse\nJane Doe\nExample Ltd")
        self.assertIn("Das passt.", out)
        self.assertNotIn("Jane Doe", out)

    def test_typed_signoff_is_kept(self):
        # A typed sign-off IS style and must survive.
        self.assertIn("LG", clean("Mache ich morgen.\n\nLG"))


class Encoding(unittest.TestCase):
    def test_crlf_is_normalised(self):
        """Mail clients emit \\r\\n. Every `$` anchor fails on the leftover
        \\r, silently — this cost a full run in the original."""
        out = clean("Kurz zum Termin.\r\n\r\nBeste Gruesse aus Springfield,\r\nJane Doe")
        self.assertNotIn("Jane Doe", out)
        self.assertNotIn("\r", out)


class Boilerplate(unittest.TestCase):
    def test_mobile_footer_and_legal_go(self):
        out = clean("Kurz: ja.\n\nSent from my iPhone\nRegistered office: Springfield")
        self.assertIn("Kurz: ja.", out)
        self.assertNotIn("iPhone", out)
        self.assertNotIn("Registered office", out)


class HtmlConversion(unittest.TestCase):
    def test_tags_become_text_and_breaks(self):
        out = collect_mail.html_to_text("<div>Hallo</div><p>Welt</p><br>Drei")
        self.assertNotIn("<", out)
        for word in ("Hallo", "Welt", "Drei"):
            self.assertIn(word, out)

    def test_script_and_style_are_dropped(self):
        out = collect_mail.html_to_text("<style>p{color:red}</style><p>Text</p>")
        self.assertNotIn("color", out)
        self.assertIn("Text", out)


if __name__ == "__main__":
    unittest.main()
