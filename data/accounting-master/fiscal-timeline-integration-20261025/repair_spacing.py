"""Preserve the rejected first build, then repair its new path line only."""
from pathlib import Path
from hashlib import sha256
import json,os,shutil,subprocess,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
TARGET=ROOT/'docs/design/proposal/manuscript-fiscal-timeline-20261025'
BACK=HERE/'rejected-spacing-build'
assert not BACK.exists();BACK.mkdir()
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
for name in ['addition.tex','integration-code-lock.json','integration-baseline.json','build.json','build.log']:
    shutil.copy2(HERE/name,BACK/name)
for name in ['accounting-product-proposal.pdf','accounting-product-proposal.log','sections/company-family-language.tex']:
    saved=BACK/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(TARGET/name,saved)
old='Thirteen focused tests and 61 regressions retain twelve complete exchanges in\n\\path{data/accounting-master/fiscal-timeline-20261025/}. They compare entire\nnative transitions, journals and archives, including an expressly renewed'
new='Thirteen focused tests and 61 regressions retain twelve complete exchanges:\n\\begin{flushleft}\\small\n\\path{data/accounting-master/fiscal-timeline-20261025/}\n\\end{flushleft}\n+They compare entire native transitions, journals and archives, including an expressly renewed'.replace('\n+They','\nThey')
for p in [HERE/'addition.tex',TARGET/'sections/company-family-language.tex']:
    text=p.read_text();assert text.count(old)==1; p.write_text(text.replace(old,new))
lock=json.loads((HERE/'integration-code-lock.json').read_text());lock['addition.tex']=sha(HERE/'addition.tex');dump(HERE/'integration-code-lock.json',lock)
baseline=json.loads((HERE/'integration-baseline.json').read_text())
for name in ['addition.tex','integration-code-lock.json']:
    baseline['evidence_hashes'][str((HERE/name).relative_to(ROOT))]=sha(HERE/name)
dump(HERE/'integration-baseline.json',baseline)
command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
cache='/tmp/accdsl-fiscal-timeline-integration-20261025-tex-cache'
env={'TEXMFVAR':cache,'TEXMFCACHE':cache,'CUDA_VISIBLE_DEVICES':'-1'};start=time.monotonic()
with (HERE/'build.log').open('w') as f:run=subprocess.run(command,cwd=TARGET,env={**os.environ,**env},stdout=f,stderr=subprocess.STDOUT,timeout=240)
dump(HERE/'build.json',{'command':command,'cwd':str(TARGET),'environment':env,'wall_seconds':time.monotonic()-start,
    'returncode':run.returncode,'pdf_sha256':sha(TARGET/'accounting-product-proposal.pdf')})
dump(HERE/'spacing-repair.json',{'reason':'New underfull path line rejected before acceptance; path moved to its own flushleft line',
    'preserved_first_attempt':{str(p.relative_to(ROOT)):sha(p) for p in BACK.rglob('*') if p.is_file()},
    'replacement':'Only the new paragraph path presentation; no claim, formula, source or runtime change',
    'script_sha256':sha(Path(__file__)),'returncode':run.returncode})
print(json.dumps({'rebuild_returncode':run.returncode}));raise SystemExit(run.returncode)
