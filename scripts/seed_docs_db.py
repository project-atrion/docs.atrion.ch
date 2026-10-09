# Fiktive Demodaten für die Screenshot-Datenbank (zum Beispiel odoo_atrion_docs).
#
# Läuft in der Odoo-Shell gegen eine eigene Datenbank, nie gegen die produktive Instanz:
#   ATRION_PASSWORD=… odoo-bin shell -c <odoo.conf> -d odoo_atrion_docs --no-http < scripts/seed_docs_db.py
#
# Das Passwort für max.mustermann@example.ch (Login wie in ATRION_LOGIN, Standard "admin")
# kommt nur aus der Umgebung. Das Skript lässt sich mehrfach ausführen.
import os

from odoo.tools.binary import BinaryBytes
from odoo.tools.misc import file_path

E = os.environ
LANG, TZ = "de_CH", "Europe/Zurich"
FIRMA = "Project Atrion AG"

for code in ("de_CH", "en_GB", "fr_CH", "it_IT"):
    env["res.lang"]._activate_and_install_lang(code)

# Firma mit Atrion-Branding
chf = env.ref("base.CHF")
chf.active = True
firma = env.ref("base.main_company")
werte = {"name": FIRMA, "country_id": env.ref("base.ch").id, "currency_id": chf.id,
         "primary_color": "#0B1F3A", "secondary_color": "#FF7A1A"}
try:
    with open(file_path("atrion_theme/static/img/logo.png"), "rb") as f:
        werte["logo"] = BinaryBytes(f.read(), "logo.png")
except FileNotFoundError:
    pass
firma.write(werte)
firma.partner_id.write({"lang": LANG, "tz": TZ})

# Hauptperson: Max Mustermann (Administrator, meldet sich für die Aufnahmen an)
admin = env.ref("base.user_admin")
admin.write({
    "name": "Max Mustermann",
    "login": E.get("ATRION_LOGIN", "admin"),
    "email": "max.mustermann@example.ch",
    "password": E["ATRION_PASSWORD"],
    "lang": LANG,
    "tz": TZ,
    "signature": f"<p>Max Mustermann<br/>{FIRMA}</p>",
})
admin.partner_id.write({"phone": "+41 44 000 00 01", "function": "Geschäftsführer"})

# Weitere fiktive Personen; Jutta Musterfrau ist das Beispiel in Formular, Suche und Chatter
Users = env["res.users"].with_context(no_reset_password=True)
LEUTE = [
    ("Jutta Musterfrau", "Bewirtschafterin", "Zürich"),
    ("Claudia Meier", "Buchhalterin", "Bern"),
    ("David Frei", "Hauswart", "Basel"),
    ("Eva Schneider", "Bewirtschafterin", "Luzern"),
    ("Fabio Rossi", "Assistent", "Winterthur"),
    ("Gabriela Huber", "Revisorin", "St. Gallen"),
    ("Hans Brunner", "Bewirtschafter", "Zug"),
    ("Irene Weber", "Buchhalterin", "Aarau"),  # archiviert, für den Filter «Inaktive Benutzer»
]
leute = {}
for i, (name, funktion, ort) in enumerate(LEUTE):
    mail = name.lower().replace(" ", ".") + "@example.ch"
    u = Users.with_context(active_test=False).search([("login", "=", mail)]) or Users.create(
        {"name": name, "login": mail, "email": mail, "lang": LANG, "tz": TZ})
    u.partner_id.write({"function": funktion, "phone": f"+41 44 000 00 {i + 10}", "city": ort,
                        "country_id": env.ref("base.ch").id})
    u.active = name != "Irene Weber"
    leute[name] = u
    # gilt als bereits angemeldet, damit keine «ausstehende Einladung» erscheint
    if not env["res.users.log"].search_count([("create_uid", "=", u.id)]):
        env["res.users.log"].with_user(u).sudo().create({})

# Alte Demonamen aus früheren Läufen entfernen
alt = Users.with_context(active_test=False).search([("login", "in", ["beat.keller@example.ch", "anna.muster@example.ch"])])
alt.write({"active": False})

# Unterhaltungen im Dialog
kanal = env.ref("mail.channel_all_employees")
if not kanal.message_ids.filtered(lambda m: "Seestrasse 12" in (m.body or "")):
    for u, text in [(leute["Jutta Musterfrau"], "Guten Morgen zusammen. Die Wohnungsabnahme an der Seestrasse 12 ist auf Freitag 10 Uhr verschoben."),
                    (leute["Claudia Meier"], "Danke Jutta. Ich nehme das Protokoll mit."),
                    (admin, "Perfekt. Eva, bitte die Schlüsselübergabe vorbereiten.")]:
        kanal.with_user(u).sudo().message_post(body=text, message_type="comment",
                                              subtype_xmlid="mail.mt_comment", author_id=u.partner_id.id)
chat = env["discuss.channel"].with_user(leute["Eva Schneider"])._get_or_create_chat(partners_to=admin.partner_id.ids)
if not chat.message_ids:
    chat.with_user(leute["Eva Schneider"]).message_post(
        body="Hallo Max, die Nebenkostenabrechnung ist bereit zur Durchsicht.",
        message_type="comment", subtype_xmlid="mail.mt_comment")

# Kein Lizenzhinweis «Diese Datenbank läuft ab» auf den Bildern
ICP = env["ir.config_parameter"].sudo()
ICP.set_str("database.expiration_date", "2099-12-31 00:00:00")
ICP.set_str("database.expiration_reason", "renewal")

env.cr.commit()
print(f"Demodaten ok: {FIRMA}, Max Mustermann + {len(leute)} Personen")
