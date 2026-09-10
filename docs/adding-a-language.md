# Adding a language

A language pack is one JSON file in `lang/`, named by its code. Copy
`lang/en.json` and work through the keys.

The measurement code reads all of this from the pack. If your language needs
something the pack cannot express, that is a bug in the split, not in your
language — please open an issue.

## Keys

| Key | What it is |
|---|---|
| `word_pattern` | Regex matching one word. Include your alphabet's letters and any joining characters (`-`, `'`). |
| `sentence_abbreviations` | Abbreviations ending in a period. Without these, "e.g." ends a sentence and the length statistics collapse. |
| `stem.length` | How many leading characters count as the stem. Inflected languages need this shorter. |
| `stem.normalize` | Character folding before stemming, e.g. `ä → a`. Empty for languages that do not need it. |
| `stopwords` | Function words excluded from the topic-vocabulary listing. |
| `greeting` / `signoff` | Regexes for how letters open and close. Anchored with `^`, used with `re.M`. |
| `markers` | Named regexes counted per 1000 words. Keep the English key names so profiles stay comparable across languages. |
| `case_sensitive_markers` | Marker names that must be matched case-sensitively. See below. |
| `particles`, `degree_words`, `evaluative` | Closed word classes. **This is the actual style signal.** |

## The capitalisation trap

Some languages distinguish meanings only by case. German polite "Sie" differs
from plural "sie" by nothing else. Matched case-insensitively, every informal
plural counts as formal address — which made a corpus of informal posts look
formal.

If your language has such a pair, list the affected marker in
`case_sensitive_markers`.

## Choosing the closed word classes

Resist the urge to include nouns. Open word classes measure what someone
writes *about*, which changes with the project. Closed classes — particles,
degree words, evaluative adjectives — depend on the speaker and stay stable.

A good test: would this word appear just as often if the person changed
industry? If yes, it belongs in the pack.

## Validating

Run against a corpus you know well and read the output. The signal that it
works: the particle inventory should make you nod. If the top entries look
generic, the list is too broad; if half the list has zero hits, it is too
narrow.
