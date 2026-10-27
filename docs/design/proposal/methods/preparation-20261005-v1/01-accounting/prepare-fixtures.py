"""Write declarative, author-selected specification cases; no product engine."""
from pathlib import Path
import hashlib
import json
import re
import datetime

ROOT = Path(__file__).resolve().parent


def journal(date, event, debit, credit, amount):
    return {"date": date, "event": event, "lines": [
        {"account": debit, "side": "debit", "amount": str(amount)},
        {"account": credit, "side": "credit", "amount": str(amount)}]}


lease = [journal("2024-01-01", "commence", "rou_cost", "lease_liability", "210")]
for y, interest in [(2024, "21"), (2025, "11")]:
    lease.extend([
        journal(f"{y}-12-31", f"interest-{y}", "interest_expense", "lease_liability", interest),
        journal(f"{y}-12-31", f"pay-{y}", "lease_liability", "cash", "121"),
        journal(f"{y}-12-31", f"depreciation-{y}", "depreciation_expense", "rou_accumulated_depreciation", "105")])
lease.append(journal("2025-12-31", "return", "rou_accumulated_depreciation", "rou_cost", "210"))
modified = lease[:4] + [journal("2025-01-01", "modify", "rou_cost", "lease_liability", "110")]
for y, interest in [(2025, "44"), (2026, "24")]:
    modified.extend([
        journal(f"{y}-12-31", f"interest-{y}", "interest_expense", "lease_liability", interest),
        journal(f"{y}-12-31", f"pay-{y}", "lease_liability", "cash", "144"),
        journal(f"{y}-12-31", f"depreciation-{y}", "depreciation_expense", "rou_accumulated_depreciation", "215/2")])
modified.append(journal("2026-12-31", "return", "rou_accumulated_depreciation", "rou_cost", "320"))

base_tax = [
    [2024,"400","800","600","50","300","75","50","125"],
    [2025,"300","600","300","75","400","100","25","125"],
    [2026,"100","400","200","50","600","150","-25","125"],
    [2027,"100","200","100","25","600","150","-25","125"],
    [2028,"100","0","0","0","600","150","-25","125"]]
changed_tax = [
    [2024,"400","800","600","50","300","75","50","125"],
    [2025,"300","600","300","90","400","100","40","140"],
    [2026,"100","400","200","60","600","180","-30","150"],
    [2027,"100","200","100","30","600","180","-30","150"],
    [2028,"100","0","0","0","600","180","-30","150"]]


def tax_case(rows, changed=False):
    fields = ["year","tax_depreciation","carrying_amount","tax_base","dtl","taxable_profit","current_tax","deferred_expense","total_tax_expense"]
    schedule = [dict(zip(fields,row)) for row in rows]
    entries = [journal("2024-01-01","purchase","ppe_cost","cash","1000")]
    for row in schedule:
        y=row["year"]
        entries.append(journal(f"{y}-12-31",f"depreciation-{y}","depreciation_expense","ppe_accumulated_depreciation","200"))
        entries.append(journal(f"{y}-12-31",f"current-{y}","current_tax_expense","current_tax_payable",row["current_tax"]))
        d=row["deferred_expense"]
        if changed and y==2025:
            entries.append(journal(f"{y}-12-31","timing-2025","deferred_tax_expense","dtl","25"))
            entries.append(journal(f"{y}-12-31","rate-2025","deferred_tax_expense","dtl","15"))
        elif d.startswith("-"):
            entries.append(journal(f"{y}-12-31",f"deferred-{y}","dtl","deferred_tax_expense",d[1:]))
        else:
            entries.append(journal(f"{y}-12-31",f"deferred-{y}","deferred_tax_expense","dtl",d))
        entries.append(journal(f"{y+1}-03-31",f"settle-{y}","current_tax_payable","cash",row["current_tax"]))
    entries.sort(key=lambda x:x["date"])
    return {"cost":"1000","book_depreciation":"200","pretax_book_profit":"500",
            "current_rates":["1/4","1/4","3/10","3/10","3/10"] if changed else ["1/4"]*5,
            "reversal_rates":["1/4","3/10","3/10","3/10","3/10"] if changed else ["1/4"]*5,
            "schedule":schedule,"journals":entries}


fixtures={
 "schema_version":"accdsl.independent.accounting.specification.v1",
 "status":"synthetic proposed specification; no product engine",
 "time_scope":"FY2024 applicability; subsequent years are frozen-rule conditional projections requiring revalidation",
 "L01":{"start":"2024-01-01","payments":["121","121"],"rate":"1/10","rou_life_years":2,"underlying_remaining_economic_life_years":10,"underlying_fair_value":"1000","initial_pv":"210",
        "schedule":[{"year":2024,"opening":"210","interest":"21","payment":"121","closing":"110","rou":"105","expense":"126"},
                    {"year":2025,"opening":"110","interest":"11","payment":"121","closing":"0","rou":"0","expense":"116"}],"journals":lease},
 "L02":{"effective":"2025-01-01","same_underlying_asset":True,"old_liability":"110","old_rou":"105","revised_rate":"1/5","payments":["144","144"],"revised_pv":"220","liability_adjustment":"110","revised_rou":"215","depreciation":"215/2",
        "schedule":[{"year":2025,"opening":"220","interest":"44","payment":"144","closing":"120","rou":"215/2"},
                    {"year":2026,"opening":"120","interest":"24","payment":"144","closing":"0","rou":"0"}],"journals":modified},
 "L03":{"facts":"practical substitution ability and economic benefit throughout use", "source":"L16.B14","expected":"identified asset test fails; no lease journals","journals":[]},
 "L04":{"facts":"implicit rate not readily determinable; supported IBR absent","expected":"MEASUREMENT_UNRESOLVED","journals":[]},
 "T01":tax_case(base_tax),"T02":tax_case(changed_tax,True),
 "T03":{"unused_loss":"100","rate":"1/4","probable_usable_profit":False,"carryback":False,"usable_taxable_differences":False,"recognized_dta":"0","unrecognized_potential":"25","journals":[]},
 "T04":{"proposed_rate":"3/10","enacted":False,"substantively_enacted":False,"expected":"no automatic remeasurement","journals":[]},
 "T05":{"tax_base":None,"expected":"TAX_BASE_UNRESOLVED","journals":[]},
 "T06":{"rate":"1/4","tax_deductions_attributed_to":"lease liability","probable_usable_profit":True,"tax_base_rou":"0","tax_base_liability":"0",
   "schedule":[{"date":"2024-01-01","rou":"210","liability":"210","dta":"105/2","dtl":"105/2"},
               {"date":"2024-12-31","rou":"105","liability":"110","dta":"55/2","dtl":"105/4"},
               {"date":"2025-12-31","rou":"0","liability":"0","dta":"0","dtl":"0"}],
   "journals":[journal("2024-01-01","lease-tax-recognize","dta","dtl","105/2"),
               journal("2024-12-31","lease-dta-reduce","deferred_tax_expense","dta","25"),
               journal("2024-12-31","lease-dtl-reduce","dtl","deferred_tax_expense","105/4"),
               journal("2025-12-31","lease-dta-reverse","deferred_tax_expense","dta","55/2"),
               journal("2025-12-31","lease-dtl-reverse","dtl","deferred_tax_expense","105/4")]},
 "negative_controls":[
   {"id":"N01","defect":"constant opening-210 interest in second base year","wrong_second_interest":"21","expected_second_interest":"11"},
   {"id":"N02","defect":"old10percent rate for genuine L02 modification","wrong_pv":"30240/121","expected_pv":"220"},
   {"id":"N03","defect":"tax-base sign reversed for taxable PPE difference","wrong_2024_dtl":"-50","expected_2024_dtl":"50"},
   {"id":"N04","defect":"discounting a recognized deferred tax liability","wrong_2024_dtl":"500/11","expected_2024_dtl":"50"},
   {"id":"N05","defect":"zero gross lease deferred balances because net initial amount is zero","wrong_dta":"0","wrong_dtl":"0","expected_dta":"105/2","expected_dtl":"105/2"}]
}
(ROOT/"fixtures.json").write_text(json.dumps(fixtures,indent=2)+"\n")

sources=[
 ("L16","aasb16-compiled-nov2022","https://www.aasb.gov.au/admin/file/content105/c9/AASB16_02-16_COMPnov22_01-24.pdf","AASB16 compilation8;31Dec2023;F2024C00049", "annual periods beginning>=2024-01-01; no end date asserted by cover", ["9","18","22","24","26","27","29","31","32","36","37","38","39","40","41","42","43","44","45","46","47","49","50","53","58","B9","B13","B14","B19","B21","B24","C1","C1D"]),
 ("T112","aasb112-compiled-sep2023","https://www.aasb.gov.au/admin/file/content105/c9/AASB112_08-15_COMPsep23_01-23.pdf","AASB112 compilation7;29Sep2023;F2023C00930","annual periods beginning>=2023-01-01 and ending>=2023-09-30; no end date asserted by cover",["4A","5","7","8","12","15","16","17","22","22A","24","27A","28","29","34","35","36","37","46","47","48","51","51A","53","56","58","60","61A","71","74","79","80","81","98J","98K","98L"]),
 ("P116","aasb116-compiled-dec2022","https://www.aasb.gov.au/admin/file/content105/c9/AASB116_08-15_COMPdec22_01-23.pdf","AASB116 compilation6;31Dec2022;F2023C00192","annual periods beginning>=2023-01-01; no end date asserted by cover",["7","15","29","30","48","50","51","55","60","61","62"]),
 ("CF107","aasb107-compiled-jun2023","https://www.aasb.gov.au/admin/file/content105/c9/AASB107_08-15_COMPjun23_01-24.pdf","AASB107 compilation5;31Dec2023;F2024C00050","annual periods beginning>=2024-01-01; no end date asserted by cover",["31","32","33","35","36","43","44","44A","44B","44C","44D"])
]
register={"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"selected primary provisions inspected; not full-current-framework acceptance", "target_period":"2024-01-01 through2024-12-31", "source_path_convention":"all paths relative to this packet", "sources":[]}
for sid,name,url,version,window,paras in sources:
    p=ROOT/"sources"/name
    txt=p.with_suffix(".txt").read_text()
    anchors=[]
    for para in paras:
        match=re.search(r"(?m)^\f?"+re.escape(para)+r"\s+[^\n]+",txt)
        if not match: raise ValueError((sid,para))
        leading_formfeeds=len(match.group(0))-len(match.group(0).lstrip("\f"))
        anchors.append({"paragraph":para,"pdf_page":txt[:match.start()+leading_formfeeds].count("\f")+1,"text_line":txt[:match.start()].count("\n")+1,"anchor":match.group(0).lstrip("\f").strip()})
    files=[]
    for ext in (".pdf",".txt"):
        path=p.with_suffix(ext)
        files.append({"path":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size})
    register["sources"].append({"id":sid,"url":url,"version":version,"cover_window":window,"files":files,"anchors":anchors,"authority":"official AASB publication; Australian incorporating standard; selected for-profit provisions only"})
register["additional_inspection"]=[
 {"source":"L16","description":"cover; physical page5 IFRS comparison;3–8 scope/exemptions;9–16 identification/components;18–21 term;22–58 selected lessee provisions;AppendixA commencement/modification/IBR;B3–B30 low value/identification/substitution/control;C1–C1D effective dates"},
 {"source":"T112","description":"cover/page5 IAS12 comparison;4A–17;selected22–29 including22A/24/27A–29;34–37;46–51A;53–61A;selected71–81;98J–98M;accompanying Example8 with footnote2 physical pages50–51"},
 {"source":"P116","description":"cover;7/15 recognition;29/30 cost policy;48–62 expense/depreciation and estimate review"},
 {"source":"CF107","description":"cover;31–36 interest/tax classification;43–44D noncash/financing reconciliation"}]
register["discovery_files"]=[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((ROOT/"sources").glob("*.html"))]
register["failed_discovery_attempts"]=[
 {"url":"https://www.aasb.gov.au/admin/file/content105/c9/AASB16_02-16_COMPdec22_01-23.pdf","result":"HTTP404; guessed filename, not source evidence"},
 {"url":"https://www.aasb.gov.au/admin/file/content105/c9/AASB112_08-15_COMPdec22_01-23.pdf","result":"HTTP404; guessed filename, not source evidence"},
 {"url":"https://standards.aasb.gov.au/aasb-16-feb-2016","result":"HTTP404"},
 {"url":"https://standards.aasb.gov.au/aasb-112-aug-2015","result":"HTTP404"},
 {"url":"https://www.aasb.gov.au/standards-pronouncements/accounting-standards/","result":"HTTP404"}]
(ROOT/"source-register.json").write_text(json.dumps(register,indent=2)+"\n")
print("Wrote fixtures.json and source-register.json")
