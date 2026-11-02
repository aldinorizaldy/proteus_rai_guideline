# source/

The **only content source** for the website. Put the export of the master
Google Doc here (**File → Download → Microsoft Word (.docx)**), replacing the
previous one, so that exactly one `.docx` is in this folder. Then run:

```bash
python scripts/build_from_docx.py     # Guideline pages, At a glance, Quick tools, data
python scripts/check_guideline.py     # Guideline tab == docx (also runs in CI)
```

CI runs both on every push, so the published site always matches the docx in
this folder. Keeping the export under version control records exactly which
draft each release was built from.

## Formatting conventions in the Google Doc

The Guideline tab is a verbatim conversion and needs only the first two rules.
The Quick tools read specific annexes; until an annex follows its rule, the
tool shows a "Coming soon" placeholder instead of guessing.

### Everywhere

1. **Heading styles, not bold text.** *Heading 1* for each main section and
   annex (one web page each), *Heading 2* / *Heading 3* inside them.
2. **Annex titles start with "Annex X:"**, e.g. `Annex A: Requirements Checklist`.
   Main sections are numbered automatically on the website; do not type numbers
   into Heading 1.
3. The tools find sections by **keywords in the title**, so keep these words in
   the titles (letters and order may change):

   | Tool needs | Title must contain |
   |---|---|
   | Principles, risks, roles | "Principles", "Risks", "Introduction" (with a Heading 2 containing "Roles") |
   | Checklist | "Requirements Checklist" (annex) |
   | Compliance card | "Compliance Card" (annex) |
   | Glossary (must / should / may) | "Glossary" (annex) |
   | Worked example | "Worked Example" (annex) |
   | Use cases | "Use-Case" or "Use Case" (annex) |
   | Risk tiers | "Risk-Tier" or "Risk Tier" (annex) |
   | Key dates | "Roadmap" (annex) |

4. **Requirement IDs** have the form **letters-hyphen-number**: `DC-01`,
   `TR-12`, `REL-3a`. Use exactly the same ID wherever a requirement is cited
   (use-case annex, worked example); IDs found in the checklist become links.
5. **Use cases** are written `UC1` … `UC7` (no space). In the use-case annex
   introduction, name them as `name (UC1)` – the menu labels come from there.

### Annex "Requirements Checklist" – one table

One table, first row = these headers (order free, spelling as shown):

| ID | Requirement | Lifecycle stage | Responsible role | Binding level | Evidence | Use case |
|----|-------------|-----------------|------------------|---------------|----------|----------|
| DC-01 | Record the licence of every dataset. | Data collection | Data provider | must | Licence list | All |

- **Binding level**: `must`, `should` or `may` only.
- **Use case** (optional column): `All`, or the IDs it applies to, e.g. `UC1, UC5`.
- Use the same spelling for the same stage or role in every row (they become
  the filter options).

### Annex "Use-Case Examples" – one Heading 2 per use case

```
Heading 2:  UC1 – Displacement monitoring
  Heading 3:  Summary
  Heading 3:  Key principles and risks
  Heading 3:  Requirements to watch        (cite IDs, e.g. DC-02, TR-01)
  Heading 3:  Expected evidence
  Heading 3:  Human oversight
```

Sub-headings are matched by their first keyword (summary, principle/risk,
requirement, evidence, oversight). Missing ones show "Coming soon".

### Annex "Risk-Tier Examples" – one table

| Use case | Example | Risk tier | Reasons | Review and oversight |
|----------|---------|-----------|---------|----------------------|
| UC1 | Settlement map | High | Concerns vulnerable populations. | Mandatory human check before release |

**Risk tier**: `Low`, `Medium` or `High`. **Use case**: one or more UC IDs.

### Annex "Compliance Card" – one table

| Stage | Parameter | Description | Allowed values |
|-------|-----------|-------------|----------------|
| Data collection | Licence verified | Every dataset licence is recorded. | yes, no, not applicable |

Each parameter gets *status*, *justification* and *evidence* fields in the
web form. **Allowed values** (optional) become the status options. The JSON
schema `docs/data/compliance_card.schema.json` is generated from this table.

### Annex "Glossary" – must / should / may

A two-column table (Term | Definition) with rows `must`, `should`, `may` (other
terms may follow). These definitions appear on the At a glance page.

### Annex "Worked Example" – one Heading 2 per step

`Step 1: …`, `Step 2: …`. Tables inside a step (a filled checklist excerpt, a
filled compliance card) are shown as they are. Steps that mention the role,
risk tier, checklist or compliance card link to that tool.

### Avoid

- Text boxes, drawings and floating images (they do not export). Use inline
  images with **Alt text** (right-click → Alt text).
- Merged table cells in the annex tables above.
- Typing section numbers by hand; Google's automatic numbering is not exported.
