#!/usr/bin/env python3
"""Bounded local proposal builds/renders with logs kept outside tool output."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
PROPOSALS = ROOT / "docs/design/proposal"
EVIDENCE = ROOT / "data/accounting-master"
STEM = "accounting-product-proposal"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within(value, base):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(base.resolve()) or path == base.resolve():
        raise ValueError(f"Path must be below {base.relative_to(ROOT)}")
    return path


def save(path, value):
    # Resolve existing symlinks before writing, including a pre-existing result.
    within(str(path), EVIDENCE)
    path.write_text(json.dumps(value, indent=2) + "\n")


def pdf_pages(pdf):
    result = subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True,
        timeout=15, check=True,
    )
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.M)
    if not match:
        raise ValueError("pdfinfo did not report a page count")
    return int(match.group(1))


def page_numbers(value, maximum):
    pages = set()
    for part in value.split(","):
        match = re.fullmatch(r"(\d+)(?:-(\d+))?", part.strip())
        if not match:
            raise ValueError("Use page numbers/ranges such as 68-70,221")
        first = int(match[1])
        last = int(match[2] or match[1])
        if not 1 <= first <= last <= maximum:
            raise ValueError("Requested pages are outside the PDF")
        if last - first >= 20:
            raise ValueError("Render at most 20 pages per invocation")
        pages.update(range(first, last + 1))
    if not 1 <= len(pages) <= 20:
        raise ValueError("Render between 1 and 20 pages per invocation")
    return sorted(pages)


def build(args, candidate, evidence):
    command = [
        "latexmk", "-lualatex", "-interaction=nonstopmode", "-halt-on-error",
        "-file-line-error", "-recorder", STEM + ".tex",
    ]
    if args.force:
        command.insert(2, "-g")
    stdout = within(str(evidence / "build-stdout.log"), EVIDENCE)
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    with stdout.open("w") as output:
        try:
            result = subprocess.run(
                command, cwd=candidate, stdout=output, stderr=subprocess.STDOUT,
                timeout=args.timeout, check=False,
            )
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
    pdf = candidate / (STEM + ".pdf")
    log = candidate / (STEM + ".log")
    diagnostics = []
    if log.exists():
        diagnostics = [
            line[:240] for line in log.read_text(errors="replace").splitlines()
            if re.search(r"(?:LaTeX|Package natbib) Warning:|Overfull \\hbox|Undefined control sequence|! LaTeX Error", line)
        ]
    record = {
        "command": command, "cwd": str(candidate.relative_to(ROOT)),
        "started_utc": started, "wall_seconds": time.monotonic() - timer,
        "exit_code": code, "stdout_log": str(stdout.relative_to(ROOT)),
        "stdout_sha256": digest(stdout), "diagnostics": diagnostics,
        "pdf_sha256": digest(pdf) if code == 0 and pdf.exists() else None,
        "page_count": pdf_pages(pdf) if code == 0 and pdf.exists() else None,
    }
    save(evidence / "build-run.json", record)
    print(json.dumps({k: record[k] for k in (
        "exit_code", "wall_seconds", "page_count", "pdf_sha256", "stdout_log"
    )} | {"diagnostic_count": len(diagnostics)}))
    return code


def render(args, candidate, evidence):
    pdf = within(str(candidate / (STEM + ".pdf")), PROPOSALS)
    pages = page_numbers(args.pages, pdf_pages(pdf))
    out = within(str(evidence / "rendered"), EVIDENCE)
    out.mkdir(parents=True, exist_ok=True)
    manifest = evidence / "render-manifest.json"
    record = {"pdf": str(pdf.relative_to(ROOT)), "pdf_sha256": digest(pdf), "pages": {}}
    if manifest.exists():
        prior = json.loads(manifest.read_text())
        if prior["pdf_sha256"] != record["pdf_sha256"]:
            raise ValueError("Use a new evidence directory after the PDF changes")
        record["pages"] = prior["pages"]
    for page in pages:
        prefix = within(str(out / f"page-{page:04d}"), EVIDENCE)
        png = within(str(prefix.with_suffix(".png")), EVIDENCE)
        result = subprocess.run(
            ["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(args.dpi),
             "-png", "-singlefile", str(pdf), str(prefix)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        if result.returncode:
            raise ValueError(f"Rendering page {page} failed: {result.stderr[:500]}")
        record["pages"][str(page)] = {
            "path": str(png.relative_to(ROOT)), "sha256": digest(png), "dpi": args.dpi,
        }
    save(manifest, record)
    print(json.dumps({"pdf_sha256": record["pdf_sha256"], "rendered_pages": pages,
                      "manifest": str(manifest.relative_to(ROOT))}))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in ("build", "render"):
        command = sub.add_parser(name)
        command.add_argument("--candidate", required=True)
        command.add_argument("--evidence", required=True)
        if name == "build":
            command.add_argument("--timeout", type=int, default=180)
            command.add_argument("--force", action="store_true",
                                 help="Retry after a recorded latexmk failure")
        else:
            command.add_argument("--pages", required=True)
            command.add_argument("--dpi", type=int, choices=range(72, 161), default=110)
    args = parser.parse_args()
    candidate = within(args.candidate, PROPOSALS)
    evidence = within(args.evidence, EVIDENCE)
    if not candidate.is_dir() or not candidate.name.startswith("manuscript-"):
        raise ValueError("Choose a distinct manuscript-* candidate directory")
    if not (candidate / (STEM + ".tex")).is_file():
        raise ValueError("Candidate main source is missing")
    if args.operation == "build" and not 1 <= args.timeout <= 600:
        raise ValueError("Build timeout must be between 1 and 600 seconds")
    evidence.mkdir(parents=True, exist_ok=True)
    return {"build": build, "render": render}[args.operation](args, candidate, evidence)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error)[:700]}), file=sys.stderr)
        sys.exit(2)
