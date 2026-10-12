"""Advance live controls while preserving historical source units."""
import json
import shutil
from complete_sources import OUT, ROOT, sha, save

assert not (OUT / 'completion.json').exists()
old_hash = 'c23bf198be1f79bec92204b074e93a01d09d736675a2df39ea20620c2000f44b'
new_hash = 'c06a9471f338e9ca79526a01ed1f9265512faeda163c8d2072baf1bf22c58f0c'
pdf = 'docs/design/proposal/manuscript-dividend-timing-20261012/accounting-product-proposal.pdf'
summary = '''The 176-page candidate adds declaration timing, conditional four-prior-year
input needs and regulatory election evidence on final PDF 116–117. The
1 December 2025 rule permits January early adoption before April effectiveness;
JPMorgan later reports the Firm elected it. Public-knowledge timing, actual
bank applicability and permissible payouts remain unresolved. All 103 source
and 119 integration checks pass; 48 displays and all 76 prior bibliography
entries remain, with two references added. Six final renders support the
bounded author review. Full readiness is not_ready.

Result: `data/accounting-master/national-bank-dividend-authority-20261012/result.md`.
'''
next_action = '''Inspect the explicit Part 3 dependencies: capital/distribution definitions
and payout limits, comparing dated text with the retained December 2025
amendment. Keep bank inputs, supervisory conditions and election/publication
facts separate; do not compute the issuer's permissible dividend. Plan:
`docs/plans/accounting-bank-capital-payout-dependencies-20261012.md`.
'''
old_next = '''Continue primary national-bank dividend-authority research following Note 26.
Verify official section identities, dated editions, conditions and dependencies;
do not treat the issuer summary or a later current page as verified law for
1 January 2026. Plan:
`docs/plans/accounting-national-bank-dividend-authority-20261012.md`.
'''
paths = [x['live'] for x in json.loads((OUT / 'baseline.json').read_text())['pointer_snapshots']]
for rel in paths:
    path = ROOT / rel
    text = path.read_text()
    if rel.endswith('accounting-master-checkpoint.md'):
        before, rest = text.split('## Current candidate\n', 1)
        text = before + '## Current candidate\n\n**Version 2.40, 176 pages**\nPDF: ' + pdf + '\nSHA256: ' + new_hash + '\n\n' + summary + '\n## Preserved Version 2.39 funding example\n' + rest
        assert old_next in text
        text = text.replace(old_next, next_action, 1)
    elif rel.endswith('next-plan.md'):
        before, rest = text.split('## Completed boundary\n', 1)
        before = before.replace('Version 2.39', 'Version 2.40').replace('manuscript-funds-transfer-20261012', 'manuscript-dividend-timing-20261012').replace(old_hash, new_hash).replace('jpmorgan-funds-transfer-20261012/result.md', 'national-bank-dividend-authority-20261012/result.md')
        text = before + '## Completed boundary\n\n' + summary + '\n## Preserved Version 2.39 funding example\n' + rest
        assert old_next in text
        text = text.replace(old_next, next_action, 1)
    elif rel.endswith('accounting-master-current.md'):
        before, rest = text.split('## Current Version 2.39 funding distinction\n', 1)
        before = before.replace('Version 2.39', 'Version 2.40').replace(old_hash, new_hash)
        before = before.replace('Version 2.40 distinguishes dated dividend capacity and consolidated restricted\ncash from parent cash.', 'Version 2.40 adds declaration timing and regulatory election evidence.\nVersion 2.39 distinguishes dated dividend capacity and restricted cash from parent cash.')
        before = before.replace('the Note 26 source inquiry', 'the primary dividend-authority inquiry').replace('Note 26 integrated; next source unit checks primary national-bank dividend authority', 'dividend timing integrated; next unit checks Part 3 definitions and payout limits')
        text = before + '## Current Version 2.40 declaration and election timing\n\n' + summary + '\n## Exact next action\n\n' + next_action + '\n## Preserved Version 2.39 funding distinction\n' + rest
        text = text.replace('official 2025 adoption explanation and a checked Ping An original/restated-history example |', 'official 2025 adoption explanation and a checked Ping An original/restated-history example; primary national-bank dividend conditions and the Version 2.40 election/timing case |')
        text = text.replace('Keep the broader corporate, financing and bank queue below |', 'Continue the explicit Part 3 capital/payout dependencies exposed by the national-bank inquiry. Keep the broader corporate, financing and bank queue below |')
    else:
        anchor = '## Current Version 2.39 restricted resources and funding\n'
        assert anchor in text
        text = text.replace(anchor, '## Current Version 2.40 declaration and election timing\n\nE07/C05/P18; MC02–05/19/21/25/28/30/32–35, G4/G7/G8/G13/G18.\n' + summary + '\n## Preserved Version 2.39 restricted resources and funding\n', 1)
        text = text.replace('next source work inspects primary national-bank dividend authority.', 'the national-bank authority inquiry and Version 2.40 are complete within scope;\nnext source work checks Part 3 definitions and payout limits.')
    path.write_text(text)
    snapshot = OUT / 'pointers-after' / rel
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, snapshot)
save('controls-after.json', [{'live': rel, 'snapshot': str((OUT / 'pointers-after' / rel).relative_to(ROOT)),
                             'sha256': sha(ROOT / rel)} for rel in paths])
print(json.dumps({'updated': paths, 'version': '2.40', 'readiness': 'not_ready'}))
