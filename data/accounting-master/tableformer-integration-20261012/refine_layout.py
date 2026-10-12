"""Repair two page breaks found in the first rendered candidate."""
import json
import os
import shutil
import subprocess
import time
from build_candidate import OUT, CAND, expected_text, sha, save
assert not (OUT/'completion.json').exists() and not (OUT/'initial-build-run.json').exists()
for name in ['build-run.json','build-stdout.log','integration-checks.json','final-renders.json']:
    shutil.copyfile(OUT/name,OUT/('initial-'+name))
save('layout-repair.json',{'initial_pdf_sha256':sha(CAND/'accounting-product-proposal.pdf'),
 'finding':'PDF 54/55 leaves one sentence-final line on 55; PDF 55/56 separates most of the short chapter conclusion from its heading.',
 'repair':'Allow one additional line on PDF 54; start the complete closing section on PDF 56.',
 'content':'No wording, equation or reference removed. The added page-break command is separately stripped for preservation checking.'})
(CAND/'chapters/03-literature.tex').write_text(expected_text('chapters/03-literature.tex'))
c=json.loads((OUT/'candidate.json').read_text());c['passage_hashes']['literature-addition.tex']=sha(OUT/'literature-addition.tex')
c['delta']+=' Two local page-break adjustments keep the added paragraph and existing chapter conclusion together.';save('candidate.json',c)
command=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
overrides={'TEXMFVAR':'/tmp/accdsl-texmfvar','TEXMFCACHE':'/tmp/accdsl-texmfvar','CUDA_VISIBLE_DEVICES':'-1'}
env=os.environ.copy();env.update(overrides);start=time.monotonic()
with (OUT/'build-stdout.log').open('w') as log:r=subprocess.run(command,cwd=CAND,env=env,stdout=log,stderr=subprocess.STDOUT)
save('build-run.json',{'command':command,'cwd':str(CAND),'environment_overrides':overrides,'wall_seconds':time.monotonic()-start,'exit_code':r.returncode})
print({'exit_code':r.returncode,'wall_seconds':time.monotonic()-start});raise SystemExit(r.returncode)
