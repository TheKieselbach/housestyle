# Getting your texts

You need a corpus of **your own writing**. This page covers how to get one out
of the places it usually lives.

> **Sent mail, never the inbox.** Your inbox is other people's writing. Every
> route below points at the *Sent* folder for that reason. Getting this wrong
> produces a profile of your correspondents.

| Source | Effort | Notes |
|---|---|---|
| Claude Code transcripts | none | already on disk |
| Gmail / Google Workspace | 10 min + wait | official export, mbox directly |
| Microsoft 365 / Outlook | 20 min | no native mbox — via Thunderbird or Graph |
| Apple Mail | 2 min | built in |
| Any IMAP provider | 20 min | Thunderbird, works for anything |
| Your own website | 1 min | `collect_web.py` |

---

## Claude Code transcripts

Nothing to export.

```bash
python3 scripts/collect_transcripts.py
```

Reads `~/.claude/projects/`, keeps only what you typed or dictated, and drops
tool output, pasted files and system messages. Usually the largest and
cleanest corpus available, and dictated passages are the most valuable
material there is — they show how you actually talk.

---

## Gmail and Google Workspace

Google exports mbox natively.

1. Go to **takeout.google.com**, signed in as the right account.
2. **Deselect all**, then scroll to **Mail** and check it.
3. Click **All Mail data included** and **select only the `Sent` label.**
   This is the important step — without it you export everything you ever
   received.
4. Confirm the format is **MBOX** under *Multiple formats*.
5. Next step → delivery by download link → **Export once** → create export.
6. Wait. Minutes for a small mailbox, hours for a large one. You get a mail
   when it is ready.
7. Unzip. The mbox files are under `Takeout/Mail/`.

```bash
python3 scripts/collect_mail.py Takeout/Mail/Sent.mbox
```

---

## Microsoft 365, Outlook.com, Exchange

Microsoft has no mbox export. Two routes.

### Via Thunderbird — no API access needed

1. Install [Thunderbird](https://www.thunderbird.net/) and add your account.
   **Choose IMAP, not POP**, so the server folders mirror properly.
2. Open the **Sent** folder and let it finish downloading. Large mailboxes take
   a while; the export only contains what has synced.
3. Menu → **Add-ons and Themes** → search **ImportExportTools NG** → add.
4. Right-click the *Sent* folder → **ImportExportTools NG** → **Export folder**.
5. Point the collector at the resulting `.mbox`.

### Via Microsoft Graph — if you already work against it

Request the sent-items folder with `subject`, `sentDateTime`, `toRecipients`
and `body`, paginated, and save the JSON.

```bash
python3 scripts/collect_mail.py sent-dump.json --format graph
```

Request it **large enough that your tooling writes it to a file** rather than
into a conversation. At several hundred mails that is the difference between
keeping the text local and not.

---

## Apple Mail

Select the **Sent** mailbox → menu **Mailbox** → **Export Mailbox…** → choose a
folder. You get an `.mbox` package. Point the collector at the `mbox` file
inside it.

---

## Any other provider — GMX, web.de, Posteo, Fastmail, mailbox.org, self-hosted

The Thunderbird route above works for **anything that speaks IMAP**, which is
effectively every mail provider. Add the account, wait for *Sent* to sync,
export with ImportExportTools NG.

If your provider offers a direct export, prefer it — fewer steps, and nothing
has to be downloaded twice.

---

## Your own published writing

```bash
python3 scripts/collect_web.py https://example.com/post-1 https://example.com/post-2
```

Add `--ai-drafted` if a model wrote the first draft and you revised it. They
are then tagged and excluded from the outlier comparison base — otherwise that
base contains exactly the vocabulary the check exists to find.

**Only collect from sources you are allowed to collect from.** Your own site,
your own exports. Several platforms forbid automated reading of their pages in
their terms of use; this project deliberately provides no way to do that and
will not accept contributions that add one.

---

## After the export

**Delete the export file once the collector has run.** It is a complete copy of
your correspondence sitting in your downloads folder, and it is no longer
needed — the collector has already stripped quotes, signatures and boilerplate
and written the result under your configured root.

```bash
rm ~/Downloads/Sent.mbox
```

Then check what actually landed in the corpus:

```bash
python3 -c "
import json,collections,sys
c=collections.Counter()
for l in open(sys.argv[1],encoding='utf-8'):
    for z in json.loads(l)['text'].split(chr(10)):
        if z.strip(): c[z.strip()[:45]]+=1
for z,n in c.most_common(8): print(f'{n:4}x {z}')
" <ROOT>/corpus/mail.jsonl
```

A line appearing fifty times is your signature, not your style. Add it to
`SIGNATURE` in `voiceprint.conf` and run the collector again.
