#!/usr/bin/env python3
"""Fetches your published texts from the web and stores them as a corpus.

Usage:  collect_web.py <url> [<url> ...] [--ai-drafted]

Pass --ai-drafted if these texts were written with a model and only revised
by you. They are then tagged and stay OUT of the comparison base used by
outlier_words.py.

That distinction matters more than it looks. Feed AI-drafted text into the
base and the base contains exactly the vocabulary the outlier check is meant
to catch — the check becomes worthless while still looking like it works.
"""
import sys, os, re, json, html, hashlib, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


# urllib happily serves file:// and ftp:// — `urlopen("file:///etc/hosts")`
# returns the file. For a tool whose job is to collect text into a corpus that
# is worth exactly one allowlist: a mistyped or pasted path must not turn into
# local file contents sitting in your corpus.
ALLOWED_SCHEMES = ("http", "https")
MAX_BYTES = 10 * 1024 * 1024


def check_url(url):
    """Returns an error string, or None if the URL is acceptable."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return (f"refused: scheme {parsed.scheme or '(none)'!r} is not allowed "
                f"(only {', '.join(ALLOWED_SCHEMES)})")
    if not parsed.netloc:
        return "refused: no host in URL"
    return None


def text_from_html(raw):
    t = re.sub(r"(?is)<(script|style|nav|footer|header|form|svg|aside).*?</\1>", " ", raw)
    m = re.search(r"(?is)<(article|main)[^>]*>(.*?)</\1>", t)
    if m:
        t = m.group(2)
    t = re.sub(r"(?i)<br\s*/?>", "\n", t)
    t = re.sub(r"(?i)</(p|div|li|h[1-6]|blockquote|tr)>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t).replace(" ", " ")
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip()


def main():
    argv = sys.argv[1:]
    ai_drafted = "--ai-drafted" in argv
    urls = [a for a in argv if not a.startswith("--")]
    if not urls:
        sys.exit(__doc__)

    target = config.corpus_path("web.jsonl")
    out, seen = [], set()
    for url in urls:
        problem = check_url(url)
        if problem:
            print(f"!! {url}: {problem}")
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "housestyle/1.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                # A redirect must not smuggle in another scheme.
                landed = check_url(response.geturl())
                if landed:
                    print(f"!! {url}: redirected to something {landed}")
                    continue
                raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                print(f"!! {url}: larger than {MAX_BYTES // 1024 // 1024} MB, skipped")
                continue
            raw = raw.decode("utf-8", "ignore")
        except Exception as e:
            print(f"!! {url}: {e}")
            continue
        t = text_from_html(raw)
        # Navigation and footer remnants are short lines without punctuation.
        t = "\n".join(l for l in t.split("\n")
                      if len(l.strip()) > 45 or l.strip().endswith((".", "?", ":", "!")))
        if len(t) < 600:
            print(f"?? {url}: only {len(t)} characters, skipped")
            continue
        key = hashlib.md5(re.sub(r"\s+", "", t[:2000]).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        out.append({"source": "web", "ai_drafted": ai_drafted, "url": url,
                    "characters": len(t), "text": t})
        print(f"ok {len(t):>6} characters  {url}")

    with open(target, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    chars = sum(r["characters"] for r in out)
    print(f"\n{len(out)} documents, {chars:,} characters (~{chars // 6:,} words)")
    if ai_drafted:
        print("tagged ai_drafted — excluded from the outlier comparison base")
    print(f"-> {target}")


if __name__ == "__main__":
    main()
