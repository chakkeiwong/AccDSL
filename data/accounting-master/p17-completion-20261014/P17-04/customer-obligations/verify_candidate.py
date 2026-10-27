"""Preservation and final-artifact checks for the scoped 2.76 supplement."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.perf_counter()
    baseline = json.loads((OUT/"manuscript-baseline.json").read_text())
    old = (ROOT/baseline["baseline_pdf"]).parent
    new = ROOT/baseline["candidate"]
    checks = []

    def check(name, ok, detail=None):
        checks.append({"name":name,"passed":bool(ok),"detail":detail})

    check("baseline_pdf", sha(old/"accounting-product-proposal.pdf") == baseline["baseline_pdf_sha256"])
    changed = []
    for record in baseline["source_files"]:
        path = record["path"]
        check("protected:"+path, sha(old/path) == record["sha256"])
        if (old/path).read_bytes() != (new/path).read_bytes():
            changed.append(path)
    check("expected_changed_sources", set(changed) == {"accounting-product-proposal.tex","sections/corporate-methods.tex"}, changed)
    new_sources = {str(p.relative_to(new)) for p in new.rglob("*") if p.is_file() and p.suffix in [".tex",".bib",".lark"]}
    added = new_sources-{r["path"] for r in baseline["source_files"]}
    check("expected_addition", added == {"sections/customer-obligations.tex"}, sorted(added))
    contents = ["\n".join(p.read_text() for p in sorted(folder.rglob("*.tex"))) for folder in [old,new]]
    counts = {}
    for name, pattern in {
        "displays": r"\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?)\}",
        "labels": r"\\label\{[^}]+\}",
        "citations": r"\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}",
    }.items():
        a,b = [Counter(re.findall(pattern,t,re.S)) for t in contents]
        counts[name] = {"before":sum(a.values()),"after":sum(b.values()),"removed":list((a-b).elements())}
        check("preserved:"+name, not (a-b), counts[name])
    check("bibliography_unchanged", (old/"references.bib").read_bytes() == (new/"references.bib").read_bytes())
    lines = (new/"accounting-product-proposal.fls").read_text().splitlines()
    cwd = Path(next(line[4:] for line in lines if line.startswith("PWD ")))
    inputs = {(cwd/line[6:]).resolve() for line in lines if line.startswith("INPUT ")}
    repo_inputs = sorted(p for p in inputs if p.is_relative_to(ROOT))
    external = [str(p.relative_to(ROOT)) for p in repo_inputs if not p.is_relative_to(new)]
    check("no_unfrozen_project_input", not external, external)
    build = json.loads((OUT/"build-run.json").read_text())
    check("build", build["exit_code"] == 0 and not build["diagnostics"], build["diagnostics"])
    check("pdf_build_hash", sha(new/"accounting-product-proposal.pdf") == build["pdf_sha256"])
    render = json.loads((OUT/"final-render-02/render-manifest.json").read_text())
    check("final_render_hash", render["pdf_sha256"] == build["pdf_sha256"])
    review = json.loads((OUT/"render-review.json").read_text())
    check("review_bound_to_pdf", review["pdf_sha256"] == build["pdf_sha256"])
    check("reviewed_pages_present", set(map(str,review["physical_pages"])) <= set(render["pages"]))
    earlier_render = json.loads((OUT/review["carried_from"]).read_text())
    for page in review["carried_by_exact_png_hash"]:
        check("carried_visual_page:"+str(page),
              earlier_render["pages"][str(page)]["sha256"] == render["pages"][str(page)]["sha256"])
    source = json.loads((OUT/"source-manifest.json").read_text())
    check("source_pdf", sha(ROOT/source["source"]) == source["pdf_sha256"])
    check("source_extract", sha(OUT/"selected-source-pages.txt") == source["selected_text_sha256"])
    calc = json.loads((OUT/"calculation-checks.json").read_text())
    check("calculation_result", calc["passed"] and all(c["passed"] for c in calc["checks"]))
    check("index_preserved", (ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes() == subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT))
    result = {"passed":all(c["passed"] for c in checks),"check_count":len(checks),
              "checks":checks,"counts":counts,
              "repo_inputs":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in repo_inputs],
              "recorder_pwd":str(cwd),"render_review":review,
              "wall_seconds":time.perf_counter()-started}
    (OUT/"manuscript-checks.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"passed":result["passed"],"checks":len(checks),"counts":counts,
                      "repo_inputs":len(repo_inputs),"failed":[c["name"] for c in checks if not c["passed"]]}))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
