#!/usr/bin/env python3
"""Single entry point, so a pip install gets `housestyle <command>` instead of
`python3 scripts/<something>.py`.

A git checkout can use either form — the scripts stay directly runnable.
"""
import sys

COMMANDS = {
    "setup":      ("setup",               "interactive setup, --check, --uninstall"),
    "transcripts": ("collect_transcripts", "collect your Claude Code transcripts"),
    "mail":       ("collect_mail",        "collect sent mail (mbox or Microsoft Graph)"),
    "web":        ("collect_web",         "collect your published pages"),
    "measure":    ("measure",             "measure a corpus and write the metrics"),
    "samples":    ("samples",             "pull a few short redacted passages"),
    "outliers":   ("outlier_words",       "flag words you do not actually use"),
}


def _version():
    try:
        from . import __version__
        return __version__
    except ImportError:
        import re, os
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "__init__.py"), encoding="utf-8") as f:
            m = re.search(r'__version__ = "([^"]+)"', f.read())
        return m.group(1) if m else "unknown"


def usage(code=0):
    print("housestyle — measure your own writing voice locally\n")
    print("Usage: housestyle <command> [options]\n")
    width = max(len(c) for c in COMMANDS)
    for name, (_, description) in COMMANDS.items():
        print(f"  {name:<{width}}  {description}")
    print("\nStart with:  housestyle setup")
    print("Then:        housestyle transcripts && housestyle measure <corpus.jsonl>")
    sys.exit(code)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        usage()
    if argv[0] in ("-V", "--version"):
        print(_version())
        return
    command = argv.pop(0)
    if command not in COMMANDS:
        print(f"Unknown command: {command}\n", file=sys.stderr)
        usage(2)

    module_name = COMMANDS[command][0]
    try:                                   # installed as a package
        module = __import__(f"{__package__}.{module_name}", fromlist=["main"])
    except (ImportError, ValueError):      # plain checkout
        import importlib, os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        module = importlib.import_module(module_name)

    # Each module documents itself in its docstring. Handling --help here
    # means every subcommand answers it, without seven copies of the check.
    if any(a in ("-h", "--help") for a in argv):
        print((module.__doc__ or "No documentation.").strip())
        return

    sys.argv = [f"housestyle {command}"] + argv
    module.main()


if __name__ == "__main__":
    main()
