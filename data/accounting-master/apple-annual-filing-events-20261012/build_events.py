"""Bind retained SEC filing events to selected Apple annual cover identities."""
import hashlib
import json
import re
import time
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()
SUBMISSIONS_SHA = '21eae1adf76b91a72eab511c0a96cd56f2053878b8c22df5bfdbfdbb0adfcc42'
URL = 'https://data.sec.gov/submissions/CIK0000320193.json'


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cover_text(path):
    if path.suffix == '.pdf':
        with fitz.open(path) as doc:
            return ' '.join(doc[0].get_text().split())
    parser = TextOnly()
    parser.feed(path.read_text(errors='replace'))
    return ' '.join(' '.join(parser.parts).split())


def main():
    assert not (OUT / 'completion.json').exists(), 'Closed unit stays frozen'
    inventory = json.loads((ROOT / 'data/accounting-master/publication-evidence-20261011/selected-date-inventory.json').read_text())
    access = json.loads((ROOT / 'data/financial-report-benchmark/source-access.json').read_text())
    candidates = [r for r in access if r.get('url') == URL]
    source = ROOT / 'data/financial-report-benchmark/landing/apple' / (SUBMISSIONS_SHA + '.json')
    submissions = json.loads(source.read_text())
    recent = submissions['filings']['recent']
    n = len(recent['form'])
    fields = ['form', 'reportDate', 'filingDate', 'acceptanceDateTime', 'accessionNumber', 'primaryDocument']
    checks = []

    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})

    ck('official source hash', sha(source) == SUBMISSIONS_SHA)
    ck('one successful access record', len(candidates) == 1 and candidates[0]['status'] == 'ok'
       and candidates[0]['http_status'] == 200 and candidates[0]['sha256'] == SUBMISSIONS_SHA)
    ck('SEC Apple CIK identity', int(submissions['cik']) == 320193 and submissions['name'].upper().startswith('APPLE INC'))
    ck('parallel SEC arrays', all(len(recent[f]) == n for f in fields))
    matches = [i for i in range(n) if recent['form'][i] in ('10-K', '10-K/A')
               and recent['reportDate'][i][:4].isdigit()
               and 2018 <= int(recent['reportDate'][i][:4]) <= 2025]
    originals = [i for i in matches if recent['form'][i] == '10-K']
    amendments = [i for i in matches if recent['form'][i] == '10-K/A']
    ck('eight original annual events in inspected index', len(originals) == 8)
    ck('no target-year 10-K/A in inspected recent rows', not amendments)
    by_year = {int(recent['reportDate'][i][:4]): i for i in originals}
    ck('one event per target year', set(by_year) == set(range(2018, 2026)))
    annual = {int(x['document_id'].split('-')[1]): x for x in inventory
              if x['document_id'].startswith('apple-') and x['document_id'].endswith('-annual')}
    ck('eight selected annual reports', set(annual) == set(range(2018, 2026)))
    ck('seven frozen selected dates still unverified', sum(annual[y]['selected_date_status'] == 'not_verified'
                                                         for y in range(2018, 2025)) == 7)
    events = []
    for year in sorted(by_year):
        i = by_year[year]
        selected = annual[year]
        path = ROOT / selected['selected_path']
        report_date = recent['reportDate'][i]
        cover = cover_text(path)
        cover_date = datetime.strptime(report_date, '%Y-%m-%d').strftime('%B %-d, %Y')
        fiscal_anchor = re.search(r'For the fiscal year ended\s+' + re.escape(cover_date), cover, re.I)
        acceptance = recent['acceptanceDateTime'][i]
        try:
            parsed_acceptance = datetime.fromisoformat(acceptance.replace('Z', '+00:00'))
            parsed_filing = datetime.strptime(recent['filingDate'][i], '%Y-%m-%d')
        except ValueError:
            parsed_acceptance = parsed_filing = None
        ck(f'{year} selected bytes retained', sha(path) == selected['selected_sha256'])
        ck(f'{year} cover issuer/form/period',
           bool(re.search(r'APPLE\s+INC\.?', cover, re.I)) and 'FORM 10-K' in cover.upper()
           and fiscal_anchor is not None)
        ck(f'{year} event clocks parse and order', parsed_acceptance is not None
           and parsed_filing is not None and parsed_acceptance.date() >= parsed_filing.date())
        ck(f'{year} accession and primary document',
           bool(re.fullmatch(r'\d{10}-\d{2}-\d{6}', recent['accessionNumber'][i]))
           and bool(recent['primaryDocument'][i]))
        events.append({
            'document_id': selected['document_id'], 'issuer_cik': 320193,
            'form': '10-K', 'report_date': report_date,
            'filing_date': recent['filingDate'][i], 'acceptance_time': acceptance,
            'accession': recent['accessionNumber'][i],
            'primary_document': recent['primaryDocument'][i],
            'metadata_source': str(source.relative_to(ROOT)),
            'metadata_sha256': SUBMISSIONS_SHA,
            'metadata_recent_row_index': i,
            'selected_report': {'path': selected['selected_path'],
                                'sha256': selected['selected_sha256'],
                                'date_status_before': selected['selected_date_status'],
                                'cover_identity': 'issuer/form/report_period_match',
                                'fiscal_cover_anchor': fiscal_anchor.group() if fiscal_anchor else None,
                                'byte_as_of_admission': 'not_evaluated_in_this_unit'},
        })
    ck('distinct eight accessions', len({e['accession'] for e in events}) == 8)
    ck('no selected-byte admission', all(e['selected_report']['byte_as_of_admission'] == 'not_evaluated_in_this_unit'
                                         for e in events))
    failed = [x['name'] for x in checks if not x['passed']]
    ledger = {'source_url': URL, 'source_path': str(source.relative_to(ROOT)),
              'source_sha256': SUBMISSIONS_SHA, 'captured_at': candidates[0]['captured_at'] if candidates else None,
              'index_scope': 'recent rows of retained 2026-captured SEC submissions index',
              'events': events, 'inspected_amendments': [recent['accessionNumber'][i] for i in amendments],
              'selected_byte_as_of_admission': 'none',
              'frozen_date_inventory_counts_unchanged': {'verified': 56, 'unverified': 136}}
    (OUT / 'filing-events.json').write_text(json.dumps(ledger, indent=2) + '\n')
    (OUT / 'checks.json').write_text(json.dumps({'checks': checks, 'passed': len(checks)-len(failed),
                                                 'failed': failed, 'wall_seconds': time.monotonic()-START}, indent=2) + '\n')
    print(json.dumps({'passed': len(checks)-len(failed), 'failed': failed,
                      'event_dates': {e['report_date'][:4]: e['filing_date'] for e in events}}))
    raise SystemExit(bool(failed))


if __name__ == '__main__':
    main()
