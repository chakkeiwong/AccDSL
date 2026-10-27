"""Freeze 3.37 documentary evidence; never execute held product work."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / 'data/accounting-master/sector-company-composition-20261016'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2) + '\n')


def verify_delta(path):
    delta = read(path)
    checks = [dict(name=x['path'], passed=sha(ROOT / x['path']) == x['sha256'])
              for x in delta['files']]
    checks.append(dict(name='predecessor-delta', passed=
                       sha(ROOT / delta['predecessor_delta']) == delta['predecessor_sha256']))
    for x in read(path.parent / 'render-manifest.json')['pages']:
        checks.append(dict(name='render/' + str(x['page']), passed=sha(ROOT / x['path']) == x['sha256']))
    return dict(checks=len(checks), failures=sum(not c['passed'] for c in checks),
                detail=checks, delta_sha256=sha(path))


def main():
    started = time.monotonic()
    assert not (OUT / 'review-delta.json').exists(), 'Frozen closeout must not be rerun'
    prior_check = verify_delta(PRIOR / 'review-delta.json')
    assert prior_check['failures'] == 0
    write(OUT / 'predecessor-integrity.json', prior_check)
    for x in read(OUT / 'input-lock.json')['files']:
        assert sha(ROOT / x['path']) == x['sha256'], x['path']
    ms = read(OUT / 'manuscript-checks.json')
    assert ms['failures'] == 0 and read(OUT / 'checks.json')['failures'] == 0
    assert sha(ROOT / ms['pdf']) == ms['pdf_sha256']
    for x in read(OUT / 'baseline-source-lock.json')['files']:
        assert sha(OUT / 'baseline-sources' / x['path']) == x['sha256']
        assert sha((ROOT / read(PRIOR / 'manuscript-checks.json')['pdf']).parent / x['path']) == x['sha256']
    whole = read(OUT / 'whole-render-manifest.json')
    assert whole['pdf_sha256'] == ms['pdf_sha256']
    assert [x['page'] for x in whole['pages']] == list(range(1, 390))
    for x in whole['sheets']:
        assert sha(ROOT / x['path']) == x['sha256']
    dense = read(OUT / 'dense-page-review/manifest.json')
    assert dense['pdf_sha256'] == ms['pdf_sha256']
    for x in dense['pages']:
        assert sha(ROOT / x['path']) == x['sha256']
    write(OUT / 'rendered-review.json', dict(
        date='2026-10-17', pdf=ms['pdf'], pdf_sha256=ms['pdf_sha256'],
        status='layout_overview_and_bounded_author_read_complete',
        overview_pages=list(range(1, 390)), overview_sheets=whole['sheets'],
        inherited_session_coverage='Sheets 1–3, pages 1–75; incremental contact sheets, per saved session handoff.',
        continuation_coverage='Sheets 4–16, pages 76–389; nine full-size page images.',
        full_size_pages=[210, 244, 289, 317, 341, 342, 351, 352, 369],
        full_size_image_pixels=[834, 1179], newly_read_section_pages=[341, 342, 351, 352],
        overview_resolution='At most 350x500 per page; sheet display reduced from 1800x2650 to 1304x1920.',
        semantic_review='semantic-review.md', whole_document_continuous_read='pending',
        independent_review='pending', human_acceptance='pending'))
    controls = []
    for name in ('docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md'):
        dest = OUT / 'controls-before' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        assert not dest.exists()
        shutil.copy2(ROOT / name, dest)
        controls.append(dict(path=name, sha256=sha(dest)))
    index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    write(OUT / 'preservation.json', dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
          git_commit=commit, index_sha256=hashlib.sha256(index).hexdigest(), controls=controls))
    prior = read(PRIOR / 'assessment-successor.json')
    new = deepcopy(prior)
    new.update(date='2026-10-17', candidate_version='3.37', candidate_pdf=ms['pdf'],
        candidate_pdf_sha256=ms['pdf_sha256'], predecessor=str((PRIOR / 'assessment-successor.json').relative_to(ROOT)),
        predecessor_sha256=sha(PRIOR / 'assessment-successor.json'),
        assessment_scope='Source, protocol and static reuse refresh; whole-PDF layout overview and bounded semantic reading; all 53 obligations retained.',
        metadata_correction='Successor I03/I04/I06 reflect delivered finite joins; first-slice prerequisites separated from later milestones. Earlier corrections remain in predecessor history.')
    affected = {'MC04','MC05','MC06','MC11','MC14','MC16','MC17','MC19','MC20','MC21','MC22','MC23','MC24','MC25','MC26','MC28','MC29','MC30','MC31','MC32','MC33','MC34','MC35','G4','G6','G7','G8','G9','G10','G13','G14','G18'}
    evidence = [dict(path=str((OUT / n).relative_to(ROOT)), sha256=sha(OUT / n)) for n in
        ('result.md','checks.json','source-dispositions.md','claim-successor.md','protocol-successor.md','reuse-successor.md','semantic-review.md','manuscript-result.md','rendered-review.json')]
    delta = ('New IFRIC 19/IAS 8 source boundaries do not settle early conversion or zero-weight CGU allocation. '
             'Eight changed method families retain separate E1–E6 targets. Static selected-source dependencies require Python >=3.10 '
             'and Pillow >=12.2.0,<13, without a resolved runtime. Whole-PDF layout and bounded semantic review preserve '
             'pending general methods, literature, independent/domain and human acceptance.')
    for row in new['rows']:
        row.update(previous_candidate_version=prior['candidate_version'], candidate_version='3.37',
                   candidate_pdf=ms['pdf'], candidate_pdf_sha256=ms['pdf_sha256'],
                   delta_assessment=delta if row['id'] in affected else 'Inherited judgment; not freshly reviewed.')
        if row['id'] in affected:
            row.setdefault('evidence_updates', []).extend(deepcopy(evidence))
    decisions = {
        'I03': ('P5 and SectorCompany/1 supply finite corporate and bank/insurer/guarantee legal/group closes, including tax, FX, gross cash and dated ownership. Wider capital, valuation and general composition remain open.',
                'Instrument-specific hedge reductions, aligned option components, dated credit schedules and earlier write-offs now have bounded methods. SectorCompany/1 joins shared legal books without adding component notional capital.'),
        'I04': ('SectorCompany/1 joins bank, insurance and guarantee components through shared legal books and statements while retaining distinct credit, cohort and prudential meanings. General sector engines and empirical valuation remain open.',
                'Delivered dated credit receipts/write-offs, insurance service/finance and retrospective measurements remain conditional on supplied facts. Their finite group composition does not validate credit forecasts, actuarial estimates or regulatory capital.'),
        'I05': ('Unsupported, failed and partial states remain explicit. Static dependency constraints and documentary field-loss obligations are inspected; runtime adapter loss and persistence remain unexecuted.',
                'Selected source declarations expose the Python/Pillow intersection, optional extras and native/terms frontier. No installed environment, lossless runtime exchange or distribution clearance is claimed.'),
        'I06': ('P5 and SectorCompany/1 derive tax, gross cash, eliminations, NCI and parent equity from legal books. Retained-control ownership changes affect subsequent attribution; actual law and broader ownership methods remain open.',
                'The sector case preserves the matched internal deposit, separate taxpayer origins, FX and NCI purchase cash 15 versus NCI carrying amount 12.96 and parent-equity debit 2.04. Whole-row closure is not inferred.')}
    for item in new['interactions']:
        if item['id'] in decisions:
            item['decision'], item['delta'] = decisions[item['id']]
            item['current_evidence'] = [str((OUT / 'semantic-review.md').relative_to(ROOT)), str((PRIOR / 'result.md').relative_to(ROOT))]
    first = new['first_implementation_slice']
    first['dependencies'] = ['source lowering/shared IR for the declared Core0 subset', 'admitted synthetic P5 inputs and operation schemas', 'atomic identity/replay/publication semantics', 'exact/adverse documentary expected exchanges']
    first['optional_import_path_dependencies'] = ['selected XBRL/PDF context-preserving exchange', 'platform-specific dependency lock, hashes and applicable notices', 'runtime compatibility under separate execution authority']
    first['later_milestones'] = ['real-package semantic/availability closure', 'wider corporate and financing methods', 'bank/insurance adapters and sector runtime', 'target-specific forecast and numerical validation']
    first['scope_note'] = 'The held bounded synthetic Core0/P5 slice does not claim wider mission closure. Later empirical or sector work is not a prerequisite for exact synthetic accounting checks.'
    checks = [dict(name=a['id'], passed=all(a[k] == b[k] for k in ('id','label','original_obligation','acceptance','recorded_status','historical_status')))
              for a, b in zip(prior['rows'], new['rows'])]
    checks += [dict(name='all53', passed=len(new['rows']) == 53),
               dict(name='six-interactions', passed=len(new['interactions']) == 6)]
    checks += [dict(name=x['id'] + '-identity-status', passed=all(x[k] == y[k] for k in ('id','question','status')))
               for x, y in zip(prior['interactions'], new['interactions'])]
    checks += [dict(name='predecessor-version', passed=all(x['previous_candidate_version'] == '3.36' for x in new['rows'])),
               dict(name='held-first-slice', passed=first['status'] == 'staged_after_execution_hold'),
               dict(name='acceptance-pending', passed=new['readiness'] == 'not_ready' and new['independent_review'] == new['human_acceptance'] == 'pending')]
    assert all(c['passed'] for c in checks)
    write(OUT / 'assessment-successor.json', new)
    write(OUT / 'assessment-checks.json', dict(checks=len(checks), failures=0, detail=checks))
    assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'], cwd=ROOT) == index
    write(OUT / 'closeout-manifest.json', dict(recorded_utc=datetime.now(timezone.utc).isoformat(), git_commit=commit,
        command='python3 data/accounting-master/source-protocol-reuse-refresh-20261016/closeout.py',
        environment=sys.executable + '; standard library only', gpu_status='N/A: no device/framework calls',
        random_seeds='N/A: deterministic integrity checks', data_version='Version 3.36 to 3.37',
        wall_seconds=round(time.monotonic()-started, 3), plan='docs/plans/accounting-whole-candidate-review-20261016.md',
        result=str((OUT / 'manuscript-result.md').relative_to(ROOT)), outputs=['assessment-successor.json','review-delta.json','review-delta-checks.json']))
    excluded = {'baseline-sources','controls-before','__pycache__'}
    files = [p for p in OUT.rglob('*') if p.is_file() and not any(x in excluded or x.startswith('render-attempt-') for x in p.relative_to(OUT).parts)]
    candidate = (ROOT / ms['pdf']).parent
    files += [p for p in candidate.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}]
    files += [ROOT / ms['pdf'], ROOT / 'docs/plans/accounting-source-protocol-reuse-refresh-20261016.md', ROOT / 'docs/plans/accounting-whole-candidate-review-20261016.md']
    write(OUT / 'review-delta.json', dict(version='3.37', candidate_pdf=ms['pdf'], candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor_delta=str((PRIOR / 'review-delta.json').relative_to(ROOT)), predecessor_sha256=sha(PRIOR / 'review-delta.json'),
        files=[dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for p in sorted(set(files))],
        scope='Fixed evidence and predecessor delta; page images bound by manifests; mutable controls excluded.',
        independent_review='pending', human_acceptance='pending', readiness='not_ready'))
    checked = verify_delta(OUT / 'review-delta.json')
    assert checked['failures'] == 0
    write(OUT / 'review-delta-checks.json', checked)
    print(json.dumps(dict(assessment_checks=len(checks), fixed_files=len(set(files)), integrity_checks=checked['checks'], failures=0)))


if __name__ == '__main__':
    main()
