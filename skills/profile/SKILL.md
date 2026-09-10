---
name: profile
description: Builds or refreshes a measured writing-style profile from the user's own texts - Claude Code transcripts, sent mail, published articles. Use for "update my style profile", "rebuild the voice profile", "refresh the corpus", "the profile is out of date", or when a new text source has become available. Writing itself is not this skill's job - that is the draft skill.
---

# Build a style profile

Runs rarely — once a quarter is plenty, or when a new source appears. Writing
loads the finished profile, not this skill.

```bash
cd <repo>/scripts
ROOT="$(grep '^ROOT=' ../housestyle.conf | cut -d= -f2-)"
```

If `housestyle.conf` does not exist yet, stop and walk the user through
`CONFIGURE-ME.md` first. Never guess a path.

## 1 · Transcripts

Runs without asking. The data is already local.

```bash
python3 collect_transcripts.py
```

This is the cheapest corpus there is and usually the largest. Start here even
if other sources are planned.

## 2 · Sent mail

Two ways in. Prefer whichever the user already has.

**mbox** — every mail client can export one, no API access needed:

```bash
python3 collect_mail.py ~/Downloads/sent.mbox
```

**Microsoft Graph** — a dump of the sent-items folder as JSON:

```bash
python3 collect_mail.py sent-dump.json --format graph
```

When pulling from an API, request the dump large enough that the environment
writes it to a **file** rather than into the conversation. At several hundred
mails that is the difference between keeping the text local and not.

**Delete the raw dump afterwards.** It is business content sitting outside
the configured root. Do it visibly, in its own command, so the user sees it
happened.

Then check whether signature remnants got through. Signature blocks change,
and the anchors in `housestyle.conf` need to follow:

```bash
python3 -c "
import json,collections,sys
c=collections.Counter()
for l in open(sys.argv[1],encoding='utf-8'):
    for z in json.loads(l)['text'].split(chr(10)):
        if z.strip(): c[z.strip()[:45]]+=1
for z,n in c.most_common(8): print(f'{n:4}x {z}')
" "$ROOT/corpus/mail.jsonl"
```

A line appearing 50 times is a signature, not style. Add it to `SIGNATURE`
and run the collector again.

## 3 · Published texts

```bash
python3 collect_web.py <url> [<url> ...]
```

Add `--ai-drafted` if the texts were written with a model and only revised.
They are then excluded from the outlier comparison base — otherwise that base
contains exactly the vocabulary the check is meant to find.

**Only collect from sources the user is allowed to collect from.** Their own
site, their own exports. Do not automate the reading of platforms whose terms
forbid it, and do not offer to.

## 4 · Measure

Per register, then overall. Registers differ sharply and the profile should
say so.

```bash
for t in transcripts mail web approved; do
  [ -f "$ROOT/corpus/$t.jsonl" ] && python3 measure.py "$ROOT/corpus/$t.jsonl" --tag $t
done
python3 measure.py "$ROOT/corpus/"*.jsonl --tag all
```

## 5 · Write the profile

Rewrite `$ROOT/style-profile.md` from scratch — replace, do not append.

**Every statement in it must trace back to a number in `metrics/` or a
passage from `samples.py`.** Sentences like "writes clearly and concisely"
are worthless. "Median 7 words, 43 percent of sentences under six words" is
something a writer can apply.

Pull anchors:

```bash
python3 samples.py "$ROOT/corpus/mail.jsonl" --kind opener --n 8
python3 samples.py "$ROOT/corpus/mail.jsonl" --kind closer --n 6
python3 samples.py "$ROOT/corpus/mail.jsonl" --kind whole  --n 5
```

Names to mask belong in `REDACT` in `housestyle.conf`.

## Limits belong in the profile

If a register is thin, say so in the profile rather than hiding it. A
register built from 700 words describes tendencies but yields no reliable
numbers. Concealing that manufactures confidence that is not there.

The same goes for eras. If someone's public writing spans a job change or a
change of role, the older material may not be their own voice at all —
employer marketing reads very differently. The break shows up in the metrics
themselves: exclamation marks and first-person-plural jump, dashes and
contrast markers collapse. Split the corpus at the break and measure only the
part that is actually theirs.
