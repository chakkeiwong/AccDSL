"""Keep the new payoff derivation with its table; preserve the first build."""
import json
import os
import shutil
import subprocess
import time
from build_candidate import ROOT, OUT, CAND, sha, save, expected_text

assert not (OUT / 'completion.json').exists()
assert not (OUT / 'initial-candidate.pdf').exists()
shutil.copyfile(CAND / 'accounting-product-proposal.pdf', OUT / 'initial-candidate.pdf')
for n in ['build-run.json','build-stdout.log','integration-checks.json','render-run.json']:
    shutil.copyfile(OUT / n, OUT / ('initial-'+n))
rows = json.loads((OUT / 'final-renders.json').read_text())
for r in rows:
    p = ROOT / r['render'];q = p.with_name(p.name.replace('final-','initial-',1));p.rename(q)
    r['render'] = str(q.relative_to(ROOT))
save('initial-renders.json', {'candidate':'data/accounting-master/insurance-vfa-integration-20261012/initial-candidate.pdf',
    'reviewed_pages':[136,137], 'rows':rows, 'status':'Superseded layout; the derivation crossed the page boundary'})
p = OUT / 'insurance-addition.tex';s = p.read_text();anchor = 'A small settlement example shows why the guarantee matters'
assert s.count(anchor) == 1;s = s.replace(anchor,'\\clearpage\n'+anchor,1);p.write_text(s)
rel = 'sections/insurance-methods.tex';(CAND / rel).write_text(expected_text(rel))
c = json.loads((OUT / 'candidate.json').read_text());c['passage_hashes']['insurance-addition.tex'] = sha(p)
c['layout_repair'] = 'One explicit page break before the new payoff example; no old or new prose removed.'
save('candidate.json', c)
command = ['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
overrides = {'TEXMFVAR':'/tmp/accdsl-texmfvar','TEXMFCACHE':'/tmp/accdsl-texmfvar','CUDA_VISIBLE_DEVICES':'-1'}
env = os.environ.copy();env.update(overrides);start = time.monotonic()
with (OUT / 'build-stdout.log').open('w') as log:
    r = subprocess.run(command, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT)
record = {'command':command,'cwd':str(CAND.relative_to(ROOT)),'environment_overrides':overrides,
    'wall_seconds':time.monotonic()-start,'exit_code':r.returncode}
save('build-run.json',record);print(json.dumps(record));raise SystemExit(r.returncode)
