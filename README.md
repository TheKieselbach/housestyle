# voiceprint

**Learn your own writing voice from your own texts — without sending those
texts to a model.**

A language model can imitate your style if you show it enough of your
writing. The usual way to do that is to paste your writing into the context.
For a private person that is a nuisance. For a business it is a decision
nobody made deliberately: every mail you ever sent, in someone else's
infrastructure, because a draft needed to sound right.

voiceprint takes the other route. It measures your writing **locally** and
produces numbers — sentence lengths, particle use, forms of address,
punctuation habits, the words you actually reach for. Only the numbers, plus
a handful of short redacted passages, go into building the profile. The
corpus stays on your machine.

---

## Start with what you already have

If you use Claude Code, your corpus already exists. Your own messages in the
transcripts are typed and dictated prose, and nobody has to export anything.

```bash
python3 scripts/setup.py                      # four questions, shows what it will create
python3 scripts/collect_transcripts.py
python3 scripts/measure.py "$ROOT/corpus/transcripts.jsonl" --tag transcripts
```

That is the whole first run. You now have a file of numbers describing how you
write, and no text has left the machine.

Add registers as you go — sent mail (mbox or Microsoft Graph), published
articles. Registers are kept apart on purpose: most people write very
differently in mail than in public. Getting your texts out of Gmail, Microsoft
365, Apple Mail or any IMAP provider is covered in
[`docs/getting-your-texts.md`](docs/getting-your-texts.md).

**Requirements: Python 3.9 and nothing else.** No packages, no account, no
network. See [`INSTALL.md`](INSTALL.md) — including exactly what gets created
and how to remove it.

## Works with whatever you already use

The measurement is plain Python and produces a Markdown profile. Paste it into
ChatGPT's custom instructions, a Claude Project or Style, a Gem, your
`.cursorrules`, or a local model's system prompt. Or read it yourself — it is
an honest description of how you write.

The `skills/` directory adds a [Claude Code](https://claude.com/claude-code)
plugin on top, which loads the profile automatically and checks drafts against
it. **That layer is optional** and deleting it changes nothing else.

## What it measures

| | |
|---|---|
| Sentence length | median, mean, p10/p90, share under 6 and over 25 words |
| Punctuation | commas, dashes, colons, brackets, question and exclamation marks per sentence |
| Markers | hedges, intensifiers, connectives, contrast, subjunctive, modals, nominal style, passive, person, forms of address |
| Closed word classes | particles, degree words, evaluative words — the actual style signal |
| Openings and closings | how you start sentences, how you greet, how you sign off |
| Topic vocabulary | reported separately and labelled **not style** |

## Three things that cost a full run each

These are in the code as comments too. They are the reason this repository
exists rather than a description of one.

**1 · Mail clients emit `\r\n`.** Every `$` anchor in a line-based regular
expression fails on the leftover `\r`, silently. Normalise before anything
else.

**2 · The signature was 43 percent of the mail corpus.** An automatic
signature block — address, service list, marketing line, booking link — hangs
on every mail and dwarfs the actual message. Worse, its canned sign-off looks
exactly like a typed one, so the profile concluded a farewell formula the
author never types. Signature anchors are configuration in this project, and
`collect_mail.py` warns when you leave them empty.

**3 · Word frequency over open word classes measures your topic, not your
style.** An early run produced a profile whose most characteristic words were
"client", "backup" and "folder". True, and useless. What someone writes
*about* changes with the project. Which particles they reach for does not.
Closed classes — particles, degree words, evaluative words — are the signal;
open classes are reported separately and clearly labelled.

## Languages

The method is language-independent. The word lists are not, so they live in
`lang/<code>.json` rather than in the code.

Shipped: **German** (`de`, the reference language — built and validated
against a real 54,000-word corpus) and **English** (`en`). Adding a language
means writing one JSON file; see `docs/adding-a-language.md`.

## What this does not do

- It does not write for you. It produces a profile; a model writes with it.
- It does not verify authorship or detect AI text.
- It will not make a model sound like you from a small corpus. Below roughly
  10,000 of your own words the numbers are noise.
- It is not a privacy guarantee for whatever you do next. It keeps *this*
  step local. What you paste elsewhere is still your call.

## Privacy

The corpus contains the full text of things you wrote. It lives under the
path you set in `voiceprint.conf`, deliberately outside this repository, and
`.gitignore` is a second net in case something is ever written here by
mistake. Sample passages — the one place actual text is meant to be shown to
a model — are redacted first: configured names, mail addresses, links, phone
numbers and amounts.

Nothing in this project sends anything anywhere. There is no telemetry, no
network call except the one in `collect_web.py`, which fetches URLs you pass
it yourself.

## Why it was built this way

The long version is in [`docs/why-measure-locally.md`](docs/why-measure-locally.md).
The short version: a guardrail that only exists in a policy document is not a
guardrail. This one is in the file layout — the corpus cannot reach a model
by accident, because the thing that reaches the model is a JSON file full of
numbers.

## Tests

```bash
python3 -W error::ResourceWarning -m unittest discover tests -v
```

34 tests, no corpus and no setup needed. They are not coverage theatre — each
one records a specific way an earlier version was wrong, including all three
bugs listed in the changelog.

## Contributing

The most useful contribution is **a language pack** — one JSON file, no code,
and it needs a native speaker. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

Apache-2.0. See `LICENSE` and `NOTICE`.
