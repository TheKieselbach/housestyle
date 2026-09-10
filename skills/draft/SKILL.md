---
name: draft
description: Writes mail, posts, proposals and other text in the user's own measured voice instead of generic prose - loads the style profile and checks the draft against it. Use for "write a mail", "reply to", "draft a post", "put this into words", "in my voice", "that doesn't sound like me", or whenever text is produced that is meant to come from the user. Also use when the user hands back a revised draft - that is when the profile learns.
---

# Write in the user's voice

## First: load the profile

```bash
ROOT="$(grep '^ROOT=' <repo>/housestyle.conf | cut -d= -f2-)"
cat "$ROOT/style-profile.md"
```

**Do not write without it.** Composing from memory is exactly the failure
this skill exists to prevent — the result will be competent, generic, and
recognisably not theirs.

If no profile exists yet, run the `profile` skill first.

## Pick the register

The profile describes separate registers, and they are not interchangeable.
A mail voice used in public reads flat; a public voice used in a client mail
reads inflated.

| Occasion | Register |
|---|---|
| Mail, proposal, scheduling, declining | **mail** |
| Public post, website, article | **public** |
| Internal note, instruction, one's own notes | **transcript** |

For mail, also settle the level of formality with this particular recipient.
If it is unclear, look it up in the corpus instead of guessing:

```bash
python3 -c "
import json,sys,re
for line in open(sys.argv[1],encoding='utf-8'):
    d=json.loads(line)
    if re.search(sys.argv[2], d['text'], re.I): print(d['text'][:200]); break
" "$ROOT/corpus/mail.jsonl" "<recipient surname>"
```

## Writing

Compose directly in the target register. Do not write "normally" first and
adapt afterwards — a rewrite keeps the foreign sentence structure underneath.

Four things this fails on most often:

1. **Sentences too long.** Check the profile's median. Most people write far
   shorter than a model writes for them; in the reference corpus the mail
   median was 7 words, with 43 percent of sentences under six.
2. **Too much throat-clearing at the top.** Look at how the profile says they
   actually open, and copy that.
3. **Exclamation marks.** Check the measured rate. It is usually near zero,
   and a model adds them freely.
4. **Public writing is sharper, not louder.** In the reference corpus
   intensifiers were *lowest* in public posts. Emphasis came from negation,
   reframing and broken expectation — never from "totally", "really",
   "absolutely".

## First check: foreign words

People recognise words that are not theirs instantly, and they are almost
always model words. In the reference corpus one flagged word appeared **once**
in 50,000 of the author's own words, another three times — against 41 for a
word they genuinely use.

```bash
python3 <repo>/scripts/outlier_words.py DRAFT.txt
```

Look at every hit. Technical terms and names may stay; replace the rest —
and replace them with a word that occurs in the corpus, not with the nearest
synonym from your own vocabulary. Anything the user marks as foreign goes
into `BLOCKLIST` in `housestyle.conf`.

## Second check: the numbers

Run the draft through the same measurement that produced the profile. This is
the honest test:

```bash
python3 -c "
import json,sys
t=open(sys.argv[1],encoding='utf-8').read()
json.dump({'text':t},open('/tmp/housestyle-draft.jsonl','w',encoding='utf-8'),ensure_ascii=False)
" DRAFT.txt
python3 <repo>/scripts/measure.py /tmp/housestyle-draft.jsonl --tag draft
```

Compare against `metrics/mail.json` or `metrics/web.json`. Three values carry
most of the signal: sentence-length median, share of sentences under six
words, exclamation marks. If the median is off by more than three words,
cut again.

## Never send unasked

Present the draft; the user releases it. This holds for mail explicitly, and
equally for anything published. Nothing goes out without an explicit yes, and
a previous yes is not a standing one.

## When the user revises the draft

This is the most valuable moment in the whole loop, and it is usually thrown
away. When a revised version comes back:

1. Put original and revision side by side and name **what** changed — not "it
   reads better now", but "three sentences merged", "'regarding' replaced by
   'on'", "closing question cut".
2. Only carry **recurring** changes into the profile. A one-off correction is
   taste on the day, not a pattern.
3. Append the revised version to the corpus so the next measurement counts it:

```bash
python3 -c "
import json,sys,datetime
t=open(sys.argv[1],encoding='utf-8').read()
with open(sys.argv[2],'a',encoding='utf-8') as f:
    f.write(json.dumps({'source':'approved','time':datetime.date.today().isoformat(),
                        'characters':len(t),'text':t},ensure_ascii=False)+'\n')
" REVISION.txt "$ROOT/corpus/approved.jsonl"
```

Rerun the `profile` skill once enough has accumulated. Approved texts are the
best material there is: they are certainly in the user's voice, because the
user signed them off.
