"""Preserve first rendered attempt and wrap provenance without deleting content."""
from pathlib import Path
from hashlib import sha256
import json,shutil
import integrate as m
HERE=m.HERE;archive=HERE/'attempt-01';assert not archive.exists();archive.mkdir()
for p in HERE.iterdir():
    if p.is_file() and (p.name in ('build.json','build.log','verification.json','source-preservation.json','selected-term-execution.tex') or p.name.startswith('page-')):
        shutil.copy2(p,archive/p.name)
shutil.copy2(m.TARGET/'accounting-product-proposal.pdf',archive/'accounting-product-proposal.pdf')
source=HERE/'selected-term-execution.tex';before=source.read_text()
old='The complete sources, expected declarations, failures and results are retained'
assert before.count(old)==1
after=before.replace(old,'\\begingroup\\raggedright'+chr(10)+old,1).rstrip()+chr(10)+'\\par\\endgroup'+chr(10)
source.write_text(after);(m.TARGET/m.NEW).write_text(after)
pres=m.read(HERE/'source-preservation.json');pres['added_source_sha256']=m.sha(source);m.dump('source-preservation.json',pres)
for name in ('build.json','build.log','verification.json'):(HERE/name).unlink()
m.dump('layout-repair.json',dict(before_sha256=sha256(before.encode()).hexdigest(),after_sha256=sha256(after.encode()).hexdigest(),
  reason='Long provenance paths overflowed page 712; use existing raggedright provenance convention',preserved_attempt='attempt-01',content_removed=False))
print('Archived first build and applied provenance wrapping')
