#!/usr/bin/env python3
"""Erzeugt die Navigation in zensical.toml aus der Ordnerstruktur unter docs/.

Reihenfolge der Bereiche steht in REIHENFOLGE, innerhalb eines Bereichs gilt die Reihenfolge
der Links auf dessen index.md. Seitentitel kommen aus der ersten Überschrift.
Aufruf ohne Argument schreibt zensical.toml, mit --check prüft die CI, ob sie aktuell ist.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TOML = ROOT / "zensical.toml"
REIHENFOLGE = {
    "benutzer": ["grundlagen", "audit", "basis", "einstellungen", "api", "mcp"],
    "technik": ["api", "mcp", "datenmodell", "audit", "erweiterung", "betrieb"],
}
OBEN = [("Start", "index.md"), ("Benutzer", "benutzer"), ("Technik", "technik"), ("Versionen", "versionen.md")]


def titel(datei):
    for zeile in datei.read_text(encoding="utf-8").splitlines():
        if zeile.startswith("# "):
            return zeile[2:].strip()
    return datei.stem


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def ordner(pfad, tiefe):
    ein = "  " * tiefe
    zeilen = [f"{ein}{q(pfad + '/index.md')},"]
    # Reihenfolge wie die Links auf der Übersichtsseite, übrige Seiten alphabetisch dahinter
    verlinkt = re.findall(r"\]\(([a-z0-9-]+\.md)\)", (DOCS / pfad / "index.md").read_text(encoding="utf-8"))
    rang = {n: i for i, n in reversed(list(enumerate(verlinkt)))}
    dateien = sorted((DOCS / pfad).glob("*.md"), key=lambda d: (rang.get(d.name, len(rang)), d.name))
    for datei in dateien:
        if datei.name != "index.md":
            zeilen.append(f"{ein}{{ {q(titel(datei))} = {q(pfad + '/' + datei.name)} }},")
    return zeilen


def nav():
    zeilen = ["nav = ["]
    for name, ziel in OBEN:
        if ziel.endswith(".md"):
            zeilen.append(f"  {{ {q(name)} = {q(ziel)} }},")
            continue
        zeilen.append(f"  {{ {q(name)} = [")
        zeilen.append(f"    {q(ziel + '/index.md')},")
        for teil in REIHENFOLGE[ziel]:
            zeilen.append(f"    {{ {q(titel(DOCS / ziel / teil / 'index.md'))} = [")
            zeilen += ordner(f"{ziel}/{teil}", 3)
            zeilen.append("    ] },")
        zeilen.append("  ] },")
    zeilen.append("]")
    return "\n".join(zeilen)


def main():
    text = TOML.read_text(encoding="utf-8")
    neu = re.sub(r"(# NAV-START.*?\n).*?(\n# NAV-ENDE)", lambda m: m.group(1) + nav() + m.group(2), text, flags=re.S)
    fehlend = [d for d in ("benutzer", "technik") for t in (DOCS / d).iterdir()
               if t.is_dir() and t.name not in REIHENFOLGE[d]]
    if fehlend:
        sys.exit(f"Ordner ohne Platz in REIHENFOLGE: {fehlend}")
    if "--check" in sys.argv:
        if neu != text:
            sys.exit("Navigation in zensical.toml ist veraltet. Bitte python scripts/gen_nav.py ausführen.")
        print("OK: Navigation aktuell.")
    else:
        TOML.write_text(neu, encoding="utf-8")
        print("Navigation geschrieben.")


if __name__ == "__main__":
    main()
