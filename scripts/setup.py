#!/usr/bin/env python3
"""Interactive setup. Creates housestyle.conf and the corpus directories.

Nothing is written until you have seen the full list and confirmed it.

Usage:  python3 scripts/setup.py [--check] [--uninstall]

  --check      report what exists and what is missing, change nothing
  --uninstall  list everything this project created and offer to remove it
"""
import os, sys, shutil, platform, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CONF = os.path.join(REPO, "housestyle.conf")
LANGS = sorted(f[:-5] for f in os.listdir(os.path.join(REPO, "lang")) if f.endswith(".json"))

TRANSCRIPTS = os.path.expanduser("~/.claude/projects")


def ask(prompt, default=""):
    hint = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{hint}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted. Nothing was written.")
        sys.exit(1)
    return answer or default


def ask_many(prompt):
    print(f"{prompt}")
    print("  One per line, empty line to finish.")
    out = []
    while True:
        try:
            line = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted. Nothing was written.")
            sys.exit(1)
        if not line:
            return out
        out.append(line)


# ─────────────────────────────────────────────────────────── requirements
def check_requirements():
    ok = True
    print("System")
    v = sys.version_info
    good = v >= (3, 9)
    print(f"  {'ok  ' if good else 'FAIL'} Python {v.major}.{v.minor}.{v.micro} (3.9 or newer needed)")
    ok &= good
    print(f"  ok   {platform.system()} {platform.release()}")
    print("  ok   no third-party packages required — standard library only")

    print("\nSources")
    if os.path.isdir(TRANSCRIPTS):
        n = len(glob.glob(os.path.join(TRANSCRIPTS, "*", "*.jsonl")))
        print(f"  ok   Claude Code transcripts found: {n} files")
        if n == 0:
            print("       (directory exists but is empty — use this machine for a while first)")
    else:
        print(f"  --   no Claude Code transcripts at {TRANSCRIPTS}")
        print("       Not a problem: mail or published texts work as a corpus too.")
    return ok


# ─────────────────────────────────────────────────────────────── check
def do_check():
    check_requirements()
    print("\nConfiguration")
    if not os.path.exists(CONF):
        print(f"  --   {CONF} does not exist yet — run without --check")
        return
    print(f"  ok   {CONF}")
    sys.path.insert(0, HERE)
    import config
    root = config.get("ROOT")
    print(f"       ROOT = {root or '(not set)'}")
    if root and os.path.isdir(os.path.expanduser(root)):
        root = os.path.expanduser(root)
        for sub in ("corpus", "metrics"):
            path = os.path.join(root, sub)
            if not os.path.isdir(path):
                print(f"       {sub}/ missing")
                continue
            files = glob.glob(os.path.join(path, "*"))
            print(f"       {sub}/ {len(files)} file(s)" if files else f"       {sub}/ exists, empty")
    elif root:
        print("       !!   ROOT does not exist")
    print(f"       LANG = {config.get('LANG') or '(not set)'}")
    for key, why in [("SIGNATURE", "your signature will stay in the mail corpus"),
                     ("REDACT", "no names will be masked in samples")]:
        if not config.get_list(key):
            print(f"       !!   {key} is empty — {why}")


# ───────────────────────────────────────────────────────────── uninstall
def do_uninstall():
    print("This project creates exactly two things outside its own directory:\n")
    created = []
    if os.path.exists(CONF):
        created.append((CONF, "your configuration"))
    root = ""
    if os.path.exists(CONF):
        sys.path.insert(0, HERE)
        import config
        root = os.path.expanduser(config.get("ROOT") or "")
    # The distinction between these two is the whole point of the project,
    # so the uninstaller had better get it right.
    for sub, what in (("corpus", "YOUR TEXTS — the sensitive one"),
                      ("metrics", "measured numbers, no text")):
        if root and os.path.isdir(os.path.join(root, sub)):
            path = os.path.join(root, sub)
            size = sum(os.path.getsize(f) for f in glob.glob(os.path.join(path, "*")) if os.path.isfile(f))
            created.append((path, f"{size // 1024} KB — {what}"))
    if not created:
        print("  Nothing found. Nothing to remove.")
    for path, what in created:
        print(f"  {path}\n      {what}")

    print("\nIt does NOT create anything else. No system files, no services, no")
    print("cron jobs, no shell profile changes, no network configuration, no")
    print("account anywhere. Deleting this repository directory plus the paths")
    print("above removes every trace.\n")

    if not created:
        return
    if ask("Delete the paths listed above? Type DELETE to confirm", "") != "DELETE":
        print("Nothing removed.")
        return
    for path, _ in created:
        shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        print(f"  removed {path}")
    print("\nThe repository directory itself is still here. Delete it by hand.")


# ───────────────────────────────────────────────────────────────── setup
def do_setup():
    print("housestyle setup\n" + "─" * 60)
    if not check_requirements():
        sys.exit("\nRequirements not met. See INSTALL.md.")

    if os.path.exists(CONF):
        print(f"\n{CONF} already exists.")
        if ask("Overwrite it? (y/N)", "n").lower() != "y":
            print("Keeping the existing configuration. Use --check to inspect it.")
            return

    print("\n" + "─" * 60)
    print("Where should the corpus live?\n")
    print("  This holds the full text of what you have written. Put it in your")
    print("  own storage — documents, OneDrive, Nextcloud. NOT inside this")
    print("  repository, and not in a temp directory.")
    default_root = os.path.expanduser("~/Documents/housestyle")
    root = os.path.expanduser(ask("\n  Path", default_root))

    print(f"\n  Language of your writing. Available: {', '.join(LANGS)}")
    lang = ask("  Language", "en" if "en" in LANGS else LANGS[0])
    while lang not in LANGS:
        print(f"  Unknown. Choose one of: {', '.join(LANGS)}")
        lang = ask("  Language", LANGS[0])

    print("\n" + "─" * 60)
    print("Names to mask before any sample text is shown to a model.")
    print("Clients, colleagues, third parties. Not yourself. Skip with an")
    print("empty line — you can add them later.")
    redact = ask_many("")

    print("\n" + "─" * 60)
    print("Signature anchors — only needed if you will collect mail.\n")
    print("  Lines that mark where your automatic signature starts. Open three")
    print("  of your own sent mails and take the first line of the block that")
    print("  appears in all of them.\n")
    print("  This matters: in the reference corpus the signature was 43 percent")
    print("  of all mail text, and its canned sign-off was mistaken for a typed")
    print("  one. Skip now and the collector will warn you later.")
    signature = ask_many("")

    print("\n" + "─" * 60)
    print("Domains that count as internal, comma-separated. Mail to them is")
    print("tagged separately, because most people write very differently")
    print("in-house. Empty is fine.")
    internal = ask("  Domains", "")

    # ── show everything before writing anything ──
    print("\n" + "═" * 60)
    print("About to create:\n")
    print(f"  {CONF}")
    print(f"      your configuration — git-ignored, stays local")
    print(f"  {root}/")
    print(f"      corpus/     your collected texts will go here")
    print(f"      metrics/    the measured numbers")
    print("\nNothing else is created anywhere. No system files, no services,")
    print("no network access, no account.")
    print("═" * 60)
    if ask("\nProceed? (Y/n)", "y").lower() not in ("y", "yes", ""):
        print("Nothing written.")
        return

    os.makedirs(os.path.join(root, "corpus"), exist_ok=True)
    os.makedirs(os.path.join(root, "metrics"), exist_ok=True)
    with open(CONF, "w", encoding="utf-8") as f:
        f.write("# Written by scripts/setup.py. Edit freely.\n")
        f.write("# Documentation: CONFIGURE-ME.md\n\n")
        f.write(f"ROOT={root}\n")
        f.write(f"LANG={lang}\n\n")
        f.write(f"REDACT={','.join(redact)}\n\n")
        f.write("SIGNATURE=\n")
        for s in signature:
            f.write(f"  {s}\n")
        f.write(f"\nINTERNAL={internal}\n\n")
        f.write("BLOCKLIST=\n")

    print(f"\nDone.\n\n  {CONF}\n  {root}/corpus\n  {root}/metrics")
    print("\nNext:\n")
    if os.path.isdir(TRANSCRIPTS):
        print("  python3 scripts/collect_transcripts.py")
        print(f"  python3 scripts/measure.py {root}/corpus/transcripts.jsonl --tag transcripts")
    else:
        print("  Get a corpus first — see docs/getting-your-texts.md")
    print("\n  python3 scripts/setup.py --check    to verify later")


if __name__ == "__main__":
    if "--check" in sys.argv:
        do_check()
    elif "--uninstall" in sys.argv:
        do_uninstall()
    else:
        do_setup()
