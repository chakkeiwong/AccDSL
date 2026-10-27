"""Publish verified2.97 routing once; archive the exact prior controls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, platform, re, shutil, subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
ARCHIVE=OUT/"control-before-r03c"
FILES=[
    "docs/plans/accounting-master-current.md",
    "docs/plans/accounting-master-checkpoint.md",
    "docs/plans/accounting-continuation-requirements-20261007.md",
    "docs/plans/accounting-p17-completion-20261014.md",
    "docs/plans/accounting-p18-completion-20261014.md",
    "data/accounting-master/next-plan.md"
]
OLD="10af497755650076da3ee4516cea72359528ba09aedef3a1082f97e800dc00a4"
NEW="2509f4a325ca8921fe7141a53792daebfeafc5aea85ea6c2969a99e3fd1425d6"
SUMMARY=("R03-B's finite insurance valuation and acquisition/treaty interaction are integrated "
         "in Version 2.97: six histories, 433 independent documentary checks and 105 "
         "preservation/build checks pass; eight rendered pages were inspected. The guarantee "
         "price is derived by replication; physical probabilities and nonfinancial risk "
         "adjustment stay separate. Timely/late treaty recognition and acquisition transfer "
         "retain different income histories. Result: "
         "data/accounting-master/finite-method-decisions-20261015/insurance/result.md. "
         "Actual calibration, wider insurance methods, R03 and full readiness remain open.")
NEXT=("Next: execute R03-C under docs/plans/accounting-bank-restructuring-funding-20261015.md "
      "for restructuring, cure, collateral and confirmed funding; then R03-D group bindings "
      "and R03-E finite corporate/authority decisions. Continue ready R04 literature, R05 "
      "future validation protocols and R06 reuse locks before R07/R08. Runtime execution remains held.")
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert not ARCHIVE.exists()
verified={}
for name in ["independent-checks.json","manuscript-checks.json"]:
    d=json.loads((OUT/name).read_text())
    assert d["passed"] and all(x["passed"] for x in d["checks"])
    verified[name]=d
pdf=ROOT/"docs/design/proposal/manuscript-insurance-valuation-20261015/accounting-product-proposal.pdf"
assert sha(pdf)==NEW and (OUT/"result.md").exists()
index=subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)
assert index==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
updates={}
for name in FILES:
    original=(ROOT/name).read_text()
    s=original.replace("manuscript-financing-changes-20261015/accounting-product-proposal.pdf",
                       "manuscript-insurance-valuation-20261015/accounting-product-proposal.pdf").replace(OLD,NEW)
    for a,b in [
        ("Version **2.96**, 284","Version **2.97**, 288"),
        ("**Version 2.96, 284","**Version 2.97, 288"),
        ("Version 2.96, 284","Version 2.97, 288"),
        ("current Version 2.96 candidate","current Version 2.97 candidate"),
        ("through 2.96","through 2.97"),("2.73–2.96","2.73–2.97"),
        ("Version2.96 and full2.72 assessment","Version2.97 and full2.72 assessment")
    ]:
        s=s.replace(a,b)
    s=re.sub(r"Next: continue R03-B[^\n]*",NEXT,s)
    s=s.replace("## Financing repair and next work — 15 October 2026",
                "## Insurance valuation and next work — 15 October 2026\n\n"+SUMMARY+
                "\n\n"+NEXT+"\n\n## Financing repair — 15 October 2026",1)
    assert s!=original and SUMMARY in s and "Next: continue R03-B" not in s
    updates[name]=s
name="data/accounting-master/p17-completion-20261014/P17-07/operation-matrix.md"
s=(ROOT/name).read_text().replace("Current candidate 2.88","Current candidate 2.97")
s=s.replace("Remaining actual expense residual unassigned; richer acquisition/reinsurance combination still needed",
            "Delivered2.97: acquisition transfer into an onerous group, timely/late held-treaty loss recovery and B125 presentation. Actual expense residual, partial/changing cover and actual facts remain")
s=s.replace("Priced guarantee with supported financial law and complete group consequences; do not treat terminal payoff as valuation",
            "Delivered2.97: exact two-state replication, distinct physical law/RA, four complete VFA histories with CSM exhaustion and investment-component exclusion. Actual financial model, admission/RA/dependence and calibration remain")
s+="\nVersion2.97 adds six insurance histories,433 independent documentary checks and105 preservation/build checks; eight affected pages inspected. See ../../finite-method-decisions-20261015/insurance/result.md. R03-C bank work now proceeds; broader insurance validation and actual-data obligations remain.\n"
updates[name]=s
parent="docs/plans/accounting-finite-method-decisions-20261015.md"
updates[parent]=(ROOT/parent).read_text()+"\n## Execution checkpoint\n\nR03-A is integrated in2.96 and R03-B's finite guarantee/acquisition-treaty methods in2.97. Their exact results and remaining limits are in data/accounting-master/finite-method-decisions-20261015/decisions.md. The audited R03-C plan is accounting-bank-restructuring-funding-20261015.md. Continue C, D and E; no full R03/P17 readiness is asserted.\n"
before={name:sha(ROOT/name) for name in updates}
for name in updates:
    p=ARCHIVE/name
    p.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/name,p)
for name,s in updates.items():
    (ROOT/name).write_text(s)
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==index
(OUT/"control-refresh.json").write_text(json.dumps({
    "recorded_utc":datetime.now(timezone.utc).isoformat(),"before":before,
    "after":{name:sha(ROOT/name) for name in updates},"index_preserved":True,"next":NEXT
},indent=2)+"\n")
commands=["python3 data/accounting-master/finite-method-decisions-20261015/insurance/"+name+".py"
          for name in ["build_cases","verify_cases","prepare_manuscript","verify_manuscript","refresh_controls"]]
commands += [
    "python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-insurance-valuation-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/insurance --timeout 240 --force",
    "python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-insurance-valuation-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/insurance/second-render --pages 207 --dpi 110",
    "python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-insurance-valuation-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/insurance/final-render --pages 1,205-208,218-220 --dpi 110",
    "python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-insurance-valuation-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/insurance/verified-render --pages 1,205-208,218-220 --dpi 110"
]
sources=json.loads((OUT/"source-support.json").read_text())["authorities"]
manifest={
    "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
    "worktree":"dirty;100 unrelated staged entries preserved;no commit",
    "commands":commands,"build_executions":4,
    "build_repairs":"Undefined citation key, overflowing path, then ambiguous predecessor reference corrected. Initial PDF/log and earlier rendered evidence preserved.",
    "environment":{"python":platform.python_version(),"execution":"CPU exact fractions and approved LuaLaTeX document build",
                   "gpu":"N/A;no numerical framework imported or GPU detected"},
    "data_version":[{"id":s["id"],"pdf":s["pdf"],"pdf_sha256":s["pdf_sha256"]} for s in sources],
    "random_seeds":"N/A;exact enumeration of authored finite law;no stochastic sampling",
    "wall_time":{"independent_checks_seconds":verified["independent-checks.json"]["wall_seconds"],
                 "final_build":json.loads((OUT/"build-run.json").read_text()),
                 "interactive_total":"not measured"},
    "plan":"docs/plans/accounting-insurance-priced-guarantee-20261015.md",
    "result":str((OUT/"result.md").relative_to(ROOT)),"candidate_pdf":str(pdf.relative_to(ROOT)),
    "candidate_pdf_sha256":NEW,
    "artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)}
                 for p in sorted(OUT.glob("*")) if p.is_file() and p.name!="run-manifest.json"]
}
(OUT/"run-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"candidate":"2.97","controls":len(FILES),"matrix":"P17-07",
                  "index_preserved":True,"next":"R03-C"}))
