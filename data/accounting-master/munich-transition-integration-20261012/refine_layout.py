"""Keep margin populations and valuation inputs together after inspecting the first build."""
import json
import os
import shutil
import subprocess
import time
from build_candidate import ROOT, OUT, CAND, sha, save, expected_text

assert not (OUT/'completion.json').exists()
initial=OUT/'initial-build';assert not initial.exists();initial.mkdir()
for name in ['build-run.json','build-stdout.log','candidate.json','insurance-addition.tex','final-renders.json']:
    shutil.copyfile(OUT/name,initial/name)
for suffix in ['pdf','log','blg']:
    name='accounting-product-proposal.'+suffix;shutil.copyfile(CAND/name,initial/name)
(OUT/'final-rendered').rename(initial/'rendered')
rows=json.loads((initial/'final-renders.json').read_text())
for row in rows:
    row['render']=str((initial/'rendered'/__import__('pathlib').Path(row['render']).name).relative_to(ROOT))
    row['text']=str((initial/'rendered'/__import__('pathlib').Path(row['text']).name).relative_to(ROOT))
(initial/'final-renders.json').write_text(json.dumps(rows,indent=2)+'\n')
save('final-renders.json',[])
addition=OUT/'insurance-addition.tex';s=addition.read_text()
anchor='The separate margin tables also clarify which contracts are being followed.'
assert s.count(anchor)==1;s=s.replace(anchor,'\\clearpage\n'+anchor,1);addition.write_text(s)
(CAND/'sections/insurance-methods.tex').write_text(expected_text('sections/insurance-methods.tex'))
c=json.loads((OUT/'candidate.json').read_text());c['passage_hashes']['insurance-addition.tex']=sha(addition);save('candidate.json',c)
command=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
overrides={'TEXMFVAR':'/tmp/accdsl-texmfvar','TEXMFCACHE':'/tmp/accdsl-texmfvar','CUDA_VISIBLE_DEVICES':'-1'}
env=os.environ.copy();env.update(overrides);start=time.monotonic()
with (OUT/'build-stdout.log').open('w') as log:
    r=subprocess.run(command,cwd=CAND,env=env,stdout=log,stderr=subprocess.STDOUT)
save('build-run.json',{'command':command,'cwd':str(CAND.relative_to(ROOT)),
    'environment_overrides':overrides,'wall_seconds':time.monotonic()-start,'exit_code':r.returncode})
save('layout-repair.json',{'finding':'First build PDF 143 strands two lines introducing issuer risk inputs; their conditions continue on 144.',
    'repair':'Start the separate-margin explanation and complete risk-input paragraph together on the next page; no prose or qualifications removed.',
    'initial_pdf_sha256':sha(initial/'accounting-product-proposal.pdf'),
    'initial_inspected_pages':[143,144],
    'final_pdf_sha256':sha(CAND/'accounting-product-proposal.pdf')})
print(json.dumps({'exit_code':r.returncode,'wall_seconds':time.monotonic()-start}));raise SystemExit(r.returncode)
