#!/usr/bin/env python3
"""Convert the Google Doc export in source/ into one Markdown page per
top-level section under docs/guideline/.

    python scripts/convert_source.py                  # newest .docx/.md in source/
    python scripts/convert_source.py source/RAI.docx  # a specific file
    python scripts/convert_source.py --level 2        # split at Heading 2 instead

What it does (content is converted, never rewritten):
  * pandoc parses the export (tracked changes accepted, comments dropped);
  * the document is split at every heading of --level (default: Heading 1);
    text before the first heading goes to docs/guideline/index.md;
  * headings, tables, footnotes (kept per section) and figures with captions
    are preserved; images are extracted to docs/assets/guideline-media/
    and large ones re-encoded as WebP;
  * the Doc's own table of contents is dropped (the site has navigation);
  * indented paragraphs (read by pandoc as block quotes) become normal
    paragraphs, unless --keep-quotes is given;
  * internal links (e.g. a table of contents or "see section 3") are pointed
    at the right page and heading;
  * the "Guideline" nav block in mkdocs.yml, the overview page and the section
    list of the "Feedback on a section" issue template are regenerated.

Previously generated section pages (docs/guideline/NN-*.md) are replaced.
Requires pandoc >= 3.1: from `pip install pypandoc_binary` (in
requirements.txt) or a system install on PATH.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source"
GUIDE = ROOT / "docs" / "guideline"
MEDIA = ROOT / "docs" / "assets" / "guideline-media"
MKDOCS_YML = ROOT / "mkdocs.yml"
ISSUE_TEMPLATE = ROOT / ".github" / "ISSUE_TEMPLATE" / "feedback-section.yml"

# Markdown dialect that Python-Markdown (+ the extensions in mkdocs.yml)
# reads natively: footnotes, pipe tables, {#id} on headings, ^sup^, ~sub~,
# ~~strike~~, definition lists. Tables pandoc cannot express as pipe tables
# (merged or multi-paragraph cells) are written as HTML tables.
WRITER = ("markdown_strict+pipe_tables+footnotes+header_attributes+raw_html"
          "+superscript+subscript+strikeout+definition_lists"
          "+fenced_code_blocks+backtick_code_blocks")


# --------------------------------------------------------------------------- #
# pandoc helpers
# --------------------------------------------------------------------------- #
def find_pandoc() -> str:
    exe = shutil.which("pandoc")
    if exe:
        return exe
    try:
        import pypandoc  # type: ignore
        return pypandoc.get_pandoc_path()
    except Exception:
        sys.exit("pandoc not found: `pip install -r requirements.txt` "
                 "or install pandoc from https://pandoc.org/installing.html")


def pandoc(args, stdin=None, cwd=None) -> str:
    res = subprocess.run([find_pandoc(), *args], input=stdin, capture_output=True,
                         text=True, encoding="utf-8", cwd=cwd)
    if res.returncode != 0:
        sys.exit(f"pandoc failed:\n{res.stderr}")
    if res.stderr.strip():
        print(res.stderr.strip(), file=sys.stderr)
    return res.stdout


def stringify(node) -> str:
    """Plain text of an AST fragment."""
    if isinstance(node, list):
        return "".join(stringify(n) for n in node)
    if not isinstance(node, dict):
        return ""
    t, c = node.get("t"), node.get("c")
    if t == "Str":
        return c
    if t in ("Space", "SoftBreak", "LineBreak"):
        return " "
    if t in ("Code", "Math"):
        return c[1]
    if t == "Note":
        return ""
    if isinstance(c, list):
        return "".join(stringify(x) for x in c if isinstance(x, (list, dict)))
    return ""


def walk(node, fn):
    """Depth-first walk calling fn(dict) on every element."""
    if isinstance(node, list):
        for n in node:
            walk(n, fn)
    elif isinstance(node, dict):
        fn(node)
        c = node.get("c")
        if isinstance(c, (list, dict)):
            walk(c, fn)


def slugify(text: str, maxlen: int = 50) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"^[\d.\s]+", "", text)            # drop "1." / "2.3 " numbering
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    if len(text) > maxlen:                            # cut at a word boundary
        text = text[:maxlen + 1].rsplit("-", 1)[0]
    return text.strip("-") or "section"


# --------------------------------------------------------------------------- #
# AST transformations
# --------------------------------------------------------------------------- #
def fix_images(blocks, page_dir: Path) -> None:
    """Make image paths relative to the page and drop size attributes
    (pandoc would otherwise emit raw <img> tags MkDocs cannot rewrite)."""
    def fn(el):
        if el.get("t") == "Image":
            attr, _alt, target = el["c"]
            attr[2] = []                       # key-values: width/height
            src = target[0]
            p = Path(src)
            if not p.is_absolute():
                p = (ROOT / p).resolve()
            if p.exists():
                target[0] = Path(rel(p, page_dir)).as_posix()
    walk(blocks, fn)


def drop_doc_toc(blocks, min_run: int = 3):
    """Remove the Google Doc's own table of contents: a run of paragraphs
    that each contain nothing but one internal link (e.g. "1.1 Scope  4").
    The website has its own navigation, and page numbers mean nothing there."""
    def is_toc_entry(b):
        if b.get("t") not in ("Para", "Plain"):
            return False
        inl = [x for x in b["c"] if x.get("t") not in ("Space", "SoftBreak", "LineBreak")]
        return (len(inl) == 1 and inl[0].get("t") == "Link"
                and inl[0]["c"][2][0].startswith("#"))
    out, run = [], []
    for b in blocks + [{"t": "Null"}]:
        if is_toc_entry(b):
            run.append(b)
            continue
        if len(run) < min_run:
            out.extend(run)
        else:
            print(f"  dropped the Doc's table of contents ({len(run)} entries)")
        run = []
        if b.get("t") != "Null":
            out.append(b)
    return out


def unwrap_quotes(blocks):
    """Google Docs exports indented paragraphs as Word indentation, which
    pandoc reads as block quotes. Turn them back into normal paragraphs
    (disable with --keep-quotes if the Doc uses real quotations)."""
    out = []
    for b in blocks:
        t, c = b.get("t"), b.get("c")
        if t == "BlockQuote":
            out.extend(unwrap_quotes(c))
            continue
        if t == "Div":
            c[1] = unwrap_quotes(c[1])
        out.append(b)
    return out


def optimize_media(blocks, max_kb: int = 300, max_px: int = 1600) -> None:
    """Re-encode large extracted raster images as WebP (resized to at most
    `max_px` on the long side) and point the image references at them."""
    try:
        from PIL import Image as PILImage
    except ImportError:
        print("  ! Pillow not installed – images left unoptimised")
        return
    done = {}
    for p in sorted(MEDIA.rglob("*")):
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"):
            continue
        if p.stat().st_size <= max_kb * 1024:
            continue
        im = PILImage.open(p)
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        im.thumbnail((max_px, max_px), PILImage.LANCZOS)
        dst = p.with_suffix(".webp")
        im.save(dst, "WEBP", quality=85, method=6)
        print(f"  {p.name}: {p.stat().st_size // 1024} KB -> {dst.name}: "
              f"{dst.stat().st_size // 1024} KB")
        p.unlink()
        done[p.relative_to(ROOT).as_posix()] = dst.relative_to(ROOT).as_posix()

    def fn(el):
        if el.get("t") == "Image":
            target = el["c"][2]
            key = Path(target[0]).as_posix()
            if key in done:
                target[0] = done[key]
    if done:
        walk(blocks, fn)


def rel(path: Path, start: Path) -> str:
    return os.path.relpath(path, start)


def figures_to_md_in_html(blocks):
    """pandoc Figure -> <figure markdown> with a normal Markdown image and a
    <figcaption>, so MkDocs validates and rewrites the image path."""
    out = []
    for b in blocks:
        if b.get("t") == "Figure":
            _attr, caption, body = b["c"]
            cap_blocks = caption[1] or []
            out.append({"t": "RawBlock", "c": ["html", '<figure markdown="1">']})
            out.extend(figures_to_md_in_html(body))
            if cap_blocks:
                inl = []
                for cb in cap_blocks:
                    inl.extend(cb.get("c", []))
                out.append({"t": "RawBlock", "c": ["html", '<figcaption markdown="span">']})
                out.append({"t": "Plain", "c": inl})
                out.append({"t": "RawBlock", "c": ["html", "</figcaption>"]})
            out.append({"t": "RawBlock", "c": ["html", "</figure>"]})
        else:
            c = b.get("c")
            if b.get("t") in ("BlockQuote", "Div") and isinstance(c, list):
                if b["t"] == "BlockQuote":
                    b["c"] = figures_to_md_in_html(c)
                else:
                    b["c"][1] = figures_to_md_in_html(c[1])
            out.append(b)
    return out


def split_sections(blocks, level: int):
    """Return (preamble_blocks, [(title, blocks), ...])."""
    preamble, sections = [], []
    for b in blocks:
        if b.get("t") == "Header" and b["c"][0] == level:
            sections.append([stringify(b["c"][2]).strip(), [b]])
        elif sections:
            sections[-1][1].append(b)
        else:
            preamble.append(b)
    # Promote headings so every page starts at H1 when splitting deeper.
    if level > 1:
        for _t, bl in sections:
            for b in bl:
                if b.get("t") == "Header":
                    b["c"][0] = max(1, b["c"][0] - (level - 1))
    return preamble, [(t, bl) for t, bl in sections]


def resolve_internal_links(preamble, sections, filenames):
    """Point '#id' links at the page and heading that contain the target.
    Ids on spans/bookmarks are mapped to their nearest preceding heading.
    Ids that are never linked to are dropped so headings get MkDocs slugs."""
    owner = {}                # id -> (page index or None for index.md, heading id)

    def index_ids(blocks, page):
        current = None
        for b in blocks:
            if b.get("t") == "Header":
                current = b["c"][1][0] or None
                if current:
                    owner[current] = (page, current)

            def fn(el, page=page):
                if el.get("t") in ("Span", "Div", "Header") and isinstance(el.get("c"), list):
                    ident = el["c"][0][0] if el["t"] != "Header" else el["c"][1][0]
                    if ident and ident not in owner:
                        owner[ident] = (page, current)
            walk(b, fn)

    index_ids(preamble, None)
    for i, (_t, bl) in enumerate(sections):
        index_ids(bl, i)

    used = set()

    def retarget(blocks, page):
        def fn(el):
            if el.get("t") != "Link":
                return
            url = el["c"][2][0]
            if not url.startswith("#"):
                return
            tgt = owner.get(url[1:])
            if not tgt:
                return
            tpage, anchor = tgt
            if anchor:
                used.add(anchor)
            here = "index.md" if page is None else filenames[page]
            there = "index.md" if tpage is None else filenames[tpage]
            frag = f"#{anchor}" if anchor else ""
            el["c"][2][0] = frag if (there == here and frag) else f"{there}{frag}"
        walk(blocks, fn)

    retarget(preamble, None)
    for i, (_t, bl) in enumerate(sections):
        retarget(bl, i)

    # Drop unused ids on headings / spans (Google Docs adds many bookmarks).
    def strip_ids(el):
        if el.get("t") == "Header":
            if el["c"][1][0] not in used:
                el["c"][1][0] = ""
        elif el.get("t") in ("Span", "Div") and isinstance(el.get("c"), list):
            el["c"][0][0] = ""
    walk(preamble, strip_ids)
    for _t, bl in sections:
        walk(bl, strip_ids)


def to_markdown(blocks, meta_api) -> str:
    doc = {"pandoc-api-version": meta_api, "meta": {}, "blocks": blocks}
    md = pandoc(["-f", "json", "-t", WRITER, "--wrap=none"], stdin=json.dumps(doc))
    # Spans/Divs left without ids render as bare <span>/<div>: unwrap them.
    md = re.sub(r"</?span>", "", md)
    md = re.sub(r"^</?div>\s*$\n?", "", md, flags=re.M)
    # Fixed column widths from the Word layout squeeze HTML tables; let the
    # site's CSS size them instead.
    md = re.sub(r"<colgroup>.*?</colgroup>\s*", "", md, flags=re.S)
    md = re.sub(r'<table style="[^"]*">', "<table>", md)
    return md.strip() + "\n"


# --------------------------------------------------------------------------- #
# Regenerating nav, overview page and issue template
# --------------------------------------------------------------------------- #
def replace_between(text: str, begin: str, end: str, new_body: str) -> str:
    pat = re.compile(rf"(^[ \t]*#\s*{re.escape(begin)}.*?$\n)(.*?)(^[ \t]*#\s*{re.escape(end)})",
                     re.S | re.M)
    if not pat.search(text):
        sys.exit(f"Marker '# {begin}' … '# {end}' not found.")
    return pat.sub(lambda m: m.group(1) + new_body + m.group(3), text, count=1)


ANNEX_RE = re.compile(r"^(annex|appendix)\b", re.I)
NUMBERED_RE = re.compile(r"^\d+(\.\d+)*\.?\s")


def nav_labels(titles):
    """Menu labels: main sections get "1. ", "2. ", … (unless the Doc already
    numbers them); annexes keep their own letters ("Annex A: …")."""
    labels, n = [], 0
    for t in titles:
        if ANNEX_RE.match(t) or NUMBERED_RE.match(t):
            labels.append(t)
        else:
            n += 1
            labels.append(f"{n}. {t}")
    return labels


def update_nav(filenames, titles):
    body = "".join(f"      - {json.dumps(label, ensure_ascii=False)}: guideline/{f}\n"
                   for label, f in zip(nav_labels(titles), filenames))
    MKDOCS_YML.write_text(replace_between(MKDOCS_YML.read_text(encoding="utf-8"),
                                          "BEGIN guideline-nav", "END guideline-nav", body),
                          encoding="utf-8")


def update_issue_template(titles):
    if not ISSUE_TEMPLATE.exists():
        return
    body = "".join(f"        - {json.dumps(t, ensure_ascii=False)}\n" for t in titles)
    body += '        - "Other / whole guideline"\n'
    ISSUE_TEMPLATE.write_text(replace_between(ISSUE_TEMPLATE.read_text(encoding="utf-8"),
                                              "BEGIN sections", "END sections", body),
                              encoding="utf-8")


def write_overview(preamble_md: str, titles, filenames, doc_title: str):
    lines = [
        f"# {doc_title or 'About this guideline'}",
        "",
        "<!-- Generated by scripts/convert_source.py – edit the Google Doc instead. -->",
        "",
    ]
    if preamble_md.strip():
        lines += [preamble_md.strip(), ""]
    lines += [
        'Read the guideline section by section, or '
        '<a href="../pdf/proteus-rai-guideline.pdf" download>download it as PDF</a>.',
        "",
    ]
    entries = list(zip(nav_labels(titles), titles, filenames))
    main = [(lab, f) for lab, t, f in entries if not ANNEX_RE.match(t)]
    annexes = [(lab, f) for lab, t, f in entries if ANNEX_RE.match(t)]
    def section_list(items):    # labels carry their own numbers: no bullets
        return (['<div class="px-section-list" markdown>', ""]
                + [f"- [{lab}]({f})" for lab, f in items] + ["", "</div>"])
    lines += ["## Main sections", ""] + section_list(main)
    if annexes:
        lines += ["", "## Annexes", ""] + section_list(annexes)
    (GUIDE / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description="Convert the Google Doc export to MkDocs pages.")
    ap.add_argument("source", nargs="?", type=Path,
                    help="file to convert (default: newest .docx/.md/.odt in source/)")
    ap.add_argument("--level", type=int, default=1,
                    help="heading level that starts a new page (default 1)")
    ap.add_argument("--keep-quotes", action="store_true",
                    help="keep indented paragraphs as block quotes")
    args = ap.parse_args()

    src = args.source
    if src is None:
        cands = [p for p in SOURCE.glob("*") if p.suffix.lower() in (".docx", ".md", ".odt")]
        if not cands:
            sys.exit("No .docx, .odt or .md file in source/ – nothing to convert.")
        src = max(cands, key=lambda p: p.stat().st_mtime)
    src = src.resolve()
    print(f"Converting {src.relative_to(ROOT) if ROOT in src.parents else src}")

    # 1. Parse to the pandoc AST, extracting embedded images.
    if MEDIA.exists():
        shutil.rmtree(MEDIA)
    reader = ["--track-changes=accept"] if src.suffix.lower() == ".docx" else []
    if src.suffix.lower() == ".md":
        reader += ["-f", "markdown", f"--resource-path={src.parent}"]
    # Run from the repo root so extracted image paths are repo-relative.
    ast = json.loads(pandoc([str(src), "-t", "json", *reader,
                             f"--extract-media={MEDIA.relative_to(ROOT).as_posix()}"],
                            cwd=ROOT))
    api = ast["pandoc-api-version"]
    doc_title = stringify(ast.get("meta", {}).get("title", {}).get("c", [])).strip()

    blocks = ast["blocks"]
    if not args.keep_quotes:
        blocks = unwrap_quotes(blocks)
    blocks = drop_doc_toc(blocks)
    optimize_media(blocks)
    blocks = figures_to_md_in_html(blocks)
    preamble, sections = split_sections(blocks, args.level)
    if not sections:
        sys.exit(f"No level-{args.level} headings found. Use Heading {args.level} "
                 "for top-level sections in the Google Doc, or pass --level.")

    titles = [t for t, _ in sections]
    filenames, seen = [], set()
    for i, t in enumerate(titles, 1):
        name = f"{i:02d}-{slugify(t)}.md"
        while name in seen:
            name = name[:-3] + "-x.md"
        seen.add(name)
        filenames.append(name)

    resolve_internal_links(preamble, sections, filenames)

    # 2. Write pages.
    for old in GUIDE.glob("[0-9][0-9]-*.md"):
        old.unlink()
    GUIDE.mkdir(parents=True, exist_ok=True)
    fix_images(preamble, GUIDE)
    for (title, bl), fname in zip(sections, filenames):
        fix_images(bl, GUIDE)
        (GUIDE / fname).write_text(to_markdown(bl, api), encoding="utf-8")
        print(f"  docs/guideline/{fname}  ({title})")
    write_overview(to_markdown(preamble, api) if preamble else "", titles, filenames, doc_title)

    # 3. Navigation and issue template.
    update_nav(filenames, titles)
    update_issue_template(titles)
    print(f"{len(sections)} sections written; mkdocs.yml nav updated.\n"
          "Next: `mkdocs serve` to review, then commit docs/ and mkdocs.yml.")


if __name__ == "__main__":
    main()
