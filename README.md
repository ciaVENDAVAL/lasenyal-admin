# lasenyal-admin

Admin for **La Senyal**: edit the website and the PDFs from the browser. No code, no AI.

**Address:** https://ciavendaval.github.io/lasenyal-admin/
(GitHub Pages: Settings → Pages → *Deploy from a branch* → `main` / root.)

| Page | Edits repo | What |
|---|---|---|
| `/` | — | Start page with the two buttons and sign-in help |
| `/web/` | `lasenyal-web` | Texts (CA·ES·EN), concerts, members, photo strip, extra pages, menu, contact/footer, main photos, colours and font |
| `/documents/` | `lasenyal-docs` | PDFs (replace = upload with the same name), names on the documents page |

Both are [Sveltia CMS](https://sveltiacms.app) (free, open source, loaded from a CDN). Every save is a commit on `main`,
so GitHub Pages rebuilds the site in 1–2 minutes and every change can be undone from the history.

## Sign in

With a GitHub token (see the start page for the steps): fine-grained, owner `ciaVENDAVAL`,
repos `lasenyal-web` + `lasenyal-docs`, permission *Contents: read and write*.
For a "Sign in with GitHub" button instead, deploy [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth)
(free Cloudflare Worker) and add `base_url:` to both `config.yml` files.

## Files

- `web/config.yml` — **generated**: edit `scripts/make_config.py`, then
  `python3 scripts/make_config.py ../lasenyal-web web/config.yml`.
  Run it again whenever text keys are added or removed in `lasenyal-web/_data/i18n/*.yml`.
- `documents/config.yml` — written by hand.
- The PDF admin must **not** be served from a folder called `pdf/` (Sveltia refuses to write to an asset folder
  with the same path as the page it runs on). That's why it is `documents/`.

## Moving to admin.lasenyal.com (optional)

Add a `CNAME` file with `admin.lasenyal.com`, a DNS `CNAME admin → ciavendaval.github.io`,
and change `logo: src:` in both configs from `/lasenyal-admin/logo.png` to `/logo.png`.
