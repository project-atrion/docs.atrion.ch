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
| `docs/benutzer/grundlagen/` | Grundfunktionen aus dem Odoo-Standard (Anmelden, Passwort, Suchen, Exportieren …) |
| `docs/benutzer/<modul>/fNN-<slug>.md` | Eine Seite je Funktion. Module: `audit`, `basis`, `einstellungen`, `api`, `mcp` |
| `docs/technik/<bereich>/<slug>.md` | Bereiche: `api`, `mcp`, `datenmodell`, `audit`, `erweiterung`, `betrieb` |
| `docs/register.yaml` | Register: Funktion → Seite, Kontexthilfe-Sichten, Playwright-Tests für die Medien |
| `docs/versionen.md` | Release `JJJJ.n` und Build `JJJJ.MM.Z`, «Was ist neu» |
| `scripts/check_docs.py` | Abdeckungsprüfung (CI-Gate) |
| `scripts/gen_nav.py` | Erzeugt die Navigation in `zensical.toml` |

## Neue Seite anlegen

1. Markdown-Datei am passenden Pfad anlegen. Benutzerseiten haben immer die Abschnitte Zweck · Wer darf das · Voraussetzungen · Schritte · Video (ab drei Schritten) · Hinweise und Fehlermeldungen · Verwandte Seiten.
2. Eintrag in `docs/register.yaml` ergänzen.
3. Seite auf der `index.md` des Bereichs verlinken (bestimmt die Reihenfolge im Menü).
4. `python scripts/gen_nav.py` ausführen.
5. `python scripts/check_docs.py && zensical build --strict` muss grün sein.

## Schreibregeln

Deutsch (de_CH) ist die Leitsprache, ohne ß. Kurze klare Sätze, Tabellen statt Prosa. Mermaid-Labels in `"…"`.

## CI und Veröffentlichung

Jeder Pull Request prüft Register, Pflichtabschnitte, Links und Navigation und baut die Website im Strict-Modus. Ein Merge auf `main` veröffentlicht automatisch auf GitHub Pages (Einstellung *Pages → Source: GitHub Actions*).

Die CI schlägt fehl, wenn eine Seite im Register fehlt, eine Seite nicht im Register steht, ein Pflichtabschnitt fehlt oder ein Link ins Leere zeigt. Sobald die Atrion-Module gebaut sind, kommt der Abgleich mit Funktionen, REST-Endpunkten und MCP-Werkzeugen aus dem Odoo-Repository dazu, ebenso die Medien aus den Playwright-Tests.

## Lizenz

Inhalte unter CC BY 4.0, Skripte unter MIT. Siehe [LICENSE](LICENSE).
