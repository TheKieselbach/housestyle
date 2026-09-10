# Configure me

Everything specific to *you* lives in one file. Nothing personal is in the
code — that is deliberate, and it is what makes this repository publishable.

```bash
cp voiceprint.conf.example voiceprint.conf
```

`voiceprint.conf` is git-ignored. Fill in these keys.

## ROOT — required

Where the corpus and the finished profile live.

**Put this outside this repository.** The corpus holds the full text of what
you have written. That belongs in your own storage, not in version control.
A folder in your documents, your OneDrive, your Nextcloud — anywhere you
already keep business material.

```
ROOT=/Users/you/Documents/voice
```

The script creates `corpus/` and `metrics/` underneath. No trailing slash.

## LANG — required

Selects the word lists under `lang/`. Shipped: `de`, `en`.

```
LANG=en
```

## SIGNATURE — strongly recommended if you collect mail

Regular expressions marking where your automatic signature starts.
Everything from the first match onward is dropped.

Skip this and you will measure your business card. In the reference corpus
the signature was **43 percent of all mail text**, and its canned sign-off
was mistaken for a typed one.

Indent one expression per line:

```
SIGNATURE=
  Kind regards from Hamburg
  Jane Doe[ \t]*[-(]
  Mail:[ \t]*jane\.doe
  Example Consulting Ltd|Main Street 1|12345 Springfield
  Book a slot here
```

Look at three or four of your own sent mails and take the first line of the
block that appears in all of them.

## REDACT — recommended

Names replaced with `[name]` before any sample text is shown to a model.
Clients, colleagues, third parties. You do not need to list yourself.

```
REDACT=Acme Corp,Jane Roe,Northwind
```

## INTERNAL — optional

Domains that count as internal. Mail to them is tagged `internal`,
everything else `external`. Most people write very differently in the two,
and separating them makes the profile sharper.

```
INTERNAL=yourcompany.com,yourgroup.local
```

## BLOCKLIST — grows over time

Words a model keeps proposing that you know are not yours. Start empty. Every
time you strike a word out of a draft because it is not how you talk, add it.

```
BLOCKLIST=leverage,robust,seamless
```

`outlier_words.py` flags these explicitly, separately from statistical
suspects.
