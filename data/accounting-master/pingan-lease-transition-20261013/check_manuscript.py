"""Verify the bounded addition and preservation of the protected manuscript."""
import collections
import json
import re
import time

import fitz

from build_candidate import BASE, CAND, OUT, ROOT, expected_text, sha, save


def features(folder, paths):
    text = "\n".join((folder / p).read_text() for p in paths if p.endswith(".tex"))
    cites = collections.Counter()
    for body in re.findall(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}", text):
        cites.update(k.strip() for k in body.split(","))
    displays = collections.Counter(re.findall(
        r"\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?"
        r"\\end\{(?:equation|align|gather|multline)\*?\}", text, re.S))
    return cites, displays


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    candidate = json.loads((OUT / "candidate.json").read_text())
    source = json.loads((OUT / "source-checks.json").read_text())
    renders = json.loads((OUT / "candidate-renders.json").read_text())
    review = json.loads((OUT / "rendered-review.json").read_text())
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    ck("source checks", source["passed"] == 51 and not source["failed"]
       and all(x["passed"] for x in source["checks"]))
    ck("protected PDF", sha(BASE / "accounting-product-proposal.pdf") == candidate["baseline_pdf_sha256"])
    for rel, digest in candidate["source_hashes"].items():
        ck("protected source " + rel, sha(BASE / rel) == digest)
        ck("exact allowed source change " + rel, (CAND / rel).read_text() == expected_text(rel))
    old_cites, old_displays = features(BASE, candidate["source_hashes"])
    new_cites, new_displays = features(CAND, candidate["source_hashes"])
    ck("all previous citation occurrences retained", not (old_cites - new_cites))
    ck("all previous displays retained", not (old_displays - new_displays))
    ck("one new bibliography record", (CAND / "references.bib").read_text()
       == (BASE / "references.bib").read_text() + (OUT / "references-addition.bib").read_text())
    bibliography_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", (CAND / "references.bib").read_text()))
    ck("cited references resolve", new_cites["pingan2019asbe"] > 0 and set(new_cites) <= bibliography_keys)
    log = (CAND / "accounting-product-proposal.log").read_text()
    ck("clean final TeX log", not re.search(r"Warning|Overfull|Underfull|undefined|^!", log, re.M))
    ck("successful build", json.loads((OUT / "build-run.json").read_text())["exit_code"] == 0)
    pdf = CAND / "accounting-product-proposal.pdf"
    with fitz.open(pdf) as doc:
        text = "\n".join(p.get_text() for p in doc)
        ck("193 PDF pages", len(doc) == renders["pdf_pages"] == 193)
        ck("version and new section in PDF", "Version 2.51" in text and "Reading an actual lease transition" in text)
        ck("reported balances in PDF", all(s in text for s in ["18,500", "17,667", "17,390", "17,212", "18,933", "7,400"]))
    ck("final PDF identity", sha(pdf) == renders["pdf_sha256"] == review["pdf_sha256"])
    ck("all seven final renders reviewed", {x["pdf_page"] for x in review["pages"] if x["inspected"]}
       == {1, 5, 103, 104, 105, 106, 191})
    for row in renders["pages"]:
        ck("render identity " + str(row["pdf_page"]), sha(ROOT / row["render"]) == row["sha256"])
    recovery = json.loads((ROOT / "data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json").read_text())
    for rel, digest in recovery["protected_hashes"].items():
        ck("frozen evidence " + rel, sha(ROOT / rel) == digest)
    failed = [x["name"] for x in checks if not x["passed"]]
    save("manuscript-checks.json", {"checks": checks, "passed": len(checks)-len(failed), "failed": failed,
         "baseline_citation_occurrences": sum(old_cites.values()), "candidate_citation_occurrences": sum(new_cites.values()),
         "baseline_unique_citation_keys": len(old_cites), "candidate_unique_citation_keys": len(new_cites),
         "baseline_display_blocks": sum(old_displays.values()), "candidate_display_blocks": sum(new_displays.values()),
         "source_files": len(candidate["source_hashes"]), "pdf_sha256": sha(pdf), "wall_seconds": time.monotonic()-start})
    print(json.dumps({"passed": len(checks)-len(failed), "failed": failed}))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
