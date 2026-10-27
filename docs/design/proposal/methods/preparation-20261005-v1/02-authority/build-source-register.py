"""Retain inspectable source pins; source matching is not semantic acceptance."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "sources"
def pin(path):
    p = ROOT / path
    return {"path": path, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}

def anchor(text_path, paragraph, needle):
    text = (ROOT / text_path).read_text()
    match = re.search(re.escape(needle).replace(r"\ ", r"\s+"), text)
    if not match:
        raise ValueError((text_path, paragraph, needle))
    pos = match.start()
    return {"paragraph": paragraph, "text_line": text[:pos].count("\n") + 1,
            "pdf_page": text[:pos].count("\f") + 1, "exact_anchor": match.group(0)}

accounting = json.loads((ROOT.parent / "01-accounting/source-register.json").read_text())
source_list = accounting.get("sources", [])
if not source_list:
    source_list = accounting.get("standards", [])
aasb_urls = {row["id"]: row["url"] for row in source_list}
sources = []
def add(id, base, url, authority, version, applicability, limits, anchors):
    pdf_name = {"U109-historical": "fasb-fas109-lower.pdf", "U740-disclosures": "fasb-tax-asu2023-09-short.pdf"}.get(id, base + ".pdf")
    files = [pin("sources/" + pdf_name), pin("sources/" + base + ".txt")]
    sources.append({"id": id, "official_url": url, "authority_class": authority,
                    "version": version, "applicability": applicability, "limits": limits,
                    "files": files, "inspected_anchors": [anchor("sources/" + base + ".txt", *a) for a in anchors]})

add("A16", "aasb16-compiled-nov2022", aasb_urls["L16"], "official_Australian_incorporating_standard",
    "Compilation8,31Dec2023,F2024C00049; incorporates amendments through10Nov2022",
    "Annual periods beginning>=2024-01-01; for-profit Tier1 comparison; no later early adoption assumed",
    "Not universal IFRS endorsement/current amendment census;2025+ arithmetic holds this rule version fixed",
    [("cover", "This compiled Standard applies"), ("IFRS comparison", "Comparison with IFRS 16"),
     ("5", "5        A lessee may elect"), ("8", "8       The election for short-term leases"),
     ("9", "9       At inception of a contract"), ("22", "22        At the commencement date"),
     ("24", "24        The cost of the right-of-use asset"),
     ("26", "26        At the commencement date"), ("32", "32        If the lease transfers ownership"),
     ("36", "36        After the commencement date"), ("37", "37        Interest on the lease liability"),
     ("44", "44      A lessee shall account"), ("45", "45      For a lease modification"),
     ("46", "46      For a lease modification")])
add("A112", "aasb112-compiled-sep2023", aasb_urls["T112"], "official_Australian_incorporating_standard",
    "Compilation7,29Sep2023,F2023C00930; amendments through14Sep2023",
    "Annual periods beginning>=2023-01-01 and ending>=2023-09-30; for-profit Tier1",
    "Tax-law inputs are synthetic; no broad current IFRS/ASBE equivalence; no later-period authority conclusion",
    [("cover", "This compiled Standard applies"), ("IAS comparison", "Comparison with IAS 12"),
     ("7", "7       The tax base of an asset"), ("12", "12      Current tax for current and prior periods"),
     ("15", "15      A deferred tax liability shall"), ("22A", "22A     A transaction that is not"),
     ("24", "24      A deferred tax asset shall"), ("46", "46      Current tax liabilities"),
     ("47", "47      Deferred tax assets"), ("48", "48      Current and deferred tax"),
     ("53", "53      Deferred tax assets and liabilities shall not be discounted."),
     ("58", "58      Current and deferred tax shall"), ("74", "74      An entity shall offset deferred tax"),
     ("98J", "98J     AASB 2021-5"), ("98L", "98L       An entity applying AASB 2021-5")])
add("U842-original", "fasb-asu2016-02", "https://storage.fasb.org/ASU%202016-02_Section%20A.pdf",
    "official_publisher_amendment_notice_not_authoritative", "ASU2016-02,February2016,SectionA",
    "Original ASC842 additions; effective-date amendments read separately in U842-dates;no full current ASC admission",
    "Cover says ASU is not authoritative. Full subsequent-amendment chain/current Codification not verified.",
    [("authority disclaimer", "An Accounting Standards Update is not\nauthoritative"),
     ("842-10-15-3", "842-10-15-3 A contract is or contains a lease"),
     ("842-10-15-4", "842-10-15-4 To determine whether a contract"),
     ("842-10-25-2", "842-10-25-2 A lessee shall classify"),
     ("842-10-25-3", "842-10-25-3 When none of the criteria"),
     ("842-10-55-2", "842-10-55-2 When determining lease classification"),
     ("842-10-25-8", "842-10-25-8 An entity shall account"),
     ("842-10-25-9", "842-10-25-9 If a lease is modified"),
     ("842-20-25-1", "842-20-25-1 At the commencement date"),
     ("842-20-25-5", "842-20-25-5 After the commencement date"),
     ("842-20-25-6", "842-20-25-6 After the commencement date"),
     ("842-20-30-1", "842-20-30-1 At the commencement date"),
     ("842-20-30-5", "842-20-30-5 At the commencement date"),
     ("842-20-35-1", "842-20-35-1 After the commencement date"),
     ("842-20-35-3", "842-20-35-3 After the commencement date")])
add("U842-dates", "fasb-asu2020-05", "https://storage.fasb.org/ASU%202020-05.pdf",
    "official_publisher_amendment_notice_not_authoritative", "ASU2020-05,June2020",
    "842-10-65-1:public business entities FY beginning after2018-12-15; all other entities after2021-12-15,interims after2022-12-15; special public-NFP provisions inspected but not used",
    "Physicalpage14 rendered inspection resolves deleted2020/2021 versus inserted2021/2022; transition/adoption history still needed",
    [("842-10-65-1", "842-10-65-1 The following represents"),
     ("842-10-65-1(b)", "b.   All other entities shall apply the pending content")])
add("U842-election", "fasb-asu2021-09", "https://storage.fasb.org/ASU%202021-09.pdf",
    "official_publisher_amendment_notice_not_authoritative", "ASU2021-09,November2021",
    "Non-PBE risk-free election by underlying-asset class; already-adopted entities FY after2021-12-15,interims after2022-12-15; otherwise with842 adoption",
    "2016 wording all-leases is stale. No risk-free election in matched case; complete currentASC still missing",
    [("842-20-30-3", "842-20-30-3 A lessee should use"),
     ("842-10-65-6", "842-10-65-6 The following represents")])
add("U109-historical", "fasb-fas109", "https://storage.fasb.org/fas109.pdf",
    "official_historical_standard_not_current_ASC", "FAS109,February1992,as retained from publisher",
    "Historical reconstruction only; not asserted operative2024 ASC740",
    "No use of obsolete US tax rates,old exceptions or presentation as2024 defaults; used only inspected plain temporary-difference/enactment mechanism",
    [("8", "8.    To implement the objectives"), ("10", "10. Income taxes currently payable"),
     ("11(d)", "d.    Expenses or losses that are deductible before"),
     ("16", "16. An enterprise shall recognize"), ("17", "17. Deferred taxes shall be determined"),
     ("18", "18. The objective is to measure"), ("27", "27. Deferred tax liabilities and assets"),
     ("66(c)/basis of conclusions", "c.    Deferred tax liabilities and assets are not discounted.")])
add("U740-enactment", "fasb-tax-asu2019-12", "https://storage.fasb.org/ASU%202019-12.pdf",
    "official_publisher_amendment_notice_not_authoritative", "ASU2019-12,December2019",
    "Public entities FY after2020-12-15; other entities FY after2021-12-15/interim after2022-12-15; selected740-270 provision inspected",
    "Physicalpage22 rendered inspection separates deletions from retained enactment requirement; not complete currentASC740",
    [("740-270-25-5", "740-270-25-5 The effects of new tax legislation"),
     ("BC35", "BC35. Topic 740 requires"),
     ("740-10-65-8", "740-10-65-8 The following represents")])
add("U740-disclosures", "fasb-tax-asu2023-09", "https://storage.fasb.org/ASU%202023-09.pdf",
    "official_publisher_amendment_notice_not_authoritative", "ASU2023-09,December2023",
    "Public business entities annual periods after2024-12-15;others after2025-12-15;early adoption permitted",
    "Retrieved as later-amendment lead; disclosures/effective-date inspection does not validate recognition/measurement;no current completeness claim",
    [("effective dates", "annual periods beginning after December 15, 2024."),
     ("early adoption", "Early adoption is permitted for annual financial statements")])
add("C16-case", "mof-single-transaction-tax-case",
    "https://kjs.mof.gov.cn/zt/kjzzss/srzzzq/sdszzyyal/202304/P020230404313918413399.pdf",
    "official_MoF_application_case_primary_interpretive_evidence", "Posted4Apr2023;five-pageworkedcase",
    "Exactcase quotesInterpretation16 section1 andASBE18;sourcecase2022 lease facts;operative transition of Interpretation16 not independently obtained",
    "Not complete standards text,currentASBE compilation,actual tax law or universal2024 admission. SourcePV deliberately rounded2600098→2600000.",
    [("case premise", "假设甲公司未来期间能够"),
     ("Interpretation16quotation", "根据《企业会计准则解释第 16 号》"),
     ("gross recognition", "分别确认相应的递"),
     ("rounding", "450 000×（P/A，5.04%，7）=2 600 098")])

for id,base,title,needles in [
    ("C21-reproduction","asbe21-wikisource","ASBE21,2018-labelled reproduction",[("14","第十四条　在租赁期开始日"),("16","第十六条　使用权资产"),("17","第十七条　租赁负债"),("21","第二十一条　承租人"),("23","第二十三条　承租人"),("28","第二十八条　租赁"),("29","第二十九条　租赁"),("32","第三十二条　对于短期")]),
    ("C18-reproduction","asbe18-wikisource","ASBE18,2006-labelled reproduction",[("5","第五条　资产的计税基础"),("11","第十一条　除下列交易"),("13","第十三条　企业应当"),("17","第十七条　资产负债表日"),("19","第十九条　企业不应当"),("21","第二十一条　企业当期")])]:
    rows=[anchor("sources/"+base+".txt",*a) for a in needles]
    for row in rows: row.pop("pdf_page")
    sources.append({"id":id,"authority_class":"secondary_reproduction_not_official_current_authority",
                    "url":"https://zh.wikisource.org/wiki/"+quote("企业会计准则第21号——租赁" if id=="C21-reproduction" else "企业会计准则第18号——所得税"),
                    "version":title,"files":[pin("sources/"+base+ext) for ext in (".html",".txt")],
                    "inspected_anchors":rows,"limits":"Proposed reading only. ASBE18 old initial exemption is incomplete relative to inspected official2023 case. Official exact pages located but returned502."})

# Original failed bytes are preserved, not replaced when a different route worked.
attempts=[
 ("sources/mof-lease2018.html","https://kjs.mof.gov.cn/zhengcefabu/201812/t20181213_3093852.htm",200,"redirect to MoF404,not source"),
 ("sources/mof-lease2018-path2.html","https://kjs.mof.gov.cn/zhengwuxinxi/zhengcefabu/201812/t20181213_3093852.html",200,"redirect to MoF404,not source"),
 ("sources/fasb-fas109.pdf","https://storage.fasb.org/FAS%20109.pdf",403,"not source;lowercase route later worked"),
 ("sources/fas109-original.pdf","https://storage.fasb.org/FAS%20109%20%28AS%20ISSUED%29.pdf",403,"not source"),
 ("sources/mof-asbe18.html","https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46230.htm",502,"exact standard page discovered in official index;not retrieved"),
 ("sources/mof-asbe21.html","https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201910/t20191028_3411190.htm",502,"exact standard page discovered in official search;not retrieved"),
 ("sources/mof-lease-notice.html","https://kjs.mof.gov.cn/zhengcefabu/201812/t20181213_3092629.htm",502,"exact2018notice from official index;not retrieved"),
 ("sources/mof-lease-notice-http.html","http://kjs.mof.gov.cn/zhengcefabu/201812/t20181213_3092629.htm",502,"same notice publicHTTP route;not retrieved"),
 ("sources/mof-lease-release-questions.html","https://kjs.mof.gov.cn/zhengcejiedu/201812/t20181213_3092642.htm",502,"release Q&A lead not retrieved"),
 ("sources/mof-interpretation16-notice.html","https://kjs.mof.gov.cn/gongzuotongzhi/202212/t20221212_3857395.htm",502,"exact2022notice discovered in official index5;not retrieved"),
 ("sources/mof-standards-index.html","https://kjs.mof.gov.cn/zt/kjzzss/",502,"broad parent index not retrieved;more specific index worked"),
 ("sources/mof-standard-list-23.html","https://kjs.mof.gov.cn/zhengcefabu/index_23.htm",502,"index not retrieved"),
 ("sources/mof-authoritative-standards-index2.html","https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/index_2.htm",502,"index not retrieved;site search found21page"),
 ("sources/mof-interpretations-index.html","https://kjs.mof.gov.cn/zt/kjzzss/qykjzzjs/",502,"interpretation index not retrieved"),
 ("sources/fasb-tax-asu2023-09.pdf","https://storage.fasb.org/ASU%202023-09%E2%80%94Income%20Taxes%20%28Topic%20740%29.pdf",403,"not source;short route later worked"),
 ("sources/asbe21-notice-wikisource.html","https://zh.wikisource.org/wiki/关于修订印发《企业会计准则第21号——租赁》的通知",404,"notice missing;not evidence")]
out={"schema":"accdsl.isolated.authority-register.v1","prepared_at":dt.datetime.now(dt.timezone.utc).isoformat(),
     "inspection_date":"2026-10-05","retrieval_time_note":"Same-daytooloutputs/headers preserved;file mtime is not asserted as exact remote publication time",
     "sources":sources,"access_failures":[dict(pin(p),url=u,http_status=c,disposition=d) for p,u,c,d in attempts],
     "discovery_files":[pin(str(p.relative_to(ROOT))) for p in SRC.glob("mof-*.html") if p.name not in {Path(a[0]).name for a in attempts}],
     "prior_access":"P08ASC403 challenge retained in baseline source-preparation;not retried or bypassed. Prior MoF22/37 failures do not determine21/18 access.",
     "search_limits":"Bing returned unrelated material,Google/duckduckgo/baidu challenge/discovery content;none used as technical support. OfficialMoF index and site-search gave inspected leads.",
     "inventory":[pin(str(p.relative_to(ROOT))) for p in sorted(SRC.rglob("*")) if p.is_file()]}
(ROOT/"source-register.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"sources":len(sources),"files":len(out["inventory"]),"anchors":sum(len(s["inspected_anchors"]) for s in sources)},ensure_ascii=False))
