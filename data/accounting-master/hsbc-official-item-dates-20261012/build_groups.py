"""Bind retained HSBC results-group dates to child links, not release dates."""
import hashlib
import json
import shutil
import time
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE_SHA = '15b074f6222ba6ff2ec2667e19317f2dd8b3e079497d88552bf8a08f8009a13d'
SOURCE = 'data/financial-report-benchmark/landing/hsbc/' + SOURCE_SHA + '.html'
CONTROLS = ['docs/plans/accounting-master-checkpoint.md',
            'docs/plans/accounting-master-current.md',
            'docs/plans/accounting-continuation-requirements-20261007.md',
            'data/accounting-master/next-plan.md']
PDF = 'docs/design/proposal/manuscript-junior-classification-20261012/accounting-product-proposal.pdf'
PDF_SHA = '9e6d0b433ebdbc30b65a17122dcbb2834b3c63d195b31ffaf2bea68eaa1fc880'
INVENTORY = 'data/accounting-master/publication-evidence-20261011/selected-date-inventory.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

class Rows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.stack = [], []
        self.download_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'tr':
            self.stack.append({'start_line': self.getpos()[0], 'cells': [],
                               'strongs': [], 'inputs': [], 'links': [],
                               'in_cell': False, 'in_strong': False})
        if tag == 'input' and 'data-url' in attrs:
            self.download_count += 1
        if not self.stack:
            return
        row = self.stack[-1]
        if tag == 'td':
            row['cells'].append('')
            row['in_cell'] = True
        if tag == 'strong':
            row['strongs'].append('')
            row['in_strong'] = True
        if tag == 'input' and 'data-url' in attrs:
            row['inputs'].append({'line': self.getpos()[0], 'attributes': attrs})
        if tag == 'a' and 'href' in attrs:
            row['links'].append({'line': self.getpos()[0], 'href': attrs['href']})

    def handle_data(self, data):
        if self.stack:
            row = self.stack[-1]
            if row['in_cell']:
                row['cells'][-1] += data
            if row['in_strong']:
                row['strongs'][-1] += data

    def handle_endtag(self, tag):
        if not self.stack:
            return
        row = self.stack[-1]
        if tag == 'td':
            row['in_cell'] = False
        if tag == 'strong':
            row['in_strong'] = False
        if tag == 'tr':
            row['end_line'] = self.getpos()[0]
            for key in ['cells', 'strongs']:
                row[key] = [' '.join(s.split()) for s in row[key]]
            self.rows.append(self.stack.pop())

def main():
    started = time.monotonic()
    assert not (OUT / 'completion.json').exists(), 'Closed unit stays frozen'
    assert not (OUT / 'baseline.json').exists(), 'Do not overwrite baseline snapshots'
    checks = []
    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})
        assert value, name
    ck('retained archive hash', sha(ROOT / SOURCE) == SOURCE_SHA)
    provenance = [r for r in json.loads((ROOT / 'data/financial-report-benchmark/source-access.json').read_text())
                  if r.get('local_path') == SOURCE]
    ck('unique official capture', len(provenance) == 1)
    provenance = provenance[0]
    ck('capture metadata agrees', provenance['sha256'] == SOURCE_SHA and provenance['http_status'] == 200
       and provenance['url'] == 'https://www.hsbc.com/investors/results-and-announcements/all-reporting/group')
    parser = Rows()
    parser.feed((ROOT / SOURCE).read_text())
    ck('all rows closed', not parser.stack)
    ck('160 retained download inputs', parser.download_count == 160)
    coverage = json.loads((ROOT / 'data/financial-report-benchmark/coverage.json').read_text())
    selected = {r['period_year']: r for r in coverage['rows'] if r['issuer_id'] == 'hsbc' and r['report_class'] == 'annual'}
    ck('eight selected annual reports', set(selected) == set(range(2018, 2026)))
    inventory = json.loads((ROOT / INVENTORY).read_text())
    counts = Counter(r['selected_date_status'] for r in inventory)
    ck('192 selected reports and 136 unverified dates', len(inventory) == 192 and
       sum(n for status, n in counts.items() if status.startswith('not_verified')) == 136)
    ck('all sixteen HSBC dates unverified', sum(r['document_id'].startswith('hsbc-') and r['selected_date_status'] == 'not_verified' for r in inventory) == 16)
    records = []
    for year, date, iso, relation in [(2024, '19 Feb 2025', '2025-02-19', 'alternate_url'),
                                      (2025, '25 Feb 2026', '2026-02-25', 'exact_selected_url')]:
        title = f'Annual Results {year} documents'
        candidates = [r for r in parser.rows if title in r['strongs']]
        ck(f'{year} unique parent row', len(candidates) == 1)
        row = candidates[0]
        ck(f'{year} date in first parent cell', row['cells'][0] == date)
        annual = [i for i in row['inputs'] if 'Annual Report and Accounts' in i['attributes'].get('data-title', '')]
        english = [i for i in annual if i['attributes']['data-title'] == f'Annual Report and Accounts {year}']
        ck(f'{year} unique English report', len(english) == 1)
        item = english[0]
        attrs = item['attributes']
        ck(f'{year} real hyperlink agrees', any(a['href'] == attrs['data-url'] for a in row['links']))
        ck(f'{year} child date repeats parent', attrs['data-date'] == date)
        ck(f'{year} input lies inside row', row['start_line'] < item['line'] < row['end_line'])
        absolute = urljoin('https://www.hsbc.com', attrs['data-url'])
        actual_relation = 'exact_selected_url' if absolute == selected[year]['source_url'] else 'alternate_url'
        ck(f'{year} selected URL relation', actual_relation == relation)
        ck(f'{year} selected PDF hash', sha(ROOT / selected[year]['local_path']) == selected[year]['sha256'])
        chinese = [i for i in annual if 'Chinese' in i['attributes']['data-title']]
        ck(f'{year} Chinese repeated date recorded', len(chinese) == 1 and chinese[0]['attributes']['data-date'] == date)
        records.append({'report_year': year, 'parent_title': title, 'parent_date_text': date,
                        'results_group_date': iso, 'parent_start_line': row['start_line'],
                        'parent_end_line': row['end_line'], 'english_report': item,
                        'official_report_url': absolute, 'selected_report': selected[year],
                        'selected_url_relation': relation, 'annual_report_inputs': annual,
                        'all_child_date_attributes': dict(Counter(i['attributes'].get('data-date') for i in row['inputs'])),
                        'individual_file_publication_date': 'not_verified', 'selected_byte_as_of_admission': 'none'})
    annual_inputs = [i for r in parser.rows for i in r['inputs'] if 'Annual Report and Accounts' in i['attributes'].get('data-title', '')]
    ck('six annual report inputs only in two groups', len(annual_inputs) == 6
       and sum(len(r['annual_report_inputs']) for r in records) == 6)
    ck('current candidate unchanged', sha(ROOT / PDF) == PDF_SHA)
    snapshots = []
    for rel in CONTROLS:
        dest = OUT / 'pointers-before' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
        snapshots.append({'live': rel, 'snapshot': str(dest.relative_to(ROOT)), 'sha256': sha(dest)})
    write('baseline.json', {'current_pdf': PDF, 'current_pdf_sha256': PDF_SHA,
                           'pointer_snapshots': snapshots, 'frozen_sources': {p: sha(ROOT / p) for p in
                           ['data/financial-report-benchmark/coverage.json', INVENTORY]}})
    write('dated-results-groups.json', {'source': provenance, 'records': records,
          'absent_annual_report_years_in_this_capture': list(range(2018, 2024)),
          'frozen_date_inventory_counts_unchanged': {'verified': 56, 'unverified': 136},
          'date_interpretation': 'parent results-group dates; individual file publication is not established',
          'url_digit_interpretation': 'caution only; no independent publication dates inferred',
          'selected_byte_admissions': 0})
    write('checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0, 'wall_seconds': time.monotonic() - started})
    print(json.dumps({'passed': len(checks), 'failed': 0, 'group_years': [r['report_year'] for r in records], 'byte_admissions': 0}))

if __name__ == '__main__':
    main()
