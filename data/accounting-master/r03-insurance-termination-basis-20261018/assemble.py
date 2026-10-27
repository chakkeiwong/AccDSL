"""One-time provenance assembly from the retained public request and readings."""
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]


def write_new(path, value):
    if path.exists():
        assert json.loads(path.read_text()) == value, "partial recovery must not replace recorded bytes"
        return
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, value):
        if not self.skip and value.strip():
            self.parts.append(value.strip())


parser = Text()
parser.feed((UNIT / "iasb-index.html").read_text())
normalized = "\n".join(parser.parts)+"\n"
if (UNIT / "iasb-index.txt").exists():
    assert (UNIT / "iasb-index.txt").read_text() == normalized
else:
    with (UNIT / "iasb-index.txt").open("x", encoding="utf-8") as handle:
        handle.write(normalized)

command = ["curl", "--location", "--max-time", "35", "--connect-timeout", "12",
           "--max-filesize", "12000000", "--silent", "--show-error", "--dump-header",
           str((UNIT / "iasb-index.headers").relative_to(ROOT)), "--output",
           str((UNIT / "iasb-index.html").relative_to(ROOT)), "--write-out",
           "http_code=%{http_code} effective_url=%{url_effective} bytes=%{size_download} seconds=%{time_total}",
           "https://www.aasb.gov.au/research-resources/iasb-support-materials/"]
recorded = (json.loads((UNIT / "acquisitions.json").read_text())[0]["metadata_recorded_utc"]
            if (UNIT / "acquisitions.json").exists() else datetime.now(timezone.utc).isoformat())
write_new(UNIT / "acquisitions.json", [{
    "id": "IASB-support-index", "source_url": command[-1],
    "navigation_source": "data/accounting-master/insurance-termination-source-20261017/aasb17-edition.html",
    "navigation_anchor": "IASB Basis for Conclusions; IASB Illustrative Examples",
    "command": command, "curl_exit_code": 0, "http_status": 200,
    "effective_url": "https://www.aasb.gov.au/international-visitor/", "download_bytes": 21635,
    "curl_wall_seconds": 3.174138, "metadata_provenance": "actual curl --write-out returned to the supervising tool call",
    "source_role": "access_boundary", "disposition": "Explicit Australia-only restriction; no Basis/Examples acquired; no bypass or retry",
    "artifacts": [binding(UNIT / name) for name in ("iasb-index.headers", "iasb-index.html", "iasb-index.txt")],
    "normalization_command": "CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 data/accounting-master/r03-insurance-termination-basis-20261018/assemble.py",
    "metadata_recorded_utc": recorded,
}])

spans = []
source = ROOT / "docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt"
for name, path, first, last, anchor, role in [
    ("standard-88-to-91", source, 56581, 56626, "     91", "primary historical Standard; original identities and termination rules"),
    ("standard-B134-to-B136", source, 59423, 59459, "     B135", "primary historical Standard; holdings change and frozen reclassification assumptions"),
]:
    lines = path.read_text().splitlines(keepends=True)
    text = "".join(lines[first-1:last])
    assert anchor in text
    spans.append({"id": name, "path": str(path.relative_to(ROOT)), "first_line": first,
                  "last_line": last, "anchor": anchor, "sha256": hashlib.sha256(text.encode()).hexdigest(),
                  "role": role})
lines = (UNIT / "iasb-index.txt").read_text().splitlines(keepends=True)
first = next(i+1 for i, line in enumerate(lines) if "This content is restricted to users in Australia only." in line)
text = lines[first-1]
spans.append({"id": "explicit-access-restriction", "path": str((UNIT / "iasb-index.txt").relative_to(ROOT)),
              "first_line": first, "last_line": first, "anchor": "restricted to users in Australia only",
              "sha256": hashlib.sha256(text.encode()).hexdigest(), "role": "access boundary, no technical accounting authority"})
write_new(UNIT / "source-review.json", {
    "editions": "EU2023/1803 historical original; live AASB access-boundary page acquired18 October2026 local date",
    "inspected_spans": spans, "basis_full_text": "not acquired; linked index access restricted",
    "combined_91_B135_disposition": "not established; preserve previous scope exclusion",
    "rule_admitted": False, "whole_rows_closed": 0,
    "not_concluded": ["absence of relevant IASB Basis guidance", "current-law treatment", "a new calculator", "general literature completeness"],
})
print(json.dumps({"acquisitions": 1, "inspected_spans": len(spans), "rule_admitted": False}))
