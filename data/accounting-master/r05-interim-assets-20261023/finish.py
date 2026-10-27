"""Record the completed source check and refresh four controls once."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
from verify import U, R, sha, load, check

PLAN = R / 'docs/plans/accounting-r05-interim-assets-20261023.md'
SUPPLEMENT = R / 'data/accounting-master/readability-repair-20261022-theta/r05-interim-assets-supplement.json'
rel = lambda p: str(p.relative_to(R))
HEADER = '''## 23 October 2026 — E3 interim asset candidates checked

Current question: future OCF predictive accuracy for the same nine companies,
next full fiscal year, pre-start cutoff and equal company weights. Annual and
latest retained interim total-assets candidates are mapped. Four interim rows
have dated source roles; none has exact-version historical admission.
Next: the distinct EU regulation lead, then exact-version release evidence.
Q, time weights, refit/service, inference and resources remain open. No user
question is pending. Latest retained does not mean latest publicly released.

'''
FRONTIER = '''The interim asset inquiry is complete at
data/accounting-master/r05-interim-assets-20261023/: nine consolidated totals,
19 anchors, four existing dated roles and one actually viewed balance sheet.
Henkel's third-period column, Midea's group/parent columns and Munich Re's
adjusted comparative are preserved. These are candidate mappings only; later
public interim reports outside the retained corpus remain possible.

Next E3 dependency: inspect the EU regulation using a distinct official lead,
then investigate exact-version release evidence. All192 historical admissions
remain false. Future Q, time weights, service/refit, inference and resources
remain open. No empirical study or whole-row closure follows. Read-only replay:
data/accounting-master/r05-interim-assets-20261023/verify.py. Completed records
stay immutable; no global continuation veto or pending user question.

'''

def write(path, data):
    with path.open('x') as f:
        json.dump(data, f, indent=2); f.write('\n')

def main():
    assert not (U / 'completion.json').exists()
    assert not (U / 'run-manifest.json').exists() and not SUPPLEMENT.exists()
    checks = check()
    start = load(U / 'start.json')
    edits = []
    for name in start['controls']:
        original = (U / 'controls-before' / name).read_bytes()
        assert (R / name).read_bytes() == original, name
        before = original.decode()
        marker = 'Next E3 dependency: map latest retained interim total-assets candidates beside\n'
        assert before.count(marker) == 1
        a = before.index(marker); b = before.index('Completed review evidence:',a)
        after = before[:a] + FRONTIER + before[b:]
        a = after.index('## 23 October 2026 — E3 total-assets candidates checked')
        b = after.index('## 22 October 2026', a)
        edits.append((name, after[:a] + HEADER + after[b:]))
    now = datetime.now(timezone.utc)
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U / 'run-manifest.json', {'git_commit':start['head'],'branch':start['branch'],
        'environment':sys.executable,'python_version':platform.python_version(),
        'cpu_gpu':'CPU only; GPU devices intentionally hidden; no ML framework imported',
        'data_version':'coverage-selected nine FY2025 interim sources bound in candidates.json',
        'random_seeds':'N/A; deterministic source and rational-unit checks',
        'started_utc':start['started_utc'],'completed_utc':now.isoformat(),
        'wall_time_seconds':(now-datetime.fromisoformat(start['started_utc'])).total_seconds(),
        'commands':[prefix+rel(U/n) for n in ('prepare.py','record_candidates.py','verify.py','finish.py')],
        'render_command':'pdftoppm -f 14 -l 14 -r 110 -singlefile -png data/financial-report-benchmark/documents/munich_re/munich_re-2025-interim_h1/original.pdf '+rel(U/'munich-interim-assets-page14'),
        'visual_inspection':'view_image on munich-interim-assets-page14.png; actually viewed',
        'plan':rel(PLAN),'result':rel(U/'result.md'),'output_paths':[rel(U),rel(SUPPLEMENT)]})
    write(SUPPLEMENT, {'scope':'nine interim asset candidates and inherited timing roles',
        'result':rel(U/'result.md'),'result_sha256':sha(U/'result.md'),'checks':checks,
        'candidate_version':'3.48','readiness':'not_ready','whole_rows_closed':0})
    for name,after in edits:
        snapshot = U / 'controls-after' / name
        snapshot.parent.mkdir(parents=True,exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R / name).write_text(after)
    assert check() == checks
    paths = [p for p in U.rglob('*') if p.is_file()] + [PLAN,SUPPLEMENT]
    write(U/'completion.json', {'status':'complete_documentary_mapping','checks':checks,
        'bindings':{rel(p):sha(p) for p in sorted(paths)},'replay':'verify.py; read only'})
    assert check() == checks
    print(json.dumps({'status':'completed and verified',**checks}))

if __name__ == '__main__':
    main()
