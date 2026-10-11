"""Record six older HSBC results groups; do not infer file release dates."""
import hashlib
import importlib.util
import json
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'data/accounting-master/hsbc-official-item-dates-20261012'
SOURCE_SHA = 'c4207a0649d2233fd39bce12b803715ec9e70f30fa4b0246e7bbfb7bb9715bb9'
SOURCE = 'data/financial-report-benchmark/landing/hsbc/' + SOURCE_SHA + '.html'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n')

def main():
    start = time.monotonic()
    assert not (OUT / 'baseline.json').exists(), 'Do not replace preserved baseline'
    spec = importlib.util.spec_from_file_location('hsbc_rows', PRIOR / 'build_groups.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    checks = []
    def ck(name, ok):
        checks.append({'name': name, 'passed': bool(ok)})
        assert ok, name
    ck('second source identity', sha(ROOT / SOURCE) == SOURCE_SHA)
    access = json.loads((ROOT / 'data/financial-report-benchmark/source-access.json').read_text())
    provenance = [r for r in access if r.get('local_path') == SOURCE]
    ck('unique official paginated capture', len(provenance) == 1 and provenance[0]['sha256'] == SOURCE_SHA
       and provenance[0]['url'] == 'https://www.hsbc.com/investors/results-and-announcements/all-reporting/group?page=1&take=100'
       and provenance[0]['http_status'] == 200)
    parser = mod.Rows()
    parser.feed((ROOT / SOURCE).read_text())
    ck('balanced table rows', not parser.stack)
    coverage = json.loads((ROOT / 'data/financial-report-benchmark/coverage.json').read_text())
    selected = {r['period_year']: r for r in coverage['rows'] if r['issuer_id'] == 'hsbc' and r['report_class'] == 'annual'}
    expected = {2018: ('19 Feb 2019', '2019-02-19'), 2019: ('18 Feb 2020', '2020-02-18'),
                2020: ('23 Feb 2021', '2021-02-23'), 2021: ('22 Feb 2022', '2022-02-22'),
                2022: ('21 Feb 2023', '2023-02-21'), 2023: ('21 Feb 2024', '2024-02-21')}
    records = []
    for year, (date, iso) in expected.items():
        title = f'Annual Results {year} documents'
        rows = [r for r in parser.rows if title in r['strongs']]
        ck(f'{year} unique English parent', len(rows) == 1)
        row = rows[0]
        ck(f'{year} parent date', row['cells'][0] == date)
        items = [i for i in row['inputs'] if i['attributes'].get('data-title') == f'Annual Report and Accounts {year}']
        ck(f'{year} unique report', len(items) == 1)
        item = items[0]
        attrs = item['attributes']
        ck(f'{year} real href agrees', any(a['href'] == attrs['data-url'] for a in row['links']))
        ck(f'{year} row contains input', row['start_line'] < item['line'] < row['end_line'])
        ck(f'{year} input repeats group date', attrs['data-date'] == date)
        ck(f'{year} exact selected URL', urljoin('https://www.hsbc.com', attrs['data-url']) == selected[year]['source_url'])
        ck(f'{year} selected byte identity', sha(ROOT / selected[year]['local_path']) == selected[year]['sha256'])
        records.append({'report_year': year, 'parent_title': title, 'parent_date_text': date,
                        'results_group_date': iso, 'parent_start_line': row['start_line'],
                        'parent_end_line': row['end_line'], 'english_report': item,
                        'selected_report': selected[year], 'selected_url_relation': 'exact_selected_url',
                        'individual_file_publication_date': 'not_verified', 'selected_byte_as_of_admission': 'none'})
    prior = json.loads((PRIOR / 'dated-results-groups.json').read_text())
    for old in prior['records']:
        rows = [r for r in parser.rows if old['parent_title'] in r['strongs']]
        ck(str(old['report_year']) + ' duplicate control unchanged', len(rows) == 1
           and rows[0]['cells'][0] == old['parent_date_text']
           and old['english_report'] in rows[0]['inputs'])
    extra = [r for r in parser.rows if 'Annual Results 2018 additional Chinese documents' in r['strongs']]
    ck('Chinese-only group excluded', len(extra) == 1 and not any(
       i['attributes'].get('data-title') == 'Annual Report and Accounts 2018' for i in extra[0]['inputs']))
    ck('2023 filename digit discrepancy explicit', records[-1]['english_report']['attributes']['data-url'].split('/')[-1].startswith('240226-')
       and records[-1]['results_group_date'] == '2024-02-21')
    inventory = json.loads((ROOT / mod.INVENTORY).read_text())
    ck('frozen date counts', len(inventory) == 192
       and sum(r['selected_date_status'].startswith('not_verified') for r in inventory) == 136)
    ck('candidate unchanged', sha(ROOT / mod.PDF) == mod.PDF_SHA)
    snapshots = []
    for rel in mod.CONTROLS:
        dest = OUT / 'pointers-before' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
        snapshots.append({'live': rel, 'snapshot': str(dest.relative_to(ROOT)), 'sha256': sha(dest)})
    inputs = [SOURCE, 'data/financial-report-benchmark/source-access.json',
              'data/financial-report-benchmark/coverage.json', mod.INVENTORY,
              str((PRIOR / 'build_groups.py').relative_to(ROOT)), str((PRIOR / 'dated-results-groups.json').relative_to(ROOT))]
    write('baseline.json', {'current_pdf': mod.PDF, 'current_pdf_sha256': mod.PDF_SHA,
                           'pointer_snapshots': snapshots, 'frozen_sources': {p: sha(ROOT / p) for p in inputs}})
    write('dated-results-groups.json', {'source': provenance[0], 'records': records,
          'recent_duplicate_controls': [2024, 2025], 'excluded_chinese_group_start_line': extra[0]['start_line'],
          'url_date_discrepancy': '2023 group 21 Feb 2024; selected URL starts 240226; neither proves individual release',
          'selected_byte_admissions': 0, 'frozen_date_inventory_counts_unchanged': {'verified': 56, 'unverified': 136}})
    write('checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0, 'wall_seconds': time.monotonic() - start})
    print(json.dumps({'source_checks': len(checks), 'failed': 0, 'years': list(expected), 'byte_admissions': 0}))

if __name__ == '__main__':
    main()
