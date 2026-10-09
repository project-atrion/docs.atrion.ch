#!/usr/bin/env python3
"""Abdeckungsprüfung der Atrion-Dokumentation (CI-Gate).

Prüft:
  R1  Jede Seite im Register existiert als Markdown-Datei.
  R2  Jede Seite unter benutzer/ und technik/ (ausser index.md) steht im Register.
  R3  Jeder Funktionsschlüssel kommt höchstens einmal vor.
  R4  Benutzerseiten haben die Pflichtabschnitte.
  R5  Jeder relative Link zeigt auf eine vorhandene Datei.
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PFLICHT_BENUTZER = ["## Wer darf das", "## Schritte", "## Hinweise und Fehlermeldungen"]
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")

fehler = []
register = yaml.safe_load((DOCS / "register.yaml").read_text(encoding="utf-8")) or []

seiten_im_register = set()
funktionen = set()
for nr, eintrag in enumerate(register, 1):
    seite = eintrag.get("seite")
    if not seite:
        fehler.append(f"R1 Registereintrag {nr} hat keine Seite")
        continue
    seiten_im_register.add(seite)
    if not (DOCS / f"{seite}.md").is_file():
        fehler.append(f"R1 Seite fehlt: docs/{seite}.md ({eintrag.get('funktion') or 'Technik'})")
    funktion = eintrag.get("funktion")
    if funktion:
        if funktion in funktionen:
            fehler.append(f"R3 Funktion doppelt im Register: {funktion}")
        funktionen.add(funktion)

for datei in sorted(DOCS.rglob("*.md")):
    rel = datei.relative_to(DOCS).with_suffix("").as_posix()
    text = datei.read_text(encoding="utf-8")
    if rel.split("/")[0] in ("benutzer", "technik") and datei.name != "index.md":
        if rel not in seiten_im_register:
            fehler.append(f"R2 Seite nicht im Register: docs/{rel}.md")
        if rel.startswith("benutzer/"):
            for kopf in PFLICHT_BENUTZER:
                if kopf not in text:
                    fehler.append(f"R4 Abschnitt «{kopf[3:]}» fehlt: docs/{rel}.md")
    for ziel in LINK.findall(text):
        if re.match(r"^[a-z]+:", ziel):
            continue
        if not (datei.parent / ziel).resolve().exists():
            fehler.append(f"R5 Link ins Leere: docs/{rel}.md → {ziel}")

if fehler:
    print(f"{len(fehler)} Fehler:")
    for f in fehler:
        print("  " + f)
    sys.exit(1)
print(f"OK: {len(register)} Registereinträge, {len(funktionen)} Funktionen, alle Seiten und Links vorhanden.")
