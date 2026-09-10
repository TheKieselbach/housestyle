"""Security constraints.

The project claims your text stays local. These tests are that claim, written
down so it cannot quietly stop being true.
"""
import os, sys, unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import config, collect_web, setup as setup_module


class SecretRedaction(unittest.TestCase):
    """Credentials get typed into chat windows, and transcripts keep them.
    A corpus is read back by a model eventually, so a leaked key would travel
    exactly where it must not."""

    def assertRedacted(self, text, must_not_contain):
        out, n = config.redact_secrets(text)
        self.assertGreater(n, 0, f"nothing redacted in {text[:40]!r}")
        self.assertNotIn(must_not_contain, out)

    def test_openai_style_key(self):
        self.assertRedacted("my key is sk-abcdefghijklmnopqrstuvwxyz012345", "abcdefghijklmnop")

    def test_github_token(self):
        self.assertRedacted("use ghp_" + "A" * 36, "ghp_AAAA")

    def test_aws_access_key(self):
        self.assertRedacted("AKIAIOSFODNN7EXAMPLE is the id", "AKIAIOSFODNN7EXAMPLE")

    def test_jwt(self):
        # Realistic segment lengths. An earlier version of this test used a
        # toy token whose header was nine characters and concluded the
        # pattern was broken; real JWT headers run to about twenty.
        jwt = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
               ".eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkEifQ"
               ".dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U")
        self.assertRedacted(f"header {jwt}", "dozjgNryP4J3")

    def test_private_key_block(self):
        pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEow\nsecretline\n-----END RSA PRIVATE KEY-----"
        self.assertRedacted(pem, "secretline")

    def test_bearer_header(self):
        self.assertRedacted("Authorization: Bearer abcdefghijklmnopqrstuvwx", "abcdefghijkl")

    def test_assignment_forms(self):
        for line in ("password=hunter2seventeen", "API_KEY: abcdefghijkl",
                     "token = zyxwvutsrqponm", "Passwort: geheimnisvoll"):
            with self.subTest(line=line):
                out, n = config.redact_secrets(line)
                self.assertGreater(n, 0, f"missed {line!r}")
                self.assertIn("[redacted]", out)

    def test_credentials_in_url(self):
        out, n = config.redact_secrets("postgres://admin:s3cretpw@db.example.com/x")
        self.assertGreater(n, 0)
        self.assertNotIn("s3cretpw", out)

    def test_clean_text_is_untouched(self):
        """Redaction must not mangle ordinary prose — it runs on every message."""
        for text in ("Moin, das passt so.", "Wir treffen uns um drei.",
                     "The password field was empty.", "Kein Token vergeben."):
            with self.subTest(text=text):
                out, n = config.redact_secrets(text)
                self.assertEqual(n, 0, f"false positive on {text!r}")
                self.assertEqual(out, text)


class UrlSchemes(unittest.TestCase):
    """urllib serves file:// and ftp:// as readily as http. A mistyped or
    pasted path must not turn into local file contents in your corpus."""

    def test_local_file_is_refused(self):
        self.assertIsNotNone(collect_web.check_url("file:///etc/passwd"))

    def test_other_schemes_are_refused(self):
        for url in ("ftp://example.com/x", "gopher://example.com",
                    "data:text/plain,hello", "/etc/passwd", "javascript:alert(1)"):
            with self.subTest(url=url):
                self.assertIsNotNone(collect_web.check_url(url), f"{url} was allowed")

    def test_http_and_https_pass(self):
        for url in ("http://example.com/a", "https://example.com/b"):
            with self.subTest(url=url):
                self.assertIsNone(collect_web.check_url(url))

    def test_scheme_without_host_is_refused(self):
        self.assertIsNotNone(collect_web.check_url("https:///no-host"))


class DeletionGuard(unittest.TestCase):
    """--uninstall removes <ROOT>/corpus and <ROOT>/metrics. A ROOT pointing at
    a personal directory would then delete folders the user made themselves."""

    def test_refuses_home_and_system_paths(self):
        paths = [os.path.expanduser("~"),
                 os.path.join(os.path.expanduser("~"), "Documents")]
        paths += [os.path.abspath(os.sep)] if os.name == "nt" else ["/", "/tmp", "/etc", "/Users"]
        for path in paths:
            with self.subTest(path=path):
                self.assertIsNotNone(setup_module._refuse_to_delete(path),
                                     f"{path} was not refused")

    def test_allows_a_dedicated_directory(self):
        # Must hold on Windows too, where an earlier version refused every
        # path because it split on "/" only.
        self.assertIsNone(setup_module._refuse_to_delete(
            os.path.join(os.path.expanduser("~"), "Documents", "housestyle-corpus")))

    def test_empty_root_is_harmless(self):
        self.assertIsNone(setup_module._refuse_to_delete(""))


class NoDangerousPrimitives(unittest.TestCase):
    """A tool handling your sent mail should not grow an eval() one day."""

    def test_source_stays_free_of_them(self):
        import re
        forbidden = re.compile(r"\b(eval|exec|os\.system|subprocess|pickle|marshal)\s*\(")
        scripts = os.path.join(REPO, "scripts")
        for name in sorted(os.listdir(scripts)):
            if not name.endswith(".py"):
                continue
            with open(os.path.join(scripts, name), encoding="utf-8") as f:
                source = f.read()
            hits = forbidden.findall(source)
            self.assertFalse(hits, f"{name} uses {hits}")

    @unittest.skipUnless(hasattr(sys, "stdlib_module_names"),
                         "sys.stdlib_module_names needs Python 3.10+")
    def test_no_dependencies_are_imported(self):
        """The no-dependency promise, checked rather than trusted."""
        import ast
        stdlib = set(sys.stdlib_module_names)
        local = {"config", "measure", "setup", "cli", "collect_mail",
                 "collect_transcripts", "collect_web", "samples", "outlier_words",
                 "housestyle"}
        scripts = os.path.join(REPO, "scripts")
        for name in sorted(os.listdir(scripts)):
            if not name.endswith(".py"):
                continue
            with open(os.path.join(scripts, name), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    mods = [node.module.split(".")[0]]
                for m in mods:
                    self.assertTrue(m in stdlib or m in local,
                                    f"{name} imports third-party {m!r}")


if __name__ == "__main__":
    unittest.main()
