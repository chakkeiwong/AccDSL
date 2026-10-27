"""Record Apple event evidence without changing frozen corpus date statuses."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RESULT = 'data/accounting-master/apple-annual-filing-events-20261012/result.md'
FRONTIER = 'data/accounting-master/apple-annual-filing-events-20261012/next-source-frontier.md'
NOTE = ("Eight original Apple 2018–2025 Form 10-K events are identified from retained\n"
        "official SEC metadata, with 43 passing source/cover/date checks. Exact\n"
        "accessions, filing dates, acceptance clocks and selected file hashes are\n"
        "preserved. Seven selected annual PDF dates remain unverified; cover\n"
        "identity does not prove selected-byte availability on the filing date.\n"
        "The frozen 56 verified/136 unverified assessment and Version 2.37 stay\n"
        "unchanged. Full readiness is not_ready. Result:\n`" + RESULT + "`.\n")
NEXT = ("Continue E01/G13 historical availability with a bounded audit of the one\n"
        "unverified Caterpillar selected annual slot. Check existing records before\n"
        "choosing a new source action, then preserve official event dates separately\n"
        "from selected-file as-of availability. Larger non-US backlogs remain.\n"
        "Do not repeat the completed Apple or JPMorgan event extraction or infer\n"
        "publication from URL/PDF timestamps. A direct version or dated release\n"
        "source is required for any stronger selected-file admission.\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    baseline = json.loads((OUT / 'baseline.json').read_text())
    outputs = {}
    for item in baseline['pointer_snapshots']:
        path = ROOT / item['live']
        assert sha(path) == item['sha256'] == sha(ROOT / item['snapshot'])
        s = path.read_text()
        if path.name == 'accounting-master-checkpoint.md':
            a, b = s.index('## Exact next action'), s.index('The [debt-perimeter source unit]')
            s = s[:a] + '## Latest Apple filing-event evidence\n\n' + NOTE + '\n## Exact next action\n\n' + NEXT + '\n' + s[b:]
        elif path.name == 'accounting-master-current.md':
            marker = '## Preserved Version 2.36 integration — entity label superseded'
            assert s.count(marker) == 1
            s = s.replace(marker, '## Apple annual filing-event evidence\n\n' + NOTE + '\n' + marker, 1)
        elif path.name == 'accounting-continuation-requirements-20261007.md':
            marker = '## Latest source-only inquiry'
            assert s.count(marker) == 1
            s = s.replace(marker, '## Latest Apple annual filing-event evidence\n\n'
                          'E01/MC01/04/05/30/33–35; G5/G11/G13/G18.\n' + NOTE +
                          '\n## Preserved junior-debt source-only inquiry', 1)
            s = s.replace('Latest source/result: `data/accounting-master/jpmorgan-junior-reconciliation-20261012/result.md`.',
                          'Latest source/result: `' + RESULT + '`.')
            s = s.replace('Next frontier: `data/accounting-master/jpmorgan-junior-reconciliation-20261012/next-source-frontier.md`.',
                          'Next frontier: `' + FRONTIER + '`.')
        else:
            a, b = s.index('## Next bounded unit'), s.index('## Wider queue and stop rules')
            s = s[:a] + '## Latest Apple filing-event evidence\n\n' + NOTE + '\n## Next bounded unit\n\n' + NEXT + '\n' + s[b:]
        assert baseline['current_pdf_sha256'] in s and 'not_ready' in s
        outputs[path] = s
    for path, content in outputs.items():
        path.write_text(content)
    print(json.dumps({'updated_controls': len(outputs), 'candidate': 'Version 2.37 unchanged'}))


if __name__ == '__main__':
    main()
