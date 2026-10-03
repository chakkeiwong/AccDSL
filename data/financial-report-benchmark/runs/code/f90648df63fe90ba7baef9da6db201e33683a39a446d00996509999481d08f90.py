#!/usr/bin/env python3
"""Acquire and QA a bounded, source-preserving financial-report corpus.

The collector is deliberately conservative. A successful HTTP response is not
accepted as a report until the bytes, extracted text, issuer, period, report
class, statement/note signals and accounting-basis signals pass checks.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import quote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PANEL = ROOT / "data/financial-report-benchmark/target-panel-v1.json"
DEFAULT_DATA = ROOT / "data/financial-report-benchmark"
USER_AGENT = "AccDSL-financial-report-corpus/1.0 (public research; bounded retrieval)"
SUCCESS_STATUSES = {"acquired_verified", "local_imported_verified", "revalidated_verified"}
QA_VERSION = "5"
HIDDEN_HTML_TAGS = {"script", "style", "noscript", "svg", "ix:header", "ix:hidden", "xbrli:context", "xbrli:unit"}


class TextExtractor(HTMLParser):
    """Small HTML text extractor for report identity checks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = dict(attrs)
        hidden = tag in HIDDEN_HTML_TAGS or "hidden" in attributes or bool(re.search(r"display\s*:\s*none", attributes.get("style") or "", re.I))
        void = tag in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
        if not void and (hidden or self.hidden_stack):
            self.hidden_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.hidden_stack:
            index = len(self.hidden_stack) - 1 - self.hidden_stack[::-1].index(tag)
            del self.hidden_stack[index:]

    def handle_data(self, data: str) -> None:
        if not self.hidden_stack:
            value = " ".join(data.split())
            if value:
                self.parts.append(value)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def issuer_aliases(issuer: dict[str, Any]) -> list[str]:
    distinctive = {
        "apple": ["apple inc."], "caterpillar": ["caterpillar inc.", "caterpillar"],
        "jpmorgan": ["jpmorgan chase"], "unilever": ["unilever"],
        "hsbc": ["hsbc holdings"], "allianz": ["allianz"],
        "saic_motor": ["saic motor", "上海汽车集团", "上汽集团"],
        "ping_an": ["ping an insurance", "中国平安保险", "中國平安保險"],
        "midea": ["midea group", "美的集团", "美的集團"],
    }
    return [issuer["legal_name"].lower(), *issuer.get("identity_aliases", distinctive.get(issuer["issuer_id"], []))]


def expected_documents(panel: dict[str, Any]) -> list[dict[str, Any]]:
    years = range(panel["coverage_window"]["start_year"], panel["coverage_window"]["end_year"] + 1)
    by_id = {item["issuer_id"]: item for item in panel["issuers"]}
    docs: list[dict[str, Any]] = []
    for issuer in panel["issuers"]:
        if issuer["standard_family"] == "us_gaap":
            classes = ["annual", "q1", "q2", "q3"]
        else:
            classes = ["annual", "interim_h1"]
        for year in years:
            for report_class in classes:
                label = {
                    "annual": f"FY{year}",
                    "q1": f"FY{year}-Q1",
                    "q2": f"FY{year}-Q2",
                    "q3": f"FY{year}-Q3",
                    "interim_h1": f"FY{year}-H1",
                }[report_class]
                templates = issuer.get("source_templates_by_class", {}).get(report_class, [])
                if report_class == "annual":
                    templates = templates or issuer.get("source_templates", [])
                candidates = [template.format(year=year) for template in templates]
                docs.append(
                    {
                        "document_id": f"{issuer['issuer_id']}-{year}-{report_class}",
                        "issuer_id": issuer["issuer_id"],
                        "legal_name": issuer["legal_name"],
                        "region": issuer["region"],
                        "industry": issuer["industry"],
                        "standard_family": issuer["standard_family"],
                        "period_year": year,
                        "period_label": label,
                        "report_class": report_class,
                        "landing_urls": issuer.get("landing_urls", []),
                        "source_candidates": candidates,
                        "source_candidate_status": "unverified_template" if candidates else "no_template",
                        "issuer_aliases": issuer_aliases(issuer),
                    }
                )
    for local in panel.get("existing_local_sources", []):
        issuer = by_id[local["issuer_id"]]
        canonical_id = f"{local['issuer_id']}-{local['period_year']}-{local['report_class']}"
        match = next((item for item in docs if item["document_id"] == canonical_id), None)
        if match is None:
            match = {
                "document_id": canonical_id,
                "issuer_id": local["issuer_id"],
                "legal_name": issuer["legal_name"],
                "region": issuer["region"],
                "industry": issuer["industry"],
                "standard_family": issuer["standard_family"],
                "period_year": local["period_year"],
                "period_label": local["period_label"],
                "report_class": local["report_class"],
                "landing_urls": issuer.get("landing_urls", []),
                "source_candidates": [],
                "issuer_aliases": issuer_aliases(issuer),
            }
            docs.append(match)
        match["local_path"] = local["local_path"]
        match["source_url"] = local["source_url"]
        match["source_kind"] = local["source_kind"]
        match["local_status"] = local.get("status")
    resolved_path = ROOT / panel.get("resolved_sources_file", "data/financial-report-benchmark/resolved-sources.json")
    resolved = read_json(resolved_path) if resolved_path.exists() else {}
    for doc in docs:
        entries = resolved.get(doc["document_id"], [])
        doc["source_metadata"] = {entry["url"]: entry for entry in entries}
        doc["source_candidates"] = list(dict.fromkeys([entry["url"] for entry in entries] + doc["source_candidates"]))
        if entries:
            doc["source_candidate_status"] = "archive_link_discovered"
    return docs


def clean_text(data: bytes, content_type: str, suffix: str) -> str:
    if data.startswith(b"%PDF-") or "pdf" in content_type.lower() or suffix.lower() == ".pdf":
        pdftotext = shutil.which("pdftotext")
        if pdftotext:
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
                handle.write(data)
                handle.flush()
                try:
                    result = subprocess.run(
                        [pdftotext, "-layout", handle.name, "-"],
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=90,
                    )
                    if result.returncode == 0:
                        return result.stdout.decode("utf-8", errors="replace")
                except (OSError, subprocess.SubprocessError):
                    pass
        return ""
    decoded = data.decode("utf-8", errors="replace")
    parser = TextExtractor()
    try:
        parser.feed(decoded)
        return "\n".join(parser.parts)
    except Exception:
        return re.sub(r"<[^>]+>", " ", html.unescape(decoded))


def magic_kind(data: bytes, content_type: str) -> str:
    head = data[:4096].lstrip().lower()
    if data.startswith(b"%PDF-"):
        return "pdf"
    if head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<html" in head[:512]:
        return "html"
    if "pdf" in content_type.lower():
        return "pdf_claimed"
    if "html" in content_type.lower() or "text/" in content_type.lower():
        return "html_claimed"
    return "unknown"


def blocked_page(text: str) -> str | None:
    lowered = text[:120_000].lower()
    patterns = [
        ("automated_access_block", "your request originates from an undeclared automated tool"),
        ("access_denied", "access denied"),
        ("cloudflare_challenge", "cf-chl-"),
        ("login_page", "please log in"),
        ("not_found_page", "<title>404"),
        ("not_found_page", "page not found"),
    ]
    for reason, needle in patterns:
        if needle in lowered:
            return reason
    return None


def basis_check(doc: dict[str, Any], text: str) -> dict[str, Any]:
    text = " ".join(text.split())
    if doc["standard_family"] == "us_gaap":
        patterns = [
            r"u\.?s\.?\s+gaap",
            r"generally accepted accounting principles in the united states",
            r"us generally accepted",
            r"united states generally accepted accounting principles",
            r"u\.?s\.?\s+generally accepted accounting principles",
            r"accounting principles generally accepted in the united states",
        ]
    elif doc["standard_family"] == "ifrs_oriented":
        patterns = [r"ifrs(?:s| accounting standards)?", r"international financial reporting standards", r"ias\)?\s+34"]
    else:
        patterns = [r"企业会计准则", r"企業會計準則", r"chinese accounting standards", r"prc gaap", r"accounting standards for business enterprises"]
    evidence = []
    for pattern in patterns:
        anchored = (r"(?:financial statements|financial report|reported results|财务报表|財務報表|财务报告)"
                    r".{0,300}?(?:prepar|accordance|conform|按照|编制|編製|遵循|符合)"
                    r".{0,250}?(?:" + pattern + r")")
        for match in re.finditer(anchored, text, re.I):
            # Negative assurance needs its full logical context; a naked
            # "not prepared" sentence must never establish preparation basis.
            if re.search(r"\bnot\b.{0,50}\b(?:prepar|accordance|conform)|\b(?:not|never)\s+in\s+accordance", match.group(), re.I):
                continue
            start, end = max(0, match.start() - 60), min(len(text), match.end() + 180)
            evidence.append({"pattern": anchored, "text_offset": start, "quote": text[start:end]})
            break
    return {"status": "verified" if evidence else "missing", "evidence": evidence,
            "interpretation": "Preparation-basis anchor; detailed jurisdiction and transition annotation remain provisional."}


def period_identity(doc: dict[str, Any], text: str) -> dict[str, Any]:
    """Check the report's own cover/filing period, not comparative-year mentions."""
    compact = " ".join(text.split()).lower().replace("–", "-").replace("—", "-")
    head = compact[:16000]
    year, cls = doc["period_year"], doc["report_class"]
    if doc["issuer_id"] == "munich_re":
        # The 2021 cover prints the report year as "2/2021" after the
        # issuer name. Match that cover only, before comparative references.
        cover = re.match(r"half-year financial report munich re 2/(20\d{2})\b", head[:200])
        if cover:
            actual_year = int(cover[1])
            return {"status": "matched" if cls == "interim_h1" and year == actual_year else "mismatch",
                    "quote": cover.group(), "observed_class": "interim_h1", "fiscal_year": actual_year}
    filing = re.search(r"for the (?:fiscal year|quarterly period) ended\s*:?\s*(?:commission file\s*)?([a-z]+)\s+(\d{1,2})\s*,?\s*(20\d{2})", head)
    if filing:
        month_name, day, actual_year = filing.groups()
        months = {name.lower(): i for i, name in enumerate(
            ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}
        month = months.get(month_name)
        if doc["issuer_id"] == "apple":
            actual_cls = {12: "q1", 3: "q2", 4: "q2", 6: "q3", 7: "q3", 9: "annual"}.get(month)
            fiscal_year = int(actual_year) + (month == 12)
        else:
            actual_cls = {3: "q1", 6: "q2", 9: "q3", 12: "annual"}.get(month)
            fiscal_year = int(actual_year)
        ok = actual_cls == cls and fiscal_year == year
        return {"status": "matched" if ok else "mismatch", "quote": filing.group(),
                "observed_class": actual_cls, "fiscal_year": fiscal_year,
                "period_end": f"{actual_year}-{month:02d}-{int(day):02d}" if month else None}
    # Cover titles precede the comparative years printed in the statements.
    titles = r"annual report(?: and accounts)?|annual financial report|interim report|half[- ]year(?:ly)?(?: financial)? report|half[- ]year results|年度报告|年度報告|半年度报告|半年度報告|中期报告|中期報告"
    title = re.search(rf"(?P<before>20\d{{2}})\s*(?:年\s*)?(?P<t1>{titles})|(?P<t2>{titles})\s*(?:for\s*)?(?P<after>20\d{{2}})", head[:6000])
    if title:
        actual_year = int(title.group("before") or title.group("after"))
        label = title.group("t1") or title.group("t2")
        actual_cls = "interim_h1" if re.search(r"interim|half|半年度|中期", label) else "annual"
        return {"status": "matched" if actual_year == year and actual_cls == cls else "mismatch",
                "quote": title.group(), "observed_class": actual_cls, "fiscal_year": actual_year}
    return {"status": "missing", "reason": "No unambiguous cover or filing period; requires source inspection."}


def identity_checks(doc: dict[str, Any], text: str, kind: str, source_url: str) -> dict[str, Any]:
    lowered = " ".join(text.lower().split())
    issuer_matches = [alias for alias in doc["issuer_aliases"] if alias.lower() in lowered[:20000]]
    period = period_identity(doc, text)
    statement_terms = [
        "balance sheet",
        "statement of financial position",
        "statements of financial position",
        "income statement",
        "statement of profit or loss",
        "statements of income",
        "statements of profit or loss",
        "income statements",
        "cash flows",
        "现金流量表",
        "资产负债表",
    ]
    note_terms = [
        "notes to consolidated",
        "notes to the consolidated",
        "basis of preparation",
        "accounting policies",
        "会计报表附注",
        "财务报表附注",
        "财务报表的编制基础",
        "重要会计政策及会计估计",
    ]
    statement_matches = [term for term in statement_terms if term in lowered]
    note_matches = [term for term in note_terms if term in lowered]
    class_terms = {
        "annual": ["annual report", "form 10-k", "year ended", "年度报告"],
        "q1": ["form 10-q", "first quarter", "three months ended", "第一季度"],
        "q2": ["form 10-q", "second quarter", "six months ended", "半年度", "中期报告"],
        "q3": ["form 10-q", "third quarter", "nine months ended", "第三季度"],
        "interim_h1": ["interim report", "half-year", "six months ended", "中期报告", "半年度报告"],
    }
    class_matches = [term for term in class_terms[doc["report_class"]] if term in lowered]
    # Report bodies routinely mention presentations, press releases or data
    # packs as investor-relations channels.  Only reject an item when the
    # source identity itself advertises a release/presentation/data pack.
    release_terms = ["presentation", "media release", "press release", "data pack", "trading update"]
    source_identity = f"{source_url} {doc.get('source_title', '')}".lower()
    release_matches = [term for term in release_terms if term in source_identity]
    basis = basis_check(doc, text)
    checks = {
        "magic_kind": kind,
        "issuer": {"status": "matched" if issuer_matches else "missing", "matches": issuer_matches[:8]},
        "period_year": period,
        "report_class": {"status": "matched" if class_matches else "missing", "matches": class_matches},
        "statements": {"status": "matched" if len(statement_matches) >= 2 else "missing", "matches": statement_matches},
        "notes": {"status": "matched" if note_matches else "missing", "matches": note_matches},
        "accounting_basis": basis,
        "release_only_signal": {"status": "present" if release_matches else "absent", "matches": release_matches},
    }
    required = ["issuer", "period_year", "report_class", "statements", "notes", "accounting_basis"]
    valid = all(checks[key]["status"] in {"matched", "verified"} for key in required)
    if release_matches or kind not in {"pdf", "html"} or len(text) < 5000:
        valid = False
    checks["qa_version"] = QA_VERSION
    checks["overall"] = "pass" if valid else "fail"
    return checks


def extension_for(kind: str, source_url: str) -> str:
    if kind.startswith("pdf") or source_url.lower().split("?")[0].endswith(".pdf"):
        return ".pdf"
    if kind.startswith("html"):
        return ".html"
    return ".bin"


def safe_fetch(url: str, retries: int = 2) -> dict[str, Any]:
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return {"url": url, "status": "network_error", "error": "Only public HTTP(S) source URLs are supported", "attempts": 0}
    url = urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%:@"), quote(parts.query, safe="=&%:/?+"), ""))
    last: dict[str, Any] = {"url": url, "status": "network_error"}
    for attempt in range(retries + 1):
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.1"})
        try:
            with urlopen(request, timeout=45) as response:
                body = response.read()
                headers = response.headers
                return {
                    "url": url,
                    "final_url": response.geturl(),
                    "http_status": getattr(response, "status", 200),
                    "content_type": headers.get("Content-Type", ""),
                    "last_modified": headers.get("Last-Modified"),
                    "body": body,
                    "attempts": attempt + 1,
                }
        except HTTPError as error:
            body = error.read(120_000) if hasattr(error, "read") else b""
            last = {
                "url": url,
                "final_url": getattr(error, "url", url),
                "http_status": error.code,
                "content_type": error.headers.get("Content-Type", "") if error.headers else "",
                "body": body,
                "attempts": attempt + 1,
                "status": "http_error",
            }
            if error.code not in {429, 500, 502, 503, 504}:
                return last
        except (URLError, TimeoutError, OSError) as error:
            last = {"url": url, "status": "network_error", "error": str(error), "attempts": attempt + 1}
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    return last


def save_bytes(data_root: Path, doc: dict[str, Any], data: bytes, suffix: str) -> tuple[Path, str]:
    target_dir = data_root / "documents" / doc["issuer_id"] / doc["document_id"]
    target_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(data).hexdigest()
    target = target_dir / f"original{suffix}"
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        target = target_dir / f"original-{digest}{suffix}"
    if not target.exists():
        temp = target.with_suffix(target.suffix + ".part")
        temp.write_bytes(data)
        temp.replace(target)
    return target, digest


def save_text(data_root: Path, doc: dict[str, Any], text: str) -> Path | None:
    if not text.strip():
        return None
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    target = data_root / "documents" / doc["issuer_id"] / doc["document_id"] / f"extracted-{digest}.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_text(encoding="utf-8") != text:
            raise ValueError(f"Hash-named extraction has changed: {target}")
    else:
        target.write_text(text, encoding="utf-8")
    return target


def result_base(doc: dict[str, Any], source_url: str | None, mode: str) -> dict[str, Any]:
    return {
        "schema_version": "accdsl.financial_report_benchmark.result.v1",
        "attempted_at": now(),
        "document_id": doc["document_id"],
        "issuer_id": doc["issuer_id"],
        "period_year": doc["period_year"],
        "period_label": doc["period_label"],
        "report_class": doc["report_class"],
        "standard_family": doc["standard_family"],
        "source_url": source_url,
        "landing_urls": doc.get("landing_urls", []),
        "mode": mode,
        "source_metadata": doc.get("source_metadata", {}).get(source_url, {}),
        "qa_version": QA_VERSION,
    }


def process_local(data_root: Path, doc: dict[str, Any]) -> dict[str, Any]:
    local = ROOT / doc["local_path"]
    result = result_base(doc, doc.get("source_url"), "local")
    result["local_source"] = doc["local_path"]
    if not local.is_file():
        result.update({"status": "missing", "failure_reason": "local_source_not_found"})
        return result
    data = local.read_bytes()
    content_type = "application/pdf" if local.suffix.lower() == ".pdf" else "text/html"
    kind = magic_kind(data, content_type)
    text = clean_text(data, content_type, local.suffix)
    blocked = blocked_page(text)
    checks = identity_checks(doc, text, kind, doc.get("source_url", ""))
    target, digest = save_bytes(data_root, doc, data, local.suffix.lower() or ".bin")
    text_target = save_text(data_root, doc, text)
    result.update(
        {
            "status": "local_imported_verified" if not blocked and checks["overall"] == "pass" else "invalid",
            "failure_reason": blocked or (None if checks["overall"] == "pass" else "identity_or_completeness_check_failed"),
            "bytes": len(data),
            "sha256": digest,
            "content_type": content_type,
            "magic_kind": kind,
            "local_path": str(target.relative_to(ROOT)),
            "extracted_text_path": str(text_target.relative_to(ROOT)) if text_target else None,
            "extracted_characters": len(text),
            "checks": checks,
        }
    )
    return result


def process_url(data_root: Path, doc: dict[str, Any], url: str) -> dict[str, Any]:
    result = result_base(doc, url, "network")
    response = safe_fetch(url, retries=1)
    result.update({key: value for key, value in response.items() if key != "body"})
    body = response.get("body", b"")
    http_status = response.get("http_status")
    if http_status is None:
        result.update({"status": "network_error", "failure_reason": response.get("error", "network_error")})
        return result
    if http_status != 200:
        if body:
            digest = hashlib.sha256(body).hexdigest()
            evidence = data_root / "access-failures" / doc["issuer_id"] / f"{digest}.bin"
            evidence.parent.mkdir(parents=True, exist_ok=True)
            evidence.write_bytes(body)
            result.update({"response_body_path": str(evidence.relative_to(ROOT)), "response_sha256": digest})
        result.update({"status": "blocked", "failure_reason": f"http_status_{http_status}"})
        return result
    content_type = response.get("content_type", "")
    kind = magic_kind(body, content_type)
    suffix = extension_for(kind, response.get("final_url", url))
    text = clean_text(body, content_type, suffix)
    block_reason = blocked_page(text)
    if block_reason:
        result.update({"status": "blocked", "failure_reason": block_reason, "bytes": len(body), "magic_kind": kind})
        return result
    target, digest = save_bytes(data_root, doc, body, suffix)
    text_target = save_text(data_root, doc, text)
    checks = identity_checks({**doc, **doc.get("source_metadata", {}).get(url, {})}, text, kind, response.get("final_url", url))
    status = "acquired_verified" if checks["overall"] == "pass" else "invalid"
    result.update(
        {
            "status": status,
            "failure_reason": None if status == "acquired_verified" else "identity_or_completeness_check_failed",
            "bytes": len(body),
            "sha256": digest,
            "magic_kind": kind,
            "local_path": str(target.relative_to(ROOT)),
            "extracted_text_path": str(text_target.relative_to(ROOT)) if text_target else None,
            "extracted_characters": len(text),
            "checks": checks,
        }
    )
    return result


def process_retained(data_root: Path, doc: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    """Re-run QA against an already retained original without downloading it.

    This is intentionally separate from acquisition.  It verifies that the
    bytes and extracted text still satisfy the current QA version and that the
    immutable file has not changed since the prior successful result.
    """
    source_url = prior.get("source_url") or doc.get("source_url")
    result = result_base(doc, source_url, "revalidate")
    relative = prior.get("local_path")
    if not relative:
        result.update({"status": "invalid", "failure_reason": "retained_source_path_missing"})
        return result
    local = ROOT / relative
    result.update({"local_path": relative, "sha256": prior.get("sha256")})
    if not local.is_file():
        result.update({"status": "invalid", "failure_reason": "retained_source_not_found", "local_path": relative})
        return result
    data = local.read_bytes()
    content_type = prior.get("content_type") or ("application/pdf" if local.suffix.lower() == ".pdf" else "text/html")
    kind = magic_kind(data, content_type)
    text = clean_text(data, content_type, local.suffix)
    blocked = blocked_page(text)
    checks = identity_checks({**doc, **doc.get("source_metadata", {}).get(source_url, {})}, text, kind, source_url or "")
    digest = hashlib.sha256(data).hexdigest()
    recorded_digest = prior.get("checks", {}).get("retained_sha256", {}).get("recorded") or prior.get("sha256")
    digest_match = bool(recorded_digest) and recorded_digest == digest
    checks["retained_sha256"] = {
        "status": "matched" if digest_match else "mismatch",
        "recorded": recorded_digest,
        "observed": digest,
    }
    valid = not blocked and digest_match and checks["overall"] == "pass"
    if not valid:
        checks["overall"] = "fail"
    text_target = save_text(data_root, doc, text)
    result.update(
        {
            "status": "revalidated_verified" if valid else "invalid",
            "failure_reason": None if valid else (blocked or ("retained_sha256_mismatch" if not digest_match else "identity_or_completeness_check_failed")),
            "bytes": len(data),
            "sha256": digest,
            "content_type": content_type,
            "magic_kind": kind,
            "local_path": relative,
            "extracted_characters": len(text),
            "extracted_text_path": str(text_target.relative_to(ROOT)) if text_target else None,
            "source_metadata": doc.get("source_metadata", {}).get(source_url, {}) or prior.get("source_metadata", {}),
            "checks": checks,
            "prior_attempted_at": prior.get("attempted_at"),
        }
    )
    return result


def append_results(data_root: Path, results: Iterable[dict[str, Any]]) -> None:
    path = data_root / "acquisition-results.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")


def latest_results(data_root: Path) -> dict[str, dict[str, Any]]:
    path = data_root / "acquisition-results.jsonl"
    if not path.exists():
        return {}
    versions: dict[tuple[str, str], dict[str, Any]] = {}
    attempts: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if item.get("local_path"):
            # A revalidation supersedes the verdict for this retained version,
            # including failure. A failed HTTP retry has no retained version
            # and cannot revoke an intact, independently verified original.
            versions[(item["document_id"], item["local_path"])] = item
        else:
            attempts.append(item)
    latest: dict[str, dict[str, Any]] = {}
    for item in [*attempts, *versions.values()]:
        if item.get("status") in SUCCESS_STATUSES and item.get("qa_version") != QA_VERSION:
            item = {**item, "status": "needs_revalidation", "failure_reason": "qa_version_outdated"}
        rank = {**{s: 3 for s in SUCCESS_STATUSES}, "invalid": 2, "needs_revalidation": 2,
                "blocked": 1, "network_error": 1, "missing": 1, "not_attempted": 0}
        old = latest.get(item["document_id"])
        if old is None or (rank.get(item.get("status"), 0), item.get("attempted_at", "")) >= (rank.get(old.get("status"), 0), old.get("attempted_at", "")):
            latest[item["document_id"]] = item
    return latest


def build_report(panel: dict[str, Any], data_root: Path) -> dict[str, Any]:
    docs = expected_documents(panel)
    latest = latest_results(data_root)
    rows: list[dict[str, Any]] = []
    for doc in docs:
        result = latest.get(doc["document_id"], {})
        checks = result.get("checks", {})
        rows.append(
            {
                "document_id": doc["document_id"],
                "issuer_id": doc["issuer_id"],
                "region": doc["region"],
                "industry": doc["industry"],
                "standard_family": doc["standard_family"],
                "period_year": doc["period_year"],
                "period_label": doc["period_label"],
                "report_class": doc["report_class"],
                "status": result.get("status", "not_attempted"),
                "source_url": result.get("source_url") or (doc.get("source_candidates") or [None])[0],
                "sha256": result.get("sha256"),
                "local_path": result.get("local_path"),
                "extracted_text_path": result.get("extracted_text_path"),
                "qa_version": result.get("qa_version"),
                "failure_reason": result.get("failure_reason", "not_attempted"),
                "basis_status": checks.get("accounting_basis", {}).get("status", "not_checked"),
                "statement_status": checks.get("statements", {}).get("status", "not_checked"),
                "notes_status": checks.get("notes", {}).get("status", "not_checked"),
            }
        )
    hashes: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row["status"] in SUCCESS_STATUSES and row["sha256"]:
            hashes.setdefault(row["sha256"], []).append(row)
    duplicates = []
    for digest, matches in hashes.items():
        if len(matches) > 1:
            duplicates.append({"sha256": digest, "document_ids": [r["document_id"] for r in matches]})
            for row in matches:
                row.update({"status": "duplicate_content", "failure_reason": "same_bytes_assigned_to_different_slots"})
    per_issuer: dict[str, dict[str, Any]] = {}
    for issuer in panel["issuers"]:
        issuer_rows = [row for row in rows if row["issuer_id"] == issuer["issuer_id"]]
        years = sorted({row["period_year"] for row in issuer_rows})
        required_classes = {row["report_class"] for row in issuer_rows}
        complete_years = [
            year
            for year in years
            if all(
                any(row["period_year"] == year and row["report_class"] == cls and row["status"] in SUCCESS_STATUSES for row in issuer_rows)
                for cls in required_classes
            )
        ]
        consecutive = 0
        best = 0
        previous = None
        for year in complete_years:
            if previous is not None and year == previous + 1:
                consecutive += 1
            else:
                consecutive = 1
            best = max(best, consecutive)
            previous = year
        per_issuer[issuer["issuer_id"]] = {
            "legal_name": issuer["legal_name"],
            "standard_family": issuer["standard_family"],
            "industry": issuer["industry"],
            "expected_documents": len(issuer_rows),
            "verified_documents": sum(row["status"] in SUCCESS_STATUSES for row in issuer_rows),
            "complete_years": complete_years,
            "longest_consecutive_complete_years": best,
            "minimum_met": best >= panel["coverage_window"]["minimum_complete_years_per_issuer"],
        }
    report = {
        "schema_version": "accdsl.financial_report_benchmark.coverage.v1",
        "generated_at": now(),
        "panel": panel.get("_panel_path", str(DEFAULT_PANEL.relative_to(ROOT))),
        "coverage_window": panel["coverage_window"],
        "expected_documents": len(rows),
        "verified_documents": sum(row["status"] in SUCCESS_STATUSES for row in rows),
        "unverified_documents": sum(row["status"] not in SUCCESS_STATUSES for row in rows),
        "duplicate_content": duplicates,
        "blocked_or_missing_documents": sum(row["status"] in {"blocked", "missing", "not_attempted"} for row in rows),
        "rows": rows,
        "per_issuer": per_issuer,
        "acceptance": {
            "status": "source_corpus_ready" if all(item["minimum_met"] for item in per_issuer.values()) and not duplicates else "not_ready",
            "reason": "Five consecutive complete years per issuer are required before benchmark annotation or model evaluation splits are promoted.",
        },
    }
    write_json(data_root / "coverage.json", report)
    with (data_root / "coverage.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    write_json(data_root / "source-evidence.json", {"generated_at": now(), "qa_version": QA_VERSION, "documents": latest})
    parts = ["<!doctype html><html lang='en'><meta charset='utf-8'><title>AccDSL source corpus</title>",
             "<style>body{font:15px system-ui;margin:2rem;line-height:1.45}table{border-collapse:collapse;width:100%}td,th{text-align:left;border-bottom:1px solid #ddd;padding:.5rem;vertical-align:top}th{background:#f4f5f6}details{max-width:60rem}code{overflow-wrap:anywhere}a{color:#145b9e}</style>",
             "<h1>Financial-report source corpus</h1>",
             f"<p>{report['verified_documents']} of {len(rows)} target slots pass source QA version {QA_VERSION}. Acquisition status: <strong>{report['acceptance']['status']}</strong>.</p>",
             "<p>These are retained source reports, not adjudicated accounting labels or model accuracy scores. Unknown publication dates, incorporated disclosures and external HTML assets require separate work before as-of tests or complete-package claims.</p>",
             "<p><a href='coverage.csv'>Coverage CSV</a> · <a href='coverage.json'>Coverage JSON</a> · <a href='source-evidence.json'>Full source evidence</a> · <a href='acquisition-results.jsonl'>Attempt history</a></p>",
             "<table><tr><th>Issuer</th><th>Verified / target</th><th>Complete years</th><th>Consecutive years</th></tr>"]
    for issuer, summary in per_issuer.items():
        parts.append(f"<tr><td><a href='#{issuer}'>{html.escape(summary['legal_name'])}</a></td><td>{summary['verified_documents']} / {summary['expected_documents']}</td><td>{', '.join(map(str, summary['complete_years'])) or 'None'}</td><td>{summary['longest_consecutive_complete_years']}</td></tr>")
    parts.append("</table>")
    for issuer, summary in per_issuer.items():
        parts.append(f"<h2 id='{issuer}'>{html.escape(summary['legal_name'])}</h2><table><tr><th>Period</th><th>Source-QA status</th><th>Files and evidence</th></tr>")
        for row in rows:
            if row["issuer_id"] != issuer:
                continue
            result = latest.get(row["document_id"], {})
            links = []
            for field, label in [("local_path", "Original"), ("extracted_text_path", "Text")]:
                if result.get(field):
                    links.append(f"<a href='{html.escape(os.path.relpath(ROOT / result[field], data_root), quote=True)}'>{label}</a>")
            if result.get("source_url"):
                links.append(f"<a href='{html.escape(result['source_url'], quote=True)}'>Public source</a>")
            details = {"sha256": result.get("sha256"), "source_metadata": result.get("source_metadata", {}), "checks": result.get("checks", {})}
            parts.append(f"<tr id='{row['document_id']}'><td>{html.escape(row['period_label'])}</td><td>{row['status']}</td><td>{' · '.join(links)}<details><summary>Identity, period and preparation-basis evidence</summary><pre style='white-space:pre-wrap'>{html.escape(json.dumps(details, ensure_ascii=False, indent=2))}</pre></details></td></tr>")
        parts.append("</table>")
    parts.append("</html>")
    (data_root / "index.html").write_text("\n".join(parts), encoding="utf-8")
    return report


def capture_landings(panel: dict[str, Any], data_root: Path, issuer_filter: str | None, urls: list[str] | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for issuer in panel["issuers"]:
        if issuer_filter and issuer["issuer_id"] != issuer_filter:
            continue
        for url in urls or issuer.get("landing_urls", []):
            response = safe_fetch(url, retries=1)
            body = response.get("body", b"")
            digest = hashlib.sha256(body).hexdigest() if body else None
            suffix = ".json" if "json" in response.get("content_type", "") else ".html"
            target = data_root / "landing" / issuer["issuer_id"] / f"{digest or 'no-body'}{suffix}"
            if body:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
            out.append(
                {
                    "captured_at": now(),
                    "issuer_id": issuer["issuer_id"],
                    "url": url,
                    "final_url": response.get("final_url", url),
                    "http_status": response.get("http_status"),
                    "status": response.get("status", "ok") if response.get("http_status", 0) == 200 else response.get("status", "error"),
                    "bytes": len(body),
                    "sha256": digest,
                    "local_path": str(target.relative_to(ROOT)) if body else None,
                    "error": response.get("error"),
                }
            )
            previous = read_json(data_root / "source-access.json") if (data_root / "source-access.json").exists() else []
            write_json(data_root / "source-access.json", previous + [out[-1]])
            print(json.dumps({"index": url, "http_status": out[-1]["http_status"], "local_path": out[-1]["local_path"]}), flush=True)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--init-grid", action="store_true", help="write the expanded expected period grid")
    parser.add_argument("--import-local", action="store_true", help="import retained local sources")
    parser.add_argument("--revalidate-retained", action="store_true", help="re-run QA and hash checks on retained originals")
    parser.add_argument("--acquire", action="store_true", help="try public source candidates")
    parser.add_argument("--capture-landing", action="store_true", help="capture issuer landing-page evidence")
    parser.add_argument("--index-url", action="append", default=[], help="capture an exact public index URL; requires --issuer")
    parser.add_argument("--index-plan", type=Path, help="JSON list of issuer_id/url public indexes, captured sequentially")
    parser.add_argument("--resolved-only", action="store_true", help="acquire only document-specific resolved links")
    parser.add_argument("--report", action="store_true", help="write coverage.json and coverage.csv")
    parser.add_argument("--issuer", help="limit acquisition or landing capture to issuer_id")
    parser.add_argument("--year", type=int, help="limit acquisition to period year")
    parser.add_argument("--class", dest="report_class", help="limit acquisition to report class")
    parser.add_argument("--only", action="append", default=[], help="document_id to process; may be repeated")
    parser.add_argument("--limit", type=int, default=0, help="maximum network URL attempts; zero means no limit")
    return parser.parse_args()


def execute(args: argparse.Namespace) -> int:
    if args.index_url and not args.issuer:
        raise SystemExit("--index-url requires --issuer")
    panel = read_json(args.panel)
    panel["_panel_path"] = str(args.panel.relative_to(ROOT) if args.panel.is_absolute() and args.panel.is_relative_to(ROOT) else args.panel)
    data_root = args.data_root
    data_root.mkdir(parents=True, exist_ok=True)
    docs = expected_documents(panel)
    if args.init_grid:
        write_json(
            data_root / "expected-grid-v1.json",
            {
                "schema_version": "accdsl.financial_report_benchmark.expected_grid.v1",
                "generated_at": now(),
                "panel": str(args.panel.relative_to(ROOT) if args.panel.is_relative_to(ROOT) else args.panel),
                "documents": docs,
            },
        )
        print(f"wrote {len(docs)} expected documents to {data_root / 'expected-grid-v1.json'}")
    selected = [
        doc
        for doc in docs
        if (not args.issuer or doc["issuer_id"] == args.issuer)
        and (args.year is None or doc["period_year"] == args.year)
        and (not args.report_class or doc["report_class"] == args.report_class)
        and (not args.only or doc["document_id"] in set(args.only))
    ]
    results: list[dict[str, Any]] = []
    def record(result: dict[str, Any]) -> None:
        append_results(data_root, [result])
        results.append(result)
        print(json.dumps({"document_id": result["document_id"], "status": result["status"], "failure_reason": result.get("failure_reason"), "source_url": result.get("source_url")}, ensure_ascii=False), flush=True)
    if args.import_local:
        for doc in selected:
            if doc.get("local_path"):
                record(process_local(data_root, doc))
    if args.revalidate_retained:
        retained: dict[tuple[str, str], dict[str, Any]] = {}
        ledger = data_root / "acquisition-results.jsonl"
        for line in ledger.read_text(encoding="utf-8").splitlines() if ledger.exists() else []:
            prior = json.loads(line)
            if prior.get("local_path"):
                retained[(prior["document_id"], prior["local_path"])] = prior
        selected_by_id = {d["document_id"]: d for d in selected}
        for (doc_id, _), prior in retained.items():
            if doc_id in selected_by_id:
                record(process_retained(data_root, selected_by_id[doc_id], prior))
    if args.acquire:
        network_count = 0
        host_failures: dict[str, int] = {}
        existing = latest_results(data_root)
        for doc in selected:
            if network_count >= args.limit > 0:
                break
            if existing.get(doc["document_id"], {}).get("status") in SUCCESS_STATUSES:
                continue
            if not doc.get("source_candidates"):
                result = result_base(doc, None, "network")
                result.update({"status": "missing", "failure_reason": "no_source_candidate"})
                record(result)
                continue
            for url in doc["source_candidates"]:
                if network_count >= args.limit > 0:
                    break
                if args.resolved_only and url not in doc.get("source_metadata", {}):
                    continue
                host = urlsplit(url).netloc
                if host_failures.get(host, 0) >= 2:
                    continue
                result = process_url(data_root, doc, url)
                record(result)
                network_count += 1
                if result["status"] == "network_error" or result.get("http_status") in {403, 429}:
                    host_failures[host] = host_failures.get(host, 0) + 1
                    if host_failures[host] >= 2:
                        print(json.dumps({"host_paused": host, "reason": "two_access_failures_in_batch"}), flush=True)
                else:
                    host_failures[host] = 0
                if results[-1]["status"] == "acquired_verified":
                    break
    if results:
        counts: dict[str, int] = {}
        for result in results:
            counts[result["status"]] = counts.get(result["status"], 0) + 1
        print(json.dumps({"processed": len(results), "statuses": counts}, sort_keys=True))
    if args.capture_landing or args.index_url:
        landings = capture_landings(panel, data_root, args.issuer, args.index_url)
        print(json.dumps({"landing_pages": len(landings)}, sort_keys=True))
    if args.index_plan:
        indexes = read_json(args.index_plan)
        known = {i["issuer_id"] for i in panel["issuers"]}
        if len(indexes) > 30 or any(i["issuer_id"] not in known or urlsplit(i["url"]).scheme not in {"http", "https"} for i in indexes):
            raise SystemExit("Index plans require at most 30 public HTTP(S) URLs and known issuers")
        for index in indexes:
            capture_landings(panel, data_root, index["issuer_id"], [index["url"]])
    if args.report:
        report = build_report(panel, data_root)
        print(
            json.dumps(
                {
                    "expected_documents": report["expected_documents"],
                    "verified_documents": report["verified_documents"],
                    "acceptance": report["acceptance"],
                },
                sort_keys=True,
            )
        )
    if not any((args.init_grid, args.import_local, args.revalidate_retained, args.acquire, args.capture_landing, args.index_url, args.index_plan, args.report)):
        print("No action requested; use --init-grid, --import-local, --revalidate-retained, --acquire, --capture-landing or --report.")
    return 0


def main() -> int:
    args = parse_args()
    started = time.monotonic()
    manifest = {
        "started_at": now(), "status": "running", "argv": sys.argv,
        "cwd": str(Path.cwd()), "python": sys.executable,
        "python_version": platform.python_version(),
        "environment": os.environ.get("CONDA_DEFAULT_ENV", "system"),
        "compute": "CPU text extraction only; no accelerator framework imported",
        "random_seeds": "N/A: deterministic source acquisition and QA",
        "git_commit": None, "git_status": "unavailable: existing repository marker is not usable",
        "collector_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "panel_path": str(args.panel), "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(),
        "qa_version": QA_VERSION, "data_root": str(args.data_root),
        "plan": "docs/plans/accounting-benchmark-corpus.md",
        "result_note": "docs/plans/accounting-benchmark-corpus-results.md",
    }
    path = args.data_root / "runs" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}-{os.getpid()}.json"
    write_json(path, manifest)
    try:
        code = execute(args)
        manifest.update({"status": "completed", "exit_code": code})
        return code
    except BaseException as error:
        manifest.update({"status": "failed", "error": f"{type(error).__name__}: {error}"})
        raise
    finally:
        manifest.update({"finished_at": now(), "wall_seconds": round(time.monotonic() - started, 3)})
        for name in ["coverage.json", "acquisition-results.jsonl", "source-access.json", "resolved-sources.json"]:
            artifact = args.data_root / name
            if artifact.exists():
                manifest.setdefault("artifact_sha256", {})[name] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        write_json(path, manifest)


if __name__ == "__main__":
    sys.exit(main())
