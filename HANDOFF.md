# HANDOFF — browser admin + "edit on the page" for a company website

Model: **La Senyal** (repos `ciaVENDAVAL/lasenyal-web`, `ciaVENDAVAL/lasenyal-admin`). Reuse it for any other site of
tyle fernández (VENDAVAL, Las Marikarmen, Cia. Filigranes…). Read the company handoff ("how to organise a company") first:
this one only adds the editing tools. Replace `<co>` with the company's short name. Ask tyle only what is unclear (max 3 numbered questions).

**Goal:** tyle (and the band) change texts, photos, PDFs, concerts, menu and colours **from the phone, without code and without AI**,
and every change is a normal commit on GitHub (history = undo).

**House rules that shaped it:** no Google, no Amazon wherever possible (no Google Fonts, no DeepL — it runs on AWS — no Google
Translate/Gemini, video on PeerTube). Free and open-source tools. Everything works on a phone.

---

## 1. The four pieces

| Piece | Lives in | What it does |
|---|---|---|
| **Forms admin** (Sveltia CMS) | repo `<co>-admin` → `https://<org>.github.io/<co>-admin/` | Start page + `/web/`: forms for every text (CA·ES·EN side by side), lists (concerts, members, gallery), simple extra pages, menu, contact/footer/main photos, colours + font, PDFs. Each Save = 1 commit. |
| **Edit on the page** | `<co>-web/assets/js/edit.js` + 1-line loader in the page template | Open any page with `#edit` → tap a text and type, tap a photo / PDF link to replace it, move between pages and languages, **Publish** once = 1 commit. |
| **Auto-translate** | `<co>-web/tools/translate.py` + `.github/workflows/translate.yml` | A text changed in ONE language is translated into the others after the push, with **Softcatalà's open models** run inside the workflow (no key, no account). `[no-translate]` in the commit message skips it. |
| **Photo prep** | `<co>-web/tools/photos.py` + `.github/workflows/photos.yml` | After an upload: keeps the untouched original in `source-images/`, shrinks to 1800 px, makes the small copy, crops portraits square. |

Login for both editors: one **GitHub fine-grained token** (owner = org, only the `<co>-web` repo, *Contents: read and write*), pasted
once per browser. On `*.github.io` the on-page editor reuses the admin's token (same origin, localStorage key `sveltia-cms.user`);
on a custom domain it asks once and keeps it in `localStorage["ls-edit-token"]`.

## 2. Copy from La Senyal

| From | To | Change |
|---|---|---|
| `lasenyal-admin/index.html`, `fonts/`, `favicon.png`, `logo.png` | `<co>-admin/` | texts, colours, logo, links |
| `lasenyal-admin/web/index.html` | `<co>-admin/web/` | — (loads Sveltia from unpkg) |
| `lasenyal-admin/scripts/make_config.py` | `<co>-admin/scripts/` | **rewrite the field lists for this site** (it generates `web/config.yml`; the Texts form is generated from the CA language file) |
| `lasenyal-web/assets/js/edit.js` | `<co>-web/` (any static folder) | nothing — configure it with `window.LS_EDIT` (§4) |
| loader at the end of `lasenyal-web/_layouts/default.html` | the site's page template, before `</body>` | `repo`, `base`, `lang`, and the settings below |
| `lasenyal-web/tools/translate.py`, `tools/facts.yml`, `.github/workflows/translate.yml` | `<co>-web/` | the 4 settings at the top of `translate.py`; names not to translate in `facts.yml` |
| `lasenyal-web/tools/photos.py`, `.github/workflows/photos.yml` | `<co>-web/` | folder names if different |
| `lasenyal-web/tools/check.py` | `<co>-web/` (if the site has no checker yet) | paths |

## 3. Set-up checklist

1. **Data first.** Every text the admin should edit must live in data files, not in templates: one texts file per language
   (`_data/i18n/<lang>.yml` in Jekyll, `content/i18n/<lang>.json` in the build.py model) + one file per list (concerts, members,
   gallery, downloads, site settings, menu, theme). Templates only read them. Photo fields accept a full path **or** a bare file
   name (`{% assign f = x.photo | split: "/" | last %}`).
2. **Repo `<co>-admin`** (public, tyle creates it): copy §2, write `make_config.py`, generate `web/config.yml`, validate it against
   Sveltia's JSON schema (`npm pack @sveltia/cms` → `schema/sveltia-cms.json`). GitHub Pages: main / root.
3. **Loader + `edit.js`** in `<co>-web`; set `window.LS_EDIT` (§4).
4. **Workflows** `translate.yml` (+ `photos.yml` if photos are uploaded raw). Both commit with `GITHUB_TOKEN` and then call
   `gh api -X POST repos/<repo>/pages/builds`, because a push made by `GITHUB_TOKEN` doesn't start other workflows or a Pages build.
5. **build.py sites (VENDAVAL model, output in `docs/`):** the editors change the *sources*, so add a workflow that runs
   `python3 build.py` on every push to `content/**`, `src/**`, `static/**` and commits `docs/` (then the Pages-build call).
   Order: translate first, then build (or run translate.py inside the build workflow before build.py).
6. **Fonts and third parties:** fonts as woff2 in the repo + `@font-face` (no Google Fonts); video as PeerTube embed
   (`https://<instance>/videos/embed/<id>?autoplay=1&muted=1&loop=1&title=0&warningTitle=0&peertubeLink=0&p2p=0`).
7. **Test before handing over** (no real token needed):
   - Sveltia: copy the admin to a temp folder, set `backend: {name: test-repo}`, seed the browser's OPFS folder
     `sveltia-cms-test` with the repo files (Playwright), remove the line that clears it in the local copy of `sveltia-cms.js`,
     then open each collection, edit, Save and diff the written files; build the site with them.
   - `edit.js`: serve the built site, mock `api.github.com` with Playwright `route()` (ref, contents, blobs, trees, commits, refs),
     edit a text / photo / PDF on a phone-sized viewport, Publish, check the commit tree and the YAML/JSON diff.
   - `translate.py`: commit a change in one language in a temp clone and run it against `HEAD~1`.
8. **Tell tyle:** how to make the token (steps are on the start page), the admin address, `…/#edit`, that translations must be
   checked, and the [no-translate] / "Translate" switch for fixing one language only.
9. Session-log line in the company's fact sheet; rules in `CLAUDE.md` / `UPDATING.md` of `<co>-web`.

## 4. Settings of `edit.js` (`window.LS_EDIT`)

```html
<script>try{if(location.hash==="#edit"||sessionStorage.getItem("ls-edit")){sessionStorage.setItem("ls-edit","1");
window.LS_EDIT={repo:"<org>/<co>-web",branch:"main",base:"{{ site.baseurl }}",lang:"{{ page.lang }}",
  files:["content/i18n/{lang}.json","content/data.json"],            /* texts that become editable; .yml or .json */
  skip:["url","href","date","photo","pdf"],                           /* keys never edited as text */
  img:{root:"/img/",small:"/img/sm/",large:"/img/lg/"},               /* replaceable images; small copy → original */
  pdf:{downloads:"content/downloads.json",name:"/pdf/<CO>_{LANG}_{kind}_{yyyy-mm}.pdf",short:"/dossier/{lang}/"}, /* or null */
  admin:"https://<org>.github.io/<co>-admin/"};
var s=document.createElement("script");s.type="module";s.src="<base>/assets/js/edit.js";document.body.appendChild(s)}
else addEventListener("hashchange",function(){if(location.hash==="#edit")location.reload()})}catch(e){}</script>
```
Defaults (if omitted) are La Senyal's Jekyll paths. `pdf.downloads` is a file `{ kind: { ca: "/pdf/…", es: …, en: … } }`;
links to those PDFs (or to the short link) open the "replace PDF" dialog. In a build.py site `base` is `""` and `lang` comes from
the template variable.

`translate.py` settings (top of the file): `LANGS` (first = reference), `I18N` (`_data/i18n/{lang}.yml` or
`content/i18n/{lang}.json`), `PAGES` (Markdown pages folder per language, or `None`), `SKIP` (keys never translated).

## 5. Lessons learned (don't repeat them)

- **Sveltia refuses to write into a folder with the same path as the page it runs on** (admin at `/pdf/` can't write `pdf/`). Name admin folders differently (`/web/`, `/documents/`).
- Set `media_libraries.default.config.slugify_filename: false`, or uploads are lower-cased and "same name → Replace" silently makes a second file.
- On phones a `select` with > 5 options becomes a search box that opens and closes the keyboard: set `dropdown_threshold: 12` on every select.
- Sveltia writes YAML 1.2, Jekyll reads YAML 1.1: never use keys like `on`/`off`/`yes`/`no` (they become true/false); use `output.yaml.quote: double` so times like `21:00` stay text.
- One Sveltia file collection per texts file, listing **every** key (generate the fields from the reference language file): keys missing from the form may be dropped on save.
- `edit.js` finds texts by exact wording: a text glued to other text or changed by a filter isn't editable there (use the forms). Read `textContent`, never `innerText` (CSS `text-transform: uppercase` would be saved). The same wording in two keys shows tick boxes.
- Adding `#edit` to an open page doesn't reload it: the loader listens to `hashchange`.
- Unpublished edits must survive page changes: texts in `sessionStorage`, files in IndexedDB.
- Commit through the Git Data API (blobs → tree → commit → ref) = one commit per Publish; re-read each file at the current head before applying edits, so admin edits made meanwhile are kept.
- Softcatalà models (https://github.com/Softcatala/nmt-models, MIT, CTranslate2 + SentencePiece): CA↔ES excellent, CA↔EN good, ES↔EN via CA. Split sentences, keep emojis / `{placeholders}` / links / bold / `6 × 4` out of the text, copy accented names back where the English model prints ⁇. Cache the models (≈350 MB) with `actions/cache`. Apertium is the fallback (good CA↔ES, poor EN). Always ask a human to check.
- Keep the check script from flagging font licences and rule files (they contain "fee", "budget"…).

## 6. Per-site notes

- **La Senyal:** Jekyll, `_data/`, done (2026-11-16). Admin `ciavendaval.github.io/lasenyal-admin`, editor `ciavendaval.github.io/lasenyal-web/#edit`.
- **VENDAVAL model sites (build.py → docs/):** need §3.5 (build workflow) and JSON settings (§4). Texts in `content/i18n/<lang>.json`, data in `content/data.json`, PDFs registered in `content/data.json` → downloads (point `pdf.downloads` at that file or split it out).
