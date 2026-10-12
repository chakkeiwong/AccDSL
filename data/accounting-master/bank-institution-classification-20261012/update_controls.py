"""Refresh source-only progress without changing the current candidate."""
import json
from record_conditions import OUT, ROOT, sha, save

assert not (OUT / 'completion.json').exists()
summary = '''The classification inquiry retains eight successful official responses and
12 located condition groups; all 48 source checks pass. Three complete
January/April sections agree. Entry averages, four-quarter exit conditions,
parent/bank routes and report-specific measures remain distinct. Two additional
definition sections were read selectively. No named bank was classified and no
new manuscript version is warranted; Version 2.42 and not_ready remain.
Result: `data/accounting-master/bank-institution-classification-20261012/result.md`.
'''
old = '''Inspect institution classification and its entry/exit clocks in dated
§§3.100, 252.5 and 238.10. Connect the bank and parent routes to retained
Part 3 definitions without assigning a named bank's category from a single
balance sheet or group label. Plan:
`docs/plans/accounting-bank-institution-classification-20261012.md`.'''
new = '''Inspect G-SIB identification and the Method 1 surcharge, score and effective
date referenced by the amended §3.11. Keep Method 1 distinct from the holding
company's overall surcharge and retain actual regulatory reports as missing
inputs. Plan: `docs/plans/accounting-bank-method1-surcharge-20261012.md`.'''
rows = []
for r in json.loads((OUT / 'baseline.json').read_text())['pointer_snapshots']:
    p = ROOT / r['live'];assert sha(p) == r['sha256'] == sha(ROOT / r['snapshot'])
    t = p.read_text()
    if p.name == 'accounting-continuation-requirements-20261007.md':
        marker = '## Current Version 2.42 capital recognition and deductions\n'
        t = t.replace(marker, '## Latest institution classification source inquiry\n\nE07/C05; MC02–05/19/21/25/28/30/32–35, G7/G8/G13/G18.\n' + summary + '\n' + marker, 1)
        t = t.replace('checks institution classification and its clocks in §§3.100, 252.5 and 238.10.', 'checks G-SIB identification and Method 1 surcharge dates after the completed\ninstitution-classification source map.', 1)
    else:
        assert t.count(old) == 1;t = t.replace(old, new, 1)
        marker = '## Next bounded unit\n' if p.name != 'accounting-master-current.md' else '## Exact next action\n'
        assert t.count(marker) == 1
        t = t.replace(marker, '## Latest institution classification source inquiry\n\n' + summary + '\n' + marker, 1)
        if p.name == 'accounting-master-current.md':
            t = t.replace('Current through Version 2.42 and the capital recognition inquiry', 'Current through Version 2.42 and the classification source inquiry', 1)
            t = t.replace('Current; capital recognition integrated; next unit checks institution classification and clocks', 'Current; classification source map complete; next unit checks Method 1 surcharge and clocks', 1)
            t = t.replace('Continue institution classification after the completed capital eligibility/deduction inquiry.', 'Continue G-SIB identification and Method 1 surcharge dates after the completed classification map.', 1)
            t = t.replace('1. Follow the direct next plan: inspect institution classification and its\n   clocks after the completed capital eligibility/deduction inquiry.', '1. Follow the direct next plan: inspect G-SIB identification and Method 1\n   surcharge dates after the completed classification source map.', 1)
    assert t != p.read_text() and 'Version 2.42' in t and 'not_ready' in t
    p.write_text(t);snap=OUT/'pointers-after'/r['live'];snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(snap.relative_to(ROOT)),'sha256':sha(snap)})
save('controls-after.json',rows)
print(json.dumps({'controls':len(rows),'candidate_unchanged':'2.42','next':'Method 1 surcharge'}))
