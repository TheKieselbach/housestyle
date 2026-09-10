#!/usr/bin/env python3
"""Pulls a few short, redacted sample passages from a corpus.

Metrics say HOW you write. They do not say what it sounds like. For that a
style profile needs a handful of real passages as anchors.

Because this is the one place where actual text has to reach a model, the
script is deliberately frugal: few samples, short ones, and names,
addresses, links and amounts stripped out first.

Usage:  samples.py <corpus.jsonl> [--kind opener|closer|whole] [--n 6]
"""
import json, sys, re, os, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def redact(text, names, lang):
    for name in names:
        text = re.sub(re.escape(name), "[name]", text, flags=re.I)
    text = re.sub(r"[\w.+-]+@[\w.-]+", "[mail]", text)
    text = re.sub(r"https?://\S+", "[link]", text)
    text = re.sub(r"\+?\d[\d /()-]{7,}", "[number]", text)
    text = re.sub(r"\b\d{1,3}(?:[.,]\d{3})*[.,]\d{2}\s?(EUR|USD|GBP|€|\$|£)", "[amount]", text)
    # A name right after the greeting is the most common leftover risk.
    greeting_word = lang["greeting"].split("(")[1].split(")")[0].split("|")[0]
    text = re.sub(rf"(?im)^([ \t]*({greeting_word}|Hi|Hello|Moin|Hallo))\s+"
                  rf"(Mr\.?|Mrs\.?|Ms\.?|Herr|Frau)?\s*[A-ZÄÖÜ][\wäöüß-]+,",
                  r"\1 [name],", text)
    return text


def main():
    argv = sys.argv[1:]
    kind, n = "whole", 6
    if "--kind" in argv:
        i = argv.index("--kind"); kind = argv[i + 1]; del argv[i:i + 2]
    if "--n" in argv:
        i = argv.index("--n"); n = int(argv[i + 1]); del argv[i:i + 2]
    if not argv:
        sys.exit(__doc__)

    lang = config.language()
    names = config.get_list("REDACT")
    greeting = re.compile(lang["greeting"], re.I | re.M)
    signoff = re.compile(lang["signoff"], re.I | re.M)

    texts = [json.loads(l)["text"] for l in open(argv[0], encoding="utf-8")]
    random.seed(7)          # same corpus, same samples — reproducible runs
    pool = []
    for t in texts:
        body = greeting.sub("", signoff.sub("", t)).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", body)
                     if 20 < len(s.strip()) < 160]
        if not sentences:
            continue
        if kind == "opener":
            pool.append(sentences[0])
        elif kind == "closer":
            pool.append(sentences[-1])
        elif 60 < len(body) < 320:
            pool.append(body)
    random.shuffle(pool)

    if not names:
        print("!! REDACT is empty in voiceprint.conf — no names will be masked.\n",
              file=sys.stderr)
    for s in pool[:n]:
        print("- " + redact(s, names, lang).replace("\n", " / "))


if __name__ == "__main__":
    main()
