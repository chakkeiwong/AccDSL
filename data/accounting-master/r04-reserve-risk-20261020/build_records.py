"""One-time documentary construction after source reading."""
import json
from pathlib import Path
import re
from compare import bind, derive

U = Path(__file__).resolve().parent
R = U.parents[2]
OLD = R / "data/accounting-master/p17-completion-20261014/P17-09/reserving-bootstrap"
S = OLD / "sources"
M = R / "docs/design/proposal/manuscript-early-conversion-20261018"


def write(name, data):
    with (U/name).open("x",encoding="utf-8") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)
        f.write("\n")


def anchor(ident, start, end, purpose):
    p=S/"england2019-lifetime.txt"
    text=p.read_text()
    lines=text.split("\n")
    lo=sum(len(line)+1 for line in lines[:start-1])
    hi=min(len(text),sum(len(line)+1 for line in lines[:end]))
    return {"id":ident,"source":bind(p),"lines":[start,end],"start":lo,"end":hi,
            "excerpt":p.read_text()[lo:hi],"purpose":purpose}


assert not (U/"comparison.json").exists(), "one-time construction"
result=derive()
paper=R/"docs/papers/On the Lifetime and One-Year Views of Reserve Risk England (2019).pdf"
assert bind(paper)["sha256"] == "d195f617ffacdb72e6f5f445d54b829cb1f47ad6dc4d0fbe55cc67b06cc70268"
assert paper.read_bytes()==(S/"england2019-lifetime.pdf").read_bytes()
anchors=[anchor(*args) for args in [
    ("edition",6,21,"accepted manuscript and exact journal-identity limitation"),
    ("moments",174,188,"Mack moments do not specify a full law"),
    ("cdr-sign",327,367,"opening less payment less closing; profit sign"),
    ("conditional-refit",420,440,"closing expectation conditioned on emerged diagonal"),
    ("bayesian-context",452,478,"source attributes future-CDR MSEPs to Bayesian chain-ladder representation"),
    ("example-only",554,563,"illustrative data and missing tail extension"),
    ("simulation-and-loss-tail",641,672,"500000 source draws; matching observations and lower CDR tail"),
    ("capital-timing",780,788,"cost-of-capital and projected-capital requirements"),
    ("historical-inputs",809,827,"3 percent discount,6 percent charge and triangle-only proxy"),
    ("capital-profiles",831,849,"best-estimate profile needs justification"),
    ("risk-profile-not-runoff",858,878,"capital profile differs from risk-margin runoff"),
    ("relative-measures",972,987,"risk functional minus mean; finite weights require conventions"),
    ("risk-choice",1016,1028,"illustrative matched levels and equivalent-confidence statement"),
    ("not-equality-significance",1066,1089,"matched amounts are not substantive equivalence; future information unavailable now"),
    ("bounds-scope",1190,1218,"expected conditional SD approximation and future-information distinction"),
    ("refitting-veto",1248,1263,"same refitted model; no universal zero-mean or independence guarantee"),
    ("all-cash-flows",1306,1331,"payment-only example; reinsurance and allocation limits"),
    ("software",1348,1356,"ResQ and Igloo identified; no accessible execution code supplied in this artifact"),
    ("ph-definition-and-weights",1642,1682,"Appendix2 integral; exact indices/sign inspected on rendered physical35"),
    ("variance-lemma",1685,1734,"Appendix3 square-integrability and expected-conditional-SD inequality"),
    ("orthogonality-corollary",1735,1792,"fixed-origin CorollaryA3.2; uncorrelated need not mean independent"),
]]
images=[]
observations={
    2:"Title, three authors, accepted-version front matter and historical effective-date discussion; no current-authority inference.",
    21:"Figure1 compares opening-normalised profiles; distinct reserve and CDR targets remain visible. Section6 introduces lifetime risk choice.",
    23:"Table10 chosen levels and Figure2 positive PH/TVaR weights. Figure2 cannot establish actual execution formula or repair Appendix2 by implication.",
    35:"Paper34: H_rho integral has exponent1/rho. Printed ws=t(Ss)-t(S(s-1)) for s>=2 is reversed. Source also asserts sum weights1. Appendix3 starts below.",
    36:"Paper35: Jensen and conditional-total-variance inequalities; CDR covariance argument explicitly says uncorrelated,not necessarily independent.",
    37:"Paper36: CorollaryA3.2 is fixed-origin and expected-risk scope. Final paragraph labels MSEP an estimate under Bayesian representation,not exact arbitrary fitted variance.",
}
for n, observation in observations.items():
    p=U/"render"/(f"appendix-{n}.png" if n>=35 else f"page-{n}.png")
    images.append({"physical_page":n,"paper_page":n-1,"image":bind(p),"observation":observation,"review":"author visual inspection"})
sources=[paper,S/"england2019-lifetime.pdf",S/"england2019-lifetime.txt",S/"england2019-openalex.json",S/"england2019-crossref.json",OLD/"inspection.md",OLD/"result.md",R/"docs/design/research/source-support.json",R/"docs/design/research/forward-snowball.json"]
sources += [M/"sections"/name for name in ["insurance-methods.tex","reserving-bootstrap.tex","bootstrap-consistency.tex","reserving-adapter.tex"]]
write("comparison.json",result)
write("source-ledger.json",{"paper":bind(paper),"metadata_date":"2026-10-14","inspection_date":"2026-10-20","bindings":[bind(p) for p in sources],"anchors":anchors,
    "new_technical_reading":"Sections5–7 and Appendices2–3 complete; Sections2.1–3.4 definitions and Section4 tables/comparison supporting them; references read as discovery.",
    "inherited_reading":"14October Appendix1 and earlier bootstrap scope; not claimed as a fresh complete-paper reread.","acquisitions":0,"upstream_execution":False})
write("render-review.json",{"paper":bind(paper),"pages":images,"source_rendering_only":True,"independent_acceptance":False})
write("source-support-ledger.json",{"date":"2026-10-20","additive":True,"records":[{
    "id":"england2019lifetime","title":"On the Lifetime and One-Year Views of Reserve Risk, with Application to IFRS17 and SolvencyII Risk Margins",
    "authors":["Peter D. England","Richard J. Verrall","Mario V. Wüthrich"],"year":2019,"doi":"10.1016/j.insmatheco.2018.12.002","local":bind(paper),
    "classification":"DIRECT_METHOD","publication_status":"institutional accepted manuscript21270; exact final-journal equality unverified",
    "technical_scope":"§§5–7,Appendices2–3 and supporting definitions/comparisons; retained prior reading separately recorded",
    "correction_status":"14October OpenAlex is_retracted false,Crossref relation empty/update fields absent; not comprehensive clearance. New local formula defect on paper34; no publisher correction check performed this unit.",
    "quarantine_status":"printed empirical PH weight equation excluded; no wholesale rejection of paper",
    "allowed":["source distinctions between capital profiles,payment/re-estimation horizons and entity-specific preferences","Appendix3 expected-SD inequality with stated information/moment conditions","Appendix2 integral definition with explicitly locally derived corrected weights"],
    "forbidden":["literal printed PH weights","actual author-software failure","current regulatory rate or accounting admission","plug-in MSEP identity,independence or VaR prudence by implication","calibration or empirical superiority"]}]})
oa=json.loads((S/"england2019-openalex.json").read_text())
write("citation-venue-ledger.json",{"date":"2026-10-20","records":[{"id":"england2019lifetime","metadata_access_date":"2026-10-14","source":bind(S/"england2019-openalex.json"),"citation_count":oa["cited_by_count"],"venue":"Insurance: Mathematics and Economics85:74–88","venue_metric":"not available","caveat":"dated discovery metadata,not quality/correctness evidence; no fresh query"}]})

text=(S/"england2019-lifetime.txt").read_text()
refs=text[text.index("\nReferences\n"):text.index("Appendix 1 –")]
refs=re.sub(r"^\s*\d+\s*$","",refs,flags=re.M).replace("\f","")
blocks=[re.sub(r"\s+"," ",p).strip() for p in re.split(r"\n\s*\n",refs) if re.search(r"\(\d{4}[ab]?\)",p)]
# Two references share a single blank-line block in the retained extract.
blocks=[part for block in blocks for part in re.split(r" (?=Diers, D \(2009\))",block)]
decisions=[]
for citation in blocks:
    if citation.startswith("Wang,"):
        category,action,reason="FOUNDATIONAL","inspect next","Primary PH-transform source; verify formula/version before broader imported theory."
    elif citation.startswith(("Artzner,","Delbaen,")):
        category,action,reason="FOUNDATIONAL","defer claim import","Coherence/allocation theory is not proved by the finite weight check; original technical sources remain required."
    elif citation.startswith("Merz, M and Wüthrich, MV (2014)"):
        category,action,reason="DIRECT_METHOD","inspect next","Original Bayesian multi-year MSEP derivation underlies estimator interpretation; local martingale proof does not validate it."
    elif citation.startswith(("Mack, T (1993)","England, PD (2002)","England, PD and Verrall, RJ (1999)")):
        category,action,reason="DIRECT_METHOD","preserve prior disposition","Existing Mack/addendum/bootstrap dossiers distinguish inspected edition and published-source barriers; no new claim from this citation."
    elif citation.startswith(("EU Commission", "IASB", "APRA", "Prudential", "International Actuarial")):
        category,action,reason="BACKGROUND","retain dated authority lead","Historical regulation/guidance or monograph; current applicable authority and entity method not inferred."
    elif citation.startswith(("Diers", "Ohlsson", "Merz", "Röhr", "Böhm", "De Felice")):
        category,action,reason="DIRECT_METHOD","defer technical import","Alternative multi-year or one-year reserve theory; needed for broad model comparison,not the local conditional-expectation proof."
    elif citation.startswith(("Barnett", "Renshaw", "Verrall", "Zehnwirth", "England, PD and Verrall, RJ (2001)")):
        category,action,reason="COMPETITOR","retain expansion queue","Different reserving/model assumptions can change distributions and profiles; no model ranking or all-method completeness."
    elif citation.startswith(("Taylor, GC and Ashe", "Ashe")):
        category,action,reason="BACKGROUND","retain data/moment lead","Origin of illustration/moment methods; no real-data replication or tail validation in this unit."
    else:
        category,action,reason="DIRECT_METHOD","retain scoped dependency","Reserving background,tail treatment or predictive distribution support; no original theorem imported through this reference alone."
    decisions.append({"citation_as_retained":citation,"classification":category,"action":action,"reason":reason,"technical_reading_this_unit":False})
write("backward-snowball-ledger.json",{"date":"2026-10-20","seed":"england2019lifetime","source":bind(S/"england2019-lifetime.txt"),"scope":"retained reference list,all entries classified; entries are discovery,not inspected originals","records":decisions})
write("forward-snowball-ledger.json",{"date":"2026-10-20","seed":"england2019lifetime","new_query":False,"retained_search_date":"2026-10-14","retained_search":bind(R/"docs/design/research/forward-snowball.json"),"records":[{"candidate":"Steinmetz/Jentsch2024 Mack bootstrap consistency; retained2023 preprint and later published-source inquiry","action":"preserve prior technical inquiry/current bootstrap-consistency section","relevance":"conditional target and backward-law validity; simulation agreement in England paper is not a consistency theorem"}],"limitation":"No fresh comprehensive forward/correction search; exact publisher-version correction of new formula defect remains unverified."})
write("claim-support-ledger.json",{"date":"2026-10-20","records":[
    {"claim":"Printed PH weights do not compute the stated survival integral","class":"PROJECT_DERIVATION","source":"Appendix2,paper34/renderphysical35","evidence":"rho1 two-loss witness; corrected telescoping masses","scope":"retained accepted edition only"},
    {"claim":"Expected future SD≤root expected conditional variance≤current-information SD of remaining payments","class":"PRIMARY_TECHNICAL_SUPPORT + PROJECT_DERIVATION","source":"Appendix3,LemmaA3.1","evidence":"method-note conditional total variance and exact four-outcome law","scope":"nested information,finite second moments; neither pathwise nor quantile guarantee"},
    {"claim":"Reverse-CDR variance sums require appropriate conditional-mean and orthogonality assumptions","class":"PROJECT_DERIVATION","source":"CorollaryA3.2 motivates; local notation proof supplied","evidence":"martingale proof and dependent-but-uncorrelated exact example","scope":"no fitted-MSEP or independent-origin guarantee"},
    {"claim":"Finite expected shortfall must retain boundary mass; CDF coverage need not give exact VaR equivalence","class":"PROJECT_DERIVATION","source":"Section6 motivates explicit finite conventions","evidence":"three-atom quantile integral versus partial-tail sum","scope":"declared mathematical convention,no accounting-disclosure ruling"},
    {"claim":"Risk measure/level,capital profile,cost timing and discounting are separate method choices","class":"PRIMARY_TECHNICAL_SUPPORT + PROJECT_DERIVATION","source":"Sections5–7","evidence":"method-note input/output requirements","scope":"optional proposed methods,no current-law or actual-company admission"}]})
write("omission-risk-ledger.json",{"date":"2026-10-20","records":[
    {"source":"final journal edition/correction notice","status":"unverified","risk":"accepted-manuscript formula error may already be corrected; no final-edition assertion"},
    {"source":"Wang1995 PH transform","status":"uninspected consequential original","risk":"finite local derivation does not establish full distortion/coherence theory"},
    {"source":"Merz/Wüthrich2014 full-picture paper","status":"uninspected consequential original","risk":"conditional-mean proof does not establish reported Bayesian MSEP estimators"},
    {"source":"Artzner1999/Delbaen2000","status":"uninspected for this inquiry","risk":"no general coherence or allocation guarantee imported"},
    {"source":"alternative reserving families and tail/calendar effects","status":"open","risk":"Mack illustration cannot establish calibrated distributions or universal capital profiles"},
    {"source":"source author's ResQ/Igloo execution","status":"not available in retained paper","risk":"printed typo does not prove numerical tables used the wrong code"},
    {"source":"current accounting/prudential authority and entity method","status":"separate unresolved obligation","risk":"historical discussion and finite law are not a current applicable risk adjustment"}]})
print(json.dumps({"constructed":True,"exact_assertions":result["exact_assertions"],"anchors":len(anchors),"source_bindings":len(sources),"backward_references":len(decisions)}))
