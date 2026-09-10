#!/usr/bin/env python3
"""Measures writing style over a corpus — locally, without sending text
anywhere.

This script is the whole point of the project. A language model could read
your style straight from the raw texts, but then every mail you ever sent
would travel through its context. Instead, numbers are produced here:
sentence lengths, particle use, forms of address, punctuation habits. A
style profile can be written from those numbers without the corpus ever
leaving the machine.

Which words count as style is language-specific and lives in lang/<code>.json.
The method is not: it works for any language with a word list.

Usage:  measure.py <corpus.jsonl> [<corpus.jsonl> ...] [--tag NAME]
"""
import json, sys, re, os, collections, statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def split_sentences(text, abbreviations):
    """Splits into sentences, protecting abbreviations that end in a period.
    Without this, "e.g." ends a sentence and the length statistics collapse."""
    if abbreviations:
        guard = "|".join(abbreviations)
        text = re.sub(rf"\b({guard})\.", r"\1<P>", text)
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
    return [p.replace("<P>", ".").strip() for p in parts if len(p.strip()) > 1]


def analyse(texts, tag, lang):
    body = "\n\n".join(texts)
    words = re.findall(lang["word_pattern"], body)
    n_w = max(1, len(words))
    sentences = [s for t in texts for s in split_sentences(t, lang["sentence_abbreviations"])]
    lengths = [len(s.split()) for s in sentences if s.split()]
    n_s = max(1, len(sentences))

    # Some markers are only distinguishable by capitalisation. In German the
    # polite "Sie" differs from plural "sie" by nothing else. Searching
    # case-insensitively counts every "ihr" as formal address — that exact
    # mistake made a corpus of informal posts look formal.
    case_sensitive = set(lang.get("case_sensitive_markers", []))

    def per_1000(pattern, name=""):
        flags = 0 if name in case_sensitive else re.I
        return round(len(re.findall(pattern, body, flags)) / n_w * 1000, 1)

    pct = lambda q: round(statistics.quantiles(lengths, n=100)[q - 1], 1) if len(lengths) > 99 else 0

    result = {
        "tag": tag,
        "language": lang["code"],
        "volume": {"texts": len(texts), "sentences": n_s, "words": n_w,
                   "characters": len(body)},
        "sentence_length_words": {
            "median": round(statistics.median(lengths), 1) if lengths else 0,
            "mean": round(statistics.fmean(lengths), 1) if lengths else 0,
            "p10": pct(10), "p90": pct(90),
            "short_under_6": round(sum(1 for l in lengths if l < 6) / n_s * 100),
            "long_over_25": round(sum(1 for l in lengths if l > 25) / n_s * 100),
        },
        "word_length_mean": round(statistics.fmean([len(w) for w in words]), 2) if words else 0,
        "punctuation_per_sentence": {
            "comma": round(body.count(",") / n_s, 2),
            "dash": round(len(re.findall(r"\s[-–—]\s", body)) / n_s, 2),
            "colon": round(body.count(":") / n_s, 2),
            "parenthesis": round(body.count("(") / n_s, 2),
            "question_mark": round(body.count("?") / n_s, 2),
            "exclamation_mark": round(body.count("!") / n_s, 2),
        },
        "markers_per_1000_words": {k: per_1000(v, k) for k, v in lang["markers"].items()},
    }

    lower = [w.lower() for w in words]
    counts = collections.Counter(lower)

    def inventory(word_list):
        """Only what actually occurs, descending, per 1000 words."""
        hits = []
        for w in word_list:
            n = sum(v for k, v in counts.items() if re.fullmatch(w, k))
            if n:
                hits.append((re.sub(r"\((\w+)\|.*?\)", r"\1", w), n, round(n / n_w * 1000, 2)))
        return sorted(hits, key=lambda t: -t[1])[:25]

    # Closed word classes are the actual style signal: which particles
    # someone reaches for depends on the speaker. Open classes (nouns)
    # depend on the topic — they filled early runs with project vocabulary
    # that said nothing about how the person writes. Kept below, clearly
    # labelled, because it is useful for a different question.
    result["particles"] = inventory(lang["particles"])
    result["degree_words"] = inventory(lang["degree_words"])
    result["evaluative"] = inventory(lang["evaluative"])

    stopwords = set(lang["stopwords"])
    result["topic_vocabulary_not_style"] = collections.Counter(
        w for w in lower if w not in stopwords and len(w) > 4).most_common(20)
    result["sentence_openers"] = collections.Counter(
        s.split()[0].strip(",.:;-–—").lower() for s in sentences
        if s.split() and s.split()[0].strip(",.:;-–—").isalpha()
    ).most_common(20)
    result["greetings"] = collections.Counter(
        m.group(0).strip() for m in re.finditer(lang["greeting"], body, re.M)).most_common(12)
    result["signoffs"] = collections.Counter(
        m.group(0).strip() for m in re.finditer(lang["signoff"], body, re.M | re.I)).most_common(12)
    return result


def main():
    argv = sys.argv[1:]
    tag = "all"
    if "--tag" in argv:
        i = argv.index("--tag"); tag = argv[i + 1]; del argv[i:i + 2]
    if not argv:
        sys.exit(__doc__)

    lang = config.language()
    texts = []
    for path in argv:
        for line in open(path, encoding="utf-8"):
            d = json.loads(line)
            if d.get("text", "").strip():
                texts.append(d["text"])
    if not texts:
        sys.exit("No texts found. Did the collectors run?")

    result = analyse(texts, tag, lang)
    target = os.path.join(config.root(), "metrics", f"{tag}.json")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    json.dump(result, open(target, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
    print(f"\n-> {target}", file=sys.stderr)


if __name__ == "__main__":
    main()
