#!/usr/bin/env python3
"""Abdeckungsprüfung der Atrion-Dokumentation (CI-Gate).

Prüft:
  R1  Jede Seite im Register existiert als Markdown-Datei.
  R2  Jede Seite unter benutzer/ und technik/ (ausser index.md) steht im Register.
  R3  Jeder Funktionsschlüssel kommt höchstens einmal vor.
  R4  Benutzerseiten haben die Pflichtabschnitte.
  R5  Jeder relative Link und jedes Bild zeigt auf eine vorhandene Datei.
  R6  Jede Benutzerseite hat mindestens einen Screenshot und keinen Abschnitt «Video».
  R7  docs/media.lock.json passt zu den Dateien: jeder Screenshot steht mit seinem Hash drin,
      und die Vimeo-ID stimmt mit dem Register überein.
  R8  Ist im Register eine Vimeo-ID gesetzt, bettet die Seite genau dieses Video ein.
"""
import hashlib
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PFLICHT_BENUTZER = ["## Wer darf das", "## Schritte", "## Hinweise"]
BILD = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
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
            if not BILD.search(text):
                fehler.append(f"R6 Kein Screenshot: docs/{rel}.md")
            if "## Video" in text:
                fehler.append(f"R6 Abschnitt «Video» nicht erlaubt: docs/{rel}.md")
    for ziel in LINK.findall(text):
        if re.match(r"^[a-z]+:", ziel):
            continue
        if not (datei.parent / ziel).resolve().exists():
            fehler.append(f"R5 Link ins Leere: docs/{rel}.md → {ziel}")

# R7/R8: Medien
lock_datei = DOCS / "media.lock.json"
lock = json.loads(lock_datei.read_text(encoding="utf-8")) if lock_datei.exists() else {}
shots = DOCS / "assets" / "screenshots"
for ordner in sorted(p for p in shots.iterdir() if p.is_dir()) if shots.exists() else []:
    eintrag = lock.get(ordner.name)
    if eintrag is None:
        fehler.append(f"R7 Screenshots ohne Eintrag in media.lock.json: {ordner.name}")
        continue
    dateien = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in ordner.glob("*.png")}
    if dateien != eintrag.get("screenshots", {}):
        fehler.append(f"R7 media.lock.json passt nicht zu den Screenshots: {ordner.name} (capture_screenshots.py ausführen)")
for eintrag_reg in register:
    slug = eintrag_reg["seite"].split("/")[-1]
    vid = str(eintrag_reg.get("vimeo") or "")
    if vid != str(lock.get(slug, {}).get("vimeo", {}).get("id", "")):
        fehler.append(f"R7 Vimeo-ID in register.yaml und media.lock.json verschieden: {slug}")
    if vid:
        text = (DOCS / f"{eintrag_reg['seite']}.md").read_text(encoding="utf-8")
        if f"player.vimeo.com/video/{vid}" not in text:
            fehler.append(f"R8 Vimeo-Video {vid} nicht eingebettet: docs/{eintrag_reg['seite']}.md")

if fehler:
    print(f"{len(fehler)} Fehler:")
    for f in fehler:
        print("  " + f)
    sys.exit(1)
print(f"OK: {len(register)} Registereinträge, {len(funktionen)} Funktionen, alle Seiten und Links vorhanden.")
