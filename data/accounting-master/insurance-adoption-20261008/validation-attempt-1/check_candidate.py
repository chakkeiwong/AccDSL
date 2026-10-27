"""Check document preservation, evidence binding and source-backed arithmetic."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import time

import fitz

START=time.monotonic()
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
OLD=ROOT/"docs/design/proposal/manuscript-insurance-20261008"
NEW=ROOT/"docs/design/proposal/manuscript-adoption-20261008"
if (OUT/"completion.json").exists():
    raise SystemExit("Closed unit; verify without regenerating its evidence")
checks=[]
inputs={}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    inputs[str(p.relative_to(ROOT))]=sha(p)
    return json.loads(p.read_text())


def check(name, ok, detail=None):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))


def verify(name, hashes):
    bad=[n for n,h in hashes.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    check(name,not bad,dict(count=len(hashes),mismatches=bad))


baseline=read(OUT/"baseline.json")
verify("V2.5 unit, source candidate and issuer inputs preserved",baseline["protected_hashes"])
relocations={r["historical_path"]:r["preserved_path"] for r in baseline["pointer_relocations"]}
verify("saved pointers preserved",{r["preserved_path"]:r["sha256"] for r in baseline["pointer_relocations"]})
previous=read(ROOT/baseline["prior_manifest"])
verify("previous manifest resolves through saved pointers",{relocations.get(n,n):h for n,h in previous["artifact_hashes"].items()})
old_files={p.relative_to(OLD) for p in OLD.rglob("*") if p.suffix in {".tex",".bib",".lark"}}
new_files={p.relative_to(NEW) for p in NEW.rglob("*") if p.suffix in {".tex",".bib",".lark"}}
check("source inventory retained",old_files==new_files)
changed=[]
diff=[]
old_tex=[]
new_tex=[]
for p in sorted(old_files):
    before=(OLD/p).read_text(); after=(NEW/p).read_text()
    inputs[str((NEW/p).relative_to(ROOT))]=sha(NEW/p)
    if before!=after:
        changed.append(str(p))
        diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(OLD/p),tofile=str(NEW/p)))
    if p.suffix==".tex":
        old_tex.append(before);new_tex.append(after)
(OUT/"manuscript-delta.diff").write_text("".join(diff))
check("only planned four sources changed",set(changed)=={"accounting-product-proposal.tex","chapters/08-modules.tex","sections/insurance-methods.tex","references.bib"})
old_tex="\n".join(old_tex);new_tex="\n".join(new_tex)
pattern=r"\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{\1\}"
displays=lambda t:[m.group() for m in re.finditer(pattern,t,re.S)]
check("all previous displays preserved verbatim",displays(old_tex)==displays(new_tex),len(displays(old_tex)))
old_ins=(OLD/"sections/insurance-methods.tex").read_text(); new_ins=(NEW/"sections/insurance-methods.tex").read_text()
before,new_part=new_ins.split("\\section{Adoption dates and the restatement of 2022}",1)
addition,after=new_part.split("\\hypertarget{interfaces-exclusions-and-acceptance-cases}{%",1)
restored=before+"\\hypertarget{interfaces-exclusions-and-acceptance-cases}{%"+after
pattern=r"This comparison uses identified editions\..*?(?=\n\nReinsurance has its own group)"
old_par=re.search(pattern,old_ins,re.S).group()
restored=re.sub(pattern,lambda _:old_par,restored,flags=re.S)
check("earlier insurance prose preserved outside explicit adoption revision",restored==old_ins)
check("source roles and material qualifications retained",all(s in addition for s in ["operative 2020 and 2025", "unlisted", "Non-controlling", "availability result", "classification overlay", "impracticable", "not a same-context"]))
old_bib=(OLD/"references.bib").read_text();new_bib=(NEW/"references.bib").read_text()
keys=lambda t:re.findall(r"@\w+\s*\{\s*([^,\s]+)",t)
check("prior bibliography bytes preserved",new_bib.startswith(old_bib))
check("three unique additions",set(keys(new_bib))-set(keys(old_bib))=={"mofinsurance2025qa","pingan2022asbe","pingan2023asbe"} and len(keys(new_bib))==len(set(keys(new_bib))))
cites=lambda t:{k.strip() for g in re.findall(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}",t) for k in g.split(",")}
check("all citations preserved and resolved",cites(old_tex)<=cites(new_tex)<=set(keys(new_bib)))
labels=re.findall(r"\\label\{([^}]+)\}",new_tex); refs=re.findall(r"\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}",new_tex)
check("unique labels and resolved references",len(labels)==len(set(labels)) and set(refs)<=set(labels))
pdf=NEW/"accounting-product-proposal.pdf"
doc=fitz.open(pdf);text=" ".join(" ".join(p.get_text().split()) for p in doc)
check("new version and material content rendered",all(s in text for s in ["Version 2.6","11,137,168","11,009,940","573,477","446,249","21 March 2024","127,228"]))
log=(NEW/"accounting-product-proposal.log").read_text()
warnings=[l for l in log.splitlines() if any(s in l for s in ["Warning","Overfull","Underfull","! "])]
check("clean final LuaLaTeX log","LuaHBTeX" in log and not warnings,warnings)
check("clean bibliography log",not re.search(r"Warning--|error message|I couldn.t open",(NEW/"accounting-product-proposal.blg").read_text()))
build=read(OUT/"build-receipt.json")
check("build receipt binds final PDF and log",build["exit_code"]==0 and build["pdf_sha256"]==sha(pdf) and build["log_sha256"]==sha(OUT/"build.log"))
render=read(OUT/"render-manifest.json"); review=read(OUT/"render-review.json")
check("render binds same PDF",render["pdf_sha256_before"]==render["pdf_sha256_after"]==sha(pdf))
check("review binds render and actual pages",review["render_manifest_sha256"]==sha(OUT/"render-manifest.json") and review["author_review_sha256"]==sha(OUT/"author-review.md") and review["page_numbers"]==render["page_numbers"])
verify("rendered bytes preserved",{r["path"]:r["sha256"] for r in render["rendered_pages"].values()})
check("human and independent acceptance separate",review["independent_reader"]==review["human_acceptance"]=="pending")
evidence=read(OUT/"evidence-checks.json")
check("source checks are current and passing",evidence["failed"]==0 and evidence["checker_sha256"]==sha(OUT/"prepare_evidence.py") and all(c["passed"] for c in evidence["checks"]))
verify("source check inputs preserved",evidence["inputs"])
verify("source claims, comparative rows and acquisition outputs bound",evidence["output_hashes"])
for r in read(OUT/"acquisition-receipts.json")["requests"]:
    verify("transport evidence "+r["attempt"],r["files"])
history=read(ROOT/"data/accounting-master/direct-p19-20261007/recovery-entry-v1.json")
counts={}
for key in ["protected_hashes","upstream_reference_hashes","controller_hashes"]:
    verify("historical "+key,history[key]);counts[key]=len(history[key])
continuation=read(ROOT/"data/accounting-master/continuation-20261007/baseline-manifest.json")
reloc={r["historical_path"]:r["preserved_path"] for r in continuation["relocations"]}
verify("P19 evidence preserved at historical pointer paths",{reloc.get(n,n):h for n,h in continuation["p19_historical_artifact_hashes"].items()})
readiness=read(ROOT/"data/accounting-master/deliverables/P19/readiness.json")
check("full proposal remains not_ready",readiness["status"]=="not_ready" and not readiness["ready"] and set(readiness["remaining_blockers"])=={"P15-"+s for s in ["E01","E05","E07","E08","E14"]})
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,
            pdf=dict(path=str(pdf.relative_to(ROOT)),sha256=sha(pdf),pages=len(doc)),changed_sources=changed,
            display_count=len(displays(old_tex)),baseline_bibliography_keys=len(keys(old_bib)),candidate_bibliography_keys=len(keys(new_bib)),
            preservation_counts=counts,checks=checks,passed=sum(c["passed"] for c in checks),failed=sum(not c["passed"] for c in checks),
            wall_seconds=time.monotonic()-START,scope="Bounded document/source/preservation evidence only")
(OUT/"candidate-checks.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({k:report[k] for k in ["passed","failed","display_count","baseline_bibliography_keys","candidate_bibliography_keys"]}))
if report["failed"]:
    print(json.dumps([c for c in checks if not c["passed"]],ensure_ascii=False))
    raise SystemExit(1)
