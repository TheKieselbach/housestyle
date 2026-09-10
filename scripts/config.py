#!/usr/bin/env python3
"""Shared configuration and language-pack loading.

Every path, name and word list that is specific to *you* lives in
`housestyle.conf`. Nothing personal belongs in the code.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CONF = os.path.join(REPO, "housestyle.conf")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path):
    """Yields one parsed record per line. Used by every collector and reader,
    so the file handle is closed in exactly one place."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def read_text(path, **kw):
    with open(path, encoding=kw.pop("encoding", "utf-8"), **kw) as f:
        return f.read()


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def _parse(path):
    """Reads a simple KEY=value file. Indented lines continue the previous
    key as a list entry, which is how multi-line keys like SIGNATURE work."""
    values, key = {}, None
    if not os.path.exists(path):
        sys.exit(
            f"No configuration found at {path}\n"
            f"Copy housestyle.conf.example to housestyle.conf and fill it in.\n"
            f"See CONFIGURE-ME.md."
        )
    for raw in read_text(path).split("\n"):
        line = raw.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace() and key:
            values.setdefault(key + "_LIST", []).append(line.strip())
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            values[key] = val.strip()
    return values


def get(key, default=""):
    return _parse(CONF).get(key, default)


def get_list(key):
    """Comma-separated value plus any indented continuation lines."""
    values = _parse(CONF)
    out = [v.strip() for v in values.get(key, "").split(",") if v.strip()]
    out += values.get(key + "_LIST", [])
    return out


def root():
    """The corpus root. Deliberately fails loudly — a wrong path here would
    silently write your corpus somewhere it does not belong."""
    path = get("ROOT")
    if not path:
        sys.exit("ROOT is not set in housestyle.conf. See CONFIGURE-ME.md.")
    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        sys.exit(f"ROOT does not exist: {path!r}\nCreate it first.")
    return path


def corpus_path(name):
    path = os.path.join(root(), "corpus", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def language():
    """Loads the word lists for the configured language."""
    code = get("LANG", "de") or "de"
    path = os.path.join(REPO, "lang", f"{code}.json")
    if not os.path.exists(path):
        available = ", ".join(sorted(
            f[:-5] for f in os.listdir(os.path.join(REPO, "lang"))
            if f.endswith(".json")))
        sys.exit(f"No language pack for {code!r}. Available: {available}\n"
                 f"See docs/adding-a-language.md.")
    return read_json(path)
