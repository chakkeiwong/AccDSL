"""Advance only live pointers, preserving before/after snapshots."""
import json
import shutil
from prepare import OUT, ROOT, sha, save

assert not (OUT/'completion.json').exists()
baseline=json.loads((OUT/'baseline.json').read_text())
for item in baseline['pointer_snapshots']:
    assert sha(ROOT/item['live'])==item['sha256'], 'Live pointer changed since this unit began'

PDF='docs/design/proposal/manuscript-visible-text-20261012/accounting-product-proposal.pdf'
HASH='f77a019fcfb7af70faadc4a5f98aee31cf969713e0d1e898b7ac6a7a65749815'
RESULT='data/accounting-master/pdf-visible-text-fidelity-20261012/result.md'
SUMMARY='''The separate 175-page candidate adds the observed HSBC cover discrepancy to
the adapter discussion on final PDF 143–144. Both extractors return an extra
2024 token; selected drawing records and the inspected render show that the
earlier text is covered before Accounts 2023 is painted. Raw text, visible
reading, rejection and historical admission remain separate. All 136 source,
schema, preservation, citation, render-binding and build checks pass. All 48
prior displays and 75 bibliography entries remain, with one cover source added.
Seven final pages were inspected. Independent/human/domain acceptance remains
pending; no parser ranking, E05 conflict or selected-byte admission follows.
'''
NEXT='''Continue the retained JPMorgan 2025 Note 26 source dependency: restricted
cash, intercompany transfer conditions and the dated bank-dividend capacity.
Bind the note and Item 1 qualification, distinguish consolidated and parent
quantities, and retain unresolved future funding and operative-law inputs.
Plan: `docs/plans/accounting-jpmorgan-funds-transfer-20261012.md`.
'''

p=ROOT/'docs/plans/accounting-master-checkpoint.md'
t=p.read_text()
t=t.replace('## Current candidate\n','## Current candidate\n\n**Version 2.38, 175 pages**\nPDF: '+PDF+'\nSHA256: '+HASH+'\n\n'+SUMMARY+'\nResult: `'+RESULT+'`.\n\n## Preserved Version 2.37 correction\n',1)
a=t.index('## Exact next action\n'); b=t.index('## Latest ASBE 25 access result',a)
t=t[:a]+'## Exact next action\n\n'+NEXT+'\n'+t[b:]
p.write_text(t)

p=ROOT/'docs/plans/accounting-master-current.md'
t=p.read_text()
t=t.replace('Version 2.37 corrects the unsupported entity label in the Note 20 junior-debt\nblock;', 'Version 2.38 adds an observed PDF visibility failure and explicit review/query\nbehavior. Version 2.37 preserves the correction to the Note 20 junior-debt\nentity label;',1)
t=t.replace('**174-page Version 2.37**','**175-page Version 2.38**',1)
t=t.replace('`9e6d0b433ebdbc30b65a17122dcbb2834b3c63d195b31ffaf2bea68eaa1fc880`.','`'+HASH+'`.',1)
t=t.replace('Current through Version 2.37, subsequent junior-debt inquiry and Apple/Caterpillar/HSBC source units','Current through Version 2.38 and the ASBE/HSBC source inquiries',1)
t=t.replace('Current; HSBC filing inquiry closed and ASBE notice discovery bounded without source; next work examines the concrete PDF text/render discrepancy','Current; PDF text/render case integrated; next source unit inspects JPMorgan Note 26 funding restrictions',1)
t=t.replace('Current through Version 2.37 and the latest HSBC event','Current through Version 2.38 and the latest bounded source inquiries',1)
t=t.replace('or Version 2.37 outputs','or Version 2.38 outputs',1)
t=t.replace('Bounded integration delivered through Version 2.37','Bounded integration delivered through Version 2.38',1)
t=t.replace('The current baseline is Version 2.37, not the superseded 2.36 entity label\nor the historical stopped controller.','The current baseline is Version 2.38; Version 2.37 and the superseded 2.36\nentity-label evidence remain protected. The stopped controller is historical.',1)
t=t.replace('## Latest ASBE 25 access result','## Current Version 2.38 visibility example\n\n'+SUMMARY+'\nResult: `'+RESULT+'`.\n\n## Latest ASBE 25 access result',1)
t=t.replace('Independent E14 preparation continues with the observed HSBC PDF cover\ndiscrepancy. Result:','The subsequent E14 cover discrepancy is now integrated in Version 2.38. Result:',1)
t=t.replace('## Current Version 2.37 correction','## Preserved Version 2.37 correction',1)
t=t.replace('1. Follow the direct next plan: explain the observed HSBC PDF cover\'s raw\n   text/render discrepancy and specify its adapter/review behavior under E14.','1. Follow the direct next plan: inspect JPMorgan 2025 Note 26 and its Item 1\n   dependency for restricted resources and dated parent-funding conditions.',1)
p.write_text(t)

p=ROOT/'docs/plans/accounting-continuation-requirements-20261007.md'
t=p.read_text()
new='''## Current Version 2.38 PDF visibility example

E14/E01/C07/P18; MC01–05/25/27/30–35, G2/G5/G9/G11/G13/G17/G18.
'''+SUMMARY+'\nThe existing annotation schema remains unchanged; six expected query outcomes\nare documentary specifications, not runtime results. Historical availability\nand the frozen 56/136 assessment are unchanged. All original MC/G requirements\nremain open to their wider acceptance evidence; full readiness is not_ready.\nResult: `'+RESULT+'`.\n\n'
t=t.replace('## Latest ASBE 25 access result',new+'## Latest ASBE 25 access result',1)
t=t.replace('Independent E14 work now examines the observed PDF cover\ntext/render discrepancy. Version 2.37 and not_ready remain unchanged.','The subsequent E14 cover repair is integrated in Version 2.38; not_ready\nremains unchanged.',1)
t=t.replace('Next source work\nseeks a distinct official ASBE 25 operative-notice route; human acceptance\ndoes not stop feasible internal preparation.','Following the bounded ASBE inquiry and cover repair, next source work\ninspects JPMorgan Note 26. Human acceptance does not stop feasible internal\npreparation.',1)
t=t.replace('## Current Version 2.37 source-fidelity correction','## Preserved Version 2.37 source-fidelity correction',1)
p.write_text(t)

p=ROOT/'data/accounting-master/next-plan.md'
t=p.read_text().replace('**174-page Version 2.37**','**175-page Version 2.38**',1)
t=t.replace('docs/design/proposal/manuscript-junior-classification-20261012/accounting-product-proposal.pdf',PDF,1)
t=t.replace('9e6d0b433ebdbc30b65a17122dcbb2834b3c63d195b31ffaf2bea68eaa1fc880',HASH,1)
t=t.replace('data/accounting-master/accounting-proposal-v237-integration-20261012/result.md',RESULT,1)
t=t.replace('## Completed boundary\n','## Completed boundary\n\n'+SUMMARY+'\n## Preserved Version 2.37 correction\n',1)
a=t.index('## Next bounded unit\n');b=t.index('## Latest ASBE 25 access result',a)
t=t[:a]+'## Next bounded unit\n\n'+NEXT+'\n'+t[b:]
p.write_text(t)

snapshots=[]
for item in baseline['pointer_snapshots']:
    p=ROOT/item['live']; dest=OUT/'pointers-after'/item['live']
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,dest)
    snapshots.append({'live':item['live'],'snapshot':str(dest.relative_to(ROOT)),'sha256':sha(dest)})
save('controls-after.json',snapshots)
print(json.dumps({'live_controls_updated':len(snapshots),'version':'2.38','readiness':'not_ready'}))
