from pathlib import Path
import hashlib, json, re
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import unquote

R = Path('/home/chakwong/python/AccDSL')
O = R / 'data/accounting-master/simulation-monograph-20261026'
C = R / 'docs/design/proposal/manuscript-simulation-foundations-20261026'
CURRENT = R / 'docs/design/proposal/manuscript-bank-exact-profile-20261026'
CURRENT_OUT = R / 'data/accounting-master/bank-time-manuscript-integration-20261026'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
B = json.loads((O / 'build-check.json').read_text())
M = json.loads((O / 'run-manifest.json').read_text())
assert M['artifacts']['builds'] == B
import fitz
current_verification = json.loads((CURRENT_OUT / 'verification.json').read_text())
assert current_verification['version'] == '5.1' and current_verification['pages'] == 715
assert sha(CURRENT / 'accounting-product-proposal.pdf') == current_verification['pdf_sha256']
assert current_verification['simulation_sources_preserved'] == 26
assert current_verification['passed_preservation']
assert not current_verification['new_warnings'] and not current_verification['out_of_page_text_blocks']
simulation_paths = [str(p.relative_to(C)) for p in (C / 'simulation').glob('*.tex')]
for relative in simulation_paths + ['simulation-foundations.tex', 'references.bib']:
    assert (CURRENT / relative).read_bytes() == (C / relative).read_bytes(), relative
current_pages = {}
standalone_rendered_text_preserved = False
for stem in ['accounting-product-proposal', 'simulation-foundations']:
    pdf = fitz.open(CURRENT / (stem + '.pdf'))
    current_pages[stem] = len(pdf)
    assert len(pdf) == (715 if stem == 'accounting-product-proposal' else 170)
    log = (CURRENT / (stem + '.log')).read_text()
    blg = (CURRENT / (stem + '.blg')).read_text()
    assert not re.search(r'Overfull|There were undefined|Missing character|multiply defined|duplicate ignored|destination.*already', log, re.I)
    assert not re.search(r'Warning--', blg)
    if stem == 'simulation-foundations':
        previous_pdf = fitz.open(C / (stem + '.pdf'))
        assert len(previous_pdf) == len(pdf)
        for index, page in enumerate(pdf):
            assert page.get_text() == previous_pdf[index].get_text(), ('standalone text changed', index + 1)
            for block in page.get_text('blocks'):
                x0, y0, x1, y1 = block[:4]
                assert min(x0, y0) >= -0.5 and x1 <= page.rect.width + 0.5 and y1 <= page.rect.height + 0.5
        standalone_rendered_text_preserved = True
links = []
for label, stem in [('latest', 'accounting-product-proposal'), ('simulation-foundations', 'simulation-foundations')]:
    for ext in ['pdf', 'tex']:
        link = R / 'docs' / ('AccDSL-' + label + '.' + ext)
        target = CURRENT / (stem + '.' + ext)
        assert link.is_symlink() and link.exists()
        assert not link.readlink().is_absolute()
        assert link.resolve() == target.resolve()
        assert sha(link) == sha(target)
        links.append({'path': str(link.relative_to(R)), 'target': str(link.readlink()), 'sha256': sha(link)})

cat = json.loads((R / 'scripts/accounting_master_catalog.json').read_text())
before = json.loads((CURRENT_OUT / 'control-before/scripts/accounting_master_catalog.json').read_text())
note = cat['active_execution_note']
allowed = {'latest_result', 'current_candidate', 'current_pdf', 'current_pdf_sha256', 'active_work_plan', 'remaining_work'}
assert {k:v for k,v in note.items() if k not in allowed} == {k:v for k,v in before['active_execution_note'].items() if k not in allowed}
assert {k:v for k,v in cat.items() if k != 'active_execution_note'} == {k:v for k,v in before.items() if k != 'active_execution_note'}
assert note['current_candidate'] == '5.1;715 pages;not_ready'
assert note['current_pdf_sha256'] == current_verification['pdf_sha256']
assert (R / note['current_pdf']).resolve() == (CURRENT / 'accounting-product-proposal.pdf').resolve()
assert note['latest_result'] == 'data/accounting-master/bank-time-manuscript-integration-20261026/result.md'
assert note['active_work_plan'] == 'docs/plans/accounting-invariant-source-authoring-20261026.md'
assert note['remaining_work'] == 'data/accounting-master/bank-time-manuscript-integration-20261026/remaining-work.md'

checkpoint_paths = [
    'docs/plans/accounting-product-design-checkpoint.md',
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-master-program.md',
    'docs/plans/accounting-mission-requirements.md',
    'docs/plans/accounting-master-current.md',
    'docs/plans/accounting-current-program-20261025.md',
    'data/accounting-master/next-plan.md',
]
for relative in checkpoint_paths:
    text = (R / relative).read_text()
    headings = re.findall(r'^## (.+)$', text, re.M)
    assert headings[0] == 'Current governing candidate — Version 5.1 — 26 October 2026', relative
    first = text.split('\n## ', 2)[1]
    assert '715-page' in first and 'not_ready' in first, relative
    assert note['current_pdf_sha256'] in first, relative
    assert note['active_work_plan'] in text, relative
    assert '53 obligations' in first and 'six interactions' in first and '46 operations' in first, relative
    if len(headings) > 1:
        assert '5.0' in headings[1], relative
    assert '713-page' not in first and '713 pages' not in first, relative

markdown = [
    'docs/README.md',
    'docs/design/README.md',
    'docs/papers/README.md',
    'docs/archive/accounting-product-design-v1.2-20261026/ARCHIVE.md',
    'data/accounting-master/simulation-monograph-20261026/result.md',
]
checked_links = []
for relative in markdown:
    p = R / relative
    for url in re.findall(r'\[[^\]]+\]\(([^)]+)\)', p.read_text()):
        if '://' in url or url.startswith('#'):
            continue
        target = unquote(url.split('#', 1)[0])
        q = p.parent / target
        assert q.exists(), (relative, url)
        checked_links.append({'document': relative, 'link': url})

assert len(json.loads((O / 'failure-cases.json').read_text())['cases']) == 67
A = json.loads((O / 'arithmetic.json').read_text())
assert A['status'] == 'pass' and A['count'] == 169
S = json.loads((O / 'preservation-check.json').read_text())
assert S['inherited_sources_identical'] == 182 and S['archive_hashes'] == 32
assert not S['changed_inherited_sources'] and not S['archive_hash_failures']
BC = json.loads((O / 'bibliography-check.json').read_text())
assert BC['candidate_entries'] == 143 and BC['new_part_cited_sources'] == 26
assert not BC['missing_keys'] and not BC['duplicate_keys']
support = json.loads((O / 'source-support.json').read_text())
for row in support['records']:
    p = R / (row.get('local_path') or row.get('path'))
    assert p.exists() and sha(p) == row['local_sha256_verified']
assert B['accounting-product-proposal']['pdf_pages'] == 714
assert B['simulation-foundations']['pdf_pages'] == 170
assert B['simulation-foundations']['new_chapter_body_pages'] == 154
V = json.loads((O / 'visual/final-v450-integration-review.json').read_text())
assert V['pdf_sha256'] == B['accounting-product-proposal']['pdf_sha256']
for row in V['images']:
    assert sha(R / row['image']) == row['image_sha256']

for relative in ['docs/design/proposal/manuscript-simulation-foundations-20261026/README.md', 'data/accounting-master/simulation-monograph-20261026/result.md', 'data/accounting-master/simulation-monograph-20261026/requirements-map.md']:
    text = (R / relative).read_text()
    assert '714' in text, relative
    assert 'fe050f0e01147e3de819678ae94e19029f1803f9d08e8b6bc5749a0dfb0f42b2' not in text, relative
for relative in ['MISSION_CONTROL.md', 'docs/README.md', 'docs/design/proposal/manuscript-bank-exact-profile-20261026/README.md']:
    text = (R / relative).read_text()
    assert '715' in text and ('5.1' in text), relative

report = {
    'checked_at': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(),
    'status': 'pass',
    'scope': 'Final documentation navigation and evidence consistency; not product or human acceptance.',
    'stable_links': links,
    'checkpoint_heads': checkpoint_paths,
    'local_markdown_links_checked': len(checked_links),
    'catalog_successor_change_keys': sorted(allowed),
    'catalog_written_by_this_check': False,
    'active_work_plan_preserved': note['active_work_plan'],
    'remaining_work_preserved': note['remaining_work'],
    'phase_status_preserved': note['phase_status'],
    'archive_hashes': S['archive_hashes'],
    'failure_cases': 67,
    'arithmetic_checks': A['count'],
    'cited_new_part_sources': BC['new_part_cited_sources'],
    'bibliography_entries': BC['candidate_entries'],
    'source_copies_verified': len(support['records']),
    'delivered_version_5_0_pages': 714,
    'current_version': '5.1',
    'current_integrated_pdf_pages': 715,
    'standalone_pdf_pages': 170,
    'new_body_pages': 154,
    'standalone_rendered_text_preserved': standalone_rendered_text_preserved,
}
(O / 'final-navigation-check.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
