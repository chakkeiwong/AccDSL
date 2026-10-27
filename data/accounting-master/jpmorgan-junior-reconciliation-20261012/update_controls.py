"""Record the bounded source result and move independent work to availability."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RESULT = 'data/accounting-master/jpmorgan-junior-reconciliation-20261012/result.md'
FRONTIER = 'data/accounting-master/jpmorgan-junior-reconciliation-20261012/next-source-frontier.md'
NOTE = ("The bounded junior-debt inquiry passes 17 source/identity/search checks.\n"
        "The selected 2018 filing, printed 258/PDF 260, reports an issuer-trust\n"
        "liquidation and distribution of junior debentures, with a dated $659m\n"
        "carrying value. That historical passage does not identify the 2025\n"
        "instruments or reconcile the parent-only balance. The narrow current\n"
        "mapping remains unverified; no manuscript increment is warranted.\n"
        "Version 2.37 and readiness not_ready are unchanged. Result:\n"
        '`' + RESULT + '`.\n')
NEXT = ("Continue independent E01/G13 historical-availability preparation. Audit the\n"
        "selected 192-report panel and current date/provenance ledgers, then choose\n"
        "a bounded subset of the 136 reports with unverified publication dates.\n"
        "Require primary evidence for the exact selected report and distinguish\n"
        "filing, issuer publication, economic-period and ingestion clocks. Do not\n"
        "transfer dates from a later version or treat search timestamps as public\n"
        "availability. Preserve source hashes, dates, uncertainty and a skeptical\n"
        "plan before substantive extraction. The junior-debt question needs a new\n"
        "direct instrument/accounting source; do not repeat its exact-term search\n"
        "unchanged. A blocked claim does not stop the independent work.\n")


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
            s = s[:a] + '## Latest junior-debt source inquiry\n\n' + NOTE + '\n## Exact next action\n\n' + NEXT + '\n' + s[b:]
        elif path.name == 'accounting-master-current.md':
            old = '| [Direct next plan](../../data/accounting-master/next-plan.md) | Current; next unit investigates the junior-debt issuer and parent-only reconciliation |'
            assert old in s
            s = s.replace(old, '| [Direct next plan](../../data/accounting-master/next-plan.md) | Current; next unit audits historical availability dates for a bounded selected-report subset |', 1)
            marker = '## Preserved Version 2.36 integration — entity label superseded'
            assert s.count(marker) == 1
            s = s.replace(marker, '## Junior-debt source-only inquiry after Version 2.37\n\n' + NOTE + '\n' + marker, 1)
        elif path.name == 'accounting-continuation-requirements-20261007.md':
            marker = '## Current Version 2.37 source-fidelity correction'
            assert s.count(marker) == 1
            s = s.replace(marker, '## Latest source-only inquiry\n\nE01/E07; MC01/02/03/05/08/15/16/21/28/30/33–35.\n' + NOTE + '\n' + marker, 1)
            s = s.replace('after Version 2.37 with the specific junior-subordinated instruments and\nparent-only reconciliation.',
                          'after Version 2.37 with a bounded historical-availability subset. The\njunior-debt current mapping awaits a new direct instrument/accounting source.')
            s = s.replace('Latest source/result: `data/accounting-master/accounting-proposal-v237-integration-20261012/result.md`.', 'Latest source/result: `' + RESULT + '`.')
            s = s.replace('Next frontier: `data/accounting-master/accounting-proposal-v237-integration-20261012/next-source-frontier.md`.', 'Next frontier: `' + FRONTIER + '`.')
        else:
            a, b = s.index('## Next bounded unit'), s.index('## Wider queue and stop rules')
            s = s[:a] + '## Latest source-only inquiry\n\n' + NOTE + '\n## Next bounded unit\n\n' + NEXT + '\n' + s[b:]
        assert baseline['current_pdf_sha256'] in s and 'not_ready' in s
        outputs[path] = s
    for path, text in outputs.items():
        path.write_text(text)
    print(json.dumps({'updated_controls': len(outputs), 'candidate': 'Version 2.37 unchanged'}))


if __name__ == '__main__':
    main()
