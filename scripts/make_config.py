"""Builds web/config.yml from the lasenyal-web language files, so every text gets a field.

Run after adding or removing keys in lasenyal-web/_data/i18n/*.yml:
    python3 scripts/make_config.py ../lasenyal-web web/config.yml
(needs: pip install pyyaml)"""
import sys, yaml
web, out = sys.argv[1], sys.argv[2]
ca = yaml.safe_load(open(f"{web}/_data/i18n/ca.yml"))

L = {  # friendly labels for the Texts form, in file order
 "meta_description": ("Google description", "Short text shown under the site name in Google results."),
 "skip": ("Interface · 'Skip to content' link", None),
 "nav": ("Menu names", "Names of the built-in pages in the menu."),
 "tagline": ("Home · Tagline", "Under the big LA SENYAL title."),
 "intro_label": ("Home · Intro label", None), "intro": ("Home · Intro (big text)", None), "intro2": ("Home · Intro (second paragraph)", None),
 "how_label": ("Home · 'How it works' label", None), "how": ("Home · How it works (3 steps)", None), "how_note": ("Home · Note under the steps", None),
 "next_label": ("Home · Upcoming concerts title", None), "none_upcoming": ("Home · Text when there are no upcoming concerts", None),
 "all_concerts": ("Home · Button to all concerts", None), "see_members": ("Home · Link to members", None),
 "watch": ("Home · Video label", None), "gallery_label": ("Home · Photo strip label (for screen readers)", None),
 "members_title": ("Members · Title", None), "members_intro": ("Members · Intro", None),
 "concerts_title": ("Concerts · Title", None), "upcoming": ("Concerts · 'Upcoming'", None), "past": ("Concerts · 'Past'", None),
 "superlunes_title": ("Concerts · Superlunes title", None), "superlunes_intro": ("Concerts · Superlunes intro", None),
 "every_monday": ("Concerts · 'Every Monday'", None), "map": ("Concerts · 'Map' link", None), "info": ("Concerts · 'Info' link", None),
 "contact": ("Footer · 'Contact'", None), "booking": ("Footer · Line next to Contact", None), "presskit": ("Footer · Press kit link", None),
 "lang_label": ("Interface · 'Language'", None), "close": ("Interface · 'Close'", None), "prev": ("Interface · 'Previous'", None), "next": ("Interface · 'Next'", None),
 "months": ("Month names", "12 months, January first."), "months_short": ("Month names, short", "12 months, January first."),
 "roles": ("Member roles", "What each role is called. Members pick one of these."),
 "pk_title": ("Press kit · Title", None), "pk_band": ("Press kit · 'The band'", None), "pk_show": ("Press kit · 'The show' title", None),
 "pk_show_text": ("Press kit · The show text", None), "pk_formats_label": ("Press kit · 'Formats' label", None), "pk_formats": ("Press kit · Formats text", None),
 "pk_archive": ("Press kit · 'Archive'", None), "pk_lineup": ("Press kit · 'Line-up'", None), "pk_video": ("Press kit · 'Live video'", None), "pk_photo": ("Press kit · 'Photo'", None),
 "a11y": ("Interface · Accessibility button texts", None),
 "menu": ("Interface · 'Menu'", None), "close_menu": ("Interface · 'Close menu'", None),
 "mans": ("Hands game · all texts", "Texts of the Mans / Manos / Hands page and of its box on the home page. {n} and {i} are numbers filled in by the page: keep them."),
}

def human(k):
    return k.replace("_", " ").capitalize()

def field(k, v, top=False):
    lab, hint = L.get(k, (human(k), None)) if top else (human(k), None)
    f = {"name": k, "label": lab}
    if hint: f["hint"] = hint
    if isinstance(v, str):
        f["widget"] = "text" if len(v) > 70 else "string"
    elif isinstance(v, list) and all(isinstance(x, str) for x in v):
        f["widget"] = "list"
        if len(v) == 12: f.update(min=12, max=12)
    elif isinstance(v, list):
        sub = v[0]
        f.update(widget="list", collapsed=False, fields=[field(a, b) for a, b in sub.items()])
        if k == "how":
            f["fields"][0]["label"] = "Title"; f["fields"][1]["label"] = "Text"; f["summary"] = "{{fields.t}}"
    elif isinstance(v, dict):
        f.update(widget="object", collapsed=True, fields=[field(a, b) for a, b in v.items()])
    elif v is None:
        f["widget"] = "string"; f["required"] = False
    else:
        raise SystemExit(f"unexpected {k}: {v!r}")
    if top: f["i18n"] = True
    return f

def mark_i18n(fs):
    for f in fs:
        f["i18n"] = True
        if "fields" in f: mark_i18n(f["fields"])
    return fs

texts = mark_i18n([field(k, v, top=True) for k, v in ca.items()])
# the 'mans.rhythms' map differs between languages: let it hold any rhythm name
for f in texts:
    if f["name"] == "mans":
        for g in f["fields"]:
            if g["name"] == "rhythms":
                g.clear(); g.update(name="rhythms", label="Rhythm names", widget="keyvalue", required=False, i18n=True,
                                    hint="Name of each rhythm in this language (key = rhythm id from the game).")
            if g["name"] in ("lanes",): g["hint"] = "Names of the drum lanes."

roles = [{"label": f"{v}", "value": k} for k, v in ca["roles"].items()]

def img(name, label, folder="/assets/img/lg", hint=None, req=True):
    f = {"name": name, "label": label, "widget": "image", "media_folder": folder, "public_folder": folder, "required": req}
    if hint: f["hint"] = hint
    return f

builtin = [{"label": "Home", "value": "home"}, {"label": "Members", "value": "members"},
           {"label": "Concerts", "value": "concerts"}, {"label": "Hands game", "value": "hands"},
           {"label": "Contact (jumps to the footer)", "value": "contact"}]
menu_types = [
  {"name": "builtin", "label": "Built-in page", "widget": "object", "summary": "{{fields.key}}",
   "fields": [{"name": "key", "label": "Page", "widget": "select", "options": builtin}]},
  {"name": "page", "label": "Page from 'Pages'", "widget": "object", "summary": "{{fields.page}}",
   "fields": [{"name": "page", "label": "Page", "widget": "relation", "collection": "pages", "value_field": "{{slug}}", "display_fields": ["title"]},
              {"name": "label", "label": "Menu name (optional)", "widget": "string", "required": False,
               "hint": "Leave empty to use the page title. The same name is used in every language."}]},
]

SITE = "https://ciavendaval.github.io/lasenyal-web"
cfg = {
 "app_title": "La Senyal · web",
 "logo": {"src": "/lasenyal-admin/logo.png"},
 "backend": {"name": "github", "repo": "ciaVENDAVAL/lasenyal-web", "branch": "main", "auth_methods": ["token"],
             "commit_messages": {"create": "Admin: create {{collection}} “{{slug}}”", "update": "Admin: update {{collection}} “{{slug}}”",
                                 "delete": "Admin: delete {{collection}} “{{slug}}”", "uploadMedia": "Admin: upload “{{path}}”", "deleteMedia": "Admin: delete “{{path}}”"}},
 "site_url": SITE + "/",
 "media_folder": "assets/img/lg",
 "public_folder": "/assets/img/lg",
 "media_libraries": {"default": {"config": {"slugify_filename": False, "max_file_size": 25000000}}},
 "slug": {"encoding": "ascii", "clean_accents": True},
 "editor": {"preview": False},
 "output": {"yaml": {"quote": "double"}, "omit_empty_optional_fields": True},
 "i18n": {"structure": "multiple_folders", "locales": ["ca", "es", "en"], "default_locale": "ca"},
 "asset_collections": [
   {"name": "pdfs", "label": "PDFs", "media_folder": "pdf", "public_folder": "/pdf", "icon": "picture_as_pdf"},
   {"name": "photos", "label": "Photos (full size)", "media_folder": "assets/img/lg", "public_folder": "/assets/img/lg", "icon": "photo_library"},
   {"name": "member_photos", "label": "Member photos", "media_folder": "assets/img/members", "public_folder": "/assets/img/members", "icon": "account_circle"},
 ],
 "singletons": [
   {"name": "downloads", "label": "PDFs: which one the links give", "icon": "picture_as_pdf", "file": "_data/downloads.yml", "fields": [
     {"name": "presskit", "label": "Press kit", "widget": "object",
      "hint": "Short links for emails: lasenyal.com/dossier/ca/ · /es/ · /en/ — they always give the PDF chosen here. To publish a new version: upload it here (name it LaSenyal_CA_presskit_2026-12.pdf) and choose it, or upload one with exactly the same name as the old one and choose Replace.",
      "fields": [
        {"name": "ca", "label": "Català", "widget": "file", "media_folder": "/pdf", "public_folder": "/pdf"},
        {"name": "es", "label": "Castellano", "widget": "file", "media_folder": "/pdf", "public_folder": "/pdf"},
        {"name": "en", "label": "English", "widget": "file", "media_folder": "/pdf", "public_folder": "/pdf"}]}]},
   {"name": "site", "label": "Site settings: contact, footer, main photos", "icon": "tune", "file": "_data/site.yml", "fields": [
     {"name": "contact", "label": "Contact", "widget": "object", "fields": [
        {"name": "email", "label": "Email", "widget": "string"},
        {"name": "phones", "label": "Phones", "widget": "list"},
        {"name": "instagram", "label": "Instagram link", "widget": "string"},
        {"name": "video", "label": "YouTube video link", "widget": "string", "hint": "Shown on the home page. A normal link like https://www.youtube.com/watch?v=…"}]},
     {"name": "footer_text", "label": "Footer line", "widget": "string", "hint": "The year is added at the end automatically."},
     {"name": "images", "label": "Main photos", "widget": "object", "fields": [
        img("hero", "Home · big top photo (wide screens)", hint="Landscape photo."),
        img("hero_mobile", "Home · big top photo (phones)", hint="Portrait photo."),
        img("video_cover", "Home · video cover (before it plays)"),
        img("intro", "Home · photo next to the intro"),
        img("band", "Members page photo (also used when the site is shared)")]}]},
   {"name": "menu", "label": "Menu", "icon": "menu", "file": "_data/menu.yml",
    "fields": [
     {"name": "header", "label": "Top bar (wide screens)", "hint": "Drag to reorder.", "widget": "list", "types": menu_types},
     {"name": "menu", "label": "Full menu (☰ button)", "widget": "list", "types": menu_types}]},
   {"name": "theme", "label": "Look: colours and font", "icon": "palette", "file": "_data/theme.yml", "fields": [
     {"name": "background", "label": "Background", "widget": "color", "default": "#0c0404"},
     {"name": "surface", "label": "Cards and borders", "widget": "color", "default": "#171211"},
     {"name": "headings", "label": "Titles", "widget": "color", "default": "#ffffff"},
     {"name": "accent", "label": "Accent (links, pink)", "widget": "color", "default": "#e675b5"},
     {"name": "box", "label": "Upcoming-concerts box (green)", "widget": "color", "default": "#0a733b"},
     {"name": "body_font", "label": "Text font", "widget": "select", "default": "Questrial",
      "options": ["Questrial", "Inter", "Work Sans", "DM Sans", "Space Grotesk", "IBM Plex Sans"],
      "hint": "Titles keep the wide ARCHIVO font. The accessibility button's 'easier font' still works."}]},
 ],
 "collections": [
   {"name": "texts", "label": "Texts (CA · ES · EN)", "icon": "translate", "i18n": True,
    "description": "All the texts of the site, in the three languages.",
    "files": [{"name": "all", "label": "All texts", "file": "_data/i18n/{{locale}}.yml", "i18n": True, "fields": texts}]},
   {"name": "concerts", "label": "Concerts", "icon": "event",
    "files": [{"name": "list", "label": "Concert list", "file": "_data/concerts.yml", "fields": [
      {"name": "concerts", "label": "Concerts", "widget": "list", "root": True, "add_to_top": True, "collapsed": True,
       "summary": "{{fields.date}} · {{fields.venue}}", "label_singular": "concert",
       "hint": "Newest at the top. Concerts move to 'past' by themselves the day after.", "fields": [
        {"name": "date", "label": "Date", "widget": "datetime", "type": "date", "format": "YYYY-MM-DD"},
        {"name": "venue", "label": "Venue", "widget": "string"},
        {"name": "place", "label": "Neighbourhood, city", "widget": "string"},
        {"name": "time", "label": "Time (optional)", "widget": "string", "required": False, "hint": "e.g. 21:00"},
        {"name": "map", "label": "Google Maps link (optional)", "widget": "string", "required": False},
        {"name": "link", "label": "Tickets / event link (optional)", "widget": "string", "required": False},
        {"name": "residency", "label": "Superlunes (weekly residency)", "widget": "boolean", "default": False, "required": False},
        {"name": "end", "label": "Last Monday (Superlunes only)", "widget": "datetime", "type": "date", "format": "YYYY-MM-DD", "required": False},
        {"name": "label", "label": "Show this instead of the dates (optional)", "widget": "string", "required": False, "hint": "e.g. 2024, if you only know the year."},
        img("photo", "Photo (Superlunes, optional)", req=False)]}]}]},
   {"name": "members", "label": "Members", "icon": "groups",
    "files": [{"name": "list", "label": "Members", "file": "_data/members.yml", "fields": [
      {"name": "members", "label": "Members", "widget": "list", "root": True, "collapsed": True, "summary": "{{fields.name}}",
       "label_singular": "member", "thumbnail": "photo", "hint": "Drag to change the order.", "fields": [
        {"name": "name", "label": "Name", "widget": "string"},
        {"name": "role", "label": "Role", "widget": "select", "options": roles, "hint": "The role names are in Texts → Member roles."},
        img("photo", "Photo", folder="/assets/img/members", hint="It is cropped square (500 × 500) automatically."),
        {"name": "instagram", "label": "Instagram link (optional)", "widget": "string", "required": False}]}]}]},
   {"name": "gallery", "label": "Photo strip (home)", "icon": "photo_library",
    "files": [{"name": "list", "label": "Photo strip", "file": "_data/gallery.yml", "fields": [
      {"name": "photos", "label": "Photos", "widget": "list", "root": True, "collapsed": True, "thumbnail": "f", "summary": "{{fields.f}}",
       "label_singular": "photo", "hint": "In order. The small version is made automatically about a minute after saving.", "fields": [
        img("f", "Photo"),
        {"name": "o", "label": "Shape", "widget": "select", "default": "l",
         "options": [{"label": "Landscape (wide)", "value": "l"}, {"label": "Portrait (tall)", "value": "p"}]},
        {"name": "alt", "label": "Description for blind visitors (optional)", "widget": "string", "required": False}]}]}]},
   {"name": "pages", "label": "Pages", "label_singular": "page", "icon": "article",
    "description": "Simple extra pages (rider, press, a project…). Add them to the Menu to link them.",
    "folder": "_extra", "create": True, "delete": True, "extension": "md", "format": "frontmatter",
    "slug": "{{title}}", "summary": "{{title}}", "i18n": True,
    "fields": [
      {"name": "title", "label": "Title", "widget": "string", "i18n": True},
      {"name": "intro", "label": "Intro (optional)", "widget": "text", "i18n": True, "required": False},
      img("image", "Photo at the top (optional)", req=False) | {"i18n": "duplicate"},
      {"name": "image_alt", "label": "Photo description (optional)", "widget": "string", "i18n": True, "required": False},
      {"name": "description", "label": "Google description (optional)", "widget": "string", "i18n": True, "required": False},
      {"name": "body", "label": "Text", "widget": "richtext", "i18n": True,
       "hint": "Headings, bold, links, lists and photos."}]},
 ],
}
# Phones: a select with more than 5 options becomes a searchable dropdown, which opens the keyboard
# and closes again. Show every short list as radio buttons instead.
def radios(x):
    if isinstance(x, dict):
        if x.get("widget") == "select" and len(x.get("options", [])) <= 12: x["dropdown_threshold"] = 12
        for v in x.values(): radios(v)
    elif isinstance(x, list):
        for v in x: radios(v)
radios(cfg)

class D(yaml.SafeDumper): pass
D.add_representer(str, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style='"' if s in ("on","off","yes","no") else None))
head = "# Sveltia CMS config for lasenyal-web — generated by scripts/make_config.py — edit that script, not this file.\n# Docs: https://sveltiacms.app/en/docs\n"
open(out, "w").write(head + yaml.dump(cfg, Dumper=D, sort_keys=False, allow_unicode=True, width=200))
print("ok", len(texts), "text fields")
