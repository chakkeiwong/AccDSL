"""Retrieve inventory-listed small model text, never model weights."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    records=[]
    selections={'heron':['README.md','config.json','preprocessor_config.json'],
                'tableformer':['README.md','config.json','model_artifacts/tableformer/accurate/tm_config.json','model_artifacts/tableformer/fast/tm_config.json']}
    for label,names in selections.items():
        metadata=json.loads((OUT/f'sources/{label}-metadata.json').read_text())
        siblings={x['rfilename']:x for x in metadata['siblings']}
        for name in names:
            meta=siblings[name];assert 'lfs' not in meta and meta['size']<1048576
            assert name.endswith(('.md','.json'))
            path=OUT/'sources'/f'{label}__{name.replace("/","__")}';assert not path.exists()
            url=f'https://huggingface.co/{metadata["id"]}/resolve/{metadata["sha"]}/{name}'
            start,tick=datetime.now(timezone.utc).isoformat(),time.monotonic()
            args=['curl','--location','--fail-with-body','--max-time','45','--max-filesize','1048576','--silent','--show-error','--dump-header',str(path)+'.headers','--output',str(path),'--write-out','%{http_code} %{size_download} %{time_total}',url]
            proc=subprocess.run(args,text=True,capture_output=True,timeout=50)
            raw=path.read_bytes() if path.exists() else b''
            blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            r=dict(model=label,repo=metadata['id'],commit=metadata['sha'],filename=name,url=url,path=str(path.relative_to(ROOT)),started_at=start,wall_seconds=time.monotonic()-tick,exit_code=proc.returncode,curl_receipt=proc.stdout,stderr=proc.stderr,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),expected_blob=meta['blobId'],computed_blob=blob,blob_matches=blob==meta['blobId'])
            records.append(r);(OUT/'text-acquisitions.json').write_text(json.dumps(records,indent=2)+'\n')
            print(json.dumps({k:r[k] for k in ['model','filename','exit_code','bytes','blob_matches']}),flush=True)
            assert proc.returncode==0 and proc.stdout.startswith('200 ') and r['blob_matches']


if __name__=='__main__':main()
