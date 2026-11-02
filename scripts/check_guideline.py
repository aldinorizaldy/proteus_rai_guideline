#!/usr/bin/env python3
"""Check that the Guideline tab says exactly what the docx says.

    python scripts/check_guideline.py                 # the export in source/
    python scripts/check_guideline.py path/to/x.docx

For every top-level section of the docx, in order, the matching page in
docs/guideline/ (from the "Guideline" nav block in mkdocs.yml) must have
  * the same title,
  * the same list of headings, and
  * the same number of words.
Text before the first heading is compared with the marked block in
docs/guideline/index.md. Exits with status 1 on any difference, so CI fails
when the pages and the docx drift apart (e.g. after a hand edit).

The only content the converter removes on purpose is the Doc's own table of
contents (page numbers have no meaning on the web); it is removed here too.
Word counts are taken from pandoc's plain-text rendering on both sides, so
formatting (bold, links, table layout) does not matter, only the words.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import convert_source as cs  # noqa: E402

WORD_RE = re.compile(r"[^\W_]+(?:['’.-][^\W_]+)*")
MD_READER = "markdown-markdown_in_html_blocks"   # keep HTML tables whole


def words(s: str) -> int:
    return len(WORD_RE.findall(s))


def plain(blocks, api) -> str:
    doc = {"pandoc-api-version": api, "meta": {}, "blocks": blocks}
    return cs.pandoc(["-f", "json", "-t", "plain", "--wrap=none"], stdin=json.dumps(doc))


def html_words(blocks) -> int:
    """Words inside raw HTML blocks (e.g. tables written as HTML)."""
    raw = []
    cs.walk(blocks, lambda el: raw.append(el["c"][1])
            if el.get("t") == "RawBlock" and el["c"][0] == "html" else None)
    if not raw:
        return 0
    return words(cs.pandoc(["-f", "html", "-t", "plain", "--wrap=none"], stdin="\n".join(raw)))


def heading_list(blocks):
    out = []
    cs.walk(blocks, lambda el: out.append((el["c"][0], cs.stringify(el["c"][2]).strip()))
            if el.get("t") == "Header" else None)
    return out


def summarise(blocks, api, raw_html=False):
    n = words(plain(blocks, api)) + (html_words(blocks) if raw_html else 0)
    return {"headings": heading_list(blocks), "words": n}


def from_docx(src: Path):
    reader = ["--track-changes=accept"] if src.suffix.lower() == ".docx" else []
    if src.suffix.lower() == ".md":
        reader += ["-f", "markdown"]
    ast = json.loads(cs.pandoc([str(src), "-t", "json", *reader]))
    api = ast["pandoc-api-version"]
    blocks = cs.drop_doc_toc(cs.unwrap_quotes(ast["blocks"]))
    preamble, sections = cs.split_sections(blocks, 1)
    return api, summarise(preamble, api), [(t, summarise(bl, api)) for t, bl in sections]


def read_md(path: Path, api, between=None):
    md = path.read_text(encoding="utf-8")
    md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)        # front matter
    if between:
        m = re.search(rf"<!-- {between[0]} -->(.*?)<!-- {between[1]} -->", md, re.S)
        md = m.group(1) if m else ""
    ast = json.loads(cs.pandoc(["-f", MD_READER, "-t", "json"], stdin=md))
    return summarise(ast["blocks"], api, raw_html=True)


def nav_files():
    yml = cs.MKDOCS_YML.read_text(encoding="utf-8")
    m = re.search(r"#\s*BEGIN guideline-nav.*?$(.*?)#\s*END guideline-nav", yml, re.S | re.M)
    if not m:
        sys.exit("guideline-nav block not found in mkdocs.yml")
    return re.findall(r"guideline/([^\s\"']+\.md)", m.group(1))


def main() -> int:
    src = cs.pick_source(sys.argv[1] if len(sys.argv) > 1 else None)
    api, pre_docx, sections = from_docx(src)
    files = nav_files()
    problems = []

    if len(files) != len(sections):
        problems.append(f"{len(sections)} sections in the docx, {len(files)} pages in the nav")

    pre_md = read_md(cs.GUIDE / "index.md", api, ("BEGIN docx-preamble", "END docx-preamble"))
    if pre_md["words"] != pre_docx["words"]:
        problems.append(f"index.md (text before the first heading): "
                        f"{pre_docx['words']} words in the docx, {pre_md['words']} on the page")

    print(f"{'Section':52} {'docx':>6} {'page':>6}")
    for i, (title, d) in enumerate(sections):
        if i >= len(files):
            break
        path = cs.GUIDE / files[i]
        if not path.exists():
            problems.append(f"{files[i]}: missing")
            continue
        p = read_md(path, api)
        flag = "" if (p["words"] == d["words"] and p["headings"] == d["headings"]) else "  <-- differs"
        print(f"{title[:52]:52} {d['words']:6} {p['words']:6}{flag}")
        if p["headings"] != d["headings"]:
            dh = [f"H{l} {t}" for l, t in d["headings"]]
            ph = [f"H{l} {t}" for l, t in p["headings"]]
            missing = [h for h in dh if h not in ph]
            extra = [h for h in ph if h not in dh]
            detail = (f"missing {missing}" if missing else "") + (f" extra {extra}" if extra else "")
            problems.append(f"{files[i]}: headings differ from the docx {detail or '(order)'}")
        if p["words"] != d["words"]:
            problems.append(f"{files[i]}: {d['words']} words in the docx, {p['words']} on the page")

    if problems:
        print("\nThe Guideline tab does not match the docx:")
        for pr in problems:
            print(f"  - {pr}")
        print("Re-run `python scripts/build_from_docx.py` and do not edit docs/guideline/ by hand.")
        return 1
    print(f"\nOK: {len(sections)} sections match the docx ({src.name}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
