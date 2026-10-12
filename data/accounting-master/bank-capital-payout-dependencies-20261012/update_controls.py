"""Advance live controls once and retain the before/after bytes."""
import json
from build_candidate import OUT, ROOT, sha, save

assert not (OUT / 'completion.json').exists()
baseline = json.loads((OUT / 'baseline.json').read_text())
summary = '''The 177-page candidate distinguishes Part 3 eligible retained income from
Part 5 retained net income and explains the amended covered-bank payout tables
on final PDF 117–118. A hypothetical history gives $2m versus $10m; supplied
buffer inputs give 40% from Table 1 but 0% from Table 2. Actual bank facts,
capital recognition, reporting reconciliation and supervisory conditions remain
unresolved. All 52 source/arithmetic and 122 integration checks pass; all 48
displays and 78 prior bibliography entries survive, with two references added.
Eight final renders support bounded author review. Full readiness is not_ready.

Result: `data/accounting-master/bank-capital-payout-dependencies-20261012/result.md`.
'''
next_old = '''Inspect the explicit Part 3 dependencies: capital/distribution definitions
and payout limits, comparing dated text with the retained December 2025
amendment. Keep bank inputs, supervisory conditions and election/publication
facts separate; do not compute the issuer's permissible dividend. Plan:
`docs/plans/accounting-bank-capital-payout-dependencies-20261012.md`.'''
next_new = '''Inspect capital eligibility and deductions in dated §§3.20 and 3.22,
retaining instrument conditions, ordering, elections and institution scope.
Do not substitute reported equity or debt labels for regulatory capital or
compute a named bank's permissible dividend. Plan:
`docs/plans/accounting-bank-capital-recognition-20261012.md`.'''
old_hash = 'c06a9471f338e9ca79526a01ed1f9265512faeda163c8d2072baf1bf22c58f0c'
new_hash = '8a0903f51fe5ba03a618ad186e430c8b33ed9789cc1c294410ee24b41a38fbc3'
rows = []
for row in baseline['pointer_snapshots']:
    path = ROOT / row['live']
    assert sha(path) == row['sha256'] == sha(ROOT / row['snapshot'])
    text = path.read_text()
    if path.name == 'accounting-master-checkpoint.md':
        text = text.replace('## Current candidate\n', '## Preserved Version 2.40 declaration and election timing\n', 1)
        marker = '## Preserved Version 2.40 declaration and election timing\n'
        current = ('## Current candidate\n\n**Version 2.41, 177 pages**\n'
                   'PDF: docs/design/proposal/manuscript-payout-definitions-20261012/accounting-product-proposal.pdf\n'
                   f'SHA256: {new_hash}\n\n' + summary + '\n## Next bounded unit\n\n' + next_new + '\n\n')
        text = text.replace(marker, current + marker, 1)
    elif path.name == 'accounting-master-current.md':
        text = text.replace('Version 2.40 adds declaration timing and regulatory election evidence.',
                            'Version 2.41 distinguishes the two income measures and combined payout tables.\nVersion 2.40 preserves declaration timing and regulatory election evidence.', 1)
        text = text.replace('**176-page Version 2.40**', '**177-page Version 2.41**', 1).replace(old_hash, new_hash, 1)
        text = text.replace('Current through Version 2.40 and the primary dividend-authority inquiry', 'Current through Version 2.41 and the Part 3 definition inquiry', 1)
        text = text.replace('Current; dividend timing integrated; next unit checks Part 3 definitions and payout limits', 'Current; Part 3 definitions integrated; next unit checks capital eligibility and deductions', 1)
        text = text.replace('Current through Version 2.40 and the latest bounded source inquiries', 'Current through Version 2.41 and the latest bounded source inquiries', 1)
        text = text.replace('Version 2.40 outputs', 'Version 2.41 outputs', 1)
        text = text.replace('delivered through Version 2.40', 'delivered through Version 2.41', 1)
        text = text.replace('current baseline is Version 2.40', 'current baseline is Version 2.41', 1)
        marker = '## Current Version 2.40 declaration and election timing\n'
        assert text.count(marker) == 1 and text.count(next_old) == 1
        text = text.replace(marker, '## Current Version 2.41 income definitions and payout tables\n\n' + summary + '\n## Preserved Version 2.40 declaration and election timing\n', 1)
        text = text.replace(next_old, next_new, 1)
        text = text.replace('primary national-bank dividend conditions and the Version 2.40 election/timing case', 'primary national-bank dividend conditions, Version 2.40 timing and Version 2.41 income/table case', 1)
        text = text.replace('Continue the explicit Part 3 capital/payout dependencies exposed by the national-bank inquiry.', 'Continue the capital eligibility/deduction dependencies after the completed Part 3 income/table inquiry.', 1)
    elif path.name == 'accounting-continuation-requirements-20261007.md':
        marker = '## Current Version 2.40 declaration and election timing\n'
        text = text.replace(marker, '## Current Version 2.41 income definitions and payout tables\n\nE07/C05/P18; MC02–05/16/19/21/25/28/30/32–35, G4/G7/G8/G13/G18.\n' + summary + '\n## Preserved Version 2.40 declaration and election timing\n', 1)
        text = text.replace('the national-bank authority inquiry and Version 2.40 are complete within scope;\nnext source work checks Part 3 definitions and payout limits.', 'the national-bank authority and Part 3 definition inquiries are complete within\nscope, integrated through Version 2.41; next source work checks capital\neligibility and deductions in §§3.20 and 3.22.', 1)
    else:
        assert path.name == 'next-plan.md' and text.count(next_old) == 1
        text = text.replace('**176-page Version 2.40**', '**177-page Version 2.41**', 1)
        text = text.replace('manuscript-dividend-timing-20261012', 'manuscript-payout-definitions-20261012', 1).replace(old_hash, new_hash, 1)
        text = text.replace('Result: data/accounting-master/national-bank-dividend-authority-20261012/result.md', 'Result: data/accounting-master/bank-capital-payout-dependencies-20261012/result.md', 1)
        text = text.replace('## Completed boundary\n', '## Completed boundary\n\n' + summary + '\n## Preserved Version 2.40 declaration and election timing\n', 1)
        text = text.replace(next_old, next_new, 1)
    assert text != path.read_text() and 'Version 2.41' in text and 'not_ready' in text
    path.write_text(text)
    snap = OUT / 'pointers-after' / row['live']
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_bytes(path.read_bytes())
    rows.append({'live': row['live'], 'snapshot': str(snap.relative_to(ROOT)), 'sha256': sha(snap)})
save('controls-after.json', rows)
print(json.dumps({'controls_updated': len(rows), 'candidate': '2.41', 'readiness': 'not_ready'}))
