# Technische Dokumentation

Für Entwickler:innen, Integrationen und den Betrieb.

| Bereich | Inhalt |
|---|---|
| [REST-API](api/index.md) | Referenz aus OpenAPI 3.1 unter `/api/atrion/v1`, Authentifizierung, Paginierung, Fehlercodes nach RFC 9457, Webhooks |
| [MCP](mcp/index.md) | MCP-Bridge für Claude Code und andere MCP-Clients, Werkzeugkatalog, Bestätigungen, Einrichtung |
| [Datenmodell](datenmodell/index.md) | Modelle und Felder je Modul |
| [Audit](audit/index.md) | Protokollumfang, Kanäle, Ereignistypen, Hash-Kette, Maskierung |
| [Erweiterung](erweiterung/index.md) | Erweiterungspunkte für Fachmodule |
| [Betrieb](betrieb/index.md) | Installation, Einstellungen, Cron-Jobs, Überwachung |

## Module

| Modul | Aufgabe |
|---|---|
| `audit_trail` | Generisches Odoo-Modul: unveränderliches, hash-verkettetes Protokoll aller Änderungen, Anmeldungen und Ereignisse |
| `atrion_basis` | Mandate als eigene Unternehmen, Verwaltungseinheiten, Zuständigkeiten, Mandatswahl, Rechte-Stufen |
| `atrion_einstellungen` | Alle Atrion-Einstellungen global mit Übersteuerung je Mandat |
| `atrion_api` | REST-Framework unter `/api/atrion/v1` mit API-Clients, Webhooks und API-Protokoll |
| `atrion_mcp` | Bridge auf den MCP-Server von Odoo 20 für Claude Code |
