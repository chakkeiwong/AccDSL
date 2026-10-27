#!/usr/bin/env python3
"""Verify and bind the exact PyPI sdist inspection; no import or install."""

import hashlib
import json
import re
import subprocess
import tarfile
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = OUT / "sources"
PLAN = ROOT / "docs/plans/accounting-easyocr-python-bidi-20261011.md"
EASY = ROOT / "data/accounting-master/easyocr-assets-20261010/sources"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2) + "\n")


def main():
    start = time.monotonic()
    checks = []

    def check(name, result):
        checks.append({"check": name, "passed": bool(result)})

    index = json.loads((SRC / "pypi-index.json").read_text())
    archive = SRC / "python_bidi-0.6.11.tar.gz"
    release = next(x for x in index["urls"] if x["filename"] == archive.name)
    check("PyPI package and candidate version", index["info"]["name"] == "python-bidi" and index["info"]["version"] == "0.6.11")
    check("candidate is non-yanked stable sdist", release["packagetype"] == "sdist" and not release["yanked"])
    check("sdist size and digest", archive.stat().st_size == release["size"] == 57647 and sha(archive) == release["digests"]["sha256"])
    check("Python requirement disclosed", index["info"]["requires_python"] == ">=3.9")
    check("PyPI license fields are null", index["info"]["license"] is None and index["info"].get("license_expression") is None)
    check("trusted PyPI response retained", all(json.loads((SRC / x).read_text())["status"] == 200 for x in ("pypi-index.json.receipt.json", archive.name + ".receipt.json")))

    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        check("bounded archive members", len(members) == 38 and all(x.isfile() and x.size < 500000 for x in members))

        def body(name):
            return tar.extractfile("python_bidi-0.6.11/" + name).read().decode("utf-8")

        meta = body("pyproject.toml")
        init = body("bidi/__init__.py")
        wrapper = body("bidi/wrapper.py")
        readme = body("README.rst")
        cargo = body("Cargo.toml")
        third = body("LICENSE-THIRD-PARTY.yml")
        lock = tomllib.loads(body("Cargo.lock"))
        lesser = body("COPYING.LESSER")
        gpl = body("COPYING")
        check("sdist metadata identity", 'name = "python-bidi"' in meta and 'version = "0.6.11"' in meta)
        check("LGPL project classifier", "GNU Library or Lesser General Public License (LGPL)" in meta)
        check("LGPLv3-or-later source header", "GNU Lesser General Public License" in init and "either version 3" in init and "any later version" in init)
        check("included LGPLv3/GPLv3 bodies", "Version 3, 29 June 2007" in lesser and "LESSER GENERAL PUBLIC LICENSE" in lesser and "GNU GENERAL PUBLIC LICENSE" in gpl)
        check("top-level Rust wrapper", "from .wrapper import get_base_level, get_display" in init and "from .bidi import get_base_level_inner, get_display_inner" in wrapper)
        check("one-argument call shape present", "str_or_bytes: StrOrBytes" in wrapper and "encoding: str =" in wrapper)
        check("README distinguishes two implementations", "from bidi.algorithm import get_display" in readme and "from bidi import get_display" in readme)
        check("declared Rust dependencies", 'pyo3 = ' in cargo and 'unicode-bidi = ' in cargo)
        check("third-party terms inventory present", "package_name: pyo3" in third and "package_name: unicode-bidi" in third)
        notice_rows = dict(re.findall(r"package_name: ([^\n]+)\n\s+package_version: ([^\n]+)", third))
        locked = {item["name"]: item["version"] for item in lock["package"]}
        mismatches = {name: (version, locked.get(name)) for name, version in notice_rows.items() if locked.get(name) != version}
        check("bundled notice/lock discrepancy reproduced", len(notice_rows) == 19 and len(mismatches) == 13)
        check("named transitive version mismatches", mismatches.get("pyo3") == ("0.22.1", "0.29.0") and mismatches.get("unicode-bidi") == ("0.3.15", "0.3.18"))

    req = (EASY / "requirements.txt").read_text()
    code = (EASY / "easyocr__easyocr.py").read_text()
    check("EasyOCR dependency unpinned", "python-bidi" in req.splitlines() and not any(x.startswith("python-bidi==") for x in req.splitlines()))
    check("EasyOCR selects top-level API", "from bidi import get_display" in code and "get_display(item[1])" in code)
    for name in ("result.md", "author-review.md", "next-source-frontier.md"):
        check(name + " retained", (OUT / name).is_file())

    if any(not x["passed"] for x in checks):
        write("checks.json", {"checks": checks, "passed": sum(x["passed"] for x in checks), "failed": sum(not x["passed"] for x in checks)})
        raise SystemExit(1)

    files = [p for p in OUT.rglob("*") if p.is_file() and p.name not in {"checks.json", "run-manifest.json", "completion.json"}]
    files += [PLAN, EASY / "requirements.txt", EASY / "easyocr__easyocr.py"]
    manifest = {
        "recorded_at": "2026-10-11",
        "unit": "EasyOCR unpinned python-bidi source and licence inspection",
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "git_state": "Unrelated work preserved; read-only .git prevents commit; no retry.",
        "plan": str(PLAN.relative_to(ROOT)),
        "result": str((OUT / "result.md").relative_to(ROOT)),
        "candidate": {"package": "python-bidi", "version": "0.6.11", "status": "source_inspection_only", "sdist_sha256": sha(archive)},
        "data_version": "PyPI JSON and 0.6.11 sdist retained 11 October 2026; EasyOCR 1.7.2 comparator",
        "commands": ["python3 data/accounting-master/easyocr-python-bidi-20261011/fetch.py pypi-index.json https://pypi.org/pypi/python-bidi/json", "python3 data/accounting-master/easyocr-python-bidi-20261011/fetch.py python_bidi-0.6.11.tar.gz <exact PyPI sdist URL in receipt>", "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/easyocr-python-bidi-20261011/closeout.py"],
        "environment": {"python": "Python 3.11", "cpu_gpu": "CPU-only source inspection; GPU intentionally hidden for closeout", "random_seeds": "N/A; deterministic"},
        "wall_time": {"metadata_request_seconds": json.loads((SRC / "pypi-index.json.receipt.json").read_text())["wall_seconds"], "sdist_request_seconds": json.loads((SRC / (archive.name + ".receipt.json")).read_text())["wall_seconds"], "closeout_seconds": time.monotonic() - start},
        "checks": len(checks),
        "artifact_hashes": {str(p.relative_to(ROOT)): sha(p) for p in files},
        "readiness": "not_ready",
        "runtime_compatibility": "not_checked",
        "legal_distribution_clearance": "not_checked",
    }
    write("run-manifest.json", manifest)
    write("checks.json", {"checks": checks, "passed": len(checks), "failed": 0, "run_manifest_sha256": sha(OUT / "run-manifest.json")})
    write("completion.json", {"status": "closed_bounded_source_inspection", "checks": len(checks), "failed": 0, "run_manifest_sha256": sha(OUT / "run-manifest.json"), "readiness": "not_ready"})
    print(json.dumps({"passed": len(checks), "failed": 0, "release": "python-bidi 0.6.11"}))


if __name__ == "__main__":
    main()
