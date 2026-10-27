"""Move four live controls to the corrected candidate once, preserving snapshots."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD_SHA = '751965e694bb2f2825d49b53710753fc3797af2f646ce3f17d489767f13117c6'
NEW_SHA = '9e6d0b433ebdbc30b65a17122dcbb2834b3c63d195b31ffaf2bea68eaa1fc880'
PDF = 'docs/design/proposal/manuscript-junior-classification-20261012/accounting-product-proposal.pdf'
RESULT = 'data/accounting-master/accounting-proposal-v237-integration-20261012/result.md'
NOTICE = ("The Note 20 junior-subordinated band is separately displayed after the\n"
          "Subsidiaries subtotal. The previous source unit and Version 2.36 incorrectly\n"
          "assigned it a Subsidiaries label; that claim is withdrawn. The correction\n"
          "passes 23 source/layout/arithmetic checks and 12 closeout checks. Version\n"
          "2.37 preserves the exact two-year 1,594/1,603 million residual while leaving\n"
          "legal issuer and accounting mechanism unverified. The prior source unit and\n"
          "2.36 files remain frozen; their passing checks did not detect this hierarchy\n"
          "error. Correction result:\n"
          "`data/accounting-master/jpmorgan-junior-classification-repair-20261012/result.md`.\n")
SUMMARY = ("The separate 174-page candidate corrects the unsupported junior-debt entity\n"
           "label on final PDF 116. All 149 integration checks pass; all other inherited\n"
           "prose, 48 displays and 75 bibliography entries remain. Twelve final page\n"
           "renders bind the bank slice, with only page 116 changed from Version 2.36.\n"
           "The corrected paragraph and its source boundary were read at normal\n"
           "resolution. Independent/human/domain/legal acceptance remains pending.\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_one(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


def checkpoint(source):
    source = replace_one(source, '**Version 2.36, 174 pages**', '**Version 2.37, 174 pages**')
    source = replace_one(source, 'manuscript-debt-perimeter-20261012', 'manuscript-junior-classification-20261012')
    source = replace_one(source, OLD_SHA, NEW_SHA)
    source = source.replace('accounting-proposal-v236-integration-20261012/result.md',
                            'accounting-proposal-v237-integration-20261012/result.md', 1)
    source = source.replace('accounting-proposal-v236-integration-20261012/four-ledger-review.md',
                            'accounting-proposal-v237-integration-20261012/four-ledger-review.md', 1)
    a, b = source.index('The bounded integration passes'), source.index('## Exact next action')
    source = source[:a] + SUMMARY + '\n' + NOTICE + '\n' + source[b:]
    source = replace_one(source, 'reading is complete (50 source, 47 closeout checks); the exact arithmetic',
                         'reading is preserved (50 source, 47 closeout checks), with the corrected\nentity label above controlling; the exact arithmetic')
    source = replace_one(source, 'Four pre-2.36 live controls are preserved in the Version 2.36 unit',
                         'Four pre-2.37 live controls are preserved in the Version 2.37 unit')
    return source


def current(source):
    a = source.index('## Current Version 2.36 integration')
    head = source[:a].replace('Version 2.36', 'Version 2.37').replace(OLD_SHA, NEW_SHA)
    head = head.replace('The subsequent Note 20/33 debt reading and Version 2.37 integration distinguish',
                        'The Note 20/33 debt reading and Version 2.36 integration distinguish')
    section = ('## Current Version 2.37 correction\n\n' + SUMMARY + '\n' + NOTICE +
               '\nPDF: ' + PDF + '\nResult: ' + RESULT + '\nFull readiness is not_ready.\n\n')
    tail = source[a:].replace('## Current Version 2.36 integration',
                              '## Preserved Version 2.36 integration — entity label superseded', 1)
    tail = tail.replace('## Preserved Version 2.36 integration — entity label superseded\n',
                        '## Preserved Version 2.36 integration — entity label superseded\n\n'
                        'Its junior-debt entity label is superseded by the Version 2.37 correction above.\n', 1)
    return head + section + tail


def supplement(source):
    marker = '## Current Version 2.36 bounded integration'
    new_section = ('## Current Version 2.37 source-fidelity correction\n\n'
                   'E01/E07/P18; MC01/02/03/05/08/15/16/21/28/30/32–35, G4/G5/G7/G11/G13.\n'
                   + SUMMARY + '\n' + NOTICE + '\nPDF: ' + PDF + '\nSHA256: ' + NEW_SHA +
                   '\nResult: ' + RESULT + '\nFull readiness is not_ready.\n\n')
    source = replace_one(source, marker,
                         new_section + '## Preserved Version 2.36 — junior-debt label superseded\n\n'
                         'Its entity-label claim is withdrawn by the Version 2.37 correction above.')
    source = replace_one(source, 'after Version 2.36 with the specific junior-subordinated instruments',
                         'after Version 2.37 with the specific junior-subordinated instruments')
    source = replace_one(source, 'Latest source/result: `data/accounting-master/accounting-proposal-v236-',
                         'Latest source/result: `data/accounting-master/accounting-proposal-v237-')
    source = replace_one(source, 'Next frontier: `data/accounting-master/accounting-proposal-v236-',
                         'Next frontier: `data/accounting-master/accounting-proposal-v237-')
    source = replace_one(source, 'Current candidate: 174-page Version 2.36, PDF SHA256 `' + OLD_SHA + '`; Version 2.35',
                         'Current candidate: 174-page Version 2.37, PDF SHA256 `' + NEW_SHA + '`; Version 2.36, Version 2.35')
    source = replace_one(source, 'advance through the 2025 parent-only income/cash example. The current',
                         'advance through the 2025 parent-only income/cash example. The preserved')
    return source


def next_plan(source):
    source = replace_one(source, '**174-page Version 2.36**', '**174-page Version 2.37**')
    source = replace_one(source, 'manuscript-debt-perimeter-20261012', 'manuscript-junior-classification-20261012')
    source = replace_one(source, OLD_SHA, NEW_SHA)
    source = replace_one(source, 'accounting-proposal-v236-integration-20261012/result.md',
                         'accounting-proposal-v237-integration-20261012/result.md')
    a, b = source.index('Version 2.36 adds'), source.index('Preserved Version 2.34')
    source = source[:a] + SUMMARY + '\n' + NOTICE + '\n' + source[b:]
    source = replace_one(source, 'Check completed\nunits to avoid duplication, then search the retained complete 2025 filing',
                         'Use the corrected\nseparate junior band, not the withdrawn Subsidiaries label. Reuse the saved\n2025 page-indexed search and inspect other direct source leads')
    return source


def main():
    baseline = json.loads((OUT / 'baseline.json').read_text())
    transforms = {
        'docs/plans/accounting-master-checkpoint.md': checkpoint,
        'docs/plans/accounting-master-current.md': current,
        'docs/plans/accounting-continuation-requirements-20261007.md': supplement,
        'data/accounting-master/next-plan.md': next_plan,
    }
    outputs = {}
    for item in baseline['pointer_snapshots']:
        live = ROOT / item['live']
        snapshot = ROOT / item['snapshot']
        assert sha(snapshot) == item['sha256'] == sha(live), item['live']
        outputs[live] = transforms[item['live']](live.read_text())
    for live, content in outputs.items():
        assert 'Version 2.37' in content and NEW_SHA in content and 'not_ready' in content
        live.write_text(content)
    print(json.dumps({'controls_updated': len(outputs), 'candidate_sha256': NEW_SHA}))


if __name__ == '__main__':
    main()
