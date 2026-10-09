# Audit-Protokoll

audit_trail ist ein generisches Odoo-20-Modul ohne Atrion-Bezug. Es beantwortet die Frage: Was hat eine Person auf der Plattform gemacht und geändert? Dafür protokolliert es Änderungen (nur geänderte Felder mit altem und neuem Wert), Anmeldungen, Sicherheits- und Fachereignisse, schreibende API- und MCP-Aufrufe sowie Lesezugriffe auf markierte sensible Modelle. Die Einträge sind unveränderlich, hash-verkettet, täglich extern verankert und liegen kompakt in monatlichen PostgreSQL-Partitionen. Geheimnisse werden nie gespeichert.

## Funktionen

| Nr. | Funktion | Für wen |
|---|---|---|
| F01 | [Protokollumfang und Requests](../../benutzer/audit/f01-requests-ansehen.md) | Lesen |
| F03 | [Maskierung sensibler Daten](../../benutzer/audit/f03-maskierung.md) | Administrieren |
| F04 | [Cron und Transaktionen ohne Request](../../benutzer/audit/f04-cron-laeufe-nachvollziehen.md) | Lesen |
| F05 | [Änderungsprotokoll](../../benutzer/audit/f05-aenderungen-alt-neu.md) | Lesen |
| F06 | [Anmeldungen und Ereignisse](../../benutzer/audit/f06-ereignisse.md) | Lesen |
| F07 | [Sensible Lesezugriffe](../../benutzer/audit/f07-lesezugriffe.md) | Lesen |
| F09 | [Audit am Datensatz](../../benutzer/audit/f09-audit-am-datensatz.md) | Lesen |
| F10 | [Hash-Kette](../../benutzer/audit/f10-eintrag-pruefen.md) | Administrieren |
| F11 | [Partitionen und Speicher](../../benutzer/audit/f11-partitionen-und-groesse.md) | Administrieren |
| F13 | [Tagesanker extern](../../benutzer/audit/f13-tagesanker.md) | Lesen, Administrieren (Erneut senden) |
| F14 | [Integritätsprüfung](../../benutzer/audit/f14-integritaet-pruefen.md) | Administrieren (Prüfung starten), Lesen (Ergebnis) |
| F15 | [Dashboard](../../benutzer/audit/f15-dashboard.md) | Lesen |
| F16 | [Berichte und Export](../../benutzer/audit/f16-berichte-und-export.md) | Lesen, Administrieren (Export JSON Lines) |
| F17 | [Einstellungen und Regeln](../../benutzer/audit/f17-einstellungen.md) | Administrieren |
| F18 | [Unveränderlichkeit](../../benutzer/audit/f18-unveraenderlichkeit.md) | Lesen, Administrieren |

Technische Details zum Modul `audit_trail` stehen unter [Technik](../../technik/index.md).
