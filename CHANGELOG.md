# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

First public release in preparation. Not published yet.

### Added
- Local style measurement over a corpus: sentence lengths, punctuation,
  markers, closed word classes, openings and sign-offs
- Language packs, shipping German and English — the method is
  language-independent, the word lists are not
- Collectors for Claude Code transcripts, sent mail (mbox and Microsoft
  Graph), and published web pages
- Redacted sample extraction, and an outlier check that flags words the author
  does not actually use
- Interactive setup assistant with `--check` and `--uninstall`, which lists
  everything it will create before writing anything
- Claude Code plugin layer (`profile` and `draft` skills), optional — the
  measurement works with any tool, or none
- 34 tests, each recording a specific way an earlier version was wrong
- Packaging: `pip install housestyle` with a `housestyle` command, alongside
  the git checkout and Claude Code plugin layouts. Configuration and language
  packs are resolved per layout rather than assumed
- `.claude-plugin/marketplace.json`, so the repository can be added as a
  Claude Code plugin marketplace directly

### Fixed — carried over from the private original
- **Blocklist compared raw words instead of stems.** An entry for an
  uninflected form never matched the inflected one it was written for.
- **Stemming truncated only.** German "tragen" and "trägt" fell to different
  stems; ASCII transliterations ("fuer") and umlaut spellings ("für") did too.
  Fixed with suffix and prefix stripping plus transliteration folding.
- **Abbreviation guard protected only the last period.** German "z. B." ended
  a sentence after the "z.", silently shortening every measured sentence that
  contained an abbreviation.
