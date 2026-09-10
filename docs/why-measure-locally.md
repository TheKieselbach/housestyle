# Why measure locally

## The decision nobody makes deliberately

The straightforward way to get a model to write like you is to show it your
writing. Paste in twenty mails, ask for a style summary, keep the summary.
It works, and it takes ten minutes.

What it also does is move twenty mails into someone else's infrastructure —
including whatever was in them. Client names. Numbers. Things said in
confidence. Nobody decides that; it happens as a side effect of wanting a
draft to sound right.

For a private person that is a nuisance. For anyone with a duty of
confidentiality — a consultant, a lawyer, a doctor, anyone under an NDA — it
is a decision that should have been made on purpose and was not.

## The alternative

Style is measurable. Not perfectly, but far better than intuition suggests,
and the measurable part is exactly the part that transfers.

Sentence length distribution. How often a comma appears. Whether someone uses
dashes. Which particles they reach for. How they open a sentence, how they
greet, how they sign off. Whether they hedge or intensify. Whether they write
in first person singular or plural.

All of that can be computed from a corpus on your own machine and expressed
as a few hundred numbers. Those numbers describe how you write. They do not
contain what you wrote.

A model given those numbers plus a handful of short, redacted passages
produces a usable style profile. The corpus never moves.

## Where the guardrail actually sits

A rule in a policy document is not a guardrail — it is an intention. This one
is in the file layout:

- The corpus lives under `ROOT`, outside the repository, by construction.
- `.gitignore` catches anything written to the repo by accident.
- The artefact that reaches a model is a JSON file of counts and medians.
- The one place raw text is meant to reach a model — sample passages — is a
  separate script with redaction built into it, and it warns when the
  redaction list is empty.

The point is not that the rules are strict. It is that following them is the
path of least resistance and breaking them takes effort.

## What it costs

Honesty about the trade-off:

- **You need a corpus.** Below roughly 10,000 of your own words the numbers
  are noise. Pasting five mails into a chat window works at a size where this
  does not.
- **Numbers miss things.** Rhythm, humour, when someone chooses to be blunt —
  none of that is in a median. That is why the profile carries a few real
  passages as anchors. It is a compromise, not a clean win.
- **The word lists are language-specific.** The method transfers; the lists
  have to be written per language.

## What it is not

It is not an anonymisation tool. It does not make the corpus safe to share —
it keeps the corpus from needing to be shared. Those are different claims,
and only the second one is being made here.
