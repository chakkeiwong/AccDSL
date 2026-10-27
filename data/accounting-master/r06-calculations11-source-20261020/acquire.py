"""Bounded official documentary acquisitions, preserving every attempt receipt."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

U=Path(__file__).resolve().parent
S=U/"sources"
SOURCES={
    "01-history":"https://specifications.xbrl.org/release-history-calculations-1-1-spec.html",
    "02-calc11":"https://www.xbrl.org/Specification/calculation-1.1/REC-2023-02-22%2Bcorrected-errata-2024-02-14/calculation-1.1-REC-2023-02-22%2Bcorrected-errata-2024-02-14.html",
    "03-oim":"https://www.xbrl.org/Specification/oim/REC-2021-10-13/oim-REC-2021-10-13.html",
    "04-xbrlxml":"https://www.xbrl.org/Specification/xbrl-xml/REC-2021-10-13/xbrl-xml-REC-2021-10-13.html",
    "05-schema":"https://www.xbrl.org/2023/calculation-1.1.xsd",
    "06-status":"https://specifications.xbrl.org/spec-group-index-calculations-2.html",
}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("source",choices=SOURCES)
    parser.add_argument("--trusted",action="store_true")
    args=parser.parse_args()
    name=args.source+("-trusted" if args.trusted else "")
    body,headers,receipt=[S/(name+suffix) for suffix in (".body",".headers",".receipt.json")]
    assert not any(p.exists() for p in (body,headers,receipt)),"attempt already retained"
    command=["curl","--location","--silent","--show-error","--fail-with-body",
             "--connect-timeout","15","--max-time","45","--max-filesize","2097152",
             "--dump-header",str(headers),"--output",str(body),"--write-out","%{json}",SOURCES[args.source]]
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    result=subprocess.run(command,capture_output=True,text=True,timeout=55)
    try:
        metrics=json.loads(result.stdout)
    except json.JSONDecodeError:
        metrics={"stdout":result.stdout}
    record={"source":args.source,"url":SOURCES[args.source],"command":command,
            "trusted_retry":args.trusted,"started_utc":started,"elapsed_seconds":time.monotonic()-start,
            "exit_code":result.returncode,"metrics":metrics,"stderr":result.stderr,
            "files":{str(p.relative_to(U)):{"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                     for p in (body,headers) if p.exists()}}
    with receipt.open("x") as f:
        json.dump(record,f,indent=2);f.write("\n")
    print(json.dumps({"source":args.source,"exit_code":result.returncode,"http_code":metrics.get("http_code"),
                      "body_bytes":body.stat().st_size if body.exists() else 0,"receipt":str(receipt)}))
    raise SystemExit(result.returncode)


if __name__=="__main__":
    main()
