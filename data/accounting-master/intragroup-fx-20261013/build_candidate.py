"""Build a protected candidate with the checked intragroup FX example."""
import datetime
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=ROOT/'docs/design/proposal/manuscript-pingan-leases-20261013'
CAND=ROOT/'docs/design/proposal/manuscript-intragroup-fx-20261013'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n')


def expected_text(rel):
    t=(BASE/rel).read_text()
    if rel=='accounting-product-proposal.tex':
        assert t.count('Version 2.51 (proposal candidate)')==1
        t=t.replace('Version 2.51 (proposal candidate)','Version 2.52 (proposal candidate)')
    elif rel=='sections/groups-fx-methods.tex':
        t+=(OUT/'fx-addition.tex').read_text()
    return t


def main():
    assert not CAND.exists() and not (OUT/'completion.json').exists()
    checked=json.loads((OUT/'source-checks.json').read_text());assert checked['passed']==49 and not checked['failed']
    digest='bc0a75b20bef0d6e045cca2461b06d30cbba6d028930e88bc1afcd6831fa1961'
    assert sha(BASE/'accounting-product-proposal.pdf')==digest
    hashes={str(p.relative_to(BASE)):sha(p) for p in sorted(BASE.rglob('*')) if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    for rel in hashes:
        p=CAND/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected_text(rel))
    save('candidate.json',{'baseline':str(BASE.relative_to(ROOT)),'baseline_pdf_sha256':digest,'source_hashes':hashes,
        'candidate':str(CAND.relative_to(ROOT)),'new_passage_sha256':sha(OUT/'fx-addition.tex'),'readiness':'not_ready'})
    command=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
    overrides={'TEXMFVAR':'/tmp/accdsl-texmfvar','TEXMFCACHE':'/tmp/accdsl-texmfvar','CUDA_VISIBLE_DEVICES':'-1'}
    env=os.environ.copy();env.update(overrides);start=time.monotonic()
    with (OUT/'build-stdout.log').open('w') as log:
        r=subprocess.run(command,cwd=CAND,env=env,stdout=log,stderr=subprocess.STDOUT)
    record={'command':command,'cwd':str(CAND.relative_to(ROOT)),'environment_overrides':overrides,
        'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'exit_code':r.returncode}
    save('build-run.json',record);print(json.dumps(record));raise SystemExit(r.returncode)


if __name__=='__main__':
    main()
