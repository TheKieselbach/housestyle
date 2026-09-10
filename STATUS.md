# Stand der Extraktion

**10.09.2026, angefangen.** Öffentliche Fassung von `efficas-stimme`.
Arbeitsname `voiceprint` — **Name ist Jonas' Entscheidung**, das Verzeichnis
lässt sich mit einem `git mv` umbenennen.

**Nichts hiervon ist veröffentlicht.** Kein Remote, kein Push, kein GitHub.

## Fertig

- `LICENSE` — Apache-2.0 im Original geholt, `NOTICE`
- `.gitignore` — Korpus kann nicht versehentlich ins Repo
- `voiceprint.conf.example` — die komplette „Konfiguriermich"-Fläche
- `lang/de.json`, `lang/en.json` — **die eigentliche Verallgemeinerung:**
  Stoppwörter, Marker, Partikel, Gradwörter, Bewertungswörter, Anrede- und
  Grußmuster raus aus dem Code, rein in Sprachpakete. Die Methode ist
  sprachunabhängig, die Wortlisten waren es nie.
- `scripts/config.py` — gemeinsamer Konfigurationslader
- `scripts/measure.py` — Portierung von `kennzahlen.py`, sprachpaketgesteuert
- `scripts/collect_transcripts.py` — Portierung von `korpus_transkripte.py`.
  **Der beste Einstieg für Fremde:** wer Claude Code nutzt, hat das Material
  schon, ohne Export aus irgendwas.
- `scripts/collect_mail.py` — Portierung von `korpus_mail.py`, **entpersonalisiert**
  (Signaturanker und interne Domänen kommen jetzt aus der Konfiguration) und
  um **mbox** erweitert, damit es ohne Graph funktioniert.

## Offen

- `scripts/samples.py` (aus `proben.py`) — Schwärzung aus Konfiguration
- `scripts/outlier_words.py` (aus `fremdwort.py`) — Stammbildung aus Sprachpaket
- `scripts/collect_web.py` (aus `korpus_blog.py`) — ohne efficas-Bezug
- `skills/profile/SKILL.md`, `skills/draft/SKILL.md` — englische Fassungen
- `.claude-plugin/plugin.json`
- `README.md` mit der Governance-Begründung — **das ist der eigentliche Wert**
- `CONFIGURE-ME.md`, `docs/why-measure-locally.md`, `docs/adding-a-language.md`
- Prüflauf gegen einen echten Korpus
- Sicherheitsdurchgang über das Ergebnis

## Der Befund, der den Sicherheitsdurchgang rechtfertigt

Im Original stehen in `korpus_mail.py` **hart verdrahtet**: Name,
Mailadresse, Firmenname, Straße, Postleitzahl, eine Werbezeile und drei
interne Domänenkürzel in `INTERN`. Alles davon ist jetzt Konfiguration.
Vor einer Veröffentlichung muss dasselbe für jede weitere Datei geprüft
werden.
