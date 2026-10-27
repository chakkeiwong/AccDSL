"""Preservation and closeout evidence for the 2.74 document candidate."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import platform
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.perf_counter()
    baseline = json.loads((OUT / "manuscript-baseline.json").read_text())
    old = (ROOT / baseline["baseline_pdf"]).parent
    new = ROOT / baseline["candidate"]
    findings = []
    def check(name, passed, detail=None):
        findings.append({"check":name,"passed":bool(passed),"detail":detail})
    check("baseline_pdf",sha(old/"accounting-product-proposal.pdf")==baseline["baseline_pdf_sha256"])
    changed=[]
    texts=[[],[]]
    for record in baseline["source_files"]:
        relative=record["path"]
        check("protected_source:"+relative,sha(old/relative)==record["sha256"])
        if (old/relative).read_bytes()!=(new/relative).read_bytes():
            changed.append(relative)
        if relative.endswith(".tex"):
            for buf,folder in zip(texts,[old,new]):
                buf.append((folder/relative).read_text())
    check("changed_source_scope",set(changed)=={"references.bib","accounting-product-proposal.tex","sections/apple-segments.tex","sections/apple-pronouncements.tex"},changed)
    before,after=["\n".join(t) for t in texts]
    patterns={"display_blocks":r"\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?)\}",
        "labels":r"\\label\{[^}]+\}","citation_occurrences":r"\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}"}
    counts={}
    for kind,pattern in patterns.items():
        a=Counter(re.findall(pattern,before,re.S)); b=Counter(re.findall(pattern,after,re.S))
        removed=list((a-b).elements())
        counts[kind]={"before":sum(a.values()),"after":sum(b.values()),"removed":removed}
        check("preserved:"+kind,not removed,counts[kind])
    oldbib=(old/"references.bib").read_text()
    newbib=(new/"references.bib").read_text()
    # Entries may be inserted beside the same issuer; their exact old contents
    # must remain intact. Physical append position is not the preservation rule.
    def entries(text):
        parts=re.split(r"(?=^@\w+\{)",text,flags=re.M)
        return {re.match(r"@\w+\{([^,]+)",part).group(1):part.strip()
                for part in parts if part.startswith("@")}
    oldentries,newentries=entries(oldbib),entries(newbib)
    check("bibliography_entries_preserved",all(newentries.get(k)==v for k,v in oldentries.items()),
          {"old_entries":len(oldentries),"new_entries":len(newentries)})
    build=json.loads((OUT/"build-run.json").read_text())
    check("build_pass",build["exit_code"]==0 and not build["diagnostics"])
    check("pdf_matches_build",sha(new/"accounting-product-proposal.pdf")==build["pdf_sha256"])
    inspected=[1,30,31,36,37,38,39,215,220]
    inspection={"pdf_sha256":build["pdf_sha256"],"physical_pages":inspected,
        "reviewer":"Codex author visual inspection",
        "findings":"No clipped text or overlapping tables/equations found on the inspected pages. Source comparison, adjacent transitions and the new bibliography entry inspected.",
        "whole_candidate_review":False,"human_comprehension":"pending"}
    (OUT/"render-review.json").write_text(json.dumps(inspection,indent=2)+"\n")
    original_index=ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt"
    check("unrelated_index_preserved",original_index.read_bytes()==subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT))
    result={"passed":all(f["passed"] for f in findings),"check_count":len(findings),"checks":findings,"counts":counts,"changed_sources":changed}
    (OUT/"manuscript-checks.json").write_text(json.dumps(result,indent=2)+"\n")
    manifest={"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "commands":["python3 data/accounting-master/p17-completion-20261014/P17-02/check_retrospective_segments.py","python3 data/accounting-master/p17-completion-20261014/P17-02/consolidate_package.py","python3 data/accounting-master/p17-completion-20261014/P17-02/verify_candidate.py"],
        "build_and_render_commands":"build-run.json; render-manifest.json; bibliography-view/render-manifest.json; execution-note.md",
        "environment":{"python":platform.python_version(),"platform":platform.platform(),"conda_env":"N/A; installed system document tools"},
        "cpu_gpu":"CPU document work; no numerical framework or GPU used","random_seeds":"N/A; deterministic",
        "data_version":"Frozen FY2024/Q1 Apple package plus retained FY2025 annual and linked dated inquiries; input hashes retained in source-run.json and connected-package-map.json",
        "plan":"docs/plans/accounting-apple-retrospective-segments-20261014.md","result":str((OUT/"result.md").relative_to(ROOT)),
        "candidate_pdf":str((new/"accounting-product-proposal.pdf").relative_to(ROOT)),"candidate_pdf_sha256":build["pdf_sha256"],
        "wall_seconds":{"verification":time.perf_counter()-start,"build":build["wall_seconds"],"source_comparison":"source-run.json","map":"package-map-checks.json","manual_review":"not instrumented; no fabricated total"},
        "outputs":{str(p.relative_to(ROOT)):sha(p) for name in ["result.md","connected-package-map.json","connected-package-map.md","package-map-checks.json","manuscript-checks.json","render-review.json","source-checks.json","retrospective-segment-readings.json"] if (p:=OUT/name).exists()},
        "readiness":"not_ready","runtime_or_controller_started":False}
    (OUT/"run-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"passed":result["passed"],"checks":len(findings),"counts":counts,"changed_sources":changed}))
    if not result["passed"]:
        raise SystemExit(1)


if __name__=="__main__":
    main()
