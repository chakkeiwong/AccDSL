"""Preserve the completed bounded inquiry; performs no network retrieval."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def binding(path):
    path = Path(path)
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size}


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def source(identifier, url, status, names, disposition, **extra):
    return {"id": identifier, "requested_url": url,
            "effective_url": url, "http_status": status,
            "retrieval_date": "2026-10-18",
            "retrieval_timestamp": "Not instrumented; date from execution record",
            "files": [binding(OUT / "sources" / name) for name in names],
            "disposition": disposition, **extra}


sources = [
    source("ifrscommunity-sandbox", "https://ifrscommunity.com/knowledge-base/impairment-of-assets/", 403,
           ["ifrscommunity-impairment.html", "ifrscommunity.headers.txt"],
           "Cloudflare challenge; no technical content inspected", execution="sandbox"),
    source("ifrscommunity-trusted", "https://ifrscommunity.com/knowledge-base/impairment-of-assets/", 403,
           ["ifrscommunity-impairment-trusted.html", "ifrscommunity-trusted.headers.txt"],
           "Trusted retry also inaccessible; no unchanged-route retry justified", execution="trusted"),
    source("grantthornton-path", "https://www.grantthornton.global/en/insights/articles/ifrs-ias-36/ifrs-ias-36-reversing-impairment-losses/", 404,
           ["grantthornton-reversal.html", "grantthornton.headers.txt"],
           "Generic error page, not the requested article; no technical support", execution="trusted"),
    source("aasb136-compilation3", "https://www.aasb.gov.au/admin/file/content105/c9/AASB136_08-15_COMPdec22_01-23.pdf", 200,
           ["aasb136-dec2022.pdf", "aasb136-dec2022.txt", "aasb136.headers.txt"],
           "Inspected historical standard/example; zero-weight reversal unresolved",
           execution="trusted", title="AASB 136 Impairment of Assets",
           version="Compilation 3, 31 December 2022; F2023C00180, registered 9 February 2023",
           applicability="Cover: annual starts on/after 1 January 2023 and before 1 July 2026; not operative October 2026 authority",
           inspected_anchors=["Cover", "104–107, printed 20–21", "109–125, printed 21–23",
                              "Example 2, IE23A–IE31, printed 40–41", "Example 4, IE38–IE43 and Schedules 1–3, printed 43–45"],
           whole_document_read=False),
    source("google-discovery", "https://www.google.com/search?q=site%3Agrantthornton.global+IAS+36+reversing+impairment+losses", 200,
           ["search.html", "search.txt", "search.headers.txt"],
           "Extracted script/redirect shell; no usable technical discovery", execution="trusted"),
    source("bing-discovery", "https://www.bing.com/search?q=IAS+36+reversal+impairment+zero+carrying+amount+allocation+Grant+Thornton&format=rss", 200,
           ["bing.xml", "bing.headers.txt"],
           "Unrelated literary-language results; unusable for topic coverage or absence inference", execution="trusted"),
]
save("source-manifest.json", {
    "schema_version": 1, "question": "All eligible non-goodwill CGU carrying weights zero with positive reversal capacities",
    "sources": sources,
    "metadata_limits": "Effective URLs follow the retained execution summary; exact original shell quoting and percent encoding were not recovered. HTTP response headers are retained. No search result is technical support.",
    "source_reading": "data/accounting-master/zero-weight-cgu-source-20261018/source-reading.md",
    "verdict": "unresolved; no fallback, calculator, manuscript edit or promotion",
})

head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
save("run-manifest.json", {
    "schema_version": 1, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    "git_commit": head, "git_branch": branch,
    "working_tree": "Pre-existing changes preserved; no commit made by this work unit",
    "plan": binding(ROOT / "docs/plans/accounting-zero-weight-cgu-source-20261018.md"),
    "result": binding(OUT / "result.md"), "source_reading": binding(OUT / "source-reading.md"),
    "source_manifest": binding(OUT / "source-manifest.json"),
    "environment": {"python": platform.python_version(), "system": platform.system(),
                    "tools": "curl, pdftotext -layout, Python standard library, shell",
                    "conda_env": "N/A — shell/documentary inquiry, no framework environment",
                    "cpu_gpu": "CPU-only document/network tools; no ML imports or GPU command; device hiding N/A"},
    "random_seeds": "N/A — deterministic documentary work", "data_version": "Source version and hashes in source-manifest.json",
    "wall_time": "Unavailable: original task-wide timing was not instrumented; no retrospective estimate",
    "commands": {
        "retrieval_form_recorded_in_handoff": "curl --location --connect-timeout 15 --max-time 45 --max-filesize 15000000 --silent --show-error --dump-header <headers> --output <file> --write-out 'status=%{http_code} bytes=%{size_download} url=%{url_effective}\\n' <URL>",
        "discovery_form": "curl with the same bounds and --get --data-urlencode; original exact shell invocation unavailable",
        "pdf_extraction": "pdftotext -layout data/accounting-master/zero-weight-cgu-source-20261018/sources/aasb136-dec2022.pdf data/accounting-master/zero-weight-cgu-source-20261018/sources/aasb136-dec2022.txt",
        "manifest_completion": "python3 data/accounting-master/zero-weight-cgu-source-20261018/record_manifests.py",
        "completion_scope": "Manifest completion performs no retrieval, re-extraction, numerical campaign or manuscript change"},
    "output_paths": [str(OUT.relative_to(ROOT))],
    "promotion": "None; source-dependent allocation remains unsupported",
    "continuation": "Continue independent ordered manuscript reading from physical 62; no global continuation veto",
    "recording_script": binding(Path(__file__)),
})

checked = 0
for record in sources:
    for item in record["files"]:
        assert binding(ROOT / item["path"]) == item
        checked += 1
print(json.dumps({"source_records": len(sources), "verified_source_file_bindings": checked,
                  "git_commit": head, "verdict": "unresolved; documentary records complete"}))
