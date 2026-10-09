#!/usr/bin/env python3
"""Erzeugt die Screenshots der Benutzerdokumentation aus einer laufenden Atrion-Instanz.

Aufruf:
    ATRION_URL=http://localhost:8070 ATRION_LOGIN=admin ATRION_PASSWORD=… \\
        python scripts/capture_screenshots.py [slug …]

Ohne slug werden alle Seiten neu aufgenommen. Die Bilder landen unter
docs/assets/screenshots/<slug>/<nn>-<schritt>.png (Fullpage, 1440 × 900, de_CH, helles Design).
Passwortfelder, QR-Codes und Geheimnisse werden maskiert. Die Instanz sollte nur fiktive
Demodaten enthalten, denn die Bilder werden öffentlich.

Videos (nicht im Repo, Upload auf Vimeo von Hand):
    python scripts/capture_screenshots.py --videos ../docs-videos [slug …]

Nimmt für jede Seite mit mindestens drei Schritten den Ablauf als Video auf, wandelt ihn mit
ffmpeg in MP4 (H.264) um und schreibt die Upload-Liste videos.csv. ffmpeg kommt aus FFMPEG,
dem PATH oder dem Python-Paket imageio-ffmpeg; ohne ffmpeg bleibt WebM.
"""
import csv
import os
import pathlib
import re
import shutil
import subprocess
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZIEL = ROOT / "docs" / "assets" / "screenshots"
URL = os.environ["ATRION_URL"].rstrip("/")
LOGIN = os.environ["ATRION_LOGIN"]
PASSWORT = os.environ["ATRION_PASSWORD"]
BENUTZER = "/odoo/action-base.action_res_users"
GEHEIM = ["input[type=password]", "[name=secret]", "[name=qrcode]"]


class Aufnahme:
    def __init__(self, browser, video_dir=None):
        self.browser = browser
        self.page = None
        self.sitzung = None  # eine Anmeldung für alle Seiten, damit die Geräteliste kurz bleibt
        self.video_dir = video_dir

    def kontext(self, anmelden, video=False):
        extra = {"record_video_dir": str(self.video_dir), "record_video_size": {"width": 1440, "height": 900}} if video else {}
        ctx = self.browser.new_context(viewport={"width": 1440, "height": 900}, locale="de-CH",
                                       timezone_id="Europe/Zurich", color_scheme="light",
                                       storage_state=self.sitzung if anmelden else None, **extra)
        # Kein Hinweis «Push-Benachrichtigungen sind blockiert» auf den Bildern
        ctx.add_init_script("Object.defineProperty(window.Notification || {}, 'permission', {get: () => 'default'})")
        return ctx

    def neu(self, anmelden=True):
        if self.page:
            self.page.context.close()
        if self.video_dir and anmelden and not self.sitzung:
            # Anmeldung ausserhalb des Videos, damit es direkt mit der Funktion beginnt
            self.page = self.kontext(True).new_page()
            self.anmelden()
            self.sitzung = self.page.context.storage_state()
            self.page.context.close()
        ctx = self.kontext(anmelden, video=bool(self.video_dir))
        self.page = ctx.new_page()
        if anmelden:
            if self.sitzung:
                self.page.goto(URL + "/odoo")
                self.page.wait_for_selector(".o_main_navbar", timeout=60000)
                self.ruhe()
            else:
                self.anmelden()
                self.sitzung = ctx.storage_state()
        return self.page

    def anmelden(self):
        p = self.page
        p.goto(URL + "/web/login")
        p.fill("input[name=login]", LOGIN)
        p.fill("input[name=password]", PASSWORT)
        p.click("button[type=submit]")
        p.wait_for_selector(".o_main_navbar", timeout=60000)
        self.ruhe()

    def ruhe(self, ms=900):
        self.page.wait_for_timeout(ms)

    def gehe(self, pfad, warte=".o_action_manager .o_view_controller"):
        self.page.goto(URL + pfad)
        self.page.wait_for_selector(warte, timeout=30000)
        self.ruhe(1200)

    def bild(self, slug, nr, name, maske=()):
        if self.video_dir:
            self.ruhe(1800)  # Pause je Schritt im Video statt Screenshot
            return
        ordner = ZIEL / slug
        ordner.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(ordner / f"{nr:02d}-{name}.png"), full_page=True,
                             mask=[self.page.locator(s) for s in (*GEHEIM, *maske)], mask_color="#0b1f3a",
                             animations="disabled", caret="hide")
        print(f"  {slug}/{nr:02d}-{name}.png")

    # Bausteine
    def benutzermenue(self):
        self.page.click(".o_menu_systray .o_user_menu")
        self.page.wait_for_selector(".o-dropdown--menu", timeout=10000)
        self.ruhe(500)

    def praeferenzen(self, reiter=None):
        self.benutzermenue()
        self.page.click(".o-dropdown--menu >> text=Meine Präferenzen")
        self.page.wait_for_selector(".modal-content .o_form_view", timeout=20000)
        self.ruhe(1000)
        if reiter:
            self.page.click(f".modal-content .nav-link >> text={reiter}")
            self.ruhe(700)

    def liste(self):
        self.gehe(BENUTZER, ".o_list_view")

    def suchpanel(self):
        self.page.click(".o_searchview_dropdown_toggler")
        self.page.wait_for_selector(".o_search_bar_menu", timeout=10000)
        self.ruhe(600)

    def formular(self, name="Jutta Musterfrau"):
        self.liste()
        self.page.click(f".o_data_row:has-text('{name}') td.o_data_cell >> nth=0")
        self.page.wait_for_selector(".o_form_view .o_form_sheet", timeout=20000)
        self.ruhe(1200)

    def aktionsmenue(self):
        self.page.click(".o_control_panel .o_cp_action_menus .dropdown-toggle")
        self.page.wait_for_selector(".o-dropdown--menu", timeout=10000)
        self.page.mouse.move(720, 600)
        self.ruhe(700)

    def identitaet(self):
        """Dialog «Zugriffskontrolle» mit dem eigenen Passwort bestätigen."""
        feld = self.page.locator(".modal-content input[type=password]").last
        try:
            feld.wait_for(timeout=3000)
        except Exception:
            return  # vor kurzem bestätigt, Odoo fragt nicht erneut
        feld.fill(PASSWORT)
        self.page.locator(".modal-footer button.btn-primary").last.click()
        self.ruhe(1500)


# Seiten: slug -> Funktion(a), die die Schritte aufnimmt
SEITEN = {}


def seite(fn):
    SEITEN[fn.__name__.replace("_", "-")] = fn
    return fn


@seite
def anmelden(a):
    p = a.neu(anmelden=False)
    p.goto(URL + "/web/login"); a.ruhe()
    a.bild("anmelden", 1, "anmeldeseite")
    p.fill("input[name=login]", LOGIN); p.fill("input[name=password]", PASSWORT)
    a.bild("anmelden", 2, "zugangsdaten")
    p.click("button[type=submit]"); p.wait_for_selector(".o_main_navbar", timeout=60000); a.ruhe(1500)
    a.bild("anmelden", 3, "startseite")


@seite
def abmelden(a):
    p = a.neu()
    a.benutzermenue()
    a.bild("abmelden", 1, "benutzermenue")
    p.click(".o-dropdown--menu >> text=Abmelden"); p.wait_for_selector("input[name=login]", timeout=30000); a.ruhe()
    a.bild("abmelden", 2, "abgemeldet")
    a.sitzung = None  # Sitzung ist abgemeldet, die nächste Seite meldet sich neu an


@seite
def passwort_zuruecksetzen(a):
    p = a.neu(anmelden=False)
    p.goto(URL + "/web/login"); a.ruhe()
    p.hover("a[href*='reset_password']")
    a.bild("passwort-zuruecksetzen", 1, "link")
    p.click("a[href*='reset_password']"); p.wait_for_selector("input[name=login]"); a.ruhe()
    p.fill("input[name=login]", "jutta.musterfrau@example.ch")
    a.bild("passwort-zuruecksetzen", 2, "formular")


@seite
def passwort_aendern(a):
    p = a.neu()
    a.praeferenzen("Sicherheit")
    a.bild("passwort-aendern", 1, "reiter-sicherheit")
    p.click(".modal-content button:has-text('Passwort ändern')"); a.ruhe(1500)
    p.locator(".modal-content input[type=password]").last.fill(PASSWORT)
    a.bild("passwort-aendern", 2, "identitaet-bestaetigen")
    a.identitaet()
    a.bild("passwort-aendern", 3, "neues-passwort")


@seite
def zwei_faktor_einrichten(a):
    p = a.neu()
    a.praeferenzen("Sicherheit")
    a.bild("zwei-faktor-einrichten", 1, "reiter-sicherheit")
    p.click(".modal-content [name=action_totp_enable_wizard]"); a.ruhe(1500)
    a.identitaet()
    a.ruhe(800)
    a.bild("zwei-faktor-einrichten", 2, "qr-code", maske=[".modal-content img"])


@seite
def alle_geraete_abmelden(a):
    p = a.neu()
    a.praeferenzen("Sicherheit")
    p.hover(".modal-content button:has-text('Abmelden')")
    a.bild("alle-geraete-abmelden", 1, "knopf")


@seite
def sprache_wechseln(a):
    p = a.neu()
    a.benutzermenue()
    a.bild("sprache-wechseln", 1, "benutzermenue")
    p.click(".o-dropdown--menu >> text=Meine Präferenzen"); p.wait_for_selector(".modal-content .o_form_view"); a.ruhe(1000)
    p.click(".modal-content [name=lang] input"); a.ruhe(800)
    a.bild("sprache-wechseln", 2, "sprache-waehlen")


@seite
def zeitzone_einstellen(a):
    p = a.neu()
    a.praeferenzen("Kalender")
    a.bild("zeitzone-einstellen", 1, "reiter-kalender")


@seite
def profil_und_signatur(a):
    a.neu()
    a.praeferenzen()
    a.bild("profil-und-signatur", 1, "praeferenzen")


@seite
def benachrichtigungen(a):
    p = a.neu()
    a.praeferenzen()
    p.hover(".modal-content [name=notification_type]")
    a.bild("benachrichtigungen", 1, "einstellung")


@seite
def darstellung(a):
    p = a.neu()
    a.praeferenzen()
    p.hover(".modal-content .o_field_widget[name*=color_scheme], .modal-content label:has-text('Design')")
    a.bild("darstellung", 1, "design-waehlen")


@seite
def apps_und_menues(a):
    p = a.neu()
    a.bild("apps-und-menues", 1, "startseite")
    a.gehe("/odoo/settings", ".o_setting_container, .o_settings_container, .settings")
    p.click(".o_main_navbar .o_menu_sections >> text=Benutzer & Unternehmen"); a.ruhe(700)
    a.bild("apps-und-menues", 2, "app-menue")
    p.keyboard.press("Escape")
    p.click(".o_main_navbar .o_menu_toggle, .o_main_navbar .o_navbar_apps_menu button"); a.ruhe(1000)
    a.bild("apps-und-menues", 3, "zurueck-zur-startseite")


@seite
def befehlspalette(a):
    p = a.neu()
    p.keyboard.press("Control+k"); a.ruhe(800)
    if not p.locator(".o_command_palette").count():
        p.keyboard.press("Meta+k"); a.ruhe(800)
    a.bild("befehlspalette", 1, "geoeffnet")
    p.keyboard.type("/Benutzer"); a.ruhe(1200)
    a.bild("befehlspalette", 2, "suche")


@seite
def tastaturkuerzel(a):
    p = a.neu()
    a.liste()
    p.keyboard.down("Control"); a.ruhe(1200)
    a.bild("tastaturkuerzel", 1, "ueberlagerung")
    p.keyboard.up("Control")


@seite
def ansichten_wechseln(a):
    p = a.neu()
    a.liste()
    p.hover(".o_switch_view.o_kanban")
    a.bild("ansichten-wechseln", 1, "liste")
    p.click(".o_switch_view.o_kanban"); p.wait_for_selector(".o_kanban_view"); a.ruhe()
    a.bild("ansichten-wechseln", 2, "kanban")


@seite
def suchen(a):
    p = a.neu()
    a.liste()
    p.click(".o_searchview_input"); p.keyboard.type("Musterfrau"); a.ruhe(800)
    a.bild("suchen", 1, "suchbegriff")
    p.keyboard.press("Enter"); a.ruhe(1200)
    a.bild("suchen", 2, "ergebnis")


@seite
def filtern(a):
    p = a.neu()
    a.liste()
    a.suchpanel()
    a.bild("filtern", 1, "filter-oeffnen")
    p.click(".o_filter_menu .o_menu_item:has-text('Inaktive')"); a.ruhe(1200)
    a.bild("filtern", 2, "gefiltert")


@seite
def gruppieren(a):
    p = a.neu()
    a.liste()
    a.suchpanel()
    p.hover(".o_group_by_menu")
    a.bild("gruppieren", 1, "gruppieren-nach")
    p.locator(".o_group_by_menu .o_menu_item").first.click(); a.ruhe(1200)
    p.keyboard.press("Escape"); p.click(".o_list_view h1, .o_control_panel .o_breadcrumb", force=True); a.ruhe(500)
    p.locator(".o_group_header").first.click(); a.ruhe(1000)
    a.bild("gruppieren", 2, "gruppiert")


@seite
def favoriten(a):
    p = a.neu()
    a.liste()
    a.suchpanel()
    p.click(".o_filter_menu .o_menu_item:has-text('Inaktive')"); a.ruhe(1000)
    p.click(".o_favorite_menu .o_add_favorite, .o_favorite_menu button:has-text('Aktuelle Suche speichern')"); a.ruhe(800)
    inp = p.locator(".o_favorite_menu input[type=text]").first
    inp.fill("Inaktive Personen"); a.ruhe(400)
    a.bild("favoriten", 1, "suche-speichern")


@seite
def sortieren_und_blaettern(a):
    p = a.neu()
    a.liste()
    p.click("th[data-name=name]"); a.ruhe(1000)
    p.hover("th[data-name=name]")
    a.bild("sortieren-und-blaettern", 1, "sortiert")
    p.hover(".o_pager")
    a.bild("sortieren-und-blaettern", 2, "blaettern")


@seite
def spalten_anpassen(a):
    p = a.neu()
    a.liste()
    p.click(".o_optional_columns_dropdown_toggle"); a.ruhe(800)
    a.bild("spalten-anpassen", 1, "spalten-waehlen")


@seite
def auswaehlen_und_massenbearbeitung(a):
    p = a.neu()
    a.liste()
    for n in (1, 2, 3):
        p.locator(".o_data_row .o_list_record_selector input").nth(n).check()
    a.ruhe(800)
    a.bild("auswaehlen-und-massenbearbeitung", 1, "auswahl")
    a.aktionsmenue()
    a.bild("auswaehlen-und-massenbearbeitung", 2, "aktionen")


@seite
def datensatz_bearbeiten(a):
    p = a.neu()
    a.liste()
    p.click(".o_control_panel .o_list_button_add"); p.wait_for_selector(".o_form_view .o_form_sheet"); a.ruhe(1200)
    a.bild("datensatz-bearbeiten", 1, "neu")
    p.fill(".o_field_widget[name=name] input, .o_field_widget[name=name] textarea", "Lara Steiner")
    p.fill(".o_field_widget[name=login] input", "lara.steiner@example.ch"); a.ruhe(600)
    p.hover(".o_form_button_save")
    a.bild("datensatz-bearbeiten", 2, "ausfuellen")


@seite
def aenderungen_verwerfen(a):
    p = a.neu()
    a.formular()
    p.fill(".o_field_widget[name=name] input, .o_field_widget[name=name] textarea", "Jutta Musterfrau-Meier"); a.ruhe(600)
    p.hover(".o_form_button_cancel")
    a.bild("aenderungen-verwerfen", 1, "geaendert")
    p.click(".o_form_button_cancel"); a.ruhe(1000)
    a.bild("aenderungen-verwerfen", 2, "verworfen")


@seite
def duplizieren(a):
    a.neu()
    a.formular()
    a.aktionsmenue()
    a.page.hover(".o-dropdown--menu >> text=Duplizieren")
    a.bild("duplizieren", 1, "aktion")


@seite
def archivieren_und_loeschen(a):
    p = a.neu()
    a.formular("Hans Brunner")
    a.aktionsmenue()
    p.hover(".o-dropdown--menu >> text=Archivieren")
    a.bild("archivieren-und-loeschen", 1, "aktionen")
    p.click(".o-dropdown--menu >> text=Archivieren"); a.ruhe(1000)
    a.bild("archivieren-und-loeschen", 2, "bestaetigen")


@seite
def exportieren(a):
    p = a.neu()
    a.liste()
    p.locator(".o_list_view thead .o_list_record_selector input").check(); a.ruhe(600)
    a.aktionsmenue()
    p.hover(".o-dropdown--menu >> text=Exportieren")
    a.bild("exportieren", 1, "aktion")
    p.click(".o-dropdown--menu >> text=Exportieren"); p.wait_for_selector(".o_export_data_dialog, .modal-content"); a.ruhe(1500)
    a.bild("exportieren", 2, "dialog")


@seite
def importieren(a):
    p = a.neu()
    a.liste()
    p.click(".o_control_panel_breadcrumbs .o_cp_action_menus .dropdown-toggle, .o_control_panel .o_cp_action_menus button"); p.mouse.move(720, 600); a.ruhe(900)
    a.bild("importieren", 1, "menue")
    p.click(".o-dropdown--menu >> text=/importieren/i"); p.wait_for_selector(".o_import_action, .o_base_import", timeout=30000); a.ruhe(1500)
    a.bild("importieren", 2, "importseite")


@seite
def chatter(a):
    p = a.neu()
    a.formular()
    p.click(".o-mail-Chatter-sendMessage"); a.ruhe(800)
    p.locator(".o-mail-Composer-input").fill("Hallo Jutta, bitte die Schlüsselliste bis Freitag ergänzen."); a.ruhe(500)
    a.bild("chatter", 1, "nachricht")
    p.click(".o-mail-Chatter-logNote"); a.ruhe(800)
    p.locator(".o-mail-Composer-input").fill("Interne Notiz: Jutta übernimmt ab Januar die Liegenschaft Seestrasse."); a.ruhe(500)
    a.bild("chatter", 2, "notiz")


@seite
def aktivitaeten(a):
    p = a.neu()
    a.formular()
    p.click(".o-mail-Chatter-activity"); p.wait_for_selector(".modal-content"); a.ruhe(1500)
    a.bild("aktivitaeten", 1, "planen")
    p.keyboard.press("Escape"); a.ruhe(500)
    p.click(".o_menu_systray button:has(i[aria-label='Aktivitäten'])"); a.ruhe(1000)
    a.bild("aktivitaeten", 2, "uebersicht")


@seite
def folgen(a):
    p = a.neu()
    a.formular()
    p.click(".o-mail-Followers-button"); a.ruhe(800)
    a.bild("folgen", 1, "follower")


@seite
def anhaenge(a):
    p = a.neu()
    a.formular()
    p.hover(".o-mail-Chatter-attachFiles, .o-mail-Chatter-topbar button[title*='Anh']")
    a.bild("anhaenge", 1, "bueroklammer")


@seite
def posteingang(a):
    p = a.neu()
    p.click(".o_menu_systray .o-mail-DiscussSystray-class"); a.ruhe(1200)
    a.bild("posteingang", 1, "nachrichtenmenue")


@seite
def discuss(a):
    p = a.neu()
    a.gehe("/odoo/discuss", ".o-mail-Discuss")
    p.click(".o-mail-Discuss :text('Eva Schneider')"); a.ruhe(1200)
    a.bild("discuss", 1, "direktnachricht")
    p.click(".o-mail-MessagingMenu-tab:has-text('Kanäle')"); a.ruhe(800)
    p.click(".o-mail-NotificationItem:has-text('Allgemein')"); a.ruhe(1500)
    a.bild("discuss", 2, "kanal")


@seite
def benutzer_einladen(a):
    p = a.neu()
    a.gehe("/odoo/settings", ".o_setting_container, .o_settings_container, .settings")
    p.fill("input[placeholder*='E-Mail']", "lara.steiner@example.ch"); a.ruhe(500)
    a.bild("benutzer-einladen", 1, "einladen")


@seite
def zugriffsrechte_setzen(a):
    p = a.neu()
    a.formular()
    p.hover(".o_form_view :text('Rolle')")
    a.bild("zugriffsrechte-setzen", 1, "rolle")


@seite
def passwort_fuer_andere_zuruecksetzen(a):
    p = a.neu()
    a.formular()
    a.aktionsmenue()
    a.bild("passwort-fuer-andere-zuruecksetzen", 1, "aktion")
    p.click(".o-dropdown--menu >> text=Passwort ändern"); p.wait_for_selector(".modal-content"); a.ruhe(1500)
    a.identitaet()
    a.bild("passwort-fuer-andere-zuruecksetzen", 2, "dialog")


def ffmpeg():
    pfad = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if pfad:
        return pfad
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def titel(slug):
    kopf = (ROOT / "docs" / "benutzer" / "grundlagen" / f"{slug}.md").read_text(encoding="utf-8").splitlines()[0]
    return kopf.lstrip("# ").strip()


def videos(ziel, gewuenscht):
    """Ein Video je Seite mit mindestens drei Schritten, als MP4 plus Upload-Liste videos.csv."""
    ziel.mkdir(parents=True, exist_ok=True)
    slugs = [s for s in gewuenscht if len(list((ZIEL / s).glob("*.png"))) >= 3]
    ff, fehler, zeilen = ffmpeg(), [], []
    with sync_playwright() as pw:
        a = Aufnahme(pw.chromium.launch(slow_mo=250), video_dir=ziel / "roh")
        for slug in slugs:
            print(slug)
            try:
                SEITEN[slug](a)
                a.ruhe(1500)
                video = a.page.video
                a.page.context.close()
                a.page = None
                webm = ziel / f"{slug}.webm"
                pathlib.Path(video.path()).replace(webm)
            except Exception as e:
                fehler.append(f"{slug}: {str(e).splitlines()[0]}")
                continue
            datei = webm
            if ff:
                datei = ziel / f"{slug}.mp4"
                subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(webm), "-c:v", "libx264", "-preset", "slow",
                                "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(datei)], check=True)
                webm.unlink()
            info = subprocess.run([ff, "-i", str(datei)], capture_output=True, text=True).stderr if ff else ""
            dauer = re.search(r"Duration: (\d+:\d+:\d+)", info)
            zeilen.append([slug, titel(slug), f"https://docs.atrion.ch/benutzer/grundlagen/{slug}/",
                           dauer.group(1) if dauer else "", datei.name])
        a.browser.close()
    shutil.rmtree(ziel / "roh", ignore_errors=True)
    with open(ziel / "videos.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["slug", "titel", "seite", "dauer", "datei"], *zeilen])
    print(f"{len(zeilen)} Videos in {ziel}" + ("" if ff else " (WebM, kein ffmpeg gefunden)"))
    return fehler


def main():
    args = sys.argv[1:]
    if "--videos" in args:
        i = args.index("--videos")
        ziel = pathlib.Path(args[i + 1]).expanduser().resolve()
        fehler = videos(ziel, args[:i] + args[i + 2:] or list(SEITEN))
    else:
        fehler = screenshots(args or list(SEITEN))
    if fehler:
        print("Fehler:\n  " + "\n  ".join(fehler))
        sys.exit(1)


def screenshots(gewuenscht):
    fehler = []
    with sync_playwright() as pw:
        a = Aufnahme(pw.chromium.launch())
        for slug in gewuenscht:
            print(slug)
            try:
                SEITEN[slug](a)
            except Exception as e:  # weiter mit der nächsten Seite, Fehler am Ende melden
                fehler.append(f"{slug}: {str(e).splitlines()[0]}")
        a.browser.close()
    return fehler


if __name__ == "__main__":
    main()
