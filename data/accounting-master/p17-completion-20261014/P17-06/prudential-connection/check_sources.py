"""Pin documentary evidence; substring checks are integrity, not legal review."""
from pathlib import Path
import hashlib,json,time
import xml.etree.ElementTree as E
import fitz
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
CHECKS=[]
def check(name,ok):CHECKS.append({"name":name,"passed":bool(ok)})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    start=time.perf_counter();records=[]
    prior=ROOT/"data/accounting-master"
    groups={"bank-capital-payout-dependencies-20261012":["3.1","3.2","3.10"],"bank-capital-recognition-20261012":["3.20","3.22"]}
    texts={}
    for folder,sections in groups.items():
        for section in sections:
            xml=prior/folder/"sources"/("ecfr-2026-01-01-"+section+".xml")
            txt=xml.with_suffix(".txt");root=E.parse(xml).getroot()
            check("retained_section:"+section,any(n.attrib.get("N")==section and n.attrib.get("TYPE")=="SECTION" for n in root.iter()))
            texts[section]=txt.read_text()
            records.append({"kind":"retained_ecfr","section":section,"requested_snapshot":"2026-01-01","path":str(xml.relative_to(ROOT)),"sha256":sha(xml),"text_path":str(txt.relative_to(ROOT)),"text_sha256":sha(txt),"prior_receipt":str((prior/folder/"access-receipts.json").relative_to(ROOT))})
    for section,expected_hash,count in [("3.31","2c67779eb2d30cf4e1cb749c7b3f8de701c7d9e57c08161f7ee91a7408e93455",10),("3.32","07719945dd7d6cda45856fed8a3190e774d1f552a3b0914de097309cfa99a3a0",72)]:
        xml=OUT/"sources"/("ecfr-2026-01-01-"+section+".xml");txt=xml.with_suffix(".txt");root=E.parse(xml).getroot()
        check("new_hash:"+section,sha(xml)==expected_hash)
        check("new_identity:"+section,root.attrib.get("N")==section and root.attrib.get("TYPE")=="SECTION")
        check("new_paragraph_inventory:"+section,len(txt.read_text().splitlines())==count)
        texts[section]=txt.read_text()
        records.append({"kind":"new_ecfr","section":section,"requested_snapshot":"2026-01-01","url":"https://www.ecfr.gov/api/versioner/v1/full/2026-01-01/title-12.xml?part=3&section="+section,"path":str(xml.relative_to(ROOT)),"sha256":sha(xml),"byte_length":xml.stat().st_size,"text_path":str(txt.relative_to(ROOT)),"text_sha256":sha(txt),"receipt":str((OUT/"access-receipts.json").relative_to(ROOT))})
    phrases={"3.2":["not reduced by any associated credit loss allowance","that is not included in tier 2 capital","Adjusted allowances for credit losses (AACL)"],
             "3.20":["up to 1.25 percent","(2) Retained earnings","(xiii) The instrument is reported"],
             "3.22":["Goodwill, net of associated deferred tax liabilities","must exclude from standardized total risk-weighted assets"],
             "3.31":["multiply each exposure amount by the risk weight"],
             "3.32":["its central bank","100 percent risk weight to all its corporate exposures","90 days or more past due or on nonaccrual"],
             "3.10":["average total consolidated assets as reported","standardized total risk-weighted assets"]}
    for section,values in phrases.items():
        for i,phrase in enumerate(values):check("operative_clause:"+section+":"+str(i),phrase in texts[section])
    tables=json.loads((OUT/"sources/ecfr-2026-01-01-3.32.tables.json").read_text())
    check("four_full_tables_retained",len(tables)==4 and sum(len(t["rows"]) for t in tables)==36)
    for part,pages,expected_pages in [(1,[39,40],46),(2,[89,90],95)]:
        p=OUT/"sources"/f"fdic-051-rcr{part}-202412.pdf";d=fitz.open(p)
        check(f"instruction_pages_part{part}",len(d)==expected_pages)
        normal=" ".join(" ".join(d[n-1].get_text() for n in pages).split())
        clauses=["Part II, item 26","sections 22(c) through (f)"] if part==1 else ["subtracting items 29 and 30 from","LESS: Excess AACL"]
        for i,phrase in enumerate(clauses):check(f"instruction_clause:{part}:{i}",phrase in normal)
        records.append({"kind":"official_fdic_instructions","part":part,"index_label":"December2024","inspected_physical_pages":pages,"revision_footers":["March2024"] if part==1 else ["March2024","December2024"],"path":str(p.relative_to(ROOT)),"sha256":sha(p),"pages":len(d),"scope":"Older operational ordering cross-check; no complete amendment-chain claim"})
    result={"passed":all(c["passed"] for c in CHECKS),"check_count":len(CHECKS),"checks":CHECKS,"wall_seconds":time.perf_counter()-start}
    (OUT/"source-manifest.json").write_text(json.dumps({"sources":records,"source_review":str((OUT/"source-review.md").relative_to(ROOT)),"source_review_sha256":sha(OUT/"source-review.md")},indent=2)+chr(10))
    (OUT/"source-checks.json").write_text(json.dumps(result,indent=2)+chr(10))
    print(json.dumps({"passed":result["passed"],"checks":len(CHECKS),"sources":len(records),"failures":[c for c in CHECKS if not c["passed"]]}))
    if not result["passed"]:raise SystemExit(1)
if __name__=="__main__":main()
