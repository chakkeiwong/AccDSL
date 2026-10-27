#!/usr/bin/env python3
"""Preservation and rendered-output checks for the bounded case insertion."""
import hashlib
import json
from pathlib import Path
import re
import time
import fitz

ROOT=Path(__file__).resolve().parents[3]
OPS=Path(__file__).resolve().parent
NEW=ROOT/'docs/design/proposal/manuscript-case-20261007'
start=time.monotonic()
checks=[]
def check(ok,label):checks.append({'check':label,'passed':bool(ok)})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

base=json.loads((OPS/'manuscript-baseline.json').read_text())
changed=[]
for r in base['sources']:
    original=ROOT/r['path'];candidate=ROOT/r['candidate']
    check(sha(original)==r['sha256'],'unchanged baseline '+r['path'])
    before=original.read_text();after=candidate.read_text()
    if before!=after:changed.append(str(candidate.relative_to(NEW)))
    if candidate.name=='accounting-product-proposal.tex':
        check(before.replace('Version 2.1','Version 2.2')==after,'main TeX only changes version')
    else:
        # Every original line remains in its original order. The two prose
        # insertions add context without deleting any original content.
        iterator=iter(after.splitlines())
        check(all(any(b==a for b in iterator) for a in before.splitlines()),'original content preserved '+r['candidate'])
check(set(changed)=={'accounting-product-proposal.tex','chapters/13-reference-company.tex','sections/source-admission.tex'},'only intended files changed')
check(sha(ROOT/base['baseline_pdf']['path'])==base['baseline_pdf']['sha256'],'baseline PDF preserved')
log=(NEW/'accounting-product-proposal.log').read_text()
diagnostics=[s for s in log.splitlines() if any(q in s for q in ['Warning','Overfull','Underfull','! '])]
check(not diagnostics,'final log has no warnings, overfull/underfull boxes or fatal error')
pdf=NEW/'accounting-product-proposal.pdf'
with fitz.open(pdf) as d:
    text='\n'.join(p.get_text() for p in d)
    pages=len(d)
check(pages==126,'126-page final candidate')
for marker in ['Version 2.2','27,343','849','10.9375','1,260.9375','15 November 2025','Both','Saturday','Container choice','restricted cash']:
    check(marker in text,'rendered text contains '+marker)
render=json.loads((OPS/'manuscript-render-manifest.json').read_text())
check(render['sha256']==sha(pdf),'render manifest binds final PDF')
for r in render['rendered_pages']:check(sha(ROOT/r['path'])==r['sha256'],'render image preserved '+str(r['pdf_page']))

# Three corrected historical E05 source locations, independent of line numbers.
fix=json.loads((ROOT/'docs/design/cases/apple/continuation-20261007/e05-anchor-repair-v1.json').read_text())
check(sha(ROOT/fix['baseline']['path'])==fix['baseline']['sha256'],'original E05 record preserved')
for r in fix['findings']:
    x=r['replacement'];s=(ROOT/x['extraction_path']).read_text()
    check(sha(ROOT/x['extraction_path'])==x['extraction_sha256'] and s[x['start']:x['end']]==x['quote'],'corrected E05 span '+r['old_span_id'])
    target={'annual_fixed_notes':'97,341','annual_swaps':'interest rate swaps','annual_assets':'364,980'}[r['old_span_id']]
    check(target in x['quote'],'corrected span supports '+r['old_span_id'])
result={'command':['python3',str(Path(__file__).relative_to(ROOT))],'wall_seconds':time.monotonic()-start,
        'pdf':{'path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'pages':pages},'changed_sources':changed,
        'checks':checks,'passed':sum(r['passed'] for r in checks),'failed':sum(not r['passed'] for r in checks),
        'scope':'Preservation/build/extracted-render/located-source checks only; visual review is separately recorded; independent/human acceptance pending.'}
(OPS/'manuscript-checks-v1.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:result[k] for k in ['passed','failed','wall_seconds']})
assert not result['failed'],[r for r in checks if not r['passed']]
