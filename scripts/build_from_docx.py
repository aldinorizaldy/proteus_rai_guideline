#!/usr/bin/env python3
"""Build every page and data file that comes from the guideline docx.

    python scripts/build_from_docx.py                 # the export in source/
    python scripts/build_from_docx.py path/to/x.docx  # a specific export

One source, several outputs, so they always match after each export:

  Guideline tab   docs/guideline/*.md (verbatim conversion, see convert_source.py)
  At a glance     docs/at-a-glance.md (sentences and lists quoted from the docx)
  Quick tools     docs/tools/**.md and docs/data/*.json:
                    requirements.json            <- Annex "Requirements Checklist" table
                    use_cases.json, use-cases/   <- Annex "Use-Case Examples" (+ "Risk-Tier")
                    compliance_card.schema.json  <- Annex "Compliance Card" table
                    risk_check.json              <- docs/data/risk_check.yml (edited by
                                                    the RAI lead) + the tier table
  Downloads       docs/downloads/proteus-rai-guideline.docx

Sections and annexes are found by title keywords (see SECTIONS), not by
number or letter, so renumbering in the Doc does not break the tools. When an
annex is still an outline, the tool shows a "Coming soon" placeholder: nothing
is invented. The formatting conventions the parser relies on are listed in
source/README.md.
"""
import argparse
import copy
import html
import json
import posixpath
import re
import shutil
import sys
from pathlib import Path

import jinja2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import convert_source as cs  # noqa: E402

ROOT = cs.ROOT
DOCS = ROOT / "docs"
DATA = DOCS / "data"
TOOLS = DOCS / "tools"
UC_DIR = TOOLS / "use-cases"
DOWNLOADS = DOCS / "downloads"
TEMPLATES = Path(__file__).resolve().parent / "templates"

DEFAULT_UCS = [f"UC{i}" for i in range(1, 8)]
# Requirement IDs: capital letters, hyphen, digits, e.g. DC-01, TR-12, REL-3a.
REQ_ID_RE = re.compile(r"\b[A-Z]{1,6}(?:-[A-Z]{1,6})*-\d{1,3}[a-z]?\b")
UC_RE = re.compile(r"\bUC\s?(\d{1,2})\b")
TIERS = ["low", "medium", "high"]

# key: (is_annex, title keywords, lower-case, first match wins)
SECTIONS = {
    "exec":       (False, ["executive summary"]),
    "intro":      (False, ["introduction"]),
    "principles": (False, ["principles"]),
    "risks":      (False, ["risk"]),
    "lifecycle":  (False, ["lifecycle"]),
    "strategies": (False, ["strateg"]),
    "metadata":   (False, ["metadata"]),
    "compliance": (False, ["compliance"]),
    "validation": (False, ["automated validation"]),
    "governance": (False, ["governance"]),
    "checklist":  (True, ["requirements checklist", "checklist"]),
    "card":       (True, ["compliance card"]),
    "glossary":   (True, ["glossary"]),
    "worked":     (True, ["worked example"]),
    "roles_map":  (True, ["roles"]),
    "usecases":   (True, ["use-case", "use case"]),
    "tiers":      (True, ["risk-tier", "risk tier"]),
    "context":    (True, ["project context", "context"]),
    "roadmap":    (True, ["roadmap"]),
}

# Column headers accepted in the annex tables (normalised: lower case, letters only).
CHECKLIST_COLS = {
    "id": "id", "requirementid": "id",
    "requirement": "requirement",
    "lifecyclestage": "stage", "stage": "stage",
    "responsiblerole": "role", "role": "role",
    "bindinglevel": "binding", "binding": "binding",
    "evidence": "evidence",
    "usecase": "use_case", "usecases": "use_case",
}
CHECKLIST_REQUIRED = ["id", "requirement", "stage", "role", "binding", "evidence"]
TIER_COLS = {
    "usecase": "use_case", "usecases": "use_case",
    "example": "example", "output": "example", "item": "example",
    "risktier": "tier", "tier": "tier",
    "reason": "reasons", "reasons": "reasons", "why": "reasons",
    "reviewandoversight": "oversight", "oversight": "oversight",
    "triggers": "oversight", "reviewandoversightitriggers": "oversight",
}
CARD_COLS = {
    "stage": "stage", "lifecyclestage": "stage",
    "parameter": "parameter", "field": "parameter",
    "description": "description", "definition": "description",
    "allowedvalues": "allowed", "values": "allowed",
}
UC_PARTS = [  # (key, heading keywords) for the sub-headings of each use case
    ("summary", ["summary", "description", "overview"]),
    ("principles", ["principle", "risk"]),
    ("requirements", ["requirement"]),
    ("evidence", ["evidence"]),
    ("oversight", ["oversight"]),
]


# --------------------------------------------------------------------------- #
# AST helpers
# --------------------------------------------------------------------------- #
def text(blocks) -> str:
    return re.sub(r"\s+", " ", cs.stringify(blocks)).strip()


def norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


def sentences(s: str):
    """Split prose into sentences (good enough for the guideline's style)."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", s.strip())
    return [p.strip() for p in parts if p.strip()]


def paragraphs(blocks):
    return [text(b["c"]) for b in blocks if b.get("t") in ("Para", "Plain")]


def headers(blocks):
    return [(b["c"][0], text(b["c"][2]), i) for i, b in enumerate(blocks)
            if b.get("t") == "Header"]


def subsections(blocks, level):
    """[(heading text, blocks)] for every heading of `level` in `blocks`."""
    out, cur = [], None
    for b in blocks:
        if b.get("t") == "Header":
            if b["c"][0] == level:
                cur = [text(b["c"][2]), []]
                out.append(cur)
                continue
            if b["c"][0] < level:
                cur = None
                continue
        if cur is not None:
            cur[1].append(b)
    return out


def lead(blocks, level):
    """Blocks before the first heading of `level` or higher (excluding H1)."""
    out = []
    for b in blocks:
        if b.get("t") == "Header":
            if b["c"][0] == 1:
                continue
            if b["c"][0] <= level:
                break
        out.append(b)
    return out


def table_rows(tbl):
    """Rows of a pandoc Table as lists of cell texts, header row first."""
    _attr, _cap, _specs, head, bodies, _foot = tbl["c"]
    rows = []
    for r in head[1]:
        rows.append([text(cell[4]) for cell in r[1]])
    for body in bodies:
        for r in body[2] + body[3]:
            rows.append([text(cell[4]) for cell in r[1]])
    return rows


def tables(blocks):
    found = []
    cs.walk(blocks, lambda el: found.append(el) if el.get("t") == "Table" else None)
    return found


def map_columns(header, mapping):
    cols = {}
    for i, h in enumerate(header):
        key = mapping.get(norm(h))
        if key and key not in cols:
            cols[key] = i
    return cols


def find_table(blocks, mapping, required):
    """The first table whose header row has all `required` columns."""
    for tbl in tables(blocks):
        rows = table_rows(tbl)
        if not rows:
            continue
        cols = map_columns(rows[0], mapping)
        if all(k in cols for k in required):
            return cols, rows[1:], tbl
    return None, [], None


def strip_ids(blocks):
    def fn(el):
        if el.get("t") == "Header":
            el["c"][1][0] = ""
    cs.walk(blocks, fn)


def shift_headers(blocks, top):
    """Re-level headings so the highest one in `blocks` becomes `top`."""
    levels = [b["c"][0] for b in blocks if b.get("t") == "Header"]
    if not levels:
        return
    d = top - min(levels)
    def fn(el):
        if el.get("t") == "Header":
            el["c"][0] = max(1, min(6, el["c"][0] + d))
    cs.walk(blocks, fn)


def rebase_links(blocks, guide_prefix, own_file):
    """Links in copied blocks are relative to docs/guideline/; re-point them."""
    def fn(el):
        if el.get("t") != "Link":
            return
        url = el["c"][2][0]
        if url.startswith("#"):
            el["c"][2][0] = guide_prefix + own_file + url
        elif url and not re.match(r"^([a-z][a-z0-9+.-]*:|/)", url, re.I):
            el["c"][2][0] = guide_prefix + url
    cs.walk(blocks, fn)


def linkify_ids(node, ids, href):
    """Turn requirement IDs (that exist in the checklist) into links."""
    if isinstance(node, list):
        out = []
        for el in node:
            if isinstance(el, dict) and el.get("t") == "Str" and ids:
                pos, s = 0, el["c"]
                for m in REQ_ID_RE.finditer(s):
                    if m.group(0) not in ids:
                        continue
                    if m.start() > pos:
                        out.append({"t": "Str", "c": s[pos:m.start()]})
                    out.append({"t": "Link", "c": [["", [], []],
                                                   [{"t": "Str", "c": m.group(0)}],
                                                   [href(m.group(0)), ""]]})
                    pos = m.end()
                if pos == 0:
                    out.append(el)
                elif pos < len(s):
                    out.append({"t": "Str", "c": s[pos:]})
                continue
            if isinstance(el, (list, dict)):
                linkify_ids(el, ids, href)
            out.append(el)
        node[:] = out
    elif isinstance(node, dict) and node.get("t") not in ("Link", "Image", "Code", "CodeBlock"):
        c = node.get("c")
        if isinstance(c, (list, dict)):
            linkify_ids(c, ids, href)


def page_rel(page: str, target: str) -> str:
    """Relative link from docs/<page> to docs/<target>."""
    return posixpath.relpath(target, posixpath.dirname(page) or ".")


def md_slug(value: str) -> str:
    """Heading anchor as Python-Markdown's toc extension makes it."""
    import unicodedata
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def inline_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# --------------------------------------------------------------------------- #
# Sections
# --------------------------------------------------------------------------- #
class Section:
    def __init__(self, key, title, label, nav_label, filename, blocks):
        self.key, self.title, self.label = key, title, label
        self.nav_label, self.filename, self.blocks = nav_label, filename, blocks

    @property
    def path(self):
        return f"guideline/{self.filename}"

    @property
    def short_title(self):
        return re.sub(r"^(annex|appendix)\s+\S+?[:.–—-]\s*", "", self.title, flags=re.I)

    def link(self, page, anchor=""):
        if anchor and not any(md_slug(t) == anchor for _l, t, _i in headers(self.blocks)):
            anchor = ""                       # heading renamed or gone: link the page
        frag = f"#{anchor}" if anchor else ""
        return f"[{self.label} · {self.short_title}]({page_rel(page, self.path)}{frag})"


class Missing(Section):
    """Stand-in when a section cannot be found: links to the overview."""
    def __init__(self, key):
        super().__init__(key, "the guideline", "Guideline", "Guideline", "index.md", [])

    def link(self, page, anchor=""):
        return f"[the full guideline]({page_rel(page, 'guideline/index.md')})"


def locate_sections(doc):
    """Map SECTIONS keys to Section objects (deep copies of the blocks, with
    repo-relative image paths and guideline-relative links)."""
    found = {}
    for key, (is_annex, words) in SECTIONS.items():
        for (title, bl), fname, nav in zip(doc.sections, doc.filenames, doc.labels):
            annex = bool(cs.ANNEX_RE.match(title))
            if annex != is_annex or not any(w in title.lower() for w in words):
                continue
            if annex:
                m = re.match(r"^(annex|appendix)\s+([A-Z0-9]+)", title, re.I)
                label = f"{m.group(1).title()} {m.group(2)}" if m else title
            else:
                label = "Section " + nav.split(".", 1)[0]
            found[key] = Section(key, title, label, nav, fname, copy.deepcopy(bl))
            break
        else:
            found[key] = Missing(key)
            print(f"  ! no section found for '{key}' (title containing {words})")
    return found


def render_blocks(blocks, doc, page, sec, ids=None, top=None):
    """Markdown for `blocks` (from section `sec`) placed on docs/<page>."""
    bl = copy.deepcopy(blocks)
    strip_ids(bl)
    if top:
        shift_headers(bl, top)
    guide_prefix = page_rel(page, "guideline") + "/"
    rebase_links(bl, guide_prefix, sec.filename)
    cs.fix_images(bl, (DOCS / page).parent)
    if ids:
        linkify_ids(bl, ids, lambda i: page_rel(page, "tools/checklist.md") + f"#{i}")
    return cs.to_markdown(bl, doc.api).strip() if bl else ""


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #
def extract_requirements(S, src_name):
    sec = S["checklist"]
    cols, rows, _ = find_table(sec.blocks, CHECKLIST_COLS, ["id", "requirement"])
    items, warnings = [], []
    if cols:
        for k in CHECKLIST_REQUIRED:
            if k not in cols:
                warnings.append(f"Annex table has no '{k}' column")
        seen = set()
        for r in rows:
            get = lambda k: r[cols[k]].strip() if k in cols and cols[k] < len(r) else ""
            rid = get("id")
            if not rid:
                continue
            if not REQ_ID_RE.fullmatch(rid):
                warnings.append(f"ID '{rid}' does not look like XX-00")
            if rid in seen:
                warnings.append(f"duplicate ID '{rid}'")
            seen.add(rid)
            binding = get("binding").lower()
            if binding and binding not in ("must", "should", "may"):
                warnings.append(f"{rid}: binding level '{binding}' is not must/should/may")
            uc_cell = get("use_case")
            items.append({
                "id": rid, "requirement": get("requirement"), "stage": get("stage"),
                "role": get("role"), "binding": binding, "evidence": get("evidence"),
                "use_cases": sorted({f"UC{n}" for n in UC_RE.findall(uc_cell)},
                                    key=lambda u: int(u[2:])),
                "use_case_text": uc_cell,
            })
    for w in warnings:
        print(f"  ! requirements: {w}")
    return {
        "status": "ok" if items else "placeholder",
        "source": {"label": sec.label, "title": sec.title, "page": sec.path},
        "generated_from": src_name,
        "has_use_case_column": bool(cols and "use_case" in cols),
        "items": items,
        "warnings": warnings,
    }


def extract_tier_table(S):
    """The tier table in the risk section (columns: Risk tier, Description, …)."""
    for tbl in tables(S["risks"].blocks):
        rows = table_rows(tbl)
        if rows and "tier" in norm(rows[0][0]):
            tiers = {}
            for r in rows[1:]:
                t = r[0].strip().lower()
                if t in TIERS:
                    tiers[t] = {"description": r[1] if len(r) > 1 else "",
                                "example": r[2] if len(r) > 2 else ""}
            return {"header": rows[0], "rows": rows[1:], "tiers": tiers, "table": tbl}
    return None


def extract_tier_examples(S):
    sec = S["tiers"]
    cols, rows, _ = find_table(sec.blocks, TIER_COLS, ["tier"])
    out = []
    if cols:
        get = lambda r, k: r[cols[k]].strip() if k in cols and cols[k] < len(r) else ""
        for r in rows:
            tier = get(r, "tier").lower()
            uc_text = get(r, "use_case") or get(r, "example")
            out.append({
                "use_cases": sorted({f"UC{n}" for n in UC_RE.findall(uc_text)}),
                "use_case_text": get(r, "use_case"), "example": get(r, "example"),
                "tier": tier if tier in TIERS else get(r, "tier"),
                "reasons": get(r, "reasons"), "oversight": get(r, "oversight"),
            })
    return out


def extract_use_cases(S, doc, req_ids):
    sec = S["usecases"]
    names = {}
    for p in paragraphs(sec.blocks):
        for m in re.finditer(r"([^,:;()]+?)\s*\((UC\s?\d{1,2})\)", p):
            uc = m.group(2).replace(" ", "")
            name = re.sub(r"^(and|or)\s+", "", m.group(1).strip())
            if uc not in names and 0 < len(name) <= 60:
                names[uc] = name[0].upper() + name[1:]
    # UC sections: headings that start with "UCn".
    parts = {}
    hs = headers(sec.blocks)
    for n, (lvl, htext, idx) in enumerate(hs):
        m = re.match(r"^UC\s?(\d{1,2})\b\s*[:.–—-]?\s*(.*)$", htext)
        if not m or lvl == 1:
            continue
        uc = f"UC{m.group(1)}"
        end = next((j for (l2, _t, j) in hs[n + 1:] if l2 <= lvl), len(sec.blocks))
        body = sec.blocks[idx + 1:end]
        if m.group(2).strip():
            names[uc] = m.group(2).strip()
        sub = {}
        intro = lead(body, lvl + 1)
        for st, sb in subsections(body, lvl + 1):
            for key, words in UC_PARTS:
                if key not in sub and any(w in st.lower() for w in words):
                    sub[key] = sb
                    break
        if intro and "summary" not in sub:
            sub["summary"] = intro
        parts[uc] = sub
    ucs = sorted(set(names) | set(parts), key=lambda u: int(u[2:])) or DEFAULT_UCS
    examples = extract_tier_examples(S)
    result = []
    for uc in ucs:
        page = f"tools/use-cases/{uc.lower()}.md"
        sub = parts.get(uc, {})
        rendered = {k: render_blocks(sub[k], doc, page, sec, ids=req_ids, top=4)
                    for k in sub}
        refs = sorted({i for k in sub for i in REQ_ID_RE.findall(text(sub[k]))
                       if i in req_ids})
        result.append({
            "id": uc, "slug": uc.lower(), "name": names.get(uc, ""),
            "found": uc in parts, "parts": rendered,
            "tiers": [e for e in examples if uc in e["use_cases"]],
            "requirements": refs,
        })
    return result


def extract_card_schema(S, stages):
    sec = S["card"]
    cols, rows, _ = find_table(sec.blocks, CARD_COLS, ["stage", "parameter"])
    params, by_stage = {}, {}
    if cols:
        get = lambda r, k: r[cols[k]].strip() if k in cols and cols[k] < len(r) else ""
        for r in rows:
            name = get(r, "parameter")
            if not name:
                continue
            stage = get(r, "stage") or "All stages"
            pid = cs.slugify(name, 40).replace("-", "_")
            while pid in params:
                pid += "_x"
            allowed = [v.strip() for v in re.split(r"[;,/]|\s+or\s+", get(r, "allowed"))
                       if v.strip()]
            status = {"type": "string", "title": "Status"}
            if allowed:
                status["enum"] = allowed
            params[pid] = {
                "type": "object", "title": name, "description": get(r, "description"),
                "properties": {
                    "status": status,
                    "justification": {"type": "string", "title": "Justification"},
                    "evidence": {"type": "string", "title": "Evidence"},
                },
            }
            by_stage.setdefault(stage, []).append(pid)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Responsible AI compliance card",
        "description": f"Generated from {sec.label} ({sec.title}). Do not edit by hand.",
        "type": "object",
        "x-status": "ok" if params else "placeholder",
        "x-source": {"label": sec.label, "title": sec.title, "page": sec.path},
        "x-stages": by_stage or {s: [] for s in stages},
        "properties": {
            "guideline_version": {"type": "string"},
            "item": {"type": "object", "properties": {
                "name": {"type": "string"}, "type": {"type": "string"},
                "version": {"type": "string"}, "submitted_by": {"type": "string"},
                "date": {"type": "string", "format": "date"}}},
            "stage": {"type": "string", "enum": list(by_stage) or stages},
            "parameters": {"type": "object", "properties": params},
        },
    }


def card_stages(S):
    """Stage names as the compliance section lists them: "(a, b, and c)"."""
    for p in paragraphs(S["compliance"].blocks) + paragraphs(S["metadata"].blocks):
        m = re.search(r"stages?\s*\(([^)]+)\)", p)
        if m:
            items = re.split(r",\s*(?:and\s+)?|\s+and\s+(?=[a-z]+ [a-z]+\)?$)", m.group(1))
            items = [re.sub(r"^and\s+", "", i).strip() for i in items if i.strip()]
            if len(items) >= 2:
                return [i[0].upper() + i[1:] for i in items]
    return []


def extract_steps(S, doc):
    sec = S["worked"]
    page = "tools/worked-example.md"
    levels = sorted({lvl for lvl, _t, _i in headers(sec.blocks) if lvl > 1})
    steps = []
    if levels:
        for title, bl in subsections(sec.blocks, levels[0]):
            low = (title + " " + text(bl)).lower()
            tools = []
            for words, name, target in (
                    (["role"], "Start here: find your role", "tools/start-here.md"),
                    (["risk tier", "tier"], "Risk self-check", "tools/risk-check.md"),
                    (["checklist", "requirement"], "Requirements checklist", "tools/checklist.md"),
                    (["compliance card", "card"], "Compliance card", "tools/compliance-card.md")):
                if any(w in low for w in words):
                    tools.append(f"[{name}]({page_rel(page, target)})")
            steps.append({"title": title, "body": render_blocks(bl, doc, page, sec, top=3),
                          "tools": tools})
    return steps


def extract_glance(S, doc, tier_table):
    page = "at-a-glance.md"
    g = {}
    intro = sentences(" ".join(paragraphs(lead(S["intro"].blocks, 2))))
    g["what"] = intro[:2]

    def one_liners(sec):
        out = []
        for title, bl in subsections(sec.blocks, 2):
            ps = paragraphs(bl)
            out.append({"title": title, "line": sentences(ps[0])[0] if ps else ""})
        return out
    g["principles"] = one_liners(S["principles"])
    g["risks"] = one_liners(S["risks"])
    g["tier_table"] = (cs.to_markdown([copy.deepcopy(tier_table["table"])], doc.api).strip()
                       if tier_table else "")

    roles = []
    for title, bl in subsections(S["intro"].blocks, 2):
        if "role" in title.lower():
            for s in sentences(" ".join(paragraphs(bl))):
                if re.match(r"^(this|the) subsection\b", s, re.I) or re.search(r"\bannex\b", s, re.I):
                    continue
                roles.append(s)
    g["roles"] = roles

    words = []
    for s in sentences(" ".join(paragraphs(S["intro"].blocks))):
        if re.search(r"\bmust\b.*\bshould\b|\bmandatory\b", s):
            words.append(s)
    g["binding"] = words
    # Definitions of must/should/may, once the glossary has them (table or
    # definition list with those terms).
    defs = {}
    for tbl in tables(S["glossary"].blocks):
        for r in table_rows(tbl):
            if len(r) >= 2 and r[0].strip().lower() in ("must", "should", "may"):
                defs[r[0].strip().lower()] = r[1]
    for b in S["glossary"].blocks:
        if b.get("t") == "DefinitionList":
            for term, defs_bl in b["c"]:
                t = text(term).lower()
                if t in ("must", "should", "may"):
                    defs[t] = text(defs_bl[0]) if defs_bl else ""
    g["binding_defs"] = defs
    v2 = []
    for key in ("exec", "validation"):
        for s in sentences(" ".join(paragraphs(S[key].blocks))):
            if re.search(r"version 2|D2\.2", s):
                v2.append({"text": s, "source": S[key].link(page)})
    g["v2"] = v2

    obligations = ""
    for b in S["exec"].blocks:
        if b.get("t") in ("BulletList", "OrderedList"):
            obligations = render_blocks([b], doc, page, S["exec"])
            break
    g["obligations"] = obligations
    return g


def roadmap_dates(S):
    out = []
    for s in sentences(" ".join(paragraphs(S["roadmap"].blocks))):
        if re.search(r"\bM\d{1,2}\b", s):
            out.append(s)
    return out


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(name, obj):
    write(DATA / name, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def update_uc_nav(use_cases):
    body = "".join(
        f"          - {json.dumps(uc['id'] + (' · ' + uc['name'] if uc['name'] else ''), ensure_ascii=False)}"
        f": tools/use-cases/{uc['slug']}.md\n" for uc in use_cases)
    yml = cs.MKDOCS_YML.read_text(encoding="utf-8")
    cs.MKDOCS_YML.write_text(cs.replace_between(yml, "BEGIN usecase-nav", "END usecase-nav", body),
                             encoding="utf-8")


def risk_check_data(S, tier_table, page):
    cfg_path = DATA / "risk_check.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    tiers = (tier_table or {}).get("tiers", {})
    qs = []
    for q in cfg.get("questions", []):
        if q.get("if_yes") not in TIERS:
            sys.exit(f"risk_check.yml: question '{q.get('id')}' needs if_yes: low|medium|high")
        qs.append({"hint": "", "source": [], **q, "source_md": " · ".join(S[k].link(page) for k in q.get("source", [])
                                                 if k in S)})
    out_tiers = {}
    for t in TIERS:
        c = (cfg.get("tiers") or {}).get(t, {})
        out_tiers[t] = {
            "description": tiers.get(t, {}).get("description", ""),
            "example": tiers.get(t, {}).get("example", ""),
            "triggers": c.get("triggers", []),
        }
    return {"status": cfg.get("status", "draft"), "note": cfg.get("note", ""),
            "questions": qs, "tiers": out_tiers,
            "tier_source": S["risks"].link(page), "examples_source": S["tiers"].link(page)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source", nargs="?", type=Path,
                    help="export to convert (default: the .docx in source/)")
    ap.add_argument("--level", type=int, default=1,
                    help="heading level that starts a new page (default 1)")
    ap.add_argument("--keep-quotes", action="store_true",
                    help="keep indented paragraphs as block quotes")
    args = ap.parse_args()

    src = cs.pick_source(args.source)
    print(f"Building from {src.relative_to(ROOT) if ROOT in src.parents else src}")
    doc = cs.parse(src, args.level, args.keep_quotes)
    S = locate_sections(doc)          # deep copies, taken before pages are written
    cs.write_guideline(doc)

    cfg = yaml.load(cs.MKDOCS_YML.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    extra = cfg.get("extra", {})

    # Data.
    reqs = extract_requirements(S, src.name)
    req_ids = {i["id"] for i in reqs["items"]}
    tier_table = extract_tier_table(S)
    use_cases = extract_use_cases(S, doc, req_ids)
    stages = card_stages(S)
    schema = extract_card_schema(S, stages)
    steps = extract_steps(S, doc)

    if DATA.exists():
        for old in DATA.glob("*.json"):
            old.unlink()
    write_json("requirements.json", reqs)
    write_json("compliance_card.schema.json", schema)
    write_json("use_cases.json", [{k: v for k, v in uc.items() if k != "parts"}
                                  for uc in use_cases])
    write_json("risk_tiers.json", {k: v for k, v in (tier_table or {}).items() if k != "table"})

    # Pages.
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATES)),
                             comment_start_string="<!--j", comment_end_string="j-->",
                             keep_trailing_newline=True, undefined=jinja2.StrictUndefined)
    env.filters["e"] = lambda s: html.escape(str(s), quote=True)
    env.filters["json"] = inline_json
    env.filters["slug"] = md_slug
    base = {"S": S, "extra": extra, "repo": cfg.get("repo_url", "").rstrip("/"), "front": cs.GENERATED_FRONT_MATTER.rstrip("\n"),
            "use_cases": use_cases, "reqs": reqs, "stages": stages}

    def render(template, page, **ctx):
        md = env.get_template(template).render(page=page, rel=lambda t: page_rel(page, t),
                                               **base, **ctx)
        write(DOCS / page, re.sub(r"\n{3,}", "\n\n", md).strip() + "\n")

    render("at-a-glance.md.j2", "at-a-glance.md", g=extract_glance(S, doc, tier_table))
    render("tools-index.md.j2", "tools/index.md", schema=schema, steps=steps)
    render("start-here.md.j2", "tools/start-here.md", dates=roadmap_dates(S))
    for old in UC_DIR.glob("uc*.md"):
        old.unlink()
    render("use-cases-index.md.j2", "tools/use-cases/index.md")
    for uc in use_cases:
        render("use-case.md.j2", f"tools/use-cases/{uc['slug']}.md", uc=uc)
    render("checklist.md.j2", "tools/checklist.md")
    rc = risk_check_data(S, tier_table, "tools/risk-check.md")
    write_json("risk_check.json", rc)
    render("risk-check.md.j2", "tools/risk-check.md", rc=rc)
    render("compliance-card.md.j2", "tools/compliance-card.md", schema=schema)
    render("worked-example.md.j2", "tools/worked-example.md", steps=steps)
    update_uc_nav(use_cases)

    # Official document for download (not committed: see .gitignore).
    if src.suffix.lower() == ".docx":
        DOWNLOADS.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, DOWNLOADS / "proteus-rai-guideline.docx")

    filled = {"Requirements checklist": reqs["status"] == "ok",
              "Use cases": any(uc["found"] for uc in use_cases),
              "Compliance card": schema["x-status"] == "ok",
              "Worked example": bool(steps),
              "Risk-tier examples": any(uc["tiers"] for uc in use_cases)}
    print(f"{len(doc.sections)} guideline sections; tools: "
          + ", ".join(f"{k} {'filled' if v else 'placeholder'}" for k, v in filled.items()))


if __name__ == "__main__":
    main()
