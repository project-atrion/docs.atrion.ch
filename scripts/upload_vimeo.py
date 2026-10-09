#!/usr/bin/env python3
"""Lädt geänderte Doku-Videos über die Vimeo REST-API hoch und bettet sie auf den Seiten ein.

Aufruf:
    VIMEO_TOKEN=… python scripts/upload_vimeo.py ../docs-videos [--ordner "Atrion Dokumentation"] [--all]

Liest videos.csv (aus capture_screenshots.py --videos) und vergleicht jede Datei mit
docs/media.lock.json. Hochgeladen wird nur, was neu ist oder sich geändert hat (--all erzwingt
alles). Ein bestehendes Video wird als neue Version unter derselben Vimeo-ID ersetzt, eine neue
Funktion bekommt ein neues Video. Videos zu entfernten Funktionen werden nur gemeldet.

Datenschutz: auf vimeo.com verborgen, Einbettung nur auf docs.atrion.ch; erlaubt der Vimeo-Plan
das nicht, fällt das Skript auf «nicht gelistet» zurück. Danach stehen ID und Datei-Hash in
media.lock.json, die ID in docs/register.yaml, und die Seite bekommt die Einbettung.

Der Token (Personal Access Token von developer.vimeo.com/apps) braucht die Scopes
public, private, create, edit, upload und video_files. Er kommt nur aus VIMEO_TOKEN.
"""
import csv
import hashlib
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTER = ROOT / "docs" / "register.yaml"
LOCK = ROOT / "docs" / "media.lock.json"
API = "https://api.vimeo.com"
DOMAIN = "docs.atrion.ch"
TOKEN = os.environ["VIMEO_TOKEN"]


def anfrage(methode, url, daten=None, kopf=None, roh=None, fehler_ok=False):
    h = {"Authorization": f"bearer {TOKEN}", "Accept": "application/vnd.vimeo.*+json;version=3.4"}
    body = roh
    if daten is not None:
        body = json.dumps(daten).encode()
        h["Content-Type"] = "application/json"
    h.update(kopf or {})
    req = urllib.request.Request(url if url.startswith("http") else API + url, data=body, method=methode, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            text = r.read()
            return r.status, dict(r.headers), (json.loads(text) if text and text[:1] in b"{[" else None)
    except urllib.error.HTTPError as e:
        if fehler_ok:
            return e.code, {}, None
        sys.exit(f"Vimeo {methode} {url}: HTTP {e.code} {e.read()[:400].decode(errors='replace')}")


def id_eintragen(slug, vid):
    text, neu, aktuell = REGISTER.read_text(encoding="utf-8").splitlines(), [], None
    for zeile in text:
        m = re.match(r"  seite: benutzer/[^/]+/(\S+)", zeile)
        if m:
            aktuell = m.group(1)
        if aktuell == slug and zeile.startswith("  vimeo:"):
            zeile = f'  vimeo: "{vid}"'
        neu.append(zeile)
    REGISTER.write_text("\n".join(neu) + "\n", encoding="utf-8")


def tus(upload_link, datei):
    groesse, offset, block = datei.stat().st_size, 0, 32 * 1024 * 1024
    with open(datei, "rb") as f:
        while offset < groesse:
            f.seek(offset)
            stueck = f.read(block)
            _, h, _ = anfrage("PATCH", upload_link, roh=stueck, kopf={
                "Tus-Resumable": "1.0.0", "Upload-Offset": str(offset),
                "Content-Type": "application/offset+octet-stream"})
            offset = int({k.lower(): v for k, v in h.items()}["upload-offset"])


def ordner_uri(name):
    if not name:
        return None
    _, _, d = anfrage("GET", "/me/projects?per_page=100")
    for p in d.get("data", []):
        if p["name"] == name:
            return p["uri"]
    _, _, p = anfrage("POST", "/me/projects", {"name": name})
    return p["uri"]


def einbetten(slug, vid, titel):
    """Video nach den Schritten auf der Seite einbetten (ersetzt eine frühere Einbettung)."""
    seite = next((ROOT / "docs" / "benutzer").glob(f"*/{slug}.md"))
    text = re.sub(r"<!-- video -->.*?<!-- /video -->\n*", "", seite.read_text(encoding="utf-8"), flags=re.S)
    block = (f'<!-- video -->\n<div class="atrion-video"><iframe src="https://player.vimeo.com/video/{vid}'
             f'?dnt=1&title=0&byline=0&portrait=0" title="Video: {titel}" allow="fullscreen; picture-in-picture" '
             f'loading="lazy"></iframe></div>\n<!-- /video -->\n\n')
    text = text.replace("## Hinweise", block + "## Hinweise", 1)
    seite.write_text(text, encoding="utf-8")


def main():
    args = sys.argv[1:]
    alle = "--all" in args
    quelle = pathlib.Path(args[0]).expanduser().resolve()
    ordner = ordner_uri(args[args.index("--ordner") + 1]) if "--ordner" in args else None
    lock = json.loads(LOCK.read_text(encoding="utf-8")) if LOCK.exists() else {}
    status = {}
    zeilen = list(csv.DictReader(open(quelle / "videos.csv", encoding="utf-8")))
    for zeile in zeilen:
        slug, datei = zeile["slug"], quelle / zeile["datei"]
        eintrag = lock.setdefault(slug, {})
        hash_ = hashlib.sha256(datei.read_bytes()).hexdigest()
        vimeo = eintrag.get("vimeo", {})
        if not alle and vimeo.get("sha256") == hash_:
            status[slug] = "unverändert"
            continue
        upload = {"approach": "tus", "size": str(datei.stat().st_size)}
        if vimeo.get("id"):
            print(f"{slug}: neue Version für {vimeo['id']}")
            _, _, v = anfrage("POST", f"/videos/{vimeo['id']}/versions", {"file_name": datei.name, "upload": upload})
            link, vid = v["upload"]["upload_link"], vimeo["id"]
            status[slug] = "geändert"
        else:
            print(f"{slug}: neues Video")
            _, _, v = anfrage("POST", "/me/videos", {
                "upload": upload,
                "name": zeile["titel"],
                "description": f"Anleitung auf {zeile['seite']}",
                "privacy": {"view": "disable", "embed": "whitelist", "download": False, "comments": "nobody"},
                "embed": {"title": {"name": "hide", "owner": "hide", "portrait": "hide"}},
            }, fehler_ok=True)
            if v is None:  # Plan ohne «verborgen»: nicht gelistet
                _, _, v = anfrage("POST", "/me/videos", {
                    "upload": upload, "name": zeile["titel"],
                    "description": f"Anleitung auf {zeile['seite']}",
                    "privacy": {"view": "unlisted", "embed": "whitelist", "download": False, "comments": "nobody"}})
            link, vid = v["upload"]["upload_link"], v["uri"].rsplit("/", 1)[-1]
            status[slug] = "neu"
        tus(link, datei)
        anfrage("PUT", f"/videos/{vid}/privacy/domains/{DOMAIN}")
        if ordner:
            anfrage("PUT", f"{ordner}/videos/{vid}")
        eintrag["vimeo"] = {"id": vid, "sha256": hash_}
        id_eintragen(slug, vid)
        einbetten(slug, vid, zeile["titel"])
        LOCK.write_text(json.dumps(dict(sorted(lock.items())), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  ok: https://vimeo.com/{vid}")
        time.sleep(1)
    in_liste = {z["slug"] for z in zeilen}
    for slug, eintrag in lock.items():
        if eintrag.get("vimeo", {}).get("id") and slug not in in_liste:
            print(f"Nicht mehr in videos.csv, auf Vimeo nicht gelöscht: {slug} (https://vimeo.com/{eintrag['vimeo']['id']})")
    zahl = {k: sum(1 for v in status.values() if v == k) for k in ("neu", "geändert", "unverändert")}
    print(f"Videos auf Vimeo: {zahl['neu']} neu, {zahl['geändert']} geändert, {zahl['unverändert']} unverändert")


if __name__ == "__main__":
    main()
