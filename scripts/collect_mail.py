#!/usr/bin/env python3
"""Turns sent mail into a style corpus.

Usage:  collect_mail.py <file> [--format graph|mbox|auto]

Two input formats:

  mbox    A standard mailbox export. Every mail client can produce one, and
          it needs no API access. Use your "Sent" folder.
  graph   A Microsoft Graph dump of a sent-items folder (JSON with a "value"
          array). Useful if you already work against Graph.

Only what *you* wrote survives. Quoted replies, signature blocks and legal
footers are removed; the greeting and sign-off stay, because those are style.

Two things that are easy to get wrong and cost a full run each:

  1. Mail clients emit \\r\\n. Every `$` anchor in a line-based regex fails on
     the leftover \\r. Normalise first.
  2. In the reference corpus the automatic signature accounted for **43
     percent** of all mail text, and its canned sign-off looked like a typed
     one. Configure SIGNATURE anchors, or you will measure your business
     card instead of your language.
"""
import json, sys, re, os, html, hashlib, collections, mailbox, email

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def html_to_text(raw):
    t = re.sub(r"(?is)<(script|style|head).*?</\1>", " ", raw)
    t = re.sub(r"(?i)<br\s*/?>", "\n", t)
    t = re.sub(r"(?i)</(p|div|tr|li|h[1-6]|blockquote)>", "\n", t)
    t = re.sub(r"(?i)<li[^>]*>", "- ", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t).replace(" ", " ").replace("​", "")
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip()


# Everything from the first hit onward is the other side's text.
QUOTE = re.compile("|".join([
    r"^\s*-{2,}\s*(Urspr(ue|ü)ngliche Nachricht|Original Message|Forwarded message|Weitergeleitete Nachricht)",
    r"^\s*(Von|From):\s*.{0,120}$",
    r"^\s*(Gesendet|Sent):\s",
    r"^\s*Am\s+\d{1,2}\.\d{1,2}\.\d{2,4}.{0,80}(schrieb|um)\b",
    r"^\s*On\s+.{5,60}\bwrote:",
    r"^\s*>",
    r"^\s*_{10,}\s*$",
]), re.M | re.I)

# Standing boilerplate that is not your prose.
BOILERPLATE = re.compile(
    r"(?im)^\s*(Sent from my \w+|Get Outlook for \w+|Gesendet von (meinem|meiner|Outlook|Mail)\b.*|"
    r"Diese (E-?Mail|Nachricht) (enth(ae|ä)lt|ist)\b|This e?-?mail\b|"
    r"Sitz der Gesellschaft|Amtsgericht\b|USt-?IdNr|Steuernummer|VAT ID|"
    r"Gesch(ae|ä)ftsf(ue|ü)hrer|Handelsregister|HRB \d|Company No|Registered office|"
    r"Tel\.?:|Mobil:|Mobile:|Fax:|www\.|https?://|\+\d{1,3}[\d /-]{6,}).*$")


def build_signature_regex():
    """Signature anchors come from your configuration, never from the code.

    Anything hardcoded here would be somebody else's name and address."""
    anchors = config.get_list("SIGNATURE")
    anchors.append(r"--[ \t]*$")          # the conventional separator
    return re.compile(r"(?im)^[ \t]*(" + "|".join(anchors) + r").*$")


def own_text(text, signature_re, signoff_re):
    """Keeps only what you wrote for this one mail."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    m = QUOTE.search(text)
    if m:
        text = text[:m.start()]

    # Cut the signature block from its first anchor — including the lines
    # just above it, in case the canned sign-off sits there.
    a = signature_re.search(text)
    if a:
        before = text[:a.start()].split("\n")
        while before and (not before[-1].strip() or signoff_re.match(before[-1])
                          or len(before[-1].strip().split()) <= 2 and before[-1].strip().istitle()):
            before.pop()
        text = "\n".join(before)

    # Keep the typed sign-off, drop what follows it (the name line).
    last = None
    for last in signoff_re.finditer(text):
        pass
    if last:
        rest = [l for l in text[last.end():].split("\n") if l.strip()][:1]
        text = text[:last.end()] + ("\n" + rest[0][:40] if rest else "")

    text = re.sub(r"<(mailto:|https?://)[^>]*>", "", text)
    text = BOILERPLATE.sub("", text)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()


def read_graph(path):
    raw = json.load(open(path, encoding="utf-8"))
    items = raw.get("value", raw if isinstance(raw, list) else [])
    for m in items:
        body = m.get("body") or {}
        text = body.get("content", "") or ""
        if (body.get("contentType") or "").lower() == "html":
            text = html_to_text(text)
        recipients = [(e.get("emailAddress") or {}).get("address", "")
                      for e in (m.get("toRecipients") or [])]
        yield text, m.get("subject", "") or "", m.get("sentDateTime", "") or "", recipients


def read_mbox(path):
    for msg in mailbox.mbox(path):
        text, is_html = "", False
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    text = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", "ignore")
                    is_html = False
                    break
                if ctype == "text/html" and not text:
                    text = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", "ignore")
                    is_html = True
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                text = payload.decode(msg.get_content_charset() or "utf-8", "ignore")
                is_html = msg.get_content_type() == "text/html"
        if is_html:
            text = html_to_text(text)
        recipients = [a for _, a in email.utils.getaddresses([msg.get("To", "")]) if a]
        yield text, msg.get("Subject", "") or "", msg.get("Date", "") or "", recipients


def main():
    argv = sys.argv[1:]
    fmt = "auto"
    if "--format" in argv:
        i = argv.index("--format"); fmt = argv[i + 1]; del argv[i:i + 2]
    if not argv:
        sys.exit(__doc__)
    path = argv[0]
    if fmt == "auto":
        fmt = "graph" if path.lower().endswith(".json") else "mbox"

    lang = config.language()
    signature_re = build_signature_regex()
    signoff_re = re.compile(lang["signoff"], re.I | re.M)
    internal = [d.lower() for d in config.get_list("INTERNAL")]
    target = config.corpus_path("mail.jsonl")

    reader = read_graph if fmt == "graph" else read_mbox
    seen, out = set(), []
    dropped = collections.Counter()
    total = 0

    for text, subject, when, recipients in reader(path):
        total += 1
        text = own_text(text, signature_re, signoff_re)
        # Deliberately low floor: "Done — what a mess." is 20 characters and
        # a strong style signal. Three words is enough to sieve out empty
        # forwards and bare confirmations.
        if len(text) < 15 or len(text.split()) < 3:
            dropped["too short or forward only"] += 1
            continue
        key = hashlib.md5(re.sub(r"\s+", "", text).encode()).hexdigest()
        if key in seen:
            dropped["duplicate"] += 1
            continue
        seen.add(key)

        domains = {a.split("@")[-1].lower() for a in recipients if "@" in a}
        kind = ("internal" if domains and internal
                and all(any(i in d for i in internal) for d in domains) else "external")
        out.append({
            "source": "mail",
            "kind": kind,
            "reply": bool(re.match(r"\s*(AW|RE|WG|FW|FWD)\s*:", subject, re.I)),
            "domains": sorted(domains),
            "time": when,
            "characters": len(text),
            "text": text,
        })

    out.sort(key=lambda s: s["time"])
    with open(target, "w", encoding="utf-8") as f:
        for s in out:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    chars = sum(s["characters"] for s in out)
    print(f"Input: {total} mails ({fmt})")
    for reason, n in dropped.most_common():
        print(f"  dropped, {reason}: {n}")
    print(f"Corpus: {len(out)} mails, {chars:,} characters (~{chars // 6:,} words)")
    print(f"  external {sum(1 for s in out if s['kind']=='external')}, "
          f"internal {sum(1 for s in out if s['kind']=='internal')}, "
          f"replies {sum(1 for s in out if s['reply'])}")
    if not config.get_list("SIGNATURE"):
        print("\n!! SIGNATURE is empty in voiceprint.conf.")
        print("   Your signature block is almost certainly still in the corpus.")
        print("   In the reference corpus that was 43 percent of all text.")
    print(f"-> {target}")


if __name__ == "__main__":
    main()
