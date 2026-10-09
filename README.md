# docs.atrion.ch

Öffentliche Dokumentation von Atrion, der offenen Liegenschaftsverwaltung auf Odoo 20. Gebaut mit [Zensical](https://zensical.org), Inhalte in Markdown, veröffentlicht über GitHub Pages.

## Lokal starten

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
zensical serve          # http://localhost:8000
```

## Aufbau

| Pfad | Inhalt |
|---|---|
| `docs/benutzer/grundlagen/` | Grundfunktionen, die es in Atrion heute gibt (Anmelden, Passwort, Suchen, Exportieren, Dialog …), je eine Seite mit Screenshot pro Schritt |
| `docs/technik/` | Technische Dokumentation (folgt mit den ersten Atrion-Modulen) |
| `docs/assets/screenshots/<slug>/` | Screenshots je Seite, erzeugt von `scripts/capture_screenshots.py` |
| `docs/register.yaml` | Register: Funktion → Seite, Kontexthilfe-Sichten, Screenshot-Ordner, Vimeo-ID |
| `scripts/capture_screenshots.py` | Nimmt Screenshots und Videos aus einer laufenden Atrion-Instanz auf |
| `scripts/check_docs.py` | Abdeckungsprüfung (CI-Gate) |
| `scripts/gen_nav.py` | Erzeugt die Navigation in `zensical.toml` |

Dokumentiert wird nur, was in Atrion schon bedienbar ist. Neue Bereiche kommen mit den Atrion-Apps dazu.

## Neue Seite anlegen

1. In `scripts/capture_screenshots.py` eine Funktion mit `@seite` ergänzen, die die Schritte ausführt und je Schritt `a.bild(...)` aufruft.
2. Markdown-Datei unter `docs/benutzer/grundlagen/<slug>.md` anlegen: Titel, ein Satz Zweck, Abschnitte **Wer darf das**, **Schritte** (nummeriert, unter jedem Schritt der Screenshot) und **Hinweise**. Menünamen so schreiben, wie sie auf dem Screenshot stehen.
3. Eintrag in `docs/register.yaml` ergänzen und die Seite auf `index.md` des Bereichs verlinken (bestimmt die Reihenfolge im Menü).
4. `python scripts/gen_nav.py` ausführen.
5. `python scripts/check_docs.py && zensical build --strict` muss grün sein.

## Screenshots neu erzeugen

Die Bilder werden öffentlich. Deshalb nie gegen die produktive Instanz mit echten Personen aufnehmen, sondern gegen eine eigene Datenbank mit fiktiven Demodaten (zum Beispiel `odoo_atrion_docs` auf Port 8070, gleiche Module wie die Instanz).

Demodatenbank einrichten (im Odoo-Checkout, mit einer eigenen `odoo.conf` für Datenbank und Port):

```bash
odoo-bin -c docs-odoo.conf -d odoo_atrion_docs -i <Module der Instanz> --stop-after-init
ATRION_PASSWORD=… odoo-bin shell -c docs-odoo.conf -d odoo_atrion_docs --no-http < ../docs.atrion/scripts/seed_docs_db.py
```

`scripts/seed_docs_db.py` legt die Firma **Project Atrion AG** an, meldet die Aufnahmen als **Max Mustermann** an und zeigt **Jutta Musterfrau** als Beispielperson, dazu einige weitere fiktive Personen mit `@example.ch`-Adressen, einen Kanal und eine Direktnachricht. Das Passwort kommt nur aus `ATRION_PASSWORD`.

```bash
pip install playwright pyyaml          # Chromium: playwright install chromium
export ATRION_URL=http://localhost:8070 ATRION_LOGIN=admin ATRION_PASSWORD=…
python scripts/capture_screenshots.py              # alle Seiten
python scripts/capture_screenshots.py filtern      # nur eine Seite
```

Viewport 1440 × 900, Fullpage, de_CH, helles Design. Passwortfelder, QR-Codes und Geheimnisse werden maskiert. Zugangsdaten nur über Umgebungsvariablen, nie ins Repo.

## Videos

Videos liegen nicht im Repo und werden nicht auf der Website eingebettet, bis sie auf Vimeo sind.

```bash
pip install imageio-ffmpeg             # falls kein ffmpeg installiert ist
python scripts/capture_screenshots.py --videos ../docs-videos
```

Das Skript nimmt für jede Seite mit mindestens drei Schritten den Ablauf auf (1440 × 900, ruhiges Tempo), wandelt ihn in MP4 (H.264, yuv420p, faststart) um und schreibt `videos.csv` (slug, Titel, Seite, Dauer, Datei) als Upload-Liste.

Nach dem Upload die Vimeo-ID in `docs/register.yaml` bei `vimeo:` eintragen und auf der Seite nach den Schritten einfügen:

```html
<div class="atrion-video"><iframe src="https://player.vimeo.com/video/<ID>?dnt=1&title=0&byline=0&portrait=0" title="<Titel der Seite>" allow="fullscreen; picture-in-picture" loading="lazy"></iframe></div>
```

`dnt=1` verhindert Tracking-Cookies von Vimeo. Das responsive Format (16:10) liefert die Klasse `atrion-video` in `atrion.css`.

## Schreibregeln

Deutsch (de_CH) ist die Leitsprache, ohne ß. Kurze klare Sätze, Tabellen statt Prosa. Mermaid-Labels in `"…"`.

## CI und Veröffentlichung

Jeder Pull Request prüft Register, Pflichtabschnitte, Screenshots, Links und Navigation und baut die Website im Strict-Modus. Ein Merge auf `main` veröffentlicht automatisch auf GitHub Pages (Einstellung *Pages → Source: GitHub Actions*).

Die CI schlägt fehl, wenn eine Seite im Register fehlt, eine Seite nicht im Register steht, ein Pflichtabschnitt fehlt, eine Benutzerseite keinen Screenshot hat oder ein Link oder Bild ins Leere zeigt.

## Lizenz

Inhalte unter CC BY 4.0, Skripte unter MIT. Siehe [LICENSE](LICENSE).
