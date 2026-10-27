"""Append source-specific judgments while preserving every previous row."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
REL=str(OUT.relative_to(ROOT))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n")
thesis=ROOT/"docs/papers/Statistical Inference for the Reserve Risk Steinmetz (2023).pdf"
assert not thesis.exists()
shutil.copy2(OUT/"sources/steinmetz2023-thesis.pdf",thesis)
paper=ROOT/"docs/papers/Bootstrap Consistency for the Mack Bootstrap Steinmetz (2024).pdf"

records={}
records["source-support"]=[
 {"id":"steinmetz2024bootstrap","classification":"DIRECT_METHOD","access_date":"2026-10-14",
  "title":"Bootstrap consistency for the Mack bootstrap","authors":["Julia Steinmetz","Carsten Jentsch"],
  "year":2024,"doi":"10.1016/j.insmatheco.2024.01.001",
  "local_path":str(paper.relative_to(ROOT)),"sha256":sha(paper),
  "publication_status":"final journal PDF; institutional handle2003/44429",
  "version_status":"Section7 materially differs from retained arXiv2303.05913v1",
  "notice_status":"No notice located in bounded Crossref exact/title and arXiv checks; not proof of absence",
  "quarantine":"Literal equation5.3 excluded from implementation; intended cancellation cross-checked against adjacent Step5 and6.1, with local algebra",
  "full_text_status":"retained; claim-focused technical reading, not full independent proof certification",
  "inspected_technical_anchors":"Sections2–6 target, algorithms and assumptions;7.1.1/7.1.2;Table3/Figures1–3;AppendixA/B proof structure and conditioning step;B.3/C/D; details in inspection.md",
  "proof_limits":"Long B.1/B.2 remainder inequalities and inherited2022 conditional CLTs not independently reproduced",
  "author_code":"not located in article/arXiv/institutional records; no runtime or outreach",
  "claims_allowed":["Conditional target and scale distinctions with stated assumptions","Backward-generator obligation and final simulation design","Scoped literal centering inconsistency with exact local repair"],
  "claims_forbidden":["Universal bootstrap invalidity","ODP consistency from Mack theorem","Validated reciprocal/gamma backward generator","Source simulation superiority or default readiness","Verified author-code defect"]},
 {"id":"steinmetz2023thesis-backward","classification":"FOUNDATIONAL",
  "title":"Statistical Inference for the Reserve Risk","authors":["Julia Steinmetz"],"year":2023,
  "local_path":str(thesis.relative_to(ROOT)),"sha256":sha(thesis),
  "publication_status":"doctoral dissertation; handle2003/41966; submittedFebruary2023, defendedJune2023",
  "version_status":"not asserted equivalent to2022 journal article",
  "notice_status":"No item-specific withdrawal notice found on institutional record; bounded check",
  "full_text_status":"207pages retained; physical64–65 inspected",
  "inspected_technical_anchors":"Chapter2 Assumption2.18 and Example2.19, printed42–43",
  "claims_allowed":["The inspected example states approximate backward moments with remainder terms"],
  "claims_forbidden":["Independent verification of whole dissertation,2022 journal proofs,or2024 generator"]}]

claims=[
 ("bootstrap-conditioning-target","Conditioning on Q differs from fixing D; authored error variance500 vs400","PROJECT_DERIVATION","check_cases.py; manuscript section12.9"),
 ("bootstrap-limit-components","The article distinguishes process-law limit from scaled estimation-component accuracy","PRIMARY_TECHNICAL_SUPPORT","Theorems4.8–4.11,Remark4.12; stated assumptions and proof-inspection limits apply"),
 ("bootstrap-backward-obligation","Forward Mack moments do not imply reciprocal backward moments","PROJECT_DERIVATION","finite positive joint law; 11/7 and12/49 at Y3 vs3/2 and3"),
 ("bootstrap-repair-assumptions","Alternative conditional claims rely on Assumption6.2; arbitrary backward family not established","PRIMARY_TECHNICAL_SUPPORT","Section5.1,Assumption6.2,AppendixC.2"),
 ("bootstrap-reserve-center","Literal5.3 is inconsistent with net-reserve error; diagonal subtraction restores Step5/6.1","PROJECT_DERIVATION","q100,U130,Uhat120:root10 vs-90; printed96 directly inspected"),
 ("bootstrap-final-comparator","Final conditional simulations use approximate backward generator7.4, unlike preprint","PRIMARY_TECHNICAL_SUPPORT","Final7.1.1/7.1.2; preprint7.1; no local ranking")
]
records["claim-support"]=[{"id":i+"-20261014","claim":c,"class":k,"source":"steinmetz2024bootstrap","anchor":a,
                          "dossier":REL,"limit":"Scoped source or local derivation; no empirical/default promotion"} for i,c,k,a in claims]

actions={
 ("Beutner","2021"):("BACKGROUND","Conditional inference distinction; no time-series theorem transferred"),
 ("Björkwall","2009"):("COMPETITOR","Retain parametric/nonparametric factor-bootstrap comparator for target-specific protocol"),
 ("Björkwall","2010"):("COMPETITOR","Calendar/separation comparator; technical inspection required before implementation"),
 ("Brockwell","1991"):("FOUNDATIONAL","Truncation-convergence dependency; no independent proof certification here"),
 ("Bruce","None"):("EMPIRICAL_EXAMPLE","Industry comparison context; not local validation"),
 ("England","2002"):("DIRECT_METHOD","Retained2001 working addendum inspected separately; journal equivalence remains unresolved"),
 ("England","1999"):("DIRECT_METHOD","Original full text retrieval route previously blocked; no repeated unsupported search"),
 ("England","2006"):("DIRECT_METHOD","Priority Mack algorithm antecedent; no uninspected theorem imported"),
 ("Gibson","None"):("EMPIRICAL_EXAMPLE","Industry reserving uncertainty context; no regulatory or calibration claim"),
 ("Hall","1992"):("FOUNDATIONAL","General bootstrap background; no Edgeworth result imported"),
 ("Hartl","2010"):("COMPETITOR","Deviance-residual GLM alternative; deferred pending target-specific comparison"),
 ("Mack","1993"):("FOUNDATIONAL","Preserve existing inspected point/moment scope; no predictive-law identification"),
 ("Pan","2016"):("BACKGROUND","Validity/pertinence concept in time series; no stationary-model transfer"),
 ("Paparoditis","2021"):("BACKGROUND","Backward-generation analogy in functional time series; no theorem transfer"),
 ("Peremans","2017"):("COMPETITOR","Robust bootstrap/outlier comparator; future technical inspection"),
 ("Peters","2010"):("COMPETITOR","Bayesian versus classical bootstrap; condition/prior changes require fair target comparison"),
 ("Pinheiro","2003"):("COMPETITOR","Claims-bootstrap methodology; retain frontier without uninspected support"),
 ("Renshaw","1998"):("FOUNDATIONAL","Incremental GLM antecedent; distinguish from cumulative Mack model"),
 ("Steinmetz","2022"):("FOUNDATIONAL","Underlying conditional CLTs; thesis related passages retained, exact journal proof not independently verified"),
 ("Tee","2017"):("EMPIRICAL_EXAMPLE","Comparative reserving study; not replicated and no ranking imported"),
 ("Verdonck","2011"):("DIRECT_METHOD","Influence diagnostic for later validation; no robustness guarantee")
}
refs=json.loads((OUT/"sources/crossref.json").read_text())["message"]["reference"]
back=[]
for r in refs:
    key=(r.get("author"),str(r.get("year")))
    cls,action=actions[key]
    back.append({"author":r.get("author"),"year":r.get("year"),"title":r.get("article-title",r.get("volume-title","see retained reference")),
                 "doi":r.get("DOI"),"classification":cls,"action":action})
records["backward-snowball"]=[{"seed":"steinmetz2024bootstrap","date":"2026-10-14",
  "inspected_context":"Introduction,comparison remarks,algorithm/proof dependencies and reference list",
  "candidates":back,"limit":"All21 indexed references classified; technical reading only as explicitly recorded"}]

cites=json.loads((OUT/"sources/citing-works.json").read_text())["results"]
forward=[]
for x in cites:
    comparator="Conformal prediction" in x["display_name"]
    forward.append({"title":x["display_name"],"doi":x.get("doi"),"publication_date":x["publication_date"],
                    "cited_by_count":x["cited_by_count"],"classification":"COMPETITOR" if comparator else "PERIPHERAL",
                    "action":"Different frequency-severity target; inspect before any future comparison" if comparator else "Outside conditional Mack-triangle inquiry; metadata-only screen",
                    "technical_inspection":"not performed"})
records["forward-snowball"]=[{"seed":"steinmetz2024bootstrap","date":"2026-10-14",
  "query":"OpenAlex works?filter=cites:W4391074055&sort=cited_by_count:desc&per-page=25",
  "source_record":REL+"/sources/citing-works.json","candidates":forward,
  "recent_order":[x["title"] for x in sorted(forward,key=lambda x:x["publication_date"],reverse=True)],
  "coverage":"All4 returned records screened by date/citation metadata; no direct correction/replication located"}]
records["citation-venue"]=[{"id":"steinmetz2024bootstrap","date":"2026-10-14","citation_count":4,
  "citation_source":"OpenAlex W4391074055","access_date":"2026-10-14",
  "venue":"Insurance: Mathematics and Economics","venue_metric":"not available",
  "venue_metric_source":"not available","caveat":"Visibility only; not correctness,coverage or superiority"}]
records["omissions"]=[
 {"id":"mack-bootstrap-independent-proof-20261014","status":"OPEN","title":"Full inherited2022 proof and long remainder verification",
  "reason":"No universal theorem/default is adopted; relevant source assumptions and proof mechanism are documented",
  "reviewer_risk":"Cannot call arbitrary generator validated or claim independent proof certification",
  "next_action":"Discharge dependencies if a concrete implementation seeks theorem-based promotion","acceptable_for_current_claims":True},
 {"id":"mack-bootstrap-author-code-20261014","status":"NOT_LOCATED","title":"Original author simulation code",
  "reason":"No code link in inspected article/arXiv/repository; no outreach authorized",
  "reviewer_risk":"No runtime replication,formula-typo implementation inference or empirical ranking",
  "next_action":"Retain an exact supported code lead if it becomes available; independent interface work continues","acceptable_for_current_claims":True},
 {"id":"mack-bootstrap-reverse-law-validation-20261014","status":"OPEN","title":"Target-specific backward law and independent conditional reference",
  "reason":"Moment reciprocity fails in exact example; Assumption6.2 remains an obligation",
  "reviewer_risk":"Candidate and reference can share the same wrong reverse model",
  "next_action":"Use exact enumerated joint laws first; justify chosen reverse law before empirical comparison","acceptable_for_current_claims":True}]

checks=[]
for name,added in records.items():
    path=ROOT/("docs/design/research/"+name+".json")
    baseline=json.loads((OUT/"before"/(name+".json")).read_text())
    current=json.loads(path.read_text())
    assert current==baseline, name
    current["records"].extend(added)
    current.setdefault("supplement_updates",[]).append({"date":"2026-10-14","dossier":REL,"historical_date_preserved":baseline["date"]})
    save(path,current)
    check={"ledger":name,"historical":len(baseline["records"]),"added":len(added),
           "historical_rows_preserved":current["records"][:len(baseline["records"])]==baseline["records"]}
    assert check["historical_rows_preserved"]
    checks.append(check)
save(OUT/"ledger-checks.json",{"passed":True,"checks":checks})
save(OUT/"source-manifest.json",{"sources":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in [paper,thesis]],
     "inspection":REL+"/inspection.md","versions":"Journal2024,arXivv1 and dissertation are separate versions"})
print(json.dumps({"passed":True,"ledgers":checks}))
