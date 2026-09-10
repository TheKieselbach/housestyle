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
