"""Check identity, exact source anchors and the declared finite diagnostic."""
import hashlib
import json
import time
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
assert not (OUT / 'completion.json').exists()
start = time.monotonic()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = []
def ck(name, value): checks.append({'name': name, 'passed': bool(value)})
b = json.loads((OUT / 'baseline.json').read_text())
for p, h in b['inputs'].items(): ck('protected input ' + p, sha(ROOT / p) == h)
e = json.loads((OUT / 'source-evidence.json').read_text())
ck('96-page identified source', len(fitz.open(ROOT / e['source'])) == e['source_pages'] == 96 and sha(ROOT / e['source']) == e['source_sha256'])
ck('nineteen exact text extracts', len(e['extracted_pages']) == 19 and all(sha(ROOT / r['text']) == r['sha256'] for r in e['extracted_pages']))
ck('six render bindings', len(e['renders']) == 6 and all(sha(ROOT / r['render']) == r['sha256'] and r['source_pdf_sha256'] == e['source_sha256'] for r in e['renders']))
ledger = json.loads((ROOT / 'docs/design/research/standards-support.json').read_text())
entry = next(r for r in ledger['records'] if r['id'] == 'aasb17')
ck('retained official identity', entry['sha256'] == e['source_sha256'] and entry['url'].startswith('https://www.aasb.gov.au/'))
anchors = [
 ('edition', 1, 'applies to annual periods beginning on or after 1 January 2023 but before 1 July 2026.'),
 ('B101(a)', 50, 'the contractual terms specify that the policyholder participates in a share of a clearly identified pool of underlying items'),
 ('B102', 50, 'using its expectations at inception of the contract and shall not reassess the conditions afterwards'),
 ('B104(b)', 50, 'the amount of the entity’s share of the fair value of the underlying items; less'),
 ('B104(b)(ii)', 50, 'fulfilment cash flows that do not vary based on the returns on underlying items.'),
 ('B106', 50, 'An entity need not hold the identified pool of underlying items.'),
 ('B107(b)(ii)', 51, 'on a present value probability-weighted average basis, not a best or worst outcome basis'),
 ('B108', 51, 'The entity’s assessment of the variability in paragraph B101(c) for this example will reflect a present value probability-weighted average of all these scenarios.'),
 ('B109', 51, 'Reinsurance contracts issued and reinsurance contracts held cannot be insurance contracts with direct participation features'),
 ('B111', 51, 'do not relate to future service and do not adjust the contractual service margin.'),
 ('B113(a)', 51, 'All the adjustments are measured using current discount rates.'),
 ('B113(b)', 51, 'for example, the effect of financial guarantees.'),
 ('B116', 51, 'a previously documented risk-management objective and strategy'),
 ('B116(b)', 52, 'credit risk does not dominate the economic offset.'),
 ('B118', 52, 'If, and only if, any of the conditions in paragraph B116 cease to be met'),
 ('48', 14, 'recognise a loss in profit or loss to the extent of that excess.'),
 ('B66(a)', 43, 'investment returns. Investments are recognised, measured and presented separately.'),
 ('Appendix A FCF', 29, 'An explicit, unbiased and probability-weighted estimate'),
 ('72', 18, 'The exercise of a right included in the terms of a contract is not a modification.'),
]
records = []
for paragraph, page, quote in anchors:
    p = OUT / 'text' / f'page-{page}.txt'
    text = ' '.join(p.read_text().split())
    at = text.find(quote)
    ck('source anchor ' + paragraph, at >= 0)
    records.append({'paragraph': paragraph, 'pdf_page': page, 'text': str(p.relative_to(ROOT)),
        'text_sha256': sha(p), 'quote': quote, 'normalized_start': at, 'normalized_end': at+len(quote),
        'offset_scope': 'Unicode code points in whitespace-normalized page text'})
(OUT / 'source-anchors.json').write_text(json.dumps(records, indent=2, ensure_ascii=False)+'\n')
f = json.loads((OUT / 'finite-diagnostic.json').read_text())
ck('15 finite arithmetic checks', f['passed'] == 15 and not f['failed'] and all(r['passed'] for r in f['checks']))
ck('three predeclared amounts left', [r['amount_left'] for r in f['rows']] == ['-10', '10', '12'])
ck('diagnostic contract retained', (OUT / 'diagnostic-contract.md').is_file())
failed = [r['name'] for r in checks if not r['passed']]
r = {'checks': checks, 'passed': len(checks)-len(failed), 'failed': failed, 'source_anchors': len(records),
     'finite_checks': f['passed'], 'wall_seconds': time.monotonic()-start,
     'scope': 'Source identity/anchors and declared payoff arithmetic; not accounting compliance, eligibility or valuation'}
(OUT / 'source-checks.json').write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['passed','failed','source_anchors','finite_checks','wall_seconds']}))
raise SystemExit(bool(failed))
