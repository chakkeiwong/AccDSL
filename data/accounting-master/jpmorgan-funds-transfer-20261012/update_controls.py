"""Refresh live controls after the bounded 2.39 integration."""
import json
import shutil
from prepare import OUT, ROOT, sha, save

assert not (OUT/'completion.json').exists()
source=json.loads((OUT/'source-manifest.json').read_text())
for x in source['pointer_snapshots']:assert sha(ROOT/x['live'])==x['sha256']
PDF='docs/design/proposal/manuscript-funds-transfer-20261012/accounting-product-proposal.pdf'
HASH='c23bf198be1f79bec92204b074e93a01d09d736675a2df39ea20620c2000f44b'
RESULT='data/accounting-master/jpmorgan-funds-transfer-20261012/result.md'
SUMMARY='''The separate 176-page candidate adds the checked Note 26 funding distinction
at final PDF 116. Approximately 30.1 billion of bank dividend capacity at
1 January 2026 differs from parent cash and 2025 subsidiary dividend receipts.
The 29.0 billion consolidated restricted-cash total cannot be subtracted from
parent-only cash. Seven paired rows, eight exact spans and 33 source/arithmetic
checks support the reading; all 136 integration checks pass. All 48 displays,
76 bibliography entries and prior prose remain. Six final renders bind the
inspected slice. Operative law, actual future transfers and independent/human/
domain acceptance stay open. Full readiness is not_ready.
'''
NEXT='''Continue primary national-bank dividend-authority research following Note 26.
Verify official section identities, dated editions, conditions and dependencies;
do not treat the issuer summary or a later current page as verified law for
1 January 2026. Plan:
`docs/plans/accounting-national-bank-dividend-authority-20261012.md`.
'''
p=ROOT/'docs/plans/accounting-master-checkpoint.md';t=p.read_text()
t=t.replace('## Current candidate\n','## Current candidate\n\n**Version 2.39, 176 pages**\nPDF: '+PDF+'\nSHA256: '+HASH+'\n\n'+SUMMARY+'\nResult: `'+RESULT+'`.\n\n## Preserved Version 2.38 visibility example\n',1)
a=t.index('## Exact next action\n');b=t.index('## Latest ASBE 25 access result',a)
t=t[:a]+'## Exact next action\n\n'+NEXT+'\n'+t[b:];p.write_text(t)
p=ROOT/'docs/plans/accounting-master-current.md';t=p.read_text()
t=t.replace('Version 2.38 adds an observed PDF visibility failure and explicit review/query\nbehavior.','Version 2.39 distinguishes dated dividend capacity and consolidated restricted\ncash from parent cash. Version 2.38 preserves the PDF visibility/review example.',1)
t=t.replace('**175-page Version 2.38**','**176-page Version 2.39**',1)
t=t.replace('f77a019fcfb7af70faadc4a5f98aee31cf969713e0d1e898b7ac6a7a65749815',HASH,1)
t=t.replace('Current through Version 2.38 and the ASBE/HSBC source inquiries','Current through Version 2.39 and the Note 26 source inquiry',1)
t=t.replace('Current; PDF text/render case integrated; next source unit inspects JPMorgan Note 26 funding restrictions','Current; Note 26 integrated; next source unit checks primary national-bank dividend authority',1)
t=t.replace('Current through Version 2.38 and the latest bounded source inquiries','Current through Version 2.39 and the latest bounded source inquiries',1)
t=t.replace('or Version 2.38 outputs','or Version 2.39 outputs',1)
t=t.replace('Bounded integration delivered through Version 2.38','Bounded integration delivered through Version 2.39',1)
t=t.replace('The current baseline is Version 2.38;','The current baseline is Version 2.39;',1)
t=t.replace('## Current Version 2.38 visibility example','## Current Version 2.39 funding distinction\n\n'+SUMMARY+'\nResult: `'+RESULT+'`.\n\n## Preserved Version 2.38 visibility example',1)
t=t.replace('1. Follow the direct next plan: inspect JPMorgan 2025 Note 26 and its Item 1\n   dependency for restricted resources and dated parent-funding conditions.','1. Follow the direct next plan: inspect official national-bank dividend\n   provisions, dated editions and dependencies after the Note 26 source unit.',1)
p.write_text(t)
p=ROOT/'docs/plans/accounting-continuation-requirements-20261007.md';t=p.read_text()
new='## Current Version 2.39 restricted resources and funding\n\nE01/E07/P18; MC01–05/08/15/16/21/25/28/30/32–35, G4/G5/G7/G11/G13.\n'+SUMMARY+'\nResult: `'+RESULT+'`.\n\n'
t=t.replace('## Current Version 2.38 PDF visibility example',new+'## Preserved Version 2.38 PDF visibility example',1)
t=t.replace('Following the bounded ASBE inquiry and cover repair, next source work\ninspects JPMorgan Note 26.','Following the bounded ASBE inquiry, cover repair and Note 26 integration,\nnext source work inspects primary national-bank dividend authority.',1)
p.write_text(t)
p=ROOT/'data/accounting-master/next-plan.md';t=p.read_text()
t=t.replace('**175-page Version 2.38**','**176-page Version 2.39**',1)
t=t.replace('docs/design/proposal/manuscript-visible-text-20261012/accounting-product-proposal.pdf',PDF,1)
t=t.replace('f77a019fcfb7af70faadc4a5f98aee31cf969713e0d1e898b7ac6a7a65749815',HASH,1)
t=t.replace('data/accounting-master/pdf-visible-text-fidelity-20261012/result.md',RESULT,1)
t=t.replace('## Completed boundary\n','## Completed boundary\n\n'+SUMMARY+'\n## Preserved Version 2.38 visibility example\n',1)
a=t.index('## Next bounded unit\n');b=t.index('## Latest ASBE 25 access result',a)
t=t[:a]+'## Next bounded unit\n\n'+NEXT+'\n'+t[b:];p.write_text(t)
after=[]
for x in source['pointer_snapshots']:
    p=ROOT/x['live'];dest=OUT/'pointers-after'/x['live'];dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,dest);after.append({'live':x['live'],'snapshot':str(dest.relative_to(ROOT)),'sha256':sha(dest)})
save('controls-after.json',after)
print(json.dumps({'updated_controls':len(after),'version':'2.39','readiness':'not_ready'}))
