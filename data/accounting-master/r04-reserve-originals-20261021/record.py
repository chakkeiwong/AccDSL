"""Bind a completed bounded access inquiry; never re-run after completion."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
S = U / 'sources'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
bind = lambda p: {'path': str(p.relative_to(R)), 'sha256': sha(p)}
now = datetime.now(timezone.utc).isoformat()
assert not (U / 'completion.json').exists(), 'Completed inquiry is immutable'

urls = {
 '02-papers': 'https://people.math.ethz.ch/~wueth/papers.html',
 '04-ssrn': 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2524352',
 '06-england-crossref': 'https://api.crossref.org/works/10.1016/j.insmatheco.2018.12.002',
 '09-city-record': 'https://openaccess.city.ac.uk/id/eprint/21270/',
 '10-elsevier-article-api': 'https://dev.elsevier.com/documentation/ArticleRetrievalAPI.wadl',
 '11-wang-full-xml': 'https://api.elsevier.com/content/article/PII:016766879500010P?view=FULL&httpAccept=text%2Fxml',
 '12-england-full-xml': 'https://api.elsevier.com/content/article/PII:S0167668718301033?view=FULL&httpAccept=text%2Fxml',
 '13-wang-publisher': 'https://linkinghub.elsevier.com/retrieve/pii/016766879500010P',
 '14-wang-sciencedirect': 'https://www.sciencedirect.com/science/article/pii/016766879500010P',
 '15-england-sciencedirect': 'https://www.sciencedirect.com/science/article/pii/S0167668718301033',
 '16-cas-search': 'https://www.casact.org/search?search_api_fulltext=Insurance%20pricing%20and%20increased%20limits%20ratemaking',
 '17-eth-search': 'https://www.research-collection.ethz.ch/search?query=Claims%20run-off%20uncertainty%3A%20the%20full%20picture',
 '18-cas-corrected-search': 'https://www.casact.org/search?query=Insurance%20pricing%20and%20increased%20limits%20ratemaking',
}
dispositions = {
 '01-eth': 'Sandbox DNS failure; no response body',
 '01-eth-trusted': 'Successful trusted author-page response; original exact URL not recovered',
 '02-papers': 'Author list identifies Merz/Wuthrich SSRN2524352/2014',
 '03-wang-crossref': 'Exact-title metadata match; original query URL not recovered',
 '04-ssrn': 'Challenge HTML; no paper',
 '05-merz-crossref': 'Exact-title metadata match; original query URL not recovered',
 '06-england-crossref': 'Journal identity; empty relation is not a correction-status check',
 '07-wang-api': 'Invalid view/request; does not establish access barrier',
 '08-england-api': 'Invalid view/request; does not establish access barrier',
 '09-city-record': 'Institutional page labels linked PDF Accepted Version',
 '10-elsevier-article-api': 'API specification permits FULL view and XML',
 '11-wang-full-xml': '401 Invalid API Key; no credentialed request attempted',
 '12-england-full-xml': '401 Invalid API Key; no credentialed request attempted',
 '13-wang-publisher': 'Redirect HTML; no technical text',
 '14-wang-sciencedirect': '403 content-provision error; no paper',
 '15-england-sciencedirect': '403 content-provision error; no paper or correction check',
 '16-cas-search': 'Wrong parameter; not evidence about exact-title availability',
 '17-eth-search': '429 explicit rate-limit page; no retry in this unit',
 '18-cas-corrected-search': 'Correct form parameter; inspected first page supplied no matching original',
}

def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')

receipts = []
for h in sorted(S.glob('*.headers')):
    stem = h.stem
    bodies = [p for p in S.glob(stem + '.*') if p.suffix in ('.html', '.json', '.xml')]
    if not bodies and (S / (stem + '.txt')).exists():
        bodies = [S / (stem + '.txt')]
    assert len(bodies) <= 1, stem
    header = h.read_text(errors='replace')
    status = re.findall(r'^HTTP/\S+\s+(\d+)', header, re.M)
    dates = re.findall(r'^date:\s*(.+)$', header, re.I | re.M)
    types = re.findall(r'^content-type:\s*(.+)$', header, re.I | re.M)
    body = bodies[0] if bodies else None
    command = None
    if int(stem[:2]) >= 9:
        command = ['curl', '--connect-timeout', '15', '--max-time', '45', '--location',
                   '--silent', '--show-error', '--dump-header', str(h.relative_to(R)),
                   '--output', str(body.relative_to(R)), '--write-out',
                   'status=%{http_code} bytes=%{size_download} type=%{content_type} effective=%{url_effective}\n', urls[stem]]
    receipts.append({'id': stem, 'url': urls.get(stem),
        'url_status': 'retained current-turn command or predecessor explicit URL' if stem in urls else 'original request URL not recovered',
        'command_argv': command, 'command_status': 'current-turn command' if command else 'exact original command not recovered',
        'request_started_utc': None, 'start_time_status': 'not captured; do not substitute server Date or file mtime',
        'server_date': dates[-1].strip() if dates else None,
        'filesystem_mtime_utc': datetime.fromtimestamp(h.stat().st_mtime, timezone.utc).isoformat(),
        'inventory_utc': now, 'http_status': int(status[-1]) if status else None,
        'content_type': types[-1].strip() if types else None,
        'headers': bind(h), 'body': bind(body) if body else None,
        'body_bytes': body.stat().st_size if body else 0, 'disposition': dispositions[stem]})
write('acquisition-receipts.json', {'receipts': receipts, 'no_new_technical_source': True})

papers = [
 {'id': 'wang1995', 'doi': '10.1016/0167-6687(95)00010-P',
  'identity': 'Title/author/journal match in retained Crossref record',
  'technical_text': 'Not acquired or inspected in this unit',
  'routes': ['03-wang-crossref', '07-wang-api', '11-wang-full-xml', '13-wang-publisher', '14-wang-sciencedirect', '18-cas-corrected-search']},
 {'id': 'merz2014', 'doi': '10.2139/ssrn.2524352',
  'identity': 'Author page and Crossref identify SSRN2524352/2014; later revision date unverified',
  'technical_text': 'Not acquired or inspected in this unit',
  'routes': ['02-papers', '04-ssrn', '05-merz-crossref', '17-eth-search']},
 {'id': 'england2019', 'doi': '10.1016/j.insmatheco.2018.12.002',
  'identity': 'Journal metadata match; institutional deposit labelled Accepted Version',
  'technical_text': 'Retained accepted manuscript read in predecessor; final-journal comparison unavailable',
  'routes': ['06-england-crossref', '08-england-api', '09-city-record', '12-england-full-xml', '15-england-sciencedirect']},
]
write('source-support-ledger.json', {'papers': papers,
    'status': 'No new original technical text admitted; route-specific blocks retained',
    'correction_retraction_status': 'Not established; metadata relation and failed publisher pages are insufficient',
    'predecessor': bind(R / 'data/accounting-master/r04-reserve-risk-20261020/source-support-ledger.json')})
write('citation-venue-ledger.json', {'scope': 'Retained Crossref snapshot; counts explanatory only',
    'records': [{'id': 'wang1995', 'count': 189, 'source': 'sources/03-wang-crossref.json'},
                {'id': 'merz2014', 'count': 13, 'source': 'sources/05-merz-crossref.json'},
                {'id': 'england2019', 'count': 16, 'source': 'sources/06-england-crossref.json'}],
    'date': '2026-10-21; exact request start times unavailable', 'venue_rank': 'not evaluated',
    'interpretation': 'No correctness, priority or ranking conclusion follows from counts'})
write('backward-snowball-ledger.json', {'new_technical_reference_lists_inspected': 0,
    'reason': 'No new technical paper acquired',
    'predecessor': bind(R / 'data/accounting-master/r04-reserve-risk-20261020/backward-snowball-ledger.json')})
write('forward-snowball-ledger.json', {'scope': 'Original/final identity and correction-status inquiry only',
    'new_citing_papers_inspected': 0, 'correction_status': 'unresolved',
    'next': 'A new accessible primary source or publisher correction record is required'})
write('claim-support-ledger.json', {'claims': [
    {'claim': 'City labels its England deposit Accepted Version', 'support': 'sources/09-city-record.html', 'status': 'checked source wording'},
    {'claim': 'FULL is a permitted Article Retrieval view', 'support': 'sources/10-elsevier-article-api.html', 'status': 'checked source wording'},
    {'claim': 'Corrected unauthenticated full-XML routes returned401 Invalid API Key', 'support': ['sources/11-wang-full-xml.xml', 'sources/12-england-full-xml.xml'], 'status': 'checked responses'},
    {'claim': 'Final publication has the same PH-weight defect', 'status': 'not checked; not admitted'},
    {'claim': 'No correction exists', 'status': 'unsupported; not admitted'}]})
write('omission-risk-ledger.json', {'open': [
    {'id': p['id'], 'reason': p['technical_text'], 'disposition': 'Hold dependent technical claim; do not substitute metadata'} for p in papers],
    'non_exhaustive': True, 'next': 'Continue independent documentary work while preserving original-source dependencies'})

ledger = load(U / 'source-ledger.json')
ledger['status'] = 'bounded_access_inquiry_complete_technical_dependencies_open'
ledger['receipts'] = 'acquisition-receipts.json'
ledger['result'] = 'result.md'
ledger['access_limits'] = 'SSRN and publisher403; corrected Elsevier API401; ETH429; inspected CAS first page has no matching original. These do not establish global unavailability.'
(U / 'source-ledger.json').write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
assessment_path = R / 'data/accounting-master/readability-repair-20261021/assessment-successor.json'
operations_path = R / 'data/accounting-master/readability-repair-20261021/operation-successor.json'
assessment, operations = load(assessment_path), load(operations_path)
assert len(assessment['rows']) == 53 and len(assessment['interactions']) == 6
assert len(operations['rows']) == 46 and all(r['full_requirement_closed'] is False for r in operations['rows'])
assert assessment['readiness'] == 'not_ready'
retained = R / ledger['retained_related_source']['path']
assert sha(retained) == ledger['retained_related_source']['sha256'] == 'd195f617ffacdb72e6f5f445d54b829cb1f47ad6dc4d0fbe55cc67b06cc70268'
statuses = {r['id']: r['http_status'] for r in receipts}
assert statuses['09-city-record'] == statuses['10-elsevier-article-api'] == 200
assert statuses['11-wang-full-xml'] == statuses['12-england-full-xml'] == 401
assert statuses['14-wang-sciencedirect'] == statuses['15-england-sciencedirect'] == 403
assert statuses['17-eth-search'] == 429 and statuses['18-cas-corrected-search'] == 200
write('assessment-supplement.json', {'baseline': bind(assessment_path), 'operations': bind(operations_path),
    'requirements': ['MC10', 'MC11', 'MC12', 'MC18', 'MC22', 'MC26', 'MC29', 'MC30', 'MC32', 'MC33', 'MC34', 'MC35'],
    'result': bind(U / 'result.md'), 'rows': 53, 'interactions': 6, 'operation_count': 46,
    'whole_rows_closed': 0, 'readiness': 'not_ready', 'candidate_unchanged': '3.46'})
write('run-manifest.json', {'recorded_utc': now,
    'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip(),
    'environment': sys.executable, 'cpu_gpu': 'CPU only; CUDA_VISIBLE_DEVICES=-1; GPU intentionally hidden',
    'data_version': 'Retained primary metadata and access responses; no new technical paper',
    'random_seeds': 'N/A acquisition and deterministic documentary checks',
    'wall_time_seconds': None, 'wall_time_status': 'Aggregate elapsed time not captured; no inference from approval waits',
    'commands': 'acquisition-receipts.json records exact current-turn curl argv; predecessor command gaps explicit',
    'record_command': 'CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r04-reserve-originals-20261021/record.py',
    'network_permissions': 'Current-turn curl requests used require_escalated and existing curl prefix',
    'plan': bind(R / 'docs/plans/accounting-reserve-originals-20261021.md'),
    'result': bind(U / 'result.md'), 'output_directory': str(U.relative_to(R))})
files = [p for p in U.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
files.append(R / 'docs/plans/accounting-reserve-originals-20261021.md')
write('completion.json', {'scope': 'Bounded access inquiry only; original technical questions remain open',
    'bindings': {str(p.relative_to(R)): sha(p) for p in sorted(files)}})
print(json.dumps({'receipts': len(receipts), 'files_bound': len(files), 'new_technical_papers': 0,
                  'whole_rows_closed': 0, 'readiness': 'not_ready'}))
