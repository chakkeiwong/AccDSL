"""Refresh all live continuation instructions and freeze their changed bytes."""
import json
import re
from build_candidate import OUT, ROOT, sha, save

assert not (OUT / 'completion.json').exists()
baseline = json.loads((OUT / 'baseline.json').read_text())
summary = '''The 179-page candidate explains instrument eligibility, Tier 2 recognition
near maturity, asset-specific tax netting and AOCI elections on final PDF 123.
The existing bank path remains hypothetical. All 37 source and 121 integration
checks pass; 48 displays and 80 prior bibliography entries remain, with two
references added. Seven final pages were inspected. The source map retains
19 condition groups from 187 paragraphs and 23 footnotes; January/April
normalized sections agree without establishing a complete amendment chain.
Actual bank classification, contracts, tax links and supervisory facts remain
open. Full readiness is not_ready.

Result: `data/accounting-master/bank-capital-recognition-20261012/result.md`.
'''
old_next = '''Inspect capital eligibility and deductions in dated §§3.20 and 3.22,
retaining instrument conditions, ordering, elections and institution scope.
Do not substitute reported equity or debt labels for regulatory capital or
compute a named bank's permissible dividend. Plan:
`docs/plans/accounting-bank-capital-recognition-20261012.md`.'''
new_next = '''Inspect institution classification and its entry/exit clocks in dated
§§3.100, 252.5 and 238.10. Connect the bank and parent routes to retained
Part 3 definitions without assigning a named bank's category from a single
balance sheet or group label. Plan:
`docs/plans/accounting-bank-institution-classification-20261012.md`.'''
old_hash = '8a0903f51fe5ba03a618ad186e430c8b33ed9789cc1c294410ee24b41a38fbc3'
new_hash = '59c9761e5da879bbd93ebb15068eda1f436980b9340dda4b9a32a4b3f813cfce'
rows = []
for row in baseline['pointer_snapshots']:
    path = ROOT / row['live']
    assert sha(path) == row['sha256'] == sha(ROOT / row['snapshot'])
    text = path.read_text()
    if path.name == 'accounting-master-checkpoint.md':
        assert text.count(old_next) == 1
        text = text.replace('## Next bounded unit\n\n' + old_next + '\n\n', '', 1)
        text, n = re.subn(r'## Exact next action\n.*?(?=\n## )', '', text, count=1, flags=re.S)
        assert n == 1
        text = text.replace('## Current candidate\n', '## Preserved Version 2.41 income definitions and payout tables\n', 1)
        marker = '## Preserved Version 2.41 income definitions and payout tables\n'
        current = ('## Current candidate\n\n**Version 2.42, 179 pages**\n'
                   'PDF: docs/design/proposal/manuscript-capital-recognition-20261012/accounting-product-proposal.pdf\n'
                   f'SHA256: {new_hash}\n\n' + summary + '\n## Next bounded unit\n\n' + new_next + '\n\n')
        text = text.replace(marker, current + marker, 1)
    elif path.name == 'accounting-master-current.md':
        text = text.replace('Version 2.41 distinguishes the two income measures and combined payout tables.',
                            'Version 2.42 explains capital eligibility and deductions.\nVersion 2.41 preserves the two income measures and combined payout tables.', 1)
        text = text.replace('**177-page Version 2.41**', '**179-page Version 2.42**', 1).replace(old_hash, new_hash, 1)
        text = text.replace('Current through Version 2.41 and the Part 3 definition inquiry', 'Current through Version 2.42 and the capital recognition inquiry', 1)
        text = text.replace('Current; Part 3 definitions integrated; next unit checks capital eligibility and deductions', 'Current; capital recognition integrated; next unit checks institution classification and clocks', 1)
        text = text.replace('Current through Version 2.41 and the latest bounded source inquiries', 'Current through Version 2.42 and the latest bounded source inquiries', 1)
        text = text.replace('Version 2.41 outputs', 'Version 2.42 outputs', 1)
        text = text.replace('delivered through Version 2.41', 'delivered through Version 2.42', 1)
        text = text.replace('current baseline is Version 2.41', 'current baseline is Version 2.42', 1)
        marker = '## Current Version 2.41 income definitions and payout tables\n'
        assert text.count(marker) == 1 and text.count(old_next) == 1
        text = text.replace(marker, '## Current Version 2.42 capital recognition and deductions\n\n' + summary + '\n## Preserved Version 2.41 income definitions and payout tables\n', 1)
        text = text.replace(old_next, new_next, 1)
        text = text.replace('Version 2.40 timing and Version 2.41 income/table case', 'Version 2.40 timing, Version 2.41 income/table case and Version 2.42 capital reconciliation', 1)
        text = text.replace('Continue the capital eligibility/deduction dependencies after the completed Part 3 income/table inquiry.', 'Continue institution classification after the completed capital eligibility/deduction inquiry.', 1)
        stale = '1. Follow the direct next plan: inspect official national-bank dividend\n   provisions, dated editions and dependencies after the Note 26 source unit.'
        assert text.count(stale) == 1
        text = text.replace(stale, '1. Follow the direct next plan: inspect institution classification and its\n   clocks after the completed capital eligibility/deduction inquiry.', 1)
    elif path.name == 'accounting-continuation-requirements-20261007.md':
        marker = '## Current Version 2.41 income definitions and payout tables\n'
        assert text.count(marker) == 1
        text = text.replace(marker, '## Current Version 2.42 capital recognition and deductions\n\nE07/C05/P18; MC02–05/16/19/21/25/28/30/32–35, G4/G7/G8/G13/G18.\n' + summary + '\n## Preserved Version 2.41 income definitions and payout tables\n', 1)
        stale = 'the national-bank authority and Part 3 definition inquiries are complete within\nscope, integrated through Version 2.41; next source work checks capital\neligibility and deductions in §§3.20 and 3.22.'
        assert text.count(stale) == 1
        text = text.replace(stale, 'the national-bank authority, Part 3 definitions and capital recognition inquiries\nare complete within scope, integrated through Version 2.42; next source work\nchecks institution classification and its clocks in §§3.100, 252.5 and 238.10.', 1)
    else:
        assert path.name == 'next-plan.md' and text.count(old_next) == 1
        text = text.replace('**177-page Version 2.41**', '**179-page Version 2.42**', 1)
        text = text.replace('manuscript-payout-definitions-20261012', 'manuscript-capital-recognition-20261012', 1).replace(old_hash, new_hash, 1)
        text = text.replace('Result: data/accounting-master/bank-capital-payout-dependencies-20261012/result.md', 'Result: data/accounting-master/bank-capital-recognition-20261012/result.md', 1)
        text = text.replace('## Completed boundary\n', '## Completed boundary\n\n' + summary + '\n## Preserved Version 2.41 income definitions and payout tables\n', 1)
        text = text.replace(old_next, new_next, 1)
    assert text != path.read_text() and 'Version 2.42' in text and 'not_ready' in text
    if path.name != 'accounting-continuation-requirements-20261007.md':
        assert text.count(new_next) == 1 and old_next not in text
    path.write_text(text)
    snap = OUT / 'pointers-after' / row['live']
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_bytes(path.read_bytes())
    rows.append({'live': row['live'], 'snapshot': str(snap.relative_to(ROOT)), 'sha256': sha(snap)})
save('controls-after.json', rows)
print(json.dumps({'controls_updated': len(rows), 'candidate': '2.42', 'stale_deep_instructions_repaired': 2, 'readiness': 'not_ready'}))
