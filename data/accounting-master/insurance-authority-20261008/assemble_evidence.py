"""Record bounded acquisitions and render the final, already-built candidate."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


attempts = ["asbe25-sandbox", "asbe25-trusted", "asbe25-http", "asbe25-search",
            "asbe25-search-http", "asbe25-implementation2025", "asbe25-issuance-search",
            "asbe25-implementation2025-https", "asbe25-release-qa"]
requests = []
for name in attempts:
    prefix = OUT / "sources" / name
    transfer_path = prefix.with_suffix(".transfer.json")
    transfer = json.loads(transfer_path.read_text())
    files = {str(p.relative_to(ROOT)): sha(p) for suffix in [".headers", ".body", ".transfer.json", ".stderr"]
             if (p := prefix.with_suffix(suffix)).exists()}
    command = ["curl", "--location", "--connect-timeout", "10", "--max-time", "30", "--silent", "--show-error",
               "--dump-header", str(prefix.with_suffix(".headers").relative_to(ROOT)),
               "--output", str(prefix.with_suffix(".body").relative_to(ROOT)), "--write-out", "%{json}"]
    url = transfer.get("url") or transfer["url_effective"]
    if "search" in name:
        word = "财会〔2020〕20号" if "issuance" in name else "保险合同"
        command.extend(["--get", "--data-urlencode", "channelid=289898", "--data-urlencode", "searchword=" + word,
                        "--data-urlencode", "perpage=50", url.split("?", 1)[0]])
    else:
        command.append(url)
    shell = shlex.join(command) + " > " + shlex.quote(str(transfer_path.relative_to(ROOT))) + " 2> " + shlex.quote(str(prefix.with_suffix(".stderr").relative_to(ROOT)))
    row = {"attempt": name, "requested_url": url, "effective_url": transfer.get("url_effective"),
           "execution": "sandbox" if name.endswith("sandbox") else "trusted",
           "exit_code": transfer.get("exitcode"), "http_code": transfer.get("http_code"),
           "transfer_seconds": transfer.get("time_total"), "received_bytes": transfer.get("size_download"),
           "transfer_file_written_at": datetime.fromtimestamp(transfer_path.stat().st_mtime, timezone.utc).isoformat(),
           "timestamp_basis": "Transfer file mtime; start time and approval latency not separately measured",
           "command": shell, "files": files,
           "disposition": "retained official text/index; inspect before supporting claims" if transfer.get("http_code") == 200 else "failed route; not source support"}
    requests.append(row)
unique = {r["requested_url"] for r in requests}
assert len(unique) <= 8
assert all(sum(r["requested_url"] == u for r in requests) <= 2 for u in unique)
save("acquisition-receipts.json", {"recorded_at": datetime.now(timezone.utc).isoformat(), "distinct_requested_urls": len(unique),
                                 "attempts": len(requests), "requests": requests,
                                 "limits": "Eight distinct URLs; at most two attempts per exact route; 30-second total timeout each",
                                 "claim_limit": "Article 120 inspected; entity adoption and later amendments remain unverified"})

candidate = ROOT / "docs/design/proposal/manuscript-insurance-20261008"
pdf = candidate / "accounting-product-proposal.pdf"
digest = sha(pdf)
document = fitz.open(pdf)
pages = {1, 5, 6, 85, 86, 87, 88, 89, 90, 91, 92, 93}
for n, page in enumerate(document, 1):
    text = " ".join(page.get_text().split())
    if "ASBE 25 premium" in text:
        pages.update([n - 1, n, n + 1])
    if "BIBLIOGRAPHY" in text or text.startswith("Bibliography"):
        pages.add(n)
pages = sorted(n for n in pages if 1 <= n <= len(document))
render = OUT / "render-final"
render.mkdir(exist_ok=False)
rendered = {}
for n in pages:
    target = render / f"page-{n:03d}.png"
    document[n - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(target)
    rendered[str(n)] = {"path": str(target.relative_to(ROOT)), "sha256": sha(target)}
assert digest == sha(pdf)
save("build-receipt.json", {"recorded_at": datetime.now(timezone.utc).isoformat(),
                          "command": "latexmk -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex",
                          "cwd": str(candidate.relative_to(ROOT)), "execution": "trusted existing font cache",
                          "exit_code": 0, "log": "data/accounting-master/insurance-authority-20261008/build.log",
                          "log_sha256": sha(OUT / "build.log"), "pdf": str(pdf.relative_to(ROOT)),
                          "pdf_sha256": digest, "pages": len(document),
                          "elapsed_time": "Not separately instrumented; unit elapsed time is in run-manifest.json"})
save("render-manifest.json", {"recorded_at": datetime.now(timezone.utc).isoformat(),
                            "pdf": str(pdf.relative_to(ROOT)), "pdf_sha256_before": digest,
                            "pdf_sha256_after": sha(pdf), "pages": len(document), "page_numbers": pages,
                            "scale": 1.5, "rendered_pages": rendered,
                            "inspection_status": "Rendering complete; author inspection recorded separately"})
print(json.dumps({"requests": len(requests), "distinct_urls": len(unique), "pdf_sha256": digest,
                  "pages": len(document), "rendered_pages": pages}))
