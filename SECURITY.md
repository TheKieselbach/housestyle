# Security

## What matters here

This project handles the full text of what you have written. The security
property it claims is narrow and specific:

> Your corpus stays on your machine. What reaches a model is a file of numbers
> plus a few short, redacted passages.

**A bug that breaks that property is the serious kind of bug here** — more
serious than a crash. Examples:

- a code path that writes corpus text inside the repository, into a temp
  directory, or anywhere outside the configured root
- redaction in `samples.py` failing to mask something it should
- a collector leaving quoted third-party text in the corpus
- anything that makes a network request that is not a URL the user passed in

## What has been checked

A security pass ran before the first release. What it found, and what came of
it — written down because "we looked at it" is not a finding:

| Checked | Result |
|---|---|
| `eval`, `exec`, `subprocess`, `pickle`, `os.system` | none present, and a test now fails if any appear |
| Third-party dependencies | none, and a test parses every import to keep it that way |
| Catastrophic regex backtracking | no nested quantifiers; 40 KB of adversarial input runs in milliseconds |
| **URL schemes in the web collector** | **was a real hole** — `urlopen` serves `file://`, so a mistyped path pulled local file contents into the corpus. Now an http/https allowlist, checked again after redirects, with a 10 MB cap |
| **Secrets in collected text** | **was a real gap** — people type credentials into chat windows, and transcripts keep them. Now redacted at collection time, with a second pass before any sample is shown |
| **Deletion in `--uninstall`** | **was a real risk** — a `ROOT` pointing at a home or system directory would have deleted folders the user made themselves. Now refused outright |
| Path traversal in corpus writes | filenames are fixed constants, not user input |

Each of these has a test in `tests/test_security.py`. They are the claim,
written down so it cannot quietly stop being true.

## Reporting

Open a [private security advisory](../../security/advisories/new) on GitHub.
Please do not open a public issue for anything in the list above.

Include what you did, what happened, and — if it involves leaked content —
please describe it rather than pasting it.

Expect a first reply within a week. This is maintained by one person alongside
other work; that is the honest expectation, not a service level.

## What is out of scope

- **The model you use.** This project keeps your corpus local. What you paste
  into a chat window afterwards is yours to decide.
- **Your storage.** Where you point `ROOT` is your call, and its backup,
  sync and encryption are your responsibility.
- **The word lists.** A language pack that misses a marker produces a worse
  profile, not a leak. Open a normal issue.

## Not a claim being made

This is not an anonymisation tool. It does not make a corpus safe to share; it
removes the need to share one. Those are different claims and only the second
is made here.
