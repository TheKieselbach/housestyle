# Contributing

## The most useful contribution

**A language pack.** The method works for any language; the word lists have to
be written per language, and that needs a native speaker. See
[`docs/adding-a-language.md`](docs/adding-a-language.md) — it is one JSON file
and no code.

Second most useful: **a report that it works, or does not, on your platform**
or with your mail provider. The install docs make claims about Windows and
about export routes; every one of them benefits from someone checking.

## Ground rules

**No dependencies.** Standard library only. A tool that reads your sent mail
should not pull in a package tree you have not read. A pull request that adds
a requirement needs to argue why the standard library cannot do it.

**No automated collection from platforms that forbid it.** Several services
prohibit automated reading of their pages in their terms of use. This project
provides no way to do that and will not merge one, however convenient.

**Every guardrail has a test.** The tests in `tests/` are not coverage
theatre — each one records a specific way an early version was wrong. If you
fix a bug, leave a test that would have caught it, with a comment saying what
went wrong.

**Comments say why, not what.** The code is short. What it does is readable.
Why a threshold is 43 percent, or why a marker is matched case-sensitively, is
not — write that down.

## Running the tests

```bash
python3 -W error::ResourceWarning -m unittest discover tests -v
```

No corpus needed. No setup needed. If they need either, that is a bug.

## Pull requests

Small and single-purpose. Say what you changed and why in the description; the
commit message can be short if the description is not.

If your change affects what gets written to disk, or what leaves the machine,
say so explicitly at the top of the description.
