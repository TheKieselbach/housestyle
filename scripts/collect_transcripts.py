#!/usr/bin/env python3
"""Extracts your own messages from Claude Code transcripts.

The source is the JSONL files under ~/.claude/projects/. The only thing of
interest there is what *you* typed or dictated — tool output, system
reminders and pasted files are noise and would wreck the metrics.

This is the cheapest possible starting corpus: if you use Claude Code, the
material already exists and needs no export from anywhere.

Result: <ROOT>/corpus/transcripts.jsonl, one message per line.
"""
import json, glob, os, re, sys, hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# Wrapper blocks the environment injects into user messages.
WRAPPERS = re.compile(
    r"<(system-reminder|command-name|command-message|command-args|"
    r"local-command-stdout|local-command-stderr|ci-monitor-event|"
    r"user-prompt-submit-hook)>.*?</\1>",
    re.S,
)
# Whole messages that are pure machine chatter.
MACHINE = re.compile(
    r"^\s*(\[Request interrupted|Caveat: The messages below|"
    r"API Error|<task-notification|\[Image #\d+\]\s*$|"
    r"This session is being continued|<scheduled-task|<[a-z-]+ name=)",
)


def strip_foreign(text):
    """Removes pasted material, keeps your own sentences.

    Pasted files and logs are stylistically worthless and would blow up the
    sentence-length statistics. Detected through three signals that almost
    never occur in typed or dictated instruction."""
    text = WRAPPERS.sub(" ", text)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)                 # code block
    text = re.sub(r"^\s*[|+][-=|+ ]{8,}.*$", " ", text, flags=re.M)    # table
    kept = []
    for line in text.split("\n"):
        s = line.strip()
        if len(s) > 40:
            # Lines with very few letters are logs, paths, hashes.
            letters = sum(c.isalpha() or c.isspace() for c in s) / len(s)
            if letters < 0.72:
                continue
        # Markdown scaffolding is formatting, not language. Left in, it
        # shows up as "sentence opener -" and "sentence opener ##".
        s = re.sub(r"^\s{0,6}([-*+]|\d{1,2}[.)])\s+", "", s)
        s = re.sub(r"^#{1,6}\s+", "", s)
        s = re.sub(r"[*_`]{1,3}", "", s)
        kept.append(s)
    return "\n".join(kept)


SPOKEN_PUNCT = re.compile(r"\b(period|comma|colon|new line|paragraph|full stop|"
                          r"Punkt|Komma|Doppelpunkt|Bindestrich|neue Zeile|Absatz)\b", re.I)
NUMBER_WORD = re.compile(
    r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|twenty|thirty|forty|fifty|hundred|thousand|"
    r"null|eins?|zwei|drei|vier|fuenf|fünf|sechs|sieben|acht|neun|zehn|elf|"
    r"zwoelf|zwölf|dreizehn|vierzehn|fuenfzehn|fünfzehn|sechzehn|siebzehn|"
    r"achtzehn|neunzehn|zwanzig|dreissig|dreißig|vierzig|fuenfzig|fünfzig|"
    r"hundert|tausend)\b", re.I)


def dictation_score(text):
    """0.0 to 1.0 — higher means more likely dictated.

    Dictated passages are the most valuable samples: they show speaking style
    unfiltered. They are recognisable by spelled-out numbers, spoken
    punctuation, and the absence of keyboard artefacts."""
    if len(text) < 80:
        return 0.0
    score = 0.0
    words = max(1, len(text.split()))
    score += min(0.4, len(NUMBER_WORD.findall(text)) / words * 12)
    score += 0.3 if SPOKEN_PUNCT.search(text) else 0.0
    if re.search(r"[`/\\_#*]|\bhttps?://|^\s*[-*\d]+[.)]\s", text, re.M):
        score -= 0.35
    # Dictation capitalises sentence starts reliably, hurried typing does not.
    starts = re.findall(r"(?:^|[.!?]\s+)([a-zA-ZäöüÄÖÜ])", text)
    if starts:
        score += 0.3 * (sum(c.isupper() for c in starts) / len(starts))
    return max(0.0, min(1.0, score))


def main():
    target = config.corpus_path("transcripts.jsonl")
    pattern = os.path.expanduser("~/.claude/projects/*/*.jsonl")

    seen, out = set(), []
    for path in glob.glob(pattern):
        project = os.path.basename(os.path.dirname(path))
        for line in open(path, errors="ignore"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "user" or d.get("isMeta"):
                continue
            content = d.get("message", {}).get("content")
            raw = ""
            if isinstance(content, str):
                raw = content
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        raw += part.get("text", "")
                    elif isinstance(part, dict) and part.get("type") == "tool_result":
                        raw = ""      # tool output is never your text
                        break
            if not raw.strip() or MACHINE.match(raw):
                continue
            text = re.sub(r"[ \t]+", " ", strip_foreign(raw)).strip()
            text = re.sub(r"\n{3,}", "\n\n", text)
            if len(text) < 12:
                continue
            key = hashlib.md5(text.encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "source": "transcript",
                "project": project,
                "time": d.get("timestamp", ""),
                "characters": len(text),
                "dictated": round(dictation_score(text), 2),
                "text": text,
            })

    if not out:
        sys.exit(f"No transcripts found under {pattern}\n"
                 f"Are you using Claude Code on this machine?")

    out.sort(key=lambda s: s["time"])
    with open(target, "w", encoding="utf-8") as f:
        for s in out:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    chars = sum(s["characters"] for s in out)
    dictated = [s for s in out if s["dictated"] >= 0.5]
    print(f"{len(out)} messages, {chars:,} characters (~{chars // 6:,} words)")
    print(f"of those likely dictated: {len(dictated)} "
          f"({sum(s['characters'] for s in dictated):,} characters)")
    print(f"-> {target}")


if __name__ == "__main__":
    main()
