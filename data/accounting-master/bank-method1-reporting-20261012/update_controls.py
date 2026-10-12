"""Refresh live records for the completed source map and ready integration."""
import json
from record_evidence import ROOT, OUT, sha, save

assert not (OUT/'completion.json').exists()
summary='''The reporting inquiry retains four publications: the current-linked FR Y-15
form/instructions and official 2024/2025 denominator notices. Sixteen condition
groups and 24 denominator entries pass 56 source checks; ten source renders
were inspected. The instructions mix page dates; dollar rounding, payment
accuracy, score rounding and report/publication/effectiveness clocks remain
distinct. The two notices use prior-year BCBS data. Score rounding, a complete
revision chain and actual bank inputs remain unresolved. Version 2.42 and
not_ready remain. Result:
`data/accounting-master/bank-method1-reporting-20261012/result.md`.
'''
old='''Inspect official FR Y-15 instructions and annual global-denominator releases
for Method 1 reporting, rounding and date selection. Retain unresolved
conventions rather than inventing a score calculation. Plan:
`docs/plans/accounting-bank-method1-reporting-20261012.md`.'''
new='''Integrate the checked Method 1, reporting-precision and denominator-date
distinctions into a separate bank-chapter candidate. Preserve Version 2.42,
the hypothetical example and unresolved score rounding. Plan:
`docs/plans/accounting-bank-reporting-integration-20261012.md`.'''
rows=[]
for r in json.loads((OUT/'baseline.json').read_text())['pointer_snapshots']:
    p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot'])
    s=p.read_text()
    if p.name=='accounting-continuation-requirements-20261007.md':
        marker='## Latest institution classification source inquiry\n'
        s=s.replace(marker,'## Latest Method 1 reporting source inquiry\n\nE07/C05; MC02–05/19/21/25/28/30/32–35, G7/G8/G13/G18.\n'+summary+'\n'+marker,1)
        s=s.replace('checks official Method 1 reporting instructions and annual denominator\nprovenance after the completed surcharge source map.','integrates checked Method 1 reporting and denominator dates after the\ncompleted reporting source map.',1)
    else:
        assert s.count(old)==1;s=s.replace(old,new,1)
        marker='## Exact next action\n' if p.name=='accounting-master-current.md' else '## Next bounded unit\n'
        assert s.count(marker)==1;s=s.replace(marker,'## Latest Method 1 reporting source inquiry\n\n'+summary+'\n'+marker,1)
        if p.name=='accounting-master-current.md':
            s=s.replace('Current through Version 2.42 and the Method 1 source inquiry','Current through Version 2.42 and the reporting-source inquiry',1)
            s=s.replace('Current; Method 1 source map complete; next unit checks reporting conventions and denominator dates','Current; reporting source map complete; next unit integrates material findings',1)
            s=s.replace('1. Follow the direct next plan: inspect official Method 1 reporting conventions\n   and annual denominators after the completed surcharge source map.','1. Follow the direct next plan: integrate checked Method 1 reporting\n   conventions and denominator dates into the bank chapter.',1)
            s=s.replace('Continue official Method 1 reporting/denominator conventions after the completed surcharge map.','Integrate checked Method 1 reporting/denominator findings after the completed source map.',1)
    assert s!=p.read_text() and 'not_ready' in s
    p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
print(json.dumps({'controls':len(rows),'next':'bank reporting integration','manuscript':'2.42 unchanged'}))
