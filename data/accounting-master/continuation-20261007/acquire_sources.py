#!/usr/bin/env python3
"""Bounded source acquisition for the proposal case; no product execution.

Retains responses and receipts. Re-running a stage reuses checked saved bytes;
it does not silently overwrite a response. A network failure is recorded and
must be inspected, including trusted rerun if the sandbox caused it.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/design/cases/apple/continuation-20261007"
OPS = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retrieve(key, url, suffix, purpose, discovery=None):
    directory = OUT / "sources"
    directory.mkdir(parents=True, exist_ok=True)
    receipt = directory / (key + ".receipt.json")
    path = directory / (key + suffix)
    if receipt.exists():
        old = json.loads(receipt.read_text())
        assert old["url"] == url
        if old["exit_code"] == 0 and old["http_status"] == 200:
            assert digest(path) == old["sha256"]
            return old
        raise RuntimeError(f"Failed attempt retained: {receipt}; use a distinct attempt key")
    if path.exists():
        raise RuntimeError(f"Unreceipted output exists: {path}")
    headers = directory / (key + ".headers")
    command = ["curl", "--http1.1", "--location", "--silent", "--show-error", "--connect-timeout", "10",
               "--max-time", "30", "--max-filesize", "30000000", "--dump-header", str(headers),
               "--output", str(path), "--write-out", "%{http_code}\n%{url_effective}\n%{content_type}", url]
    start = datetime.now(timezone.utc)
    result = subprocess.run(command, capture_output=True, text=True, timeout=40)
    end = datetime.now(timezone.utc)
    fields = result.stdout.splitlines()
    record = {"url": url, "purpose": purpose, "discovered_from": discovery,
              "retrieved_at": end.isoformat(), "wall_seconds": (end-start).total_seconds(),
              "exit_code": result.returncode, "http_status": int(fields[0]) if fields and fields[0].isdigit() else None,
              "final_url": fields[1] if len(fields)>1 else None, "content_type": fields[2] if len(fields)>2 else None,
              "path": str(path.relative_to(ROOT)), "sha256": digest(path) if path.exists() else None,
              "headers": str(headers.relative_to(ROOT)), "error": result.stderr.strip() or None,
              "command": command, "historical_byte_availability": "not established by current retrieval"}
    receipt.write_text(json.dumps(record, indent=2)+"\n")
    print(key, result.returncode, record["http_status"], path.stat().st_size if path.exists() else 0, flush=True)
    return record


def feeds(years, attempt):
    for year in years:
        params = dict(exchange="CIK", symbol="0000320193", filingTypeList="8-K,S-3,S-3ASR,10-K,10-Q",
                      formGroupIdList="", excludeNoDocuments="true", includeHtmlDocument="true",
                      year=year, pageSize=100, pageNumber=0, LanguageId=1)
        url = "https://investor.apple.com/feed/SECFiling.svc/GetEdgarFilingList?" + urlencode(params)
        record = retrieve(f"issuer-{year}-{attempt}", url, ".json", "Resolve annual/interim incorporated filing targets")
        if record["exit_code"] != 0:
            raise RuntimeError("Network error; inspect receipt before more requests")
        if record["http_status"] == 200:
            rows = json.loads((ROOT / record["path"]).read_text())["GetEdgarFilingListResult"]
            assert len(rows) < 100, "Potential truncated feed: pagination required"


def requested(queue_path, attempt):
    queue = json.loads(Path(queue_path).read_text())
    for entry in queue:
        r = retrieve(entry["key"] + "-" + attempt, entry["url"], entry["suffix"],
                     entry["purpose"], entry["discovered_from"])
        if r["exit_code"] in (5, 6, 7):
            raise RuntimeError("Network error; inspect receipt before more requests")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["feeds", "queue"])
    parser.add_argument("values", nargs="+")
    parser.add_argument("--attempt", default="v1")
    args = parser.parse_args()
    if args.mode == "feeds":
        feeds([int(s) for s in args.values], args.attempt)
    else:
        assert len(args.values) == 1
        requested(args.values[0], args.attempt)
