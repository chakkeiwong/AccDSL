"""Publish verified2.98 routing once and preserve the exact previous controls."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,re,shutil,subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
ARCHIVE=OUT/"control-before-r03d"
FILES=["docs/plans/accounting-master-current.md","docs/plans/accounting-master-checkpoint.md",
"docs/plans/accounting-continuation-requirements-20261007.md","docs/plans/accounting-p17-completion-20261014.md",
"docs/plans/accounting-p18-completion-20261014.md","data/accounting-master/next-plan.md"]
OLD="2509f4a325ca8921fe7141a53792daebfeafc5aea85ea6c2969a99e3fd1425d6"
NEW="39f54220018fececdd6498f28346158dff3115c332dde38b7e15686116e689f0"
SUMMARY=("R03-C's finite bank repair is integrated in Version 2.98: seven histories, 224 independent documentary checks and 106 preservation/build checks pass; seven rendered pages inspected. Modification, credit-impairment cure, delayed collateral, write-off and confirmed funding retain distinct evidence and timing. Result: data/accounting-master/finite-method-decisions-20261015/bank/result.md. Actual calibration, broader methods and full readiness remain open.")
NEXT=("Next: execute R03-D under docs/plans/accounting-group-bindings-20261015.md for common group/perimeter/FX records and replay; then R03-E finite corporate/authority decisions. Continue ready R04 literature, R05 future validation protocols and R06 reuse locks before R07/R08. Runtime execution remains held.")
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert not ARCHIVE.exists()
verified={}
for name in ["independent-checks.json","manuscript-checks.json"]:
    d=json.loads((OUT/name).read_text())
    assert d["passed"] and all(x["passed"] for x in d["checks"])
    verified[name]=d
pdf=ROOT/"docs/design/proposal/manuscript-bank-restructuring-20261015/accounting-product-proposal.pdf"
assert sha(pdf)==NEW and (OUT/"result.md").exists()
index=subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)
assert index==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
updates={}
for name in FILES:
    original=(ROOT/name).read_text()
    s=original.replace("manuscript-insurance-valuation-20261015/accounting-product-proposal.pdf",
                       "manuscript-bank-restructuring-20261015/accounting-product-proposal.pdf").replace(OLD,NEW)
    for a,b in [
        ("Version **2.97**, 288","Version **2.98**, 292"),
        ("**Version 2.97, 288","**Version 2.98, 292"),
        ("Version 2.97, 288","Version 2.98, 292"),
        ("current Version 2.97 candidate","current Version 2.98 candidate"),
        ("through 2.97","through 2.98"),("2.73–2.97","2.73–2.98"),
        ("Version2.97 and full2.72 assessment","Version2.98 and full2.72 assessment")
    ]:
        s=s.replace(a,b)
    s=re.sub(r"Next: execute R03-C[^\n]*",NEXT,s)
    s=s.replace("## Insurance valuation and next work — 15 October 2026",
                "## Bank restructuring and next work — 15 October 2026\n\n"+SUMMARY+
                "\n\n"+NEXT+"\n\n## Insurance valuation — 15 October 2026",1)
    assert s!=original and SUMMARY in s and "Next: execute R03-C" not in s
    updates[name]=s
name="data/accounting-master/p17-completion-20261014/P17-06/operation-matrix.md"
s=(ROOT/name).read_text().replace("current candidate2.89","current candidate2.98")
s=s.replace("Broader restructuring/derecognition, cures, collateral recoveries and actual legal terms remain","Delivered2.98: non-derecognising modification/cure versus still-impaired interest, full legal release and late collateral/write-off. Actual legal/credit findings, fees, partial transfers and continuing involvement remain")
s=s.replace("Actual facility eligibility, collateral, venues, funding costs, maturity and stress behavior; no invented central-bank funding","Delivered2.98: synthetic eligibility/haircut/capacity and full/partial/pending confirmed-receipt paths; actual facility, venues, costs, maturity and calibrated stress behavior remain")
s+="\nVersion2.98 bank result: ../../finite-method-decisions-20261015/bank/result.md. Continue R03-D group bindings; preserve actual authority/calibration and full P17-06 obligations.\n"
updates[name]=s
name="docs/plans/accounting-finite-method-decisions-20261015.md"
updates[name]=(ROOT/name).read_text()+"\nR03-C's scoped bank methods are integrated in2.98. The next audited plan is accounting-group-bindings-20261015.md; R03-D and E remain, with wider method/source residuals retained.\n"
name="data/accounting-master/finite-method-decisions-20261015/decisions.md"
s=(ROOT/name).read_text()
s=s.replace("Historical AASB9 source passages located; existing bank/commitment/prudential methods | accounting-bank-restructuring-funding-20261015.md audited and ready | Execute exact paths; preserve POCI/new-asset and actual legal/funding decisions | Active; no closure yet", "AASB9 rights/interest/risk/collateral and AASB107 cash passages inspected; bank/source-reading.md | bank-restructuring-funding-20261015.md;seven cases,224 checks | Actual laws/legal findings, fees, partial transfers/continuing involvement and facility terms remain | Scoped repair delivered2.98; broader bank obligations remain")
s=s.replace("Ready after current bank unit", "Active under accounting-group-bindings-20261015.md")
updates[name]=s
before={n:sha(ROOT/n) for n in updates}
for n in updates:
 p=ARCHIVE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,p)
for n,s in updates.items():(ROOT/n).write_text(s)
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==index
(OUT/"control-refresh.json").write_text(json.dumps({"before":before,"after":{n:sha(ROOT/n) for n in updates},"index_preserved":True,"next":NEXT},indent=2)+"\n")
manifest={"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
"worktree":"dirty;100 unrelated staged entries preserved;no commit",
"commands":["python3 data/accounting-master/finite-method-decisions-20261015/bank/"+n+".py" for n in ["build_cases","refine_cases","verify_cases","prepare_manuscript","verify_manuscript","refresh_controls"]],
"document_commands":["python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-bank-restructuring-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/bank --timeout 240 --force", "python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-bank-restructuring-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/bank/accepted-render --pages 1,192-197 --dpi 110"],
"build_executions":4,"prior_render_directories":["final-render","verified-render"],
"environment":{"python":platform.python_version(),"execution":"CPU exact fractions;approved LuaLaTeX build","gpu":"N/A;no framework imported or GPU operation"},
"data_version":[{"id":s["id"],"pdf_sha256":s["pdf_sha256"]} for s in json.loads((OUT/"source-support.json").read_text())["authorities"]],
"random_seeds":"N/A;authored finite laws enumerated without sampling",
"wall_time":{"checks_seconds":verified["independent-checks.json"]["wall_seconds"],"build":json.loads((OUT/"build-run.json").read_text()),"interactive_total":"not measured"},
"plan":"docs/plans/accounting-bank-restructuring-funding-20261015.md","result":str((OUT/"result.md").relative_to(ROOT)),
"candidate_pdf":str(pdf.relative_to(ROOT)),"candidate_pdf_sha256":NEW,
"artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sorted(OUT.glob("*")) if p.is_file() and p.name!="run-manifest.json"]}
(OUT/"run-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"candidate":"2.98","controls":6,"index_preserved":True,"next":"R03-D"}))
