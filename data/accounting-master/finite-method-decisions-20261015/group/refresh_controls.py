"""Publish verified2.99 routing once, preserving exact previous controls."""
from pathlib import Path
import hashlib,json,platform,re,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
ARCHIVE=OUT/"control-before-r03e"
FILES=["docs/plans/accounting-master-current.md","docs/plans/accounting-master-checkpoint.md",
       "docs/plans/accounting-continuation-requirements-20261007.md","docs/plans/accounting-p17-completion-20261014.md",
       "docs/plans/accounting-p18-completion-20261014.md","data/accounting-master/next-plan.md"]
OLD="39f54220018fececdd6498f28346158dff3115c332dde38b7e15686116e689f0"
NEW="393f4cf191a44ac8e671248a6c10562674d5c5a03a3a42e4f60c30b8c10e70e8"
SUMMARY=("R03-D's finite group binding is integrated in Version 2.99: 22 documentary exchanges, "
    "1,516 independent financial/closure/world checks and 106 preservation/build checks pass; "
    "five rendered pages inspected. Exact entities, books, control/perimeter, rate direction/time, "
    "NCI history and separate disposal branches connect to common request/replay rules. Result: "
    "data/accounting-master/finite-method-decisions-20261015/group/result.md. Broader group "
    "methods, actual facts, runtime and full readiness remain open.")
NEXT=("Next: execute R03-E under docs/plans/accounting-corporate-residual-decisions-20261015.md "
    "for finite restoration, assurance/mixed contracts, WIP/joint-product, tax/closing and "
    "authority decisions; reconcile R03 residuals. Continue ready R04 literature, R05 future "
    "validation protocols and R06 reuse locks before R07/R08. Runtime execution remains held.")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not ARCHIVE.exists()
verified={n:json.loads((OUT/n).read_text()) for n in ["independent-checks.json","manuscript-checks.json"]}
assert all(v["passed"] and all(c["passed"] for c in v["checks"]) for v in verified.values())
pdf=ROOT/"docs/design/proposal/manuscript-group-bindings-20261015/accounting-product-proposal.pdf"
assert sha(pdf)==NEW and (OUT/"result.md").exists()
index=subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)
assert index==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
updates={}
for name in FILES:
    original=(ROOT/name).read_text()
    s=original.replace("manuscript-bank-restructuring-20261015/accounting-product-proposal.pdf",
                       "manuscript-group-bindings-20261015/accounting-product-proposal.pdf").replace(OLD,NEW)
    for a,b in [("Version **2.98**, 292","Version **2.99**, 294"),("Version 2.98, 292","Version 2.99, 294"),
        ("current Version 2.98 candidate","current Version 2.99 candidate"),("through 2.98","through 2.99"),
        ("2.73–2.98","2.73–2.99"),("Version2.98 and full2.72 assessment","Version2.99 and full2.72 assessment")]:
        s=s.replace(a,b)
    s=re.sub(r"Next: execute R03-D[^\n]*",NEXT,s)
    s=s.replace("## Bank restructuring and next work — 15 October 2026",
        "## Group bindings and next work — 15 October 2026\n\n"+SUMMARY+"\n\n"+NEXT+
        "\n\n## Bank restructuring — 15 October 2026",1)
    assert SUMMARY in s and "Next: execute R03-D" not in s
    updates[name]=s
name="data/accounting-master/p17-completion-20261014/P17-05/operation-matrix.md"
s=(ROOT/name).read_text().replace("Refreshed through2.96","Refreshed through2.99")
s=s.replace("Business, valuation/tax and actual rights; next case joins acquisition to later translation/disposal",
    "Delivered2.81/2.99: acquisition through translation/disposal, exact group/source-book/perimeter/rate bindings and separate branch replay. Actual business/control, valuation/tax and rights remain")
s+="\nVersion2.99 supplies the finite common group profile,22 exchanges and1,516 independent documentary checks. See ../../finite-method-decisions-20261015/group/result.md. Wider currency/elimination methods and actual facts remain; continue R03-E and later full integration.\n"
updates[name]=s
name="docs/plans/accounting-finite-method-decisions-20261015.md"
updates[name]=(ROOT/name).read_text()+"\nR03-D's finite common group profile is integrated in2.99. R03-E proceeds under accounting-corporate-residual-decisions-20261015.md; then reconcile remaining A–E design/source decisions before R04/R05/R06 and final review.\n"
name="data/accounting-master/finite-method-decisions-20261015/decisions.md"
s=(ROOT/name).read_text().replace("Group/FX case2.81 retained | Bind exact source/party/date/state/replay; do not infer identity from labels | Active under accounting-group-bindings-20261015.md",
    "GroupForeignOperation/1,22 exchanges,1,516 checks;group/result.md | Actual control/valuation/tax, broader group methods and runtime remain; no corporate-schema coercion | Finite common binding delivered2.99")
s=s.replace("Parent R03-E | Inspect precise remaining restoration, assurance, mixed modification, WIP/joint products, tax/closing and standards obligations | Open; no blanket private-facts disposition",
    "accounting-corporate-residual-decisions-20261015.md | Inspect precise remaining restoration, assurance, mixed modification, WIP/joint products, tax/closing and standards obligations | Active; no blanket private-facts disposition")
updates[name]=s
before={n:sha(ROOT/n) for n in updates}
for n in updates:
    p=ARCHIVE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,p)
for n,s in updates.items():(ROOT/n).write_text(s)
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==index
(OUT/"control-refresh.json").write_text(json.dumps({"before":before,"after":{n:sha(ROOT/n) for n in updates},
    "index_preserved":True,"next":NEXT},indent=2)+"\n")
manifest={
    "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
    "worktree":"dirty;100 unrelated staged entries preserved;no commit",
    "commands":["python3 data/accounting-master/finite-method-decisions-20261015/group/"+n+".py" for n in
        ["build_bindings","finish_package","verify_bindings","prepare_manuscript","verify_manuscript","refresh_controls"]],
    "document_commands":[
        "python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-group-bindings-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/group --timeout 240 --force",
        "python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-group-bindings-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/group/final-render --pages 1,172-175 --dpi 110"],
    "build_executions":1,
    "initial_packet":"Unverified first draft preserved; Decoder schema and receipt continuity repaired before final verification.",
    "environment":{"python":platform.python_version(),"execution":"CPU exact fractions/jsonschema;approved LuaLaTeX",
        "gpu":"N/A;no framework import or GPU operation"},
    "data_version":json.loads((OUT/"portable-exchanges.json").read_text())["source_pins"],
    "random_seeds":"N/A;exact documentary arithmetic, no sampling",
    "wall_time":{"checks_seconds":verified["independent-checks.json"]["wall_seconds"],
        "build":json.loads((OUT/"build-run.json").read_text()),"interactive_total":"not measured"},
    "plan":"docs/plans/accounting-group-bindings-20261015.md","result":str((OUT/"result.md").relative_to(ROOT)),
    "candidate_pdf":str(pdf.relative_to(ROOT)),"candidate_pdf_sha256":NEW,
    "artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sorted(OUT.glob("*")) if p.is_file() and p.name!="run-manifest.json"]}
(OUT/"run-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"candidate":"2.99","controls":6,"index_preserved":True,"next":"R03-E"}))
