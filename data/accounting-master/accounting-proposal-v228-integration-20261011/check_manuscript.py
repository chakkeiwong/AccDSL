#!/usr/bin/env python3
"""Check the Version 2.28 instrument-terms manuscript delta."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASELINE_TREE = ROOT / "docs/design/proposal/manuscript-jpmorgan-guarantees-20261011"
CANDIDATE = ROOT / "docs/design/proposal/manuscript-jpmorgan-terms-20261011"
start = time.monotonic()
checks: list[dict] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(label: str, ok: bool, details=None) -> None:
    row = {"check": label, "passed": bool(ok)}
    if details is not None:
        row["details"] = details
    checks.append(row)


def source_files(tree: Path) -> set[Path]:
    return {
        path.relative_to(tree)
        for path in tree.rglob("*")
        if path.is_file() and path.suffix in {".tex", ".bib", ".lark"}
    }


def displays(text: str) -> list[str]:
    pattern = re.compile(
        r"\\\[.*?\\\]|"
        r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?"
        r"\\end\{\1\}",
        re.S,
    )
    return [match.group(0) for match in pattern.finditer(text)]


base = json.loads((OUT / "baseline.json").read_text(encoding="utf-8"))
baseline_pdf = ROOT / base["baseline_pdf"]["path"]
candidate_pdf = ROOT / base["candidate_pdf"]["path"]
check("protected Version 2.27 PDF identity", baseline_pdf.is_file() and sha(baseline_pdf) == base["baseline_pdf"]["sha256"])
check("protected Version 2.27 PDF has 168 pages", len(fitz.open(baseline_pdf)) == 168)
check("Version 2.28 candidate PDF identity", candidate_pdf.is_file() and sha(candidate_pdf) == base["candidate_pdf"]["sha256"])

old_files = source_files(BASELINE_TREE)
new_files = source_files(CANDIDATE)
check("candidate source inventory matches baseline", old_files == new_files)
changed: list[str] = []
before_tex: list[str] = []
after_tex: list[str] = []
for rel in sorted(old_files):
    before = (BASELINE_TREE / rel).read_text(encoding="utf-8")
    after = (CANDIDATE / rel).read_text(encoding="utf-8")
    if before != after:
        changed.append(rel.as_posix())
    if rel.suffix == ".tex":
        before_tex.append(before)
        after_tex.append(after)
    if rel.as_posix() == "accounting-product-proposal.tex":
        expected = before.replace(
            "Version 2.27 (proposal candidate) \\quad 11 October 2026",
            "Version 2.28 (proposal candidate) \\quad 11 October 2026",
        )
        check("main TeX has only the Version 2.28 title change", after == expected)
    elif rel.as_posix() == "chapters/15-banking.tex":
        check("bank chapter has a reader-facing delta", before != after)
        prefix, addition = after.split("The complete Form~10-Ks", 1)
        addition, suffix = addition.split("Loan origination can debit loans", 1)
        check("all original bank prose retained verbatim", prefix + "Loan origination can debit loans" + suffix == before)
        flat = " ".join(after.split())
        required = [
            "The complete Form~10-Ks",
            "fully and unconditionally guaranteed",
            "direct, unsecured general obligations",
            "ranking equally with its other unsecured and unsubordinated debt",
            "Claims under the parent guarantee generally rank behind those of subsidiary creditors",
            "payment, not collection",
            "on demand after issuer nonpayment",
            "principal, interest and other amounts",
            "2016~Indenture",
            "issuer is excused from paying",
            "actually due",
            "Issuer defenses and counterclaims carry over, except those arising solely from insolvency or bankruptcy status",
            "current balance, valuation or accounting recognition",
        ]
        for phrase in required:
            check("bank source qualification: " + phrase, phrase in flat)
    else:
        check("unchanged source file: " + rel.as_posix(), before == after)

check(
    "only intended source files changed",
    set(changed) == {"accounting-product-proposal.tex", "chapters/15-banking.tex"},
    changed,
)
before_all = "\n".join(before_tex)
after_all = "\n".join(after_tex)
check("actual TeX delta is nonempty", before_all != after_all)
before_displays = displays(before_all)
after_displays = displays(after_all)
check("all 48 displayed equations remain", len(before_displays) == len(after_displays) == 48)
check("displayed equations are byte-for-byte unchanged", before_displays == after_displays)

labels = re.findall(r"\\label\{([^{}]+)\}", after_all)
refs = re.findall(r"\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}", after_all)
check("labels remain unique", len(labels) == len(set(labels)))
check("all literal references resolve", set(refs) <= set(labels), sorted(set(refs) - set(labels)))

old_bib = (BASELINE_TREE / "references.bib").read_text(encoding="utf-8")
new_bib = (CANDIDATE / "references.bib").read_text(encoding="utf-8")
check("bibliography is unchanged from Version 2.27", old_bib == new_bib)
bib_keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)", new_bib)
check("bibliography retains 71 entries", len(bib_keys) == 71)
check("bibliography keys remain unique", len(bib_keys) == len(set(bib_keys)))
citation_groups = re.findall(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}", after_all)
cited = {key.strip() for group in citation_groups for key in group.split(",")}
check("all citations resolve", cited <= set(bib_keys), sorted(cited - set(bib_keys)))
check("all four JPMorgan sources remain cited", {"jpmorgan2022tenk", "jpmorgan2023tenk", "jpmorgan2024tenk", "jpmorgan2025tenk"} <= cited)

with fitz.open(candidate_pdf) as document:
    candidate_pages = len(document)
    candidate_text = " ".join(" ".join(page.get_text() for page in document).split())
candidate_text = re.sub(r"(?<=\w)-\s+(?=\w)", "", candidate_text)
check("candidate PDF has the bound page count", candidate_pages == base["candidate_pdf"]["pages"])
check("candidate PDF renders the Version 2.28 title", "Version 2.28" in candidate_text)
for phrase in ["payment, not collection", "direct, unsecured general obligations", "actually due", "current balance, valuation or accounting recognition", "insolvency or bankruptcy status"]:
    check("candidate PDF renders: " + phrase, phrase in candidate_text)

log = (CANDIDATE / "accounting-product-proposal.log").read_text(encoding="utf-8")
bad_log = [
    line for line in log.splitlines()
    if re.search(r"^! |Overfull|Underfull|LaTeX Warning|Package .* Warning|undefined citation|undefined reference", line, re.I)
]
check("final TeX log has no fatal/warning/box diagnostics", not bad_log, bad_log[:12])
blg = (CANDIDATE / "accounting-product-proposal.blg").read_text(encoding="utf-8")
check("BibTeX log has no errors", not re.search(r"Warning--|error message|I couldn.t open", blg, re.I))

terms = json.loads((ROOT / base["source_unit"] / "terms.json").read_text(encoding="utf-8"))
check("instrument-terms source checks remain 48/0", terms.get("passed") == 48 and terms.get("failed") == 0)
closeout = json.loads((ROOT / base["source_unit"] / "closeout-checks.json").read_text(encoding="utf-8"))
check("instrument-terms closeout remains passing", closeout.get("failed") == 0)
for row in terms["records"]:
    text_path, pdf_path = ROOT / row["text"], ROOT / row["pdf"]
    check(str(row["year"]) + " source identities retained", sha(text_path) == row["text_sha256"] and sha(pdf_path) == row["pdf_sha256"])
    lines = text_path.read_text().splitlines()
    for key, span in row["spans"].items():
        if span["start_line"] is None:
            check(str(row["year"]) + " absent funding wording retained", span["marker"] not in " ".join(lines).lower())
        else:
            quote = "\n".join(lines[span["start_line"]-1:span["end_line"]]).strip()
            check(str(row["year"]) + " source-bound span: " + key, quote == span["quote"] and hashlib.sha256(quote.encode()).hexdigest() == span["quote_sha256"])

report = {
    "recorded_at": "2026-10-11",
    "command": ["python3", str(Path(__file__).relative_to(ROOT))],
    "checker_sha256": sha(Path(__file__)),
    "baseline": base,
    "candidate_pdf": {"path": str(candidate_pdf.relative_to(ROOT)), "sha256": sha(candidate_pdf), "pages": candidate_pages},
    "changed_sources": changed,
    "display_count": len(after_displays),
    "source_check_counts": {"instrument_terms": 48},
    "checks": checks,
    "passed": sum(row["passed"] for row in checks),
    "failed": sum(not row["passed"] for row in checks),
    "wall_seconds": time.monotonic() - start,
    "scope": "Version 2.28 source preservation, instrument-term integration, citation/equation integrity and build binding; independent reader and domain acceptance remain pending.",
}
(OUT / "manuscript-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: report[key] for key in ["passed", "failed", "display_count", "changed_sources"]}, indent=2))
if report["failed"]:
    raise SystemExit(1)
