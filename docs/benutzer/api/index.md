# REST-API

atrion_api ist das REST-Framework aller Atrion-Module unter /api/atrion/v1: eine Route, eine Prüfkette, ein Fehlerformat (RFC 9457). Fachmodule registrieren ihre Operationen per Dekorator auf eigenen Dienstmodellen; REST, MCP und Assistenten nutzen denselben Einstieg atrion.api.dienst.ausfuehren(). Dazu kommen API-Clients mit technischem Benutzer und Schlüsseln, signierte Webhooks, die Core-Ressourcen der Phase 1 und das API-Protokoll als Sicht auf audit.request.

## Funktionen

| Nr. | Funktion | Für wen |
|---|---|---|
| F01 | [API-Clients verwalten](../../benutzer/api/f01-api-client-einrichten.md) | API: Schreiben, Systemadministration (Stufen), API: Lesen (ansehen) |
| F02 | [Schlüssel erzeugen, rotieren, widerrufen](../../benutzer/api/f02-schluessel-erzeugen-rotieren.md) | API: Schreiben |
| F10 | [Rate-Limit und IP-Sperre](../../benutzer/api/f10-sperren-aufheben.md) | API: Administrieren |
| F15 | [Ereignisse: Outbox und Feed](../../benutzer/api/f15-ereignistypen.md) | API: Lesen, API: Administrieren (schalten) |
| F16 | [Webhooks](../../benutzer/api/f16-webhook-einrichten.md) | API: Administrieren |
| F17 | [API-Protokoll](../../benutzer/api/f17-api-protokoll.md) | API: Administrieren, Audit: Lesen |
| F18 | [Dashboard](../../benutzer/api/f18-dashboard.md) | API: Lesen |
| F19 | [Einstellungen](../../benutzer/api/f19-einstellungen-api.md) | API: Administrieren |
| F20 | [Berichte](../../benutzer/api/f20-berichte.md) | API: Lesen, Export API: Administrieren |

Technische Details zum Modul `atrion_api` stehen unter [Technik](../../technik/index.md).
