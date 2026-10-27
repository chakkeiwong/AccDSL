#!/usr/bin/env python3
"""Source-bound proposal annotations and deterministic arithmetic, not a runtime."""
from collections import Counter
from datetime import date
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/design/cases/apple/continuation-20261007"
OPS = Path(__file__).resolve().parent
P02 = "data/accounting-master/deliverables/P02/case.json"
case = json.loads((ROOT / P02).read_text())
notes = {n["id"]: n for n in case["notes"]}
sources = {}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def add_source(key, original, extracted, provenance):
    sources[key] = dict(original_path=original, original_sha256=sha((ROOT/original).read_bytes()),
                        extraction_path=extracted, extraction_sha256=sha((ROOT/extracted).read_bytes()),
                        provenance=provenance, text=(ROOT/extracted).read_text())


def anchor(key, start, end, quote=True):
    d = sources[key]
    assert 0 <= start < end <= len(d["text"]), (key, start, end)
    s = d["text"][start:end]
    r = {k:d[k] for k in ("original_path", "original_sha256", "extraction_path", "extraction_sha256")}
    r.update(source_id=key, start=start, end=end, offset_unit="Unicode code points", span_sha256=sha(s.encode()))
    if quote:
        r["quote"] = s
    if d["original_path"].endswith(".pdf"):
        r.update(pdf_page=d["text"][:start].count("\f")+1,
                 ending_pdf_page=d["text"][:end-1].count("\f")+1)
    return r


def match(key, pattern, bounds=None):
    t = sources[key]["text"]
    lo, hi = bounds or (0, len(t))
    hits = list(re.finditer(pattern, t[lo:hi], re.S))
    assert len(hits) == 1, (key, pattern, len(hits))
    return anchor(key, lo+hits[0].start(), lo+hits[0].end())


def note_anchor(note_id, pattern):
    n = notes[note_id]["anchor"]
    return match(note_id.split(".")[0], pattern, (n["start"], n["end"]))


def exhibit(key, number):
    t = sources[key]["text"]
    hits = list(re.finditer(r"(?i)\bExhibit\s+"+re.escape(number)+r"\b", t))
    assert hits, (key, number)
    start = hits[-1].start()
    later = re.search(r"(?i)\bExhibit\s+\d+\.\d+\b", t[hits[-1].end():])
    end = hits[-1].end()+later.start() if later else len(t)
    return dict(target_span=anchor(key, start, end, quote=False),
                target_opening=anchor(key, start, min(start+900,end)),
                identity_check="Located the referenced filing and exhibit number and inspected its opening issuer/title. Blank grant fields remain blank; the filing's cited date is not inferred to be an executed grant date. No byte identity with SEC originals asserted.")


add_source("annual", "docs/design/cases/apple/annual-2024.pdf", "docs/design/cases/apple/annual-2024.txt", "P02 pinned annual original and extraction")
add_source("interim", "docs/design/cases/apple/interim-2025q1.html", "docs/design/cases/apple/interim-2025q1.txt", "P02 pinned interim original and extraction")
for key in ["proxy-2025", "annual-2024-official", "registration-2021"]:
    add_source(key, f"docs/design/cases/apple/p02-v1/{key}.html", f"docs/design/cases/apple/p02-v1/{key}.txt", "docs/design/cases/apple/p02-v1/acquisition.json")
corpus = json.loads((ROOT/"data/financial-report-benchmark/coverage.json").read_text())
corpus_ids = ["apple-2018-q2", "apple-2018-annual", "apple-2019-annual", "apple-2020-annual", "apple-2021-q1", "apple-2022-q1", "apple-2023-q1"]
for r in corpus["rows"]:
    if r["document_id"] in corpus_ids:
        assert sha((ROOT/r["local_path"]).read_bytes()) == r["sha256"]
        add_source(r["document_id"], r["local_path"], r["extracted_text_path"], "data/financial-report-benchmark/coverage.json:"+r["document_id"])
add_source("annual-2017", "docs/design/cases/apple/continuation-20261007/sources/annual-2017-mirror-trusted-v1.pdf",
           "docs/design/cases/apple/continuation-20261007/sources/annual-2017-mirror-trusted-v1.txt",
           "Public mirror; acquisition receipt; 2017 period, Apple identity and Exhibit 10.8/10.20 inspected")

targets = {}
for n in ["4.1", "10.19", "10.20", "10.21", "10.22", "19.1", "21.1", "23.1", "31.1", "31.2", "32.1", "97.1"]:
    targets["annual.exhibit."+n] = exhibit("annual", n)
targets["annual.exhibit.24.1"] = {"target_opening":match("annual", r"Power of Attorney\s+KNOW ALL PERSONS.*?(?=\f)")}
corpus_targets = {
    "10.3": ("apple-2022-q1", "10.1"), "10.4": ("annual-2017", "10.8"),
    "10.5": ("annual-2017", "10.20"), "10.6": ("apple-2018-q2", "10.2"),
    "10.7": ("apple-2018-annual", "10.17"), "10.8": ("apple-2019-annual", "10.15"),
    "10.9": ("apple-2020-annual", "10.16"), "10.10": ("apple-2020-annual", "10.17"),
    "10.11": ("apple-2021-q1", "10.1"), "10.12": ("apple-2021-q1", "10.2"),
    "10.17": ("apple-2023-q1", "10.1"), "10.18": ("apple-2023-q1", "10.2")}
for n, (doc, target) in corpus_targets.items():
    targets["annual.exhibit."+n] = exhibit(doc, target)
targets["annual.exhibit.4.26"] = {"target_opening":match("registration-2021", r"INDENTURE\s+Dated as of October\s+28, 2021")}

zip_path = OUT/"sources/annual-2024-taxonomy-trusted-v1.zip"
with zipfile.ZipFile(zip_path) as z:
    members = [{"name":n, "size":len(z.read(n)), "sha256":sha(z.read(n))} for n in z.namelist()]
    xsd = ET.fromstring(z.read("aapl-20240928.xsd"))
    imports = [dict(e.attrib, status="external_schema_not_retained_in_this_archive") for e in xsd.findall("{http://www.w3.org/2001/XMLSchema}import")]
    linkbases = [e.attrib for e in xsd.iter("{http://www.xbrl.org/2003/linkbase}linkbaseRef")]
taxonomy = dict(archive={"path":str(zip_path.relative_to(ROOT)), "sha256":sha(zip_path.read_bytes())},
                members=members, declared_imports=imports, declared_linkbases=linkbases,
                status="issuer_extension_package_retained; transitive_taxonomy_closure_unverified",
                review="XML members and declared imports inspected; no Arelle runtime validation, schema closure, licence clearance or installation compatibility asserted")

frontier=[]
for e in case["external"]["exhibit_inventory"]:
    row={k:e.get(k) for k in ["id","number","description","referenced_form","referenced_date_or_period","referenced_exhibit","target_links"]}
    row["baseline_contents_status"]=e["contents_status"]
    row["reference_source"]=e.get("source", e.get("pdf_index_row"))
    if e["id"] in targets:
        row.update(document_status="retained_target_located", **targets[e["id"]])
        row["semantic_status"]="selected_terms_only" if e["number"] in ["4.1","4.26"] else "target_identity_inspected; substantive_translation_pending"
        row["next_action"]="Inspect remaining substantive provisions and material outgoing references before using them in queries."
    elif e["number"] in ["101","104"]:
        row["document_status"]="extension_archive_retained_external_taxonomies_open" if e["id"].startswith("annual") else "inline_facts_retained_package_frontier_open"
        row["semantic_status"]="No taxonomy equivalence or complete extraction claim"
        row["next_action"]="Resolve schema, linkbase and imported taxonomy versions/licences; validate later in an authorised runtime stage."
    else:
        row["document_status"]="unresolved_target"
        row["semantic_status"]="not_inspected"
        row["next_action"]="Acquire exact exhibit through a legitimate public route, match title/date/parties, then inspect. Current issuer feed challenge and SEC denial do not establish permanent unavailability."
        relevant = []
        for p in (OUT/"sources").glob("*.receipt.json"):
            r=json.loads(p.read_text())
            if e["target_links"] and r["url"]==e["target_links"][0] or r.get("discovered_from")=={"path":P02,"id":e["id"]}:
                relevant.append(str(p.relative_to(ROOT)))
        row["exact_target_attempt_receipts"]=relevant
        row["route_level_blockers"]=["issuer-2013-trusted-v1.receipt.json", "sec-annual-exhibit-4-2-trusted-v1.receipt.json"]
    frontier.append(row)

obligations=[]
for e in case["external"]["partIII_and_package_obligations"]:
    obligations.append({"baseline_obligation":e,"continuation_status":"retained_proxy_or_summary_requires_material_translation" if "proxy" in json.dumps(e).lower() else "retained_or_explicitly_omitted; inspect_original_obligation",
                        "warning":"A located proxy passage or summary does not supply full semantics; preserve the January 2025 ownership date and unspecified omitted instruments."})

S=[]
def assertion(identifier, note_id, pattern, kind, proposition, effect, unknown):
    S.append(dict(id=identifier, source=note_anchor(note_id,pattern), note_id=note_id,
                  type=kind, interpretation=proposition, proposed_consequence=effect,
                  remaining_facts=unknown, translation_status="author_proposed; no human admission"))

assertion("A01", "annual.note.1", r"The consolidated financial statements include.*?subsidiaries\.", "perimeter", "Apple Inc. and wholly owned subsidiaries are the disclosed consolidation perimeter.", "Use consolidated amounts for group statements; issuer-only bond rights require their separate perimeter.", "Dated entity/control history and eliminations.")
assertion("A02", "annual.note.1", r"The Company’s fiscal year is.*?associated quarters, months and periods of those fiscal years\.", "calendar", "Fiscal-year labels use the last Saturday of September; 2024 spans 52 weeks and 2023 spans 53.", "Classify contractual dates against the fiscal calendar, not the year in a bond name.", "Payment calendar and business-day adjustment rules for individual series.")
assertion("A03", "annual.note.1", r"Certain prior period amounts.*?presentation\.", "qualification", "Current comparatives may have been reclassified.", "Preserve report version; do not overwrite originally reported classifications.", "Complete reconciliation to earlier original filings.")
assertion("A04", "annual.note.2", r"Revenue allocated to the\ndelivered hardware.*?provided\.", "recognition_policy", "Hardware recognition and straight-line bundled-service recognition have different timing.", "Separate delivered revenue and deferred service obligation; sales cash cannot identify current revenue.", "Contract allocations, SSP estimates and service cohorts.")
assertion("A05", "annual.note.2", r"For certain long-term service arrangements.*?undelivered services\.", "scope_exclusion", "Some unbilled undelivered service consideration is neither recognised as revenue nor quantified here.", "Do not set undisclosed future consideration to zero.", "Contract details and omitted amounts.")
assertion("A06", "annual.note.3", r"The following table.*?in thousands\):", "unit_and_measurement", "EPS uses income in millions and weighted-average shares in thousands.", "Multiply income/share-table ratio by 1,000 for dollars per share; ending shares are not this denominator.", "Share timing, future dilution and earnings.")
assertion("A07", "annual.note.4", r"As of September 28, 2024, cash and cash equivalents included.*?Note 7, “Income Taxes”\)\.", "restriction", "Reported cash and cash equivalents include $2.6 billion restricted escrow for the State Aid obligation.", "Correct P02 cash_excluding_restricted; gross reported cash cannot be treated as unrestricted funding.", "Exact restricted balance and legally available funds at the requested date.")
assertion("A08", "annual.note.4", r"The Company may use derivative instruments.*?interest rates\.", "conditional_policy", "Hedging is partial and discretionary; offset is not assured.", "Preserve hedge allocation, designation and terms as separate state; do not equate notional with net exposure.", "Actual hedge contracts and series allocations.")
assertion("A09", "annual.note.5", r"The following table.*?\(in millions\):", "measurement", "PP&E table reports gross classes and accumulated depreciation.", "The gross-minus-accumulated bridge checks a balance; it does not identify asset cohorts or future depreciation.", "Useful lives, acquisitions, retirements and cohort state.")
assertion("A10", "annual.note.6", r"Other Non-Current Assets.*?Total other non-current assets[^\n]*", "component_schedule", "Deferred tax assets are a component of other non-current assets.", "Prevent double counting a disclosed component and its containing balance-sheet line.", "Tax jurisdiction and recoverability analysis; other component histories.")
assertion("A11", "annual.note.7", r"As of September 28, 2024, the adjusted recovery amount.*?restricted from general use\.", "dated_obligation", "State Aid tax recovery and restricted escrow are linked dated disclosures.", "A restriction belongs to the tax obligation; do not use escrow a second time for debt funding.", "Settlement movements, tax bases and jurisdiction-specific law.")
assertion("A12", "annual.note.8", r"Payments under the Company’s lease arrangements may be fixed or variable.*?underlying leased assets\.", "conditional_payment", "Variable lease payments primarily depend on output purchases.", "Keep output-linked payments separate from the fixed maturity/discount bridge.", "Output scenarios, contract terms, renewals and modifications.")
assertion("A13", "annual.note.8", r"As of September 28, 2024, the Company had \$849 million.*?21 years\.", "not_yet_commenced", "Additional fixed obligations relate to leases not yet commenced.", "Do not add $849m to recognised lease liabilities without the recognition event and treatment.", "Commencement dates, contract allocation, rates and treatment authority.")
assertion("A14", "annual.note.9", r"The Company has outstanding Notes.*?in arrears\.", "contract_class", "Term Notes are senior unsecured with interest payable in arrears.", "Keep principal, carrying adjustments, fair value and future payment obligations as separate quantities.", "Series instruments, current holdings, modifications and hedge terms.")
assertion("A15", "annual.note.9", r"The effective interest rates for the Notes include.*?hedging\.", "measurement_qualification", "Disclosed effective rates include discount/premium amortisation and applicable hedge adjustments.", "Coupon cash is not interchangeable with interest expense.", "Series carrying amounts and effective-interest/hedge schedules.")
assertion("A16", "annual.note.10", r"The Company’s share repurchase programs do not obligate.*?amount of shares\.", "permission_not_obligation", "Repurchase authority has no minimum required purchase.", "Future repurchases require a scenario choice, not a mandatory liability.", "Future board/management choices and transaction dates.")
assertion("A17", "annual.note.11", r"RSUs granted under\nthe 2022 Plan generally vest.*?one-for-one basis\.", "qualified_vesting", "RSUs generally vest over four years conditional on continuing employment and settle in shares one-for-one.", "Retain generally and employment conditions; do not project all awards on a universal four-year schedule.", "Grant notices, award-specific exceptions, performance and forfeitures.")
assertion("A18", "annual.note.12", r"Future payments under unconditional purchase obligations.*?\(in millions\):", "scope_qualification", "The table includes remaining terms over one year at September 28.", "Keep shorter commitments unquantified; do not equate all purchase obligations with recognised liabilities.", "Short-term commitments, delivery/recognition events and contract changes.")
assertion("A19", "annual.note.12", r"In the opinion of management.*?asserted legal and other claims\.", "management_assessment", "Management's loss assessment is qualified by materiality, asserted claims and existing accruals.", "Do not derive zero liability or a numerical loss probability.", "Case facts, accrual amounts and later developments.")
assertion("A20", "annual.note.12", r"Substantially all.*?Vietnam\.", "qualitative_quantifier", "Hardware manufacturing is substantially outsourced in the listed locations.", "Keep the quantifier qualitative; no invented supplier haircut or exact percentage.", "Supplier concentration, capacity and disruption scenarios.")
assertion("A21", "annual.note.13", r"Operating income for each segment.*?segment\.", "aggregation_definition", "Segment income includes directly attributable operating expenses.", "Reconcile to consolidated income through R&D and corporate expenses; do not add segment and product revenue partitions.", "Cross-classified cells and cost allocations.")
assertion("I01", "interim.note.1", r"These condensed consolidated financial statements.*?2024 Form 10-K”\)\.", "incorporation", "The quarterly statements must be read with the annual statements and notes.", "Retain the annual-to-interim source dependency; interim note absence is not a zero balance or policy repeal.", "Changes and qualifications since the annual report.")
assertion("I02", "interim.note.1", r"The Company’s fiscal years 2025 and 2024 span 52 weeks each\.", "calendar", "FY2025 and FY2024 each span 52 weeks.", "With the last-Saturday policy, FY2025 ends 27 September 2025.", "Instrument settlement calendars remain separate.")
assertion("I03", "interim.note.2", r"As of December.*?greater than three years\.", "expectation", "The 64/25/9/2 percent deferred-revenue schedule is management's dated realisation expectation.", "Use an expectation record, not probabilities over all histories or an exact cash receipt schedule.", "Contract cohorts, revisions, new sales and timing.")
assertion("I04", "interim.note.3", r"The following table.*?in thousands\):", "unit_and_measurement", "Quarterly EPS uses quarterly income and weighted-average share counts.", "Quarterly and annual weighted averages must not be summed or replaced with point-in-time shares.", "Timing and dilution mechanisms.")
assertion("I05", "interim.note.4", r"As of December\s+28, 2024 and September\s+28, 2024, the carrying amount.*?respectively\.", "measurement_qualification", "The quarterly note separately reports carrying amounts of term debt subject to fair value hedges.", "Keep hedged debt carrying amounts distinct from derivative notionals and total debt; the disclosure does not supply series allocation.", "Hedge designations, contracts, instrument allocation and valuation inputs.")
assertion("I06", "interim.note.5", r"Inventories.*?Total inventories\s*\$\s*6,911\s*\$\s*7,286", "component_schedule", "Inventory comprises components and finished goods at the two dates.", "2,792 + 4,119 = 6,911 at the displayed centres; the movement does not identify purchases and consumption.", "Purchase/production/sale flows, allowances and FX.")
assertion("I07", "interim.note.6", r"As of December.*?respectively \(collectively the “Notes”\)\.", "measurement", "Quarterly debt narrative reports rounded carrying amount, not principal.", "Use the 10,848 + 83,956 balance-sheet components for the displayed carrying bridge; do not substitute fair value.", "Quarterly principal, measurement movements and series allocations.")
assertion("I08", "interim.note.7", r"The Company’s share repurchase program does not obligate.*?amount of shares\.", "permission_not_obligation", "Quarterly repurchase authority still has no minimum requirement.", "An extrapolated future repurchase is a scenario assumption.", "Subsequent decisions and settlement timing.")
assertion("I09", "interim.note.8", r"As of December.*?years\.", "management_estimate", "Unrecognised RSU cost is $29.2bn over a weighted-average 2.9-year expected recognition period.", "Do not turn the weighted average into a constant annual expense or cash liability.", "Grant-level service/performance/forfeiture and tax facts.")
assertion("I10", "interim.note.9", r"In the opinion of management.*?asserted legal and other claims\.", "management_assessment", "Quarterly contingency opinion preserves the material-loss and accrual qualifications.", "Keep the dated opinion; no zero-risk or probability inference.", "Case facts and quantified accruals.")
assertion("I11", "interim.note.10", r"A reconciliation.*?\(in millions\):", "aggregation_definition", "Quarterly segment income reconciles to consolidated operations.", "53,174 - 8,268 - 2,074 = 42,832; product and region remain overlapping views of the same sales.", "Cross-classification and future cost response.")

# All notes receive a query-exposure disposition; selected assertions do not
# pretend to exhaust the note's semantic content.
note_review=[]
for n in case["notes"]:
    ids=[s["id"] for s in S if s["note_id"]==n["id"]]
    assert ids,n["id"]
    note_review.append(dict(note_id=n["id"], source=n["anchor"], assertion_ids=ids,
                           affected_model_areas=n["affected_model_areas"],
                           residual=n["unresolved_meaning"],
                           status="selected_material_assertions_proposed; full_translation_open"))

annual = sources["annual"]["text"]
description_start=annual.index("DESCRIPTION OF DEBT SECURITIES")
description_end=annual.index("Exhibit 10.19",description_start)
bounds=(description_start,description_end)
term_anchors={
    "summary_qualification":match("annual",r"The following description of the Notes is a summary.*?context requires otherwise\.",bounds),
    "zero_2025":match("annual",r"We issued €1,000,000,000 aggregate principal amount of the 0\.000% 2025 Notes.*?was outstanding\.",bounds),
    "coupon_2025":match("annual",r"We issued €1,250,000,000 aggregate principal amount of the 0\.875% 2025 Notes.*?was outstanding\.",bounds),
    "currency_and_calendar":match("annual",r"All payments of principal of, the redemption price.*?successor thereto, is open\.",bounds),
    "call_dates":match("annual",r"“Par Call Date” means.*?2031 Notes\)\.",bounds),
    "par_call":match("annual",r"If any of the 0\.000% 2025 Notes.*?principal amount of the Notes being redeemed\.",bounds)}

def fiscal_year(d):
    end=date(d.year,9,30)
    from datetime import timedelta
    end-=timedelta(days=(end.weekday()-5)%7)
    return d.year if d<=end else d.year+1

amount=Fraction(1250000000)
coupon=amount*Fraction("0.875")/100
query=dict(status="partially_identified_conditional_answer", source_anchors=term_anchors,
           question="Which fiscal years contain the two euro Notes called 2025, and what gross contractual cash follows if their disclosed October 18 faces remain outstanding to scheduled maturity?",
           facts=[dict(series="0.875% 2025 Notes",issuer="Apple Inc. only",currency="EUR",principal_as_of="2024-10-18",principal="1250000000",annual_coupon_rate="0.00875",scheduled_maturity="2025-05-24",fiscal_year=fiscal_year(date(2025,5,24)),coupon_eur=str(coupon),principal_plus_coupon_eur=str(amount+coupon)),
                  dict(series="0.000% 2025 Notes",issuer="Apple Inc. only",currency="EUR",principal_as_of="2024-10-18",principal="1000000000",annual_coupon_rate="0",scheduled_maturity="2025-11-15",fiscal_year=fiscal_year(date(2025,11,15)),coupon_eur="0",principal_plus_coupon_eur="1000000000")],
           assumptions=["No repurchase, cancellation, new issuance, conversion, default or early/tax redemption changes these disclosed faces.","Euro remains the contractual payment currency; no withholding/additional amounts branch.","Amounts are scheduled gross principal and coupon; adjusted payment dates require exact series rules and holiday evidence."],
           unresolved=["2013 and 2018 base indentures and 2017/2019 series certificates; do not substitute the retained 2021 indenture.","October 18 holdings cannot be backdated to September 28 or carried to December 28 without further facts.","Both scheduled 2025 maturity dates fall on Saturday; executable settlement dates are not established here.","USD conversion, hedges, discount/premium, accrued interest, tax and subsequent events are not identified."],
           dependencies={"gross_contractual_cash":["zero_2025","coupon_2025","currency_and_calendar","call_dates","par_call"],
                         "fiscal_buckets":["A02","I02","zero_2025","coupon_2025"],
                         "funding_available":["A07","A11","actual_cash_date_and_restrictions"],
                         "income_and_retained_earnings":["A15","effective_interest_schedule","FX","tax","hedges"],
                         "OCI_and_total_equity":["hedge_designations","FX","tax"],
                         "closing_balance_sheet":["principal_settlement","carrying_amount","accruals","FX","hedges"],
                         "cash_flow_statement":["principal_and_coupon_cash","classified_treatment","hedge_cash"]})

# Display-centre arithmetic only; no rounding distribution is asserted.
calculations={
    "annual_principal_to_carrying_musd":97341-321-358,
    "annual_current_plus_noncurrent_musd":10912+85750,
    "annual_principal_maturity_sum_musd":10930+12342+9936+7800+5153+51180,
    "annual_fy2025_principal_minus_current_carrying_musd":10930-10912,
    "quarter_current_plus_noncurrent_musd":10848+83956,
    "quarter_carrying_change_musd":10848+83956-96662,
    "quarter_carrying_reconciliation_residual_after_cash_repayments_musd":10848+83956-96662+1009,
    "quarter_financing_cash_sum_musd":-2921-3856-23606-1009-7944-35,
    "quarter_cash_change_musd":29935+9792-39371,
    "quarter_closing_cash_including_restricted_musd":29943+29935+9792-39371,
    "annual_cash_less_reported_restricted_component_musd":29943-2600,
    "annual_ppe_musd":119128-73448,
    "quarter_ppe_musd":120615-74546,
    "quarter_inventory_musd":2792+4119,
    "annual_lease_liabilities_musd":13518+1272-1984-376,
    "annual_segment_to_consolidated_income_musd":162044-31370-7458,
    "quarter_segment_to_consolidated_income_musd":53174-8268-2074,
    "quarter_rsu_thousands":163326+61391-35683-2278}
cash_flow=match("interim",r"CONDENSED CONSOLIDATED STATEMENTS OF CASH FLOWS.*?Cash paid for income taxes, net\s*\$\s*18,651\s*\$\s*7,255")
corrections=[dict(id="CASH-01",baseline=P02,affected_observations=["annual.bs.2024-09-28.cash","annual.bs.2023-09-30.cash"],
                  field="measurement",old="cash_excluding_restricted",replacement="cash_and_cash_equivalents_as_reported",
                  verdict="2024 exclusion is wrong relative to Note 4; exclusion in the 2023 label is unsupported by a bare balance-sheet caption",
                  evidence_assertion="A07",scope="2024 includes disclosed restricted escrow; do not assert a 2023 restriction amount from the 2024 footnote",
                  review_action="Propose replacement annotation; author-verifiable contradiction in metadata; human admission pending",
                  invalidation=["Reject use of the old measurement flag for unrestricted-liquidity/funding calculations.","Invalidate downstream liquidity sufficiency and any funding scenario relying on that flag; preserve historical results against their original evidence.","Preserve reported numbers and correctly scoped cash reconciliation; no source restatement or genuine disclosure conflict inferred."])]

extra_frontier=[
    dict(id="X01",origin="annual.exhibit.4.1",targets=["annual.exhibit.4.2","annual.exhibit.4.19","annual.exhibit.4.15","annual.exhibit.4.21"],role="contract qualifications for the two euro 2025 Notes",status="unresolved_targets_prevent_exact_contract_execution"),
    dict(id="X02",origin="annual.exhibit.10.19/10.20/10.21/10.22",targets=["annual.exhibit.10.13","individual grant notices"],role="forms incorporate the 2022 plan and award-specific grant facts",status="plan_unresolved; private_grant_facts_not_identified"),
    dict(id="X03",origin="annual.exhibit.101",targets=[e["schemaLocation"] for e in imports],role="external taxonomy definitions",status="declared_direct_imports_retained_as_frontier; transitive_closure_not_inspected"),
    dict(id="X04",origin="interim.note.1",targets=["annual"],role="annual financial statements and notes",status="retained_source; semantic_dependencies_remain"),
    dict(id="X05",origin="annual Part III",targets=["proxy-2025"],role="Items 10–14 incorporate dated proxy material",status="retained_source; full_material_translation_open"),
    dict(id="X06",origin="annual omitted debt instruments",targets=[],role="Item 601(b)(4)(iii) instruments without a public identity in this package",status="reported_omission; exact_inventory_unknown"),
    dict(id="X07",origin="retained exhibit bodies",targets=[],role="other substantive outgoing references and amendments",status="not_exhaustively_scanned; recursive_closure_open"),
]
report=dict(schema_version="accdsl.apple.proposal-supplement.v1",plan="docs/plans/accounting-continuation-audit-20261007.md",
            baseline={"path":P02,"sha256":sha((ROOT/P02).read_bytes())},
            sources={k:{a:b for a,b in v.items() if a!="text"} for k,v in sources.items()},
            reference_frontier=frontier,package_obligations=obligations,additional_frontier=extra_frontier,
            taxonomy=taxonomy,material_assertions=S,note_dispositions=note_review,query=query,
            calculation_results=calculations,quarter_cash_flow_source=cash_flow,corrections=corrections,
            coverage={"known_exhibit_rows":len(frontier),"document_status_counts":dict(Counter(r["document_status"] for r in frontier)),
                      "known_package_obligations":len(obligations),"notes_with_selected_assertions":len(note_review),
                      "selected_assertions":len(S),"fully_formalised_notes":0,"human_admitted_translations":0,
                      "semantic_coverage_fraction":None,"recursive_reference_closure":False},
            effective_observation_overrides=[dict(observation_id=o["id"], baseline_measurement=o["measurement"],
                    measurement="cash_and_cash_equivalents_as_reported", value_usd=o["value_usd"],
                    correction_id="CASH-01", status="author_corrected_annotation; human_admission_pending")
                    for o in case["observations"] if o["id"] in corrections[0]["affected_observations"]],
            acceptance={"E01":"partial; source and semantic frontier remains open","E05":"open; metadata error is not a genuine disclosure conflict",
                        "E14":"partial; concrete taxonomy frontier added without runtime validation",
                        "whole_proposal":"not_ready","implementation_enabled":False})
(OUT/"case-supplement-v1.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report["coverage"],indent=2))
