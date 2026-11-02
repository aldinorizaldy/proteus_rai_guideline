# PROTEUS Responsible AI Guideline

[![Deploy](https://github.com/aldinorizaldy/proteus_rai_guideline/actions/workflows/deploy.yml/badge.svg)](https://github.com/aldinorizaldy/proteus_rai_guideline/actions/workflows/deploy.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-6F309E.svg)](LICENSE)

The Responsible AI (RAI) Guideline of **PROTEUS – The Copernicus Agent for
Next-Generation Environmental Intelligence**, a Horizon Europe project
(GA No. 101296397, managed by HaDEA). The guideline is owned by the
Helmholtz-Zentrum Dresden-Rossendorf (HZDR), the consortium's RAI lead.

This repository publishes the guideline as a website with a downloadable PDF,
and archives every release on Zenodo with a citable DOI.

**Live site:** <https://aldinorizaldy.github.io/proteus_rai_guideline/>
**PDF:** <https://aldinorizaldy.github.io/proteus_rai_guideline/pdf/proteus-rai-guideline.pdf>

> **Moving the repository** (e.g. to an organisation account): GitHub redirects
> the old URLs, but the site URL changes. Update the owner and repository name
> everywhere, then push:
>
> ```bash
> grep -rl "aldinorizaldy/proteus_rai_guideline\|aldinorizaldy.github.io" --exclude-dir=site --exclude-dir=.git . \
>   | xargs sed -i '' -e 's#aldinorizaldy/proteus_rai_guideline#<owner>/<repo>#g' \
>                     -e 's#aldinorizaldy.github.io/proteus_rai_guideline#<owner>.github.io/<repo>#g'
> ```
>
> Also fill in the real authors in `CITATION.cff`, `.zenodo.json` and `docs/cite.md`.

---

## Build locally

Requires Python 3.9+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && mkdocs serve
```

Open <http://127.0.0.1:8000>. Pages reload as you edit. Before pushing, check
the build the same way CI does:

```bash
mkdocs build --strict
```

**PDF (optional locally – CI always builds it):**

```bash
python -m playwright install chromium     # once; or add `--channel chrome` below to use installed Chrome
mkdocs build --strict && python scripts/build_pdf.py
# -> site/pdf/proteus-rai-guideline.pdf
```

`mkdocs serve` does not create the PDF, so the "PDF" buttons return 404 locally
until you run the commands above.

## Update the content from the Google Doc

The Google Doc is the master copy, and the docx exported from it is the only
content source for the site. To publish a new draft:

1. In Google Docs: **File → Download → Microsoft Word (.docx)**.
2. Save it in `source/`, replacing the old export (exactly one `.docx` there).
3. Build everything that comes from the docx, then check it:

   ```bash
   python scripts/build_from_docx.py      # Guideline pages, At a glance, Quick tools, data
   python scripts/check_guideline.py      # Guideline tab == docx (headings, word counts)
   python -m unittest discover -s tests   # optional: pipeline test on a sample docx
   ```

4. Review with `mkdocs serve`, then commit `source/`, `docs/` and `mkdocs.yml`
   and push. CI repeats steps 3 and redeploys.

What is generated (do not edit by hand, the next build overwrites it):

| Output | From |
|---|---|
| `docs/guideline/*.md` | the whole docx, verbatim, one page per Heading 1 |
| `docs/at-a-glance.md` | sentences and lists quoted from sections 1–4 |
| `docs/tools/**.md`, `docs/data/*.json` | the annexes (checklist, use cases, risk tiers, compliance card, worked example) |
| `docs/downloads/proteus-rai-guideline.docx` | the docx itself (build time only, not committed) |

Hand-maintained: `docs/data/risk_check.yml` (questions, logic and triggers of
the risk self-check, for the RAI lead), the page layouts in
`scripts/templates/`, and the home, cite, changelog and contribute pages.

The formatting conventions the tools rely on (annex tables, use-case headings,
requirement IDs) are in [`source/README.md`](source/README.md). While an annex
is still an outline, its tool shows a "Coming soon" placeholder.

## Release a new version

1. Add the changes under `## [Unreleased]` in [`CHANGELOG.md`](CHANGELOG.md).
2. Set the version and date everywhere (site badge, PDF cover, `CITATION.cff`, cite page):

   ```bash
   python scripts/bump_version.py 1.0 2027-03-31
   ```

3. Commit and push to `main`, then tag:

   ```bash
   git tag v1.0 && git push origin v1.0
   ```

4. On GitHub: **Releases → Draft a new release**, choose tag `v1.0`, paste the
   changelog entry, optionally attach the PDF (download it from the live site),
   and **Publish release**.
5. Zenodo archives the release automatically and mints a DOI. After the
   **first** release, copy the *concept DOI* (it resolves to the latest
   version) from the Zenodo record and set it once:

   ```bash
   python scripts/bump_version.py 1.0 2027-03-31 --doi 10.5281/zenodo.1234567
   ```

   Commit and push. Also update the DOI badge at the top of this README.

## One-time setup

1. **GitHub Pages:** repository **Settings → Pages → Build and deployment →
   Source: GitHub Actions**.
2. **Zenodo:** sign in at <https://zenodo.org> with GitHub, open
   **Account → GitHub**, and switch on this repository. Then publish a GitHub
   release (step 4 above). Zenodo reads the metadata from `.zenodo.json`.
   - If the Zenodo upload fails with a grant error, the grant ID
     `10.13039/501100000780::101296397` is not in Zenodo's funder database yet.
     Remove the `grants` block from `.zenodo.json`, re-release, and add the
     grant in the Zenodo record by hand later.
3. **Brand assets:** the PNGs in `docs/assets/` were extracted from the
   PROTEUS PowerPoint template. If you replace them, keep the file names and run
   `python scripts/prepare_assets.py` to regenerate the transparent logo,
   favicons and hero image. CI also runs this.

## Repository layout

```text
docs/                    Website content (Markdown)
  guideline/             One page per guideline section (generated)
  at-a-glance.md         5-minute summary (generated)
  tools/                 Quick tools pages (generated)
  data/                  Tool data (generated JSON; risk_check.yml is hand-edited)
  assets/                Logos, globe, EU flag, favicons, extracted figures
  stylesheets/           extra.css (PROTEUS theme), tools.css (tools, banner)
  javascripts/tools.js   Checklist, risk self-check, compliance card (plain JS)
overrides/               Material theme overrides (hero, header PDF button, EU footer)
includes/                Shared link definitions and the PDF cover page
scripts/
  build_from_docx.py     docx -> Guideline pages, At a glance, Quick tools, data
  convert_source.py      docx -> Guideline pages (library used by the above)
  check_guideline.py     Fails if the Guideline tab differs from the docx
  templates/             Layouts of the generated At a glance and tool pages
  build_pdf.py           Built site -> PDF (headless Chromium)
  prepare_assets.py      Favicons, transparent logo, optimised hero image
  bump_version.py        Set version, date and DOI everywhere
source/                  The Google Doc export (+ formatting conventions)
tests/                   Pipeline test with a sample docx
.github/workflows/       Build + deploy to GitHub Pages
CITATION.cff, .zenodo.json   Citation and Zenodo archiving metadata
```

## Licence

- Guideline text and figures: [CC BY 4.0](LICENSE)
- Code (scripts, templates, styles, workflows): [MIT](LICENSE-code)

---

Funded by the European Union under GA No. 101296397. Views and opinions
expressed are however those of the author(s) only and do not necessarily
reflect those of the European Union or HaDEA. Neither the European Union nor
the granting authority can be held responsible for them.
