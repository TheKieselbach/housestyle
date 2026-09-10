# Install

## Requirements

| | |
|---|---|
| **Python** | 3.9 or newer. `python3 --version` |
| **Packages** | none. Standard library only, deliberately — see below |
| **Disk** | a few MB for the code, plus whatever your corpus weighs |
| **Network** | not required, except `collect_web.py` fetching URLs you pass it |
| **Account** | none, anywhere |

**Why no dependencies.** A tool that handles your sent mail should not pull in
a tree of packages you did not read. Everything here is `re`, `json`,
`statistics`, `mailbox` — all shipped with Python.

### Platforms

- **macOS** — tested. Python 3 is present on modern macOS; `brew install python`
  if not.
- **Linux** — expected to work, same standard library. Untested.
- **Windows** — expected to work. The Python is portable; the shell commands in
  the docs are bash. In PowerShell, `python3` is usually `python`, and paths use
  backslashes. Untested — [reports welcome](../../issues).

## Install

```bash
git clone <this repository>
cd housestyle
python3 scripts/setup.py
```

The setup assistant asks four questions, **shows you the complete list of what
it will create, and writes nothing until you confirm.**

```bash
python3 scripts/setup.py --check      # what exists, what is missing
python3 scripts/setup.py --uninstall  # list and remove everything created
```

## Which AI tool does this work with?

Two layers, and only one of them is tied to a product.

### The measurement — any tool, or none

`scripts/` is plain Python. It reads your texts and writes a style profile.
Nothing in it knows or cares which model you use. The output is a Markdown file
full of numbers and a few sample passages.

Use it with whatever you already have:

| Tool | Where the profile goes |
|---|---|
| **ChatGPT** | Custom Instructions, or a Project's instructions |
| **Claude** (web/app) | Project knowledge, or a Style |
| **Gemini** | Gems / saved info |
| **Cursor, Windsurf, Copilot** | `.cursorrules`, `AGENTS.md`, or the equivalent |
| **A local model** | system prompt |
| **No AI at all** | read it yourself — it is an honest description of how you write |

You paste roughly one page. Your corpus stays where it is.

### The plugin — Claude Code only

`skills/` and `.claude-plugin/` are the [Claude Code](https://claude.com/claude-code)
plugin format. They add convenience: loading the profile automatically before
writing, running the outlier check on a draft, feeding your revisions back into
the corpus.

**This layer is optional.** Delete those two directories and everything above
still works.

One thing does assume Claude Code: `collect_transcripts.py` reads
`~/.claude/projects/`. If you do not use Claude Code, you have no transcripts —
use mail or published texts instead. See
[`docs/getting-your-texts.md`](docs/getting-your-texts.md).

## What gets created

Everything, exhaustively:

| Path | What | Contains |
|---|---|---|
| `voiceprint.conf` | your configuration | paths, names to mask, signature anchors |
| `<ROOT>/corpus/` | collected texts | **your writing, in full — the sensitive one** |
| `<ROOT>/metrics/` | measurements | counts and medians. No text |
| `<ROOT>/style-profile.md` | the profile | numbers plus a few redacted passages |

`<ROOT>` is the path you choose during setup. It is deliberately outside this
repository.

**Nothing else is created.** No system files. No services or daemons. No cron
jobs or scheduled tasks. No changes to your shell profile, PATH, or any
configuration outside this directory. No account anywhere. No telemetry, no
analytics, no crash reporting, no update check.

`/tmp` is touched only by the draft-check snippet in the `draft` skill, which
writes one file you can delete.

## Uninstall

```bash
python3 scripts/setup.py --uninstall
```

It lists every path it created with sizes, marks which one holds your actual
text, and removes them only after you type `DELETE`.

Then delete the repository directory. That is all of it — there is nothing
registered anywhere to clean up.

## Verify it works

```bash
python3 -m unittest discover tests -v
```

No corpus needed; the tests run against fixtures.
