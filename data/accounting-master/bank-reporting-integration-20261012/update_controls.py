"""Advance only live manuscript pointers; preserve historical assessments."""
import json
from build_candidate import OUT, ROOT, CAND, sha, save

assert not (OUT/'completion.json').exists()
pdf=str((CAND/'accounting-product-proposal.pdf').relative_to(ROOT))
digest=sha(ROOT/pdf)
assert digest=='47516cce310d21b716e5226fd159a173985f58da0528909706b6c182842fd068'
summary='''Version 2.43 adds the Method 1 input, denominator-vintage, reporting-precision
and information-date explanation on final PDF 118–119. All 125 integration
checks pass; all 48 displays and 82 prior references remain, with five
references added. Eight final pages were inspected. The source inquiry passed
56 checks and verified 24 denominator entries. Actual bank inputs, score
rounding, reporting-rule history and independent/human/domain acceptance stay
open. Full readiness is not_ready.

Result: `data/accounting-master/bank-reporting-integration-20261012/result.md`.
'''
old='''Integrate the checked Method 1, reporting-precision and denominator-date
distinctions into a separate bank-chapter candidate. Preserve Version 2.42,
the hypothetical example and unresolved score rounding. Plan:
`docs/plans/accounting-bank-reporting-integration-20261012.md`.'''
new='''Inspect the exact official denominator-index link and March 2026 proposed
rule, preserving proposed/final/effective status and unresolved score rounding.
Keep the checked Version 2.43 example and source boundaries. Plan:
`docs/plans/accounting-bank-method1-rule-history-20261012.md`.'''
oldpdf='docs/design/proposal/manuscript-capital-recognition-20261012/accounting-product-proposal.pdf'
oldhash='59c9761e5da879bbd93ebb15068eda1f436980b9340dda4b9a32a4b3f813cfce'
rows=[]
for r in json.loads((OUT/'baseline.json').read_text())['pointer_snapshots']:
    p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot']);s=p.read_text()
    if p.name=='accounting-master-checkpoint.md':
        a=s.index('## Current candidate\n');b=s.index('## Latest institution classification',a)
        prior=s[a+len('## Current candidate\n'):b]
        current=f'## Current candidate\n\n**Version 2.43, 180 pages**\nPDF: {pdf}\nSHA256: {digest}\n\n'+summary+'\n'
        s=s[:a]+current+'## Preserved Version 2.42 capital recognition\n'+prior+s[b:]
    elif p.name=='next-plan.md':
        s=s.replace('**179-page Version 2.42**','**180-page Version 2.43**',1)
        s=s.replace(oldpdf,pdf,1).replace(oldhash,digest,1)
        s=s.replace('Result: data/accounting-master/bank-capital-recognition-20261012/result.md','Result: data/accounting-master/bank-reporting-integration-20261012/result.md',1)
        s=s.replace('## Completed boundary\n','## Completed boundary\n\n'+summary+'\n## Preserved Version 2.42 capital recognition\n',1)
    elif p.name=='accounting-master-current.md':
        s=s.replace('Version 2.42 explains capital eligibility and deductions.','Version 2.43 explains Method 1 inputs, reporting precision and denominator dates.\nVersion 2.42 preserves capital eligibility and deductions.',1)
        s=s.replace('**179-page Version 2.42**','**180-page Version 2.43**',1).replace(oldhash,digest,1)
        s=s.replace('Current through Version 2.42','Current through Version 2.43')
        s=s.replace('or Version 2.42 outputs','or Version 2.43 outputs',1)
        s=s.replace('delivered through Version 2.42','delivered through Version 2.43',1)
        s=s.replace('The current baseline is Version 2.42','The current baseline is Version 2.43',1)
        s=s.replace('Current; reporting source map complete; next unit integrates material findings','Current; Version 2.43 integrated; next unit checks exact denominator/rule-history leads',1)
        s=s.replace('## Current Version 2.42 capital recognition and deductions\n','## Current Version 2.43 bank reporting inputs\n\n'+summary+'\n## Preserved Version 2.42 capital recognition and deductions\n',1)
        s=s.replace('1. Follow the direct next plan: integrate checked Method 1 reporting\n   conventions and denominator dates into the bank chapter.','1. Follow the direct next plan: inspect the exact denominator-index and\n   March 2026 proposed-rule leads after the Version 2.43 integration.',1)
        s=s.replace('Integrate checked Method 1 reporting/denominator findings after the completed source map.','Inspect exact denominator-index and March 2026 proposed-rule leads after Version 2.43.',1)
    else:
        s=s.replace('## Latest Method 1 reporting source inquiry\n','## Current Version 2.43 bank reporting inputs\n\nE07/C05 and E14/C08; MC02–05/19/21/25/28/30/32–35, G7/G8/G13/G18.\n'+summary+'\n## Latest Method 1 reporting source inquiry\n',1)
        s=s.replace('## Current Version 2.42 capital recognition and deductions','## Preserved Version 2.42 capital recognition and deductions',1)
        s=s.replace('integrated through Version 2.42; next source work\nintegrates checked Method 1 reporting and denominator dates after the\ncompleted reporting source map.','integrated through Version 2.43; next source work\nchecks the exact denominator-index and March 2026 proposed-rule leads after\nthe completed reporting integration.',1)
    if p.name!='accounting-continuation-requirements-20261007.md':
        assert s.count(old)==1;s=s.replace(old,new,1)
    assert s!=p.read_text() and 'not_ready' in s
    p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
print(json.dumps({'controls':len(rows),'candidate':'2.43','pages':180,'next':'Method 1 rule-history inquiry'}))
