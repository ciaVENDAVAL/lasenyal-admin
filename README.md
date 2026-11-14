# lasenyal-admin

Admin for **La Senyal**: edit the website and swap PDFs from the browser. No code, no AI.

**Address:** https://ciavendaval.github.io/lasenyal-admin/ (GitHub Pages from `main`, root)

| Page | Edits | What |
|---|---|---|
| `/` | — | Start page and sign-in help |
| `/web/` | `lasenyal-web` | Texts (CA·ES·EN), concerts, members, photo strip, extra pages, menu, contact/footer, main photos, colours and font, **PDFs** (`pdf/` + `_data/downloads.yml` → short links `/dossier/<lang>/`) |

[Sveltia CMS](https://sveltiacms.app) (free, open source, loaded from a CDN). Every save is a commit on `main` of
lasenyal-web; GitHub Pages rebuilds in 1–2 minutes; everything can be undone from the history.
lasenyal-docs is the private office repo and is **not** edited here.

## Sign in
GitHub token: fine-grained, owner `ciaVENDAVAL`, repo `lasenyal-web`, *Contents: read and write* (steps on the start page).
For a "Sign in with GitHub" button instead, deploy [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth)
(free Cloudflare Worker) and add `base_url:` to `web/config.yml`.

## Files
- `web/config.yml` — **generated**: edit `scripts/make_config.py`, then
  `python3 scripts/make_config.py ../lasenyal-web web/config.yml`.
  Run it again whenever text keys are added or removed in `lasenyal-web/_data/i18n/*.yml`.
- File names are **not** slugified on upload (`slugify_filename: false`), so `LaSenyal_CA_presskit_…pdf` keeps its
  capitals and "same name → Replace" really replaces.
- Never serve an admin from a folder with the same name as an asset folder it writes to (e.g. `pdf/`):
  Sveltia refuses to write there.

## Moving to admin.lasenyal.com (optional)
Add a `CNAME` file with `admin.lasenyal.com`, a DNS `CNAME admin → ciavendaval.github.io`,
and change `logo: src:` in `web/config.yml` (in `scripts/make_config.py`) from `/lasenyal-admin/logo.png` to `/logo.png`.
