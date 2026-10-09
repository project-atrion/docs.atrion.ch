# MCP und Claude Code

atrion_mcp macht Atrion für Claude Code und andere MCP-Clients nutzbar. Das Modul baut keinen eigenen MCP-Server, sondern legt sich als Bridge über den MCP-Server von Odoo 20 (ai_mcp, Route /mcp). Es ergänzt Werkzeugkatalog, Werkzeugstatus, Mandats-Opt-out, eine serverseitige Bestätigung schreibender Werkzeuge sowie das MCP-Protokoll auf audit.request.

## Funktionen

| Nr. | Funktion | Für wen |
|---|---|---|
| F01 | [Werkzeugkatalog und Synchronisation](../../benutzer/mcp/f01-werkzeuge-ansehen.md) | MCP: Lesen, MCP: Administrieren (Synchronisieren) |
| F02 | [Werkzeugstatus und Freischaltung](../../benutzer/mcp/f02-werkzeug-freischalten-sperren.md) | MCP: Administrieren |
| F07 | [Bestätigung mit Vorschau und Code](../../benutzer/mcp/f07-bestaetigungen-verfolgen.md) | MCP: Schreiben |
| F08 | [Bestätigung in Atrion](../../benutzer/mcp/f08-bestaetigung-annehmen.md) | MCP: Schreiben, MCP: Administrieren (alle Bestätigungen) |
| F09 | [MCP-Protokoll](../../benutzer/mcp/f09-mcp-protokoll.md) | MCP: Lesen (Meine Aufrufe), MCP: Administrieren |
| F10 | [Dashboard](../../benutzer/mcp/f10-dashboard.md) | MCP: Administrieren |
| F11 | [Einstellungen](../../benutzer/mcp/f11-einstellungen-mcp.md) | MCP: Administrieren, Basis: Administrieren (mcp.mandat_erlaubt je Mandat) |
| F12 | [Schritt MCP-Freigabe in der Mandatseröffnung](../../benutzer/mcp/f12-eroeffnung-mcp-freigabe.md) | Basis: Administrieren |
| F13 | [OAuth und Token-Begrenzung](../../benutzer/mcp/f13-oauth-zustimmung.md) | MCP: Lesen, MCP: Administrieren (OAuth-Clients) |
| F14 | [Einrichtungsseite und Datenschutzhinweis](../../benutzer/mcp/f14-claude-code-einrichten.md) | MCP: Lesen |
| F15 | [MCP-Stufe und Personensperre](../../benutzer/mcp/f15-mcp-stufe-und-sperre.md) | Systemadministration (Stufe), MCP: Administrieren (Sperre) |

Technische Details zum Modul `atrion_mcp` stehen unter [Technik](../../technik/index.md).
