"""Retain public source responses; never infer technical support from HTTP success."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,sys,time,shutil

base=Path(__file__).resolve().parent
(base/'sources').mkdir(exist_ok=True)
requests=json.loads(Path(sys.argv[1]).read_text())
def fetch(row):
    dest=base/'sources'/row['name'];start=time.monotonic()
    if dest.exists():
        old=dest.read_bytes(); history=base/'sources'/'response-history';history.mkdir(exist_ok=True)
        saved=history/(hashlib.sha256(old).hexdigest()+'-'+dest.name)
        if not saved.exists():shutil.copyfile(dest,saved)
    p=subprocess.run(['curl','-L','--max-time','35','--retry','0','-A','AccDSL scholarly research; local primary-source preservation',
                      '-sS','-w','%{http_code}',row['url'],'-o',str(dest)],capture_output=True,text=True)
    result=dict(row,elapsed_seconds=round(time.monotonic()-start,3),exit_code=p.returncode,http_status=p.stdout[-3:],stderr=p.stderr)
    if dest.exists():
        data=dest.read_bytes();result.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),is_pdf=data.startswith(b'%PDF-'))
    return result
with ThreadPoolExecutor(max_workers=5) as pool: results=list(pool.map(fetch,requests))
out=base/(Path(sys.argv[1]).stem+'-results.json')
out.write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
