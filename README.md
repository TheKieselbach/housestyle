# housestyle

**Learn your own writing voice from your own texts — without sending those
texts to a model.**

A language model can imitate your style if you show it enough of your
writing. The usual way to do that is to paste your writing into the context.
For a private person that is a nuisance. For a business it is a decision
nobody made deliberately: every mail you ever sent, in someone else's
infrastructure, because a draft needed to sound right.

housestyle takes the other route. It measures your writing **locally** and
produces numbers. Only the numbers, plus a handful of short redacted
passages, go into building the profile. The corpus stays on your machine.

---

## What you actually get

Ask any model to decline a proposal, and you get this:

> Dear Mr Fisher,
>
> Thank you for your message and for the detailed proposal. Having carefully
> reviewed the approach you outlined, I would like to share some thoughts.
> While I appreciate the thinking behind it, I am concerned that the
> associated costs may be considerable. I would therefore suggest that we
> explore alternative avenues together. Please do not hesitate to reach out
> should you have any questions.

Competent. Polite. Not you. Give the same model your profile, and it writes
to the measurements instead:

> Hi Tom,
>
> too expensive. We tried it twice, it didn't work.
> I'll look at it tomorrow and come back to you.
>
> Cheers

Every difference traces to a number, not to taste:

| Measurement | What it changed |
|---|---|
| Sentence median **7 words**, 48 % under six | The long, hedged sentences collapse |
| Intensifiers and hedges at **0 per 1000 words** | "carefully", "considerable", "I would like to" go |
| Greeting measured as **"Hi"**, sign-off as **"Cheers"** | No "Dear …", no "Please do not hesitate" |
| Exclamation marks **0.0 per sentence** | None appear |
| Informal address throughout | No formal register |

That is the point of measuring rather than asking a model to guess: **you can
see why a sentence changed.**

## What the measurement looks like

Real output from `measure.py`, abridged:

```json
{
 "volume":   { "texts": 180, "sentences": 633, "words": 3917 },
 "sentence_length_words": {
    "median": 7, "mean": 6.3, "p10": 2.0, "p90": 9.0,
    "short_under_6": 48, "long_over_25": 0 },
 "punctuation_per_sentence": {
    "comma": 0.39, "dash": 0.07, "colon": 0.15, "exclamation_mark": 0.0 },
 "markers_per_1000_words": {
    "hedges": 0.0, "intensifiers": 0.0, "questions": 12.3 },
 "particles": [ ["also", 48, 12.25], ["gern", 40, 10.21], ["ja", 31, 7.91] ]
}
```

From that plus a few short redacted passages you write `style-profile.md` —
roughly one page. **That page is what you paste into your AI tool.** It says
things like *"median 7 words; 48 percent of sentences under six; opens with
Hi, closes with Cheers; intensifiers essentially absent — emphasis comes from
negation, not from adverbs."*

Every line of it is a claim you can check against a number. That is the
difference from "write in a casual tone": a model can follow it, and you can
tell when it did not.

## How you use it day to day

1. **Once a quarter** — refresh the corpus and remeasure. Ten minutes.
2. **Once, then rarely** — paste `style-profile.md` into your tool's
   instructions: ChatGPT custom instructions, a Claude Project, a Gem, your
   `.cursorrules`. It stays there.
3. **Per draft** — check it against your own vocabulary:
   ```bash
   housestyle outliers draft.txt
   ```
   It lists words whose stem you almost never use. In the reference corpus
   one flagged word appeared **once** in 50,000 of the author's own words.
   Not every hit is wrong — technical terms land there too. It is a list to
   look at, not a list to delete.
4. **When you rewrite a draft** — put the rewritten version back into the
   corpus. Texts you approved are the best material there is, because they
   are certainly in your voice.

With the Claude Code plugin, steps 2 to 4 happen on their own.

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
path you set in `housestyle.conf`, deliberately outside this repository, and
`.gitignore` is a second net in case something is ever written here by
mistake. Sample passages — the one place actual text is meant to be shown to
a model — are redacted first: configured names, mail addresses, links, phone
numbers and amounts.

**Secrets are redacted when the corpus is written.** People type API keys and
passwords into chat windows, and transcripts keep them. Keys, tokens, private
key blocks and credentials in URLs are replaced with placeholders before
anything is stored — and again before any sample is shown to a model.

Nothing in this project sends anything anywhere. There is no telemetry, no
network call except the one in `collect_web.py`, which fetches URLs you pass
it yourself — and only over http and https, never `file://`.

What was checked before release, and what it found, is in
[`SECURITY.md`](SECURITY.md).

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

52 tests, no corpus and no setup needed. They are not coverage theatre — each
one records a specific way an earlier version was wrong, or a security
constraint that must keep holding.

## Contributing

The most useful contribution is **a language pack** — one JSON file, no code,
and it needs a native speaker. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

Apache-2.0. See `LICENSE` and `NOTICE`.
