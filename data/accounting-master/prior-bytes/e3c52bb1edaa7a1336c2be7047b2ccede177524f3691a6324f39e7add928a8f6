#!/usr/bin/env python3
"""Resolve exact report links from locally retained issuer/regulator indexes."""
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/financial-report-benchmark"


def link_title(issuer, anchor):
    title = " ".join(anchor.get_text(" ", strip=True).split())
    if issuer == "munich_re" and title.lower().startswith("download"):
        # The oldest archive labels each link in its nearest paragraph/text
        # element. Never borrow a title from the encompassing year accordion.
        container = anchor.find_parent(["p", "mr-e-text"])
        if container is not None and len(container.find_all("a", href=True)) == 1:
            surrounding = " ".join(container.get_text(" ", strip=True).split())
            candidate = surrounding.split(title, 1)[0].strip()
            if classify_link(issuer, candidate, anchor["href"]):
                return candidate
    return title


def classify_link(issuer, title, url):
    if issuer == "ping_an" and "irasia.com/listco/hk/pingan/" in url and ".pdf" in url.lower():
        match = re.fullmatch(r"([零〇一二三四五六七八九]{4})年中期报告", title)
        if match:
            year = int(match[1].translate(str.maketrans("零〇一二三四五六七八九", "00123456789")))
            return year, "interim_h1"
    if issuer == "henkel" and ".pdf" in url.lower():
        match = re.match(r"(Annual Report|Half-year financial report|Financial Report Q2 & HY) (20\d{2})", title, re.I)
        if match:
            return int(match[2]), "annual" if match[1].lower().startswith("annual") else "interim_h1"
    if issuer == "munich_re" and ".pdf" in url.lower():
        match = re.fullmatch(r"(Annual report \(Group\)|Annual Report|Half-year financial report) (20\d{2})", title, re.I)
        if match:
            return int(match[2]), "annual" if match[1].lower().startswith("annual") else "interim_h1"
    if issuer == "saic_motor":
        match = re.fullmatch(r"上海汽车集团股份有限公司\s*(20\d{2})\s*年\s*(半年度|年度)报告", title)
        if match:
            return int(match[1]), "interim_h1" if match[2] == "半年度" else "annual"
    mirror_codes = {"apple": "NASDAQ_AAPL", "caterpillar": "NYSE_CAT", "jpmorgan": "NYSE_JPM", "unilever": "LSE_ULVR", "hsbc": "NYSE_HSBC", "allianz": "NYSE_AZ"}
    if "annualreports.com/HostedData/AnnualReportArchive/" in url and issuer in mirror_codes:
        match = re.search(re.escape(mirror_codes[issuer]) + r"_(20\d{2})\.pdf$", url)
        if match:
            return int(match[1]), "annual"
    if issuer == "hsbc":
        match = re.fullmatch(r"(Annual Report(?: and Accounts)?|Interim Report) (20\d{2})", title, re.I)
        if match:
            return int(match[2]), "annual" if match[1].lower().startswith("annual") else "interim_h1"
    if issuer == "midea":
        match = re.match(r"(20\d{2})\s", title)
        if match and ".pdf" in url.lower():
            if re.search(r"半年度报告|H1", title, re.I):
                return int(match[1]), "interim_h1"
            if re.search(r"年度报告|年报", title):
                return int(match[1]), "annual"
    if issuer == "jpmorgan" and "jpmorganchase.com/" in url:
        match = re.search(r"/annualreport-?(20\d{2})\.pdf$", url, re.I)
        if match:
            return int(match[1]), "annual"
    return None


def main():
    target = DATA / "resolved-sources.json"
    resolved = json.loads(target.read_text()) if target.exists() else {}
    access = json.loads((DATA / "source-access.json").read_text())
    def add(doc_id, entry):
        entries = resolved.setdefault(doc_id, [])
        if not any(e["url"] == entry["url"] for e in entries):
            entries.append(entry)
    def provenance(index):
        return {"landing_url": index["url"], "landing_path": index["local_path"],
                "landing_sha256": index["sha256"], "discovered_at": index["captured_at"],
                "publication_date": None, "publication_date_status": "not_verified"}
    for index in access:
        if index.get("http_status") != 200 or not index.get("local_path"):
            continue
        path = ROOT / index["local_path"]
        if path.suffix == ".json" and "portalJsonpController" in index["url"]:
            raw = re.sub(r"^corpus\((.*)\);?\s*$", r"\1", path.read_text(), flags=re.S)
            payload = json.loads(raw)
            for article in payload.get("articleList", []):
                content = article["content"]
                title = content["articleTitle"]
                match = re.fullmatch(r"(20\d{2})年(年度|中期|半年度)报告", title)
                if not match or not 2018 <= int(match[1]) <= 2025:
                    continue
                cls = "annual" if match[2] == "年度" else "interim_h1"
                for attachment in content.get("atts", []):
                    if attachment.get("attType") == "PDF":
                        add(f"ping_an-{match[1]}-{cls}", {**provenance(index),
                            "url": urljoin("https://www.pingan.cn", attachment["attPath"]),
                            "source_title": title, "source_kind": "issuer_archive",
                            "archive_article_id": content["articleId"],
                            "archive_created_at": content.get("createDate"),
                            "archive_updated_at": content.get("updateDate"),
                        })
            continue
        if path.suffix == ".json" and "/GetEdgarFilingList?" in index["url"]:
            for filing in json.loads(path.read_text()).get("GetEdgarFilingListResult", []):
                date = datetime.strptime(filing["FilingDate"], "%m/%d/%Y %H:%M:%S").date().isoformat()
                form = filing["FilingTypeMnemonic"]
                matches = [(doc_id, e) for doc_id, entries in resolved.items()
                           if doc_id.startswith(index["issuer_id"] + "-")
                           for e in entries if e.get("source_kind") == "regulator_filing"
                           and e.get("publication_date") == date
                           and e.get("source_title", "").startswith(form + " ")]
                if len(matches) != 1:
                    continue
                doc_id, sec = matches[0]
                for document in filing["DocumentList"]:
                    if document["DocumentType"] not in {"HTML", "CONVPDF", "PDF"} or not document.get("Url"):
                        continue
                    add(doc_id, {**provenance(index), "url": document["Url"],
                        "source_title": sec["source_title"], "source_kind": "issuer_filing_mirror",
                        "representation_type": document["DocumentType"], "regulator_url": sec["url"],
                        "accession_number": sec["accession_number"], "report_date": sec["report_date"],
                        "publication_date": date, "publication_date_status": "issuer_and_regulator_filing_date",
                    })
            continue
        if path.suffix == ".json" and "jpmorganchase.com/services/json/" in index["url"]:
            for item in json.loads(path.read_text()).get("items", []):
                year = int(item["year"])
                if not 2018 <= year <= 2025:
                    continue
                filing = item.get("docs", {}).get("tenkDoc", {})
                title, link = filing.get("title", ""), filing.get("link", "")
                if not link:
                    continue
                cls = "annual" if "10-K" in title else {"1st": "q1", "2nd": "q2", "3rd": "q3"}.get(item["quarter"]) if "10-Q" in title else None
                if cls:
                    add(f"jpmorgan-{year}-{cls}", {**provenance(index), "url": urljoin(index["url"], link), "source_title": title, "source_kind": "issuer_archive"})
            continue
        if path.suffix == ".json" and "data.sec.gov/submissions/" in index["url"]:
            payload = json.loads(path.read_text())
            filings = payload.get("filings", {}).get("recent", payload)
            cik = {"apple": 320193, "caterpillar": 18230, "jpmorgan": 19617}.get(index["issuer_id"])
            if not cik:
                continue
            for i, form in enumerate(filings.get("form", [])):
                if form not in {"10-K", "10-Q"}:
                    continue
                end = filings["reportDate"][i]
                if not end:
                    continue
                year, month, _ = map(int, end.split("-"))
                if index["issuer_id"] == "apple":
                    cls = "annual" if form == "10-K" else {12: "q1", 3: "q2", 4: "q2", 6: "q3", 7: "q3"}.get(month)
                    year += month == 12
                else:
                    cls = "annual" if form == "10-K" else {3: "q1", 6: "q2", 9: "q3"}.get(month)
                if cls is None or not 2018 <= year <= 2025:
                    continue
                accession = filings["accessionNumber"][i]
                url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{filings['primaryDocument'][i]}"
                add(f"{index['issuer_id']}-{year}-{cls}", {
                    "url": url, "source_title": f"{form} for period ended {end}", "source_kind": "regulator_filing",
                    "landing_url": index["url"], "landing_path": index["local_path"], "landing_sha256": index["sha256"],
                    "discovered_at": index["captured_at"], "accession_number": accession, "report_date": end,
                    "publication_date": filings["filingDate"][i], "publication_date_status": "regulator_filing_date",
                })
            continue
        if path.suffix != ".html":
            continue
        soup = BeautifulSoup(path.read_text(errors="replace"), "html.parser")
        for anchor in soup.find_all("a", href=True):
            title = link_title(index["issuer_id"], anchor)
            url = urljoin(index["final_url"], anchor["href"])
            match = classify_link(index["issuer_id"], title, url)
            if not match or not 2018 <= match[0] <= 2025:
                continue
            doc_id = f"{index['issuer_id']}-{match[0]}-{match[1]}"
            entry = {
                "url": url, "source_title": title, "source_kind": "public_mirror" if any(host in url for host in ["annualreports.com/", "irasia.com/"]) else "issuer_archive",
                "landing_url": index["url"], "landing_path": index["local_path"],
                "landing_sha256": index["sha256"], "discovered_at": index["captured_at"],
                "original_href": anchor["href"], "publication_date": None,
                "publication_date_status": "not_verified",
            }
            add(doc_id, entry)
    for entries in resolved.values():
        priority = {"issuer_archive": 0, "issuer_filing_mirror": 1, "regulator_filing": 2, "public_mirror": 3}
        entries.sort(key=lambda entry: (priority.get(entry.get("source_kind"), 2), entry.get("representation_type") != "HTML"))
    target.write_text(json.dumps(resolved, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    counts = {}
    for key in resolved:
        issuer = key.split("-")[0]
        counts[issuer] = counts.get(issuer, 0) + 1
    print(json.dumps({"resolved_slots": len(resolved), "per_issuer": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
