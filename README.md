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

The Google Doc is the master copy. To publish a new draft:

1. In Google Docs: **File → Download → Microsoft Word (.docx)**. Use
   *Heading 1* for each top-level section (Introduction, Principles, …). Text
   before the first Heading 1 goes on the guideline overview page.
2. Save it as `source/<name>.docx`. Replace the old export rather than adding a second one.
3. Convert:

   ```bash
   python scripts/convert_source.py         # --level 2 to split at Heading 2 instead
   ```

   This writes one page per section to `docs/guideline/NN-<slug>.md`, extracts
   images to `docs/assets/guideline-media/`, and regenerates the "Guideline"
   navigation in `mkdocs.yml`, the overview page and the section list of
   the feedback issue template. Headings, tables, figures with captions and
   footnotes are preserved. The text itself is not changed.
4. Review with `mkdocs serve`, then commit `source/`, `docs/` and `mkdocs.yml`
   and push. The site redeploys automatically.

Do not edit the generated `docs/guideline/NN-*.md` files by hand. The next
conversion overwrites them. All other pages (home, cite, changelog,
contribute) are maintained directly in `docs/`.

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
  assets/                Logos, globe, EU flag, favicons, extracted figures
  stylesheets/extra.css  PROTEUS colour tokens and theme
overrides/               Material theme overrides (hero, header PDF button, EU footer)
includes/                Shared link definitions and the PDF cover page
scripts/
  convert_source.py      Google Doc export -> Markdown pages (pandoc)
  build_pdf.py           Built site -> PDF (headless Chromium)
  prepare_assets.py      Favicons, transparent logo, optimised hero image
  bump_version.py        Set version, date and DOI everywhere
source/                  Google Doc exports
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
