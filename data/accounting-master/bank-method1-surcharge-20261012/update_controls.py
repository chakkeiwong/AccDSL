"""Refresh source-only progress without changing the current candidate."""
import json
from record_conditions import OUT, ROOT, sha, save

assert not (OUT / 'completion.json').exists()
summary = """The Method 1 inquiry retains five successful API responses, one excluded 429,
and two official annual-CFR editions. Ten condition groups and three distinct
tables pass 52 source checks. The bank reference uses Method 1, while the BHC
overall surcharge takes the greater of Methods 1 and 2. Score, determination
and effective dates remain separate. Annual definitions agree after disclosed
production-metadata exclusion; a January/April table-caption punctuation
difference is preserved. Actual inputs and reporting conventions remain open.
Version 2.42 and not_ready remain unchanged. Result:
`data/accounting-master/bank-method1-surcharge-20261012/result.md`.
"""
old = """Inspect G-SIB identification and the Method 1 surcharge, score and effective
date referenced by the amended §3.11. Keep Method 1 distinct from the holding
company's overall surcharge and retain actual regulatory reports as missing
inputs. Plan: `docs/plans/accounting-bank-method1-surcharge-20261012.md`."""
new = """Inspect official FR Y-15 instructions and annual global-denominator releases
for Method 1 reporting, rounding and date selection. Retain unresolved
conventions rather than inventing a score calculation. Plan:
`docs/plans/accounting-bank-method1-reporting-20261012.md`."""
rows = []
for r in json.loads((OUT / 'baseline.json').read_text())['pointer_snapshots']:
    p = ROOT / r['live'];assert sha(p) == r['sha256'] == sha(ROOT / r['snapshot'])
    t = p.read_text()
    if p.name == 'accounting-continuation-requirements-20261007.md':
        marker = '## Current Version 2.42 capital recognition and deductions\n'
        t = t.replace(marker, '## Latest Method 1 surcharge source inquiry\n\nE07/C05; MC02–05/19/21/25/28/30/32–35, G7/G8/G13/G18.\n' + summary + '\n' + marker, 1)
        t = t.replace('checks G-SIB identification and Method 1 surcharge dates after the completed\ninstitution-classification source map.', 'checks official Method 1 reporting instructions and annual denominator\nprovenance after the completed surcharge source map.', 1)
    else:
        assert t.count(old) == 1;t = t.replace(old, new, 1)
        marker = '## Next bounded unit\n' if p.name != 'accounting-master-current.md' else '## Exact next action\n'
        assert t.count(marker) == 1
        t = t.replace(marker, '## Latest Method 1 surcharge source inquiry\n\n' + summary + '\n' + marker, 1)
        if p.name == 'accounting-master-current.md':
            t = t.replace('Current through Version 2.42 and the classification source inquiry', 'Current through Version 2.42 and the Method 1 source inquiry', 1)
            t = t.replace('Current; classification source map complete; next unit checks Method 1 surcharge and clocks', 'Current; Method 1 source map complete; next unit checks reporting conventions and denominator dates', 1)
            t = t.replace('Continue G-SIB identification and Method 1 surcharge dates after the completed classification map.', 'Continue official Method 1 reporting/denominator conventions after the completed surcharge map.', 1)
            t = t.replace('1. Follow the direct next plan: inspect G-SIB identification and Method 1\n   surcharge dates after the completed classification source map.', '1. Follow the direct next plan: inspect official Method 1 reporting conventions\n   and annual denominators after the completed surcharge source map.', 1)
    assert t != p.read_text() and 'Version 2.42' in t and 'not_ready' in t
    p.write_text(t);snap=OUT/'pointers-after'/r['live'];snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(snap.relative_to(ROOT)),'sha256':sha(snap)})
save('controls-after.json',rows)
print(json.dumps({'controls':len(rows),'candidate_unchanged':'2.42','next':'Method 1 reporting'}))
