# Fehlercodes

!!! info "Vorabdokumentation"
    Diese Seite beschreibt den geplanten Inhalt aus dem Feinkonzept. Referenzen entstehen beim Bau automatisch aus dem Code.

## Inhalt

Ergebnis- und Fehlerformat (HTTP 200, `isError`, Problemobjekt), je Code ein Abschnitt: `mcp_deaktiviert`, `keine_berechtigung`, `person_gesperrt`, `hinweis_bestaetigen`, `werkzeug_gesperrt`, `werkzeug_unbekannt`, `schreiben_nicht_erlaubt`, `limit_erreicht`, `mandat_ausgeschlossen`, `validierung`, `bestaetigung_ausstehend`, `bestaetigung_ungueltig`, `interner_fehler`; HTTP 401 mit `resource_metadata`

## Quelle

erzeugt aus der Fehlercode-Liste des Moduls, Einleitung von Hand

<small>Modul `atrion_mcp`</small>
