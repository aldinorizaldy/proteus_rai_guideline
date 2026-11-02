"""End-to-end test of the docx pipeline on a sample guideline.

    python -m unittest discover -s tests -v

Copies the repository to a temporary folder, builds it from
tests/fixtures/sample-guideline.docx (filled Annexes A, B, D, E, G, H; two use
cases), and checks that the tools fill in from the annexes, that use cases
missing from the docx show placeholders, that the Guideline check passes (and
fails after a hand edit), and that `mkdocs build --strict` passes.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "sample-guideline.docx"
COPY = ["docs", "overrides", "includes", "scripts", "mkdocs.yml", "CHANGELOG.md"]


def run(args, cwd, check=True):
    res = subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True)
    if check and res.returncode != 0:
        raise AssertionError(f"{' '.join(args)} failed:\n{res.stdout}\n{res.stderr}")
    return res


class SampleBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="rai-test-"))
        for name in COPY:
            src = REPO / name
            if src.is_dir():
                shutil.copytree(src, cls.tmp / name,
                                ignore=shutil.ignore_patterns("downloads", "__pycache__"))
            else:
                shutil.copy2(src, cls.tmp / name)
        (cls.tmp / "source").mkdir()
        cls.build = run(["scripts/build_from_docx.py", str(FIXTURE)], cls.tmp)
        cls.docs = cls.tmp / "docs"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def read(self, rel):
        return (self.docs / rel).read_text(encoding="utf-8")

    def data(self, name):
        return json.loads(self.read(f"data/{name}"))

    # Guideline tab ---------------------------------------------------------
    def test_guideline_pages_match_docx(self):
        res = run(["scripts/check_guideline.py", str(FIXTURE)], self.tmp)
        self.assertIn("OK:", res.stdout)

    def test_check_fails_after_hand_edit(self):
        page = next((self.docs / "guideline").glob("03-*.md"))
        original = page.read_text(encoding="utf-8")
        try:
            page.write_text(original.replace("can be inspected", "can be inspected easily"),
                            encoding="utf-8")
            res = run(["scripts/check_guideline.py", str(FIXTURE)], self.tmp, check=False)
            self.assertEqual(res.returncode, 1, res.stdout)
            self.assertIn("words in the docx", res.stdout)
        finally:
            page.write_text(original, encoding="utf-8")

    # Checklist ---------------------------------------------------------------
    def test_requirements_parsed_from_annex_a(self):
        reqs = self.data("requirements.json")
        self.assertEqual(reqs["status"], "ok")
        self.assertEqual([i["id"] for i in reqs["items"]], ["DC-01", "DC-02", "TR-01", "RE-01"])
        tr = reqs["items"][2]
        self.assertEqual((tr["stage"], tr["role"], tr["binding"]),
                         ("Model training", "FM developer", "should"))
        self.assertEqual(tr["use_cases"], ["UC1", "UC2"])
        self.assertEqual(reqs["items"][0]["use_cases"], [])          # "All"
        page = self.read("tools/checklist.md")
        self.assertIn('id="TR-01"', page)
        self.assertNotIn("Coming soon", page)

    # Use cases -----------------------------------------------------------------
    def test_use_case_pages_from_annex_g_and_h(self):
        uc1 = self.read("tools/use-cases/uc1.md")
        self.assertIn("# UC1 · Sample displacement monitoring", uc1)
        self.assertIn("UC1 maps sample settlements", uc1)
        self.assertIn("[DC-02](../checklist.md#DC-02)", uc1)          # deep link
        self.assertIn("An analyst reviews every map", uc1)
        self.assertIn("| **High** | Settlement map", uc1)
        self.assertNotIn("Coming soon", uc1)
        uc2 = self.read("tools/use-cases/uc2.md")
        self.assertIn("Coming soon", uc2)                           # no oversight sub-heading
        self.assertIn("[RE-01](../checklist.md#RE-01)", uc2)

    def test_use_case_pages_follow_the_docx(self):
        self.assertEqual(sorted(p.name for p in (self.docs / "tools/use-cases").glob("uc*.md")),
                         ["uc1.md", "uc2.md"])
        ucs = self.data("use_cases.json")
        self.assertEqual([u["id"] for u in ucs], ["UC1", "UC2"])

    # Compliance card, worked example, at a glance -------------------------------
    def test_compliance_card_schema_from_annex_b(self):
        schema = self.data("compliance_card.schema.json")
        self.assertEqual(schema["x-status"], "ok")
        self.assertEqual(list(schema["x-stages"]), ["Data collection", "Model training"])
        lic = schema["properties"]["parameters"]["properties"]["licence_verified"]
        self.assertEqual(lic["properties"]["status"]["enum"], ["yes", "no", "not applicable"])
        self.assertIn('name="licence_verified.status"', self.read("tools/compliance-card.md"))

    def test_worked_example_steps(self):
        page = self.read("tools/worked-example.md")
        self.assertIn("## Step 2: Fill in the compliance card", page)
        self.assertIn("[Compliance card](compliance-card.md)", page)

    def test_at_a_glance_quotes_the_docx(self):
        page = self.read("at-a-glance.md")
        self.assertIn("Transparency means that sample outputs can be inspected.", page)
        self.assertNotIn("More text follows", page)                  # first sentence only
        self.assertIn("**must**: A mandatory requirement.", page)    # from the glossary
        self.assertIn("Sample developers are responsible for the compliance card.", page)

    def test_start_here_dates_from_roadmap(self):
        self.assertIn("Audits are planned for M15 to M18.", self.read("tools/start-here.md"))

    # Whole site ------------------------------------------------------------------
    def test_strict_build(self):
        res = subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict",
                              "--site-dir", str(self.tmp / "site")],
                             cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr[-3000:])


class OutlineBuild(unittest.TestCase):
    """The current guideline (outline annexes) must build with placeholders."""

    def test_placeholders_for_outline(self):
        reqs = json.loads((REPO / "docs/data/requirements.json").read_text(encoding="utf-8"))
        if reqs["status"] == "ok":
            self.skipTest("Annex A is filled in the current docx")
        page = (REPO / "docs/tools/checklist.md").read_text(encoding="utf-8")
        self.assertIn("Coming soon", page)
        self.assertIn("This will be filled from [Annex", page)


if __name__ == "__main__":
    unittest.main()
