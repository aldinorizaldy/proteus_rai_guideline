#!/usr/bin/env python3
"""Set the guideline version and release date everywhere it appears.

    python scripts/bump_version.py 1.0 2027-03-31
    python scripts/bump_version.py 1.0            # date defaults to today

Updates mkdocs.yml (home badge, PDF), CITATION.cff, docs/cite.md and turns
the "## [Unreleased]" changelog entries into "## [X.Y] – DATE".
Optionally also sets the DOI:  --doi 10.5281/zenodo.1234567
"""
import argparse
import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sub(path: str, pattern: str, repl: str, count: int = 0) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    new, n = re.subn(pattern, repl, text, count=count, flags=re.M)
    if n == 0:
        print(f"  ! pattern not found in {path}: {pattern}")
    p.write_text(new, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="MAJOR.MINOR, e.g. 1.0")
    ap.add_argument("date", nargs="?", default=dt.date.today().isoformat(),
                    help="release date YYYY-MM-DD (default: today)")
    ap.add_argument("--doi", help="Zenodo DOI, e.g. 10.5281/zenodo.1234567")
    a = ap.parse_args()
    if not re.fullmatch(r"\d+\.\d+", a.version):
        raise SystemExit("Version must look like 1.0")
    dt.date.fromisoformat(a.date)
    year = a.date[:4]

    sub("mkdocs.yml", r'^(\s*version:\s*)"[^"]*"', rf'\g<1>"{a.version}"')
    sub("mkdocs.yml", r'^(\s*release_date:\s*)"[^"]*"', rf'\g<1>"{a.date}"')
    sub("CITATION.cff", r'^version:.*$', f'version: "{a.version}"')
    sub("CITATION.cff", r'^date-released:.*$', f'date-released: "{a.date}"')
    sub("docs/cite.md", r'\(Version [^)]*\)', f"(Version {a.version})")
    sub("docs/cite.md", r'^(\s*version\s*=\s*)\{[^}]*\}', rf'\g<1>{{{a.version}}}')
    sub("docs/cite.md", r'^(\s*year\s*=\s*)\{[^}]*\}', rf'\g<1>{{{year}}}')
    sub("docs/cite.md", r'\(\d{4}\)\. PROTEUS', f"({year}). PROTEUS")

    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    if f"## [{a.version}]" not in text:
        text = text.replace("## [Unreleased]",
                            f"## [Unreleased]\n\n## [{a.version}] – {a.date}", 1)
        changelog.write_text(text, encoding="utf-8")

    if a.doi:
        for f in ("mkdocs.yml", "CITATION.cff", "docs/cite.md"):
            sub(f, r"10\.5281/zenodo\.[0-9X]+", a.doi)
        cite = ROOT / "docs" / "cite.md"
        cite.write_text(re.sub(r"<!-- BEGIN doi-placeholder.*?<!-- END doi-placeholder -->\n\n?",
                               "", cite.read_text(encoding="utf-8"), flags=re.S),
                        encoding="utf-8")

    print(f"Version {a.version} ({a.date}) set. Review with `git diff`, then commit and tag v{a.version}.")


if __name__ == "__main__":
    main()
