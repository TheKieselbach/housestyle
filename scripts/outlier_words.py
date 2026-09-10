#!/usr/bin/env python3
"""Finds words in a draft that you yourself never use.

The occasion: a draft came back with two words that felt immediately wrong
to their supposed author. The counter-check confirmed it — 1 and 3
occurrences in 50,000 of their own words, against 41 for a word they
actually use. This script runs that check automatically.

Inflected languages need stem comparison, not whole-word comparison, or
every inflected form is a false alarm. Stem length and character
normalisation come from the language pack.

Usage:  outlier_words.py <draft.txt> [--threshold 2]
"""
import sys, os, re, json, glob, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# Only these corpora are your unaltered own language. An explicit allow-list,
# not "everything except" — otherwise a new corpus silently slips into the
# comparison base.
#
# Deliberately outside by default:
#   web.jsonl   anything drafted with AI and merely revised. Feed that in and
#               the base contains exactly the AI vocabulary this check is
#               supposed to find.
OWN = ("transcripts.jsonl", "mail.jsonl", "approved.jsonl")


def make_stem(lang):
    cfg = lang.get("stem", {})
    length = cfg.get("length", 6)
    mapping = cfg.get("normalize", {})

    def stem(word):
        w = word.lower()
        for a, b in mapping.items():
            w = w.replace(a, b)
        return w[:length]
    return stem


def corpus_counts(root, lang, stem):
    counts = collections.Counter()
    total = 0
    for path in glob.glob(os.path.join(root, "corpus", "*.jsonl")):
        if os.path.basename(path) not in OWN:
            continue
        for line in open(path, encoding="utf-8"):
            for w in re.findall(lang["word_pattern"], json.loads(line)["text"]):
                counts[stem(w)] += 1
                total += 1
    return counts, total


def main():
    argv = sys.argv[1:]
    threshold = 2
    if "--threshold" in argv:
        i = argv.index("--threshold"); threshold = int(argv[i + 1]); del argv[i:i + 2]
    if not argv:
        sys.exit(__doc__)

    lang = config.language()
    stem = make_stem(lang)
    counts, total = corpus_counts(config.root(), lang, stem)
    if not total:
        sys.exit(f"Comparison base is empty. Expected one of {OWN} "
                 f"under {os.path.join(config.root(), 'corpus')}.")
    blocked_words = [w.strip().lower() for w in config.get_list("BLOCKLIST")]

    text = open(argv[0], encoding="utf-8").read()
    words = re.findall(lang["word_pattern"], text)

    suspect, blocked = {}, []
    for w in words:
        if len(w) < 5:
            continue          # short function words say nothing about style
        if any(w.lower().startswith(b[:6]) for b in blocked_words):
            blocked.append(w); continue
        n = counts[stem(w)]
        if n <= threshold:
            suspect[w] = n

    print(f"Comparison base: {total:,} words")
    if blocked:
        print("\nBLOCKED — you marked these as not yours:")
        for w in sorted(set(blocked)):
            print(f"  {w}")
    if suspect:
        print(f"\nSUSPECT — stem occurs at most {threshold}x in your own writing:")
        for w, n in sorted(suspect.items(), key=lambda x: (x[1], x[0])):
            print(f"  {n:>3}x  {w}")
    if not suspect and not blocked:
        print("\nNothing stands out.")
    print("\nNot every hit is a mistake — technical terms and names land here "
          "too.\nThis is a list to look at, not a list to delete.")


if __name__ == "__main__":
    main()
