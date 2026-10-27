"""One fixed, bounded HTTPS source batch; records each receipt immediately."""
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
REQUESTS = [
    ("01-environment", "https://raw.githubusercontent.com/microsoft/table-transformer/16d124f616109746b7785f03085100f1f6247575/environment.yml"),
    ("02-bbox", "https://raw.githubusercontent.com/kensho-technologies/grits/8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1/grits/bbox.py"),
    ("03-project", "https://raw.githubusercontent.com/kensho-technologies/grits/8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1/pyproject.toml"),
    ("04-rect-docs", "https://pymupdf.readthedocs.io/en/latest/rect.html"),
]


def main():
    assert (UNIT / "protection.json").is_file(), "prepare first"
    for stem, _ in REQUESTS:
        assert not list((UNIT / "sources").glob(stem + ".*")), "one-time acquisition"
    for stem, url in REQUESTS:
        body = UNIT / "sources" / (stem + ".body")
        header = UNIT / "sources" / (stem + ".headers")
        command = ["curl", "--silent", "--show-error", "--location", "--connect-timeout", "10",
            "--max-time", "35", "--max-filesize", "2097152", "--proto", "=https",
            "--proto-redir", "=https", "--dump-header", str(header.relative_to(ROOT)),
            "--output", str(body.relative_to(ROOT)), "--write-out", "%{json}\n", url]
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        receipt = json.loads(result.stdout)
        with (UNIT / "sources" / (stem + ".receipt.json")).open("x") as handle:
            json.dump(receipt, handle, indent=2); handle.write("\n")
        with (UNIT / "sources" / (stem + ".invocation.json")).open("x") as handle:
            json.dump({"argv": command, "started_utc": started, "returncode": result.returncode,
                       "stderr": result.stderr}, handle, indent=2); handle.write("\n")
        print(json.dumps({"source": stem, "status": receipt["http_code"], "exitcode": result.returncode,
                          "bytes": receipt["size_download"], "seconds": receipt["time_total"]}), flush=True)


if __name__ == "__main__":
    main()
