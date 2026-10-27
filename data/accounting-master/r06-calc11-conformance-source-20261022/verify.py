"""Freeze the bounded source result once; no-argument replay is read-only."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
PLAN = R / 'docs/plans/accounting-r06-calc11-conformance-source-20261022.md'
SUPPLEMENT = REVIEW / 'r06-calc11-conformance-source-supplement.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def check():
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip() == p['head']
    assert sha(R / '.git/index') == p['index_sha256']
    rows = [x for x in subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'],cwd=R,text=True).split('\0') if x]
    assert {x[3:] for x in rows} == set(p['tracked_dirty']) and all(x[:2]==' M' for x in rows)
    for name,digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R/name) == digest, name
    d = load(U/'source-ledger.json')
    assert len(d['sources']) == 3 and len(d['anchors']) == 18
    texts = {}
    for s in d['sources']:
        for key in ('body','visible'):
            assert sha(R/s[key]['path']) == s[key]['sha256']
        receipt = load(R/s['receipt'])
        assert receipt['exit_code'] == 0 and receipt['metrics']['http_code'] == 200
        assert (R/s['body']['path']).stat().st_size == receipt['metrics']['size_download']
        texts[s['id']] = ' '.join((R/s['visible']['path']).read_text().split())
    old = d['prior_recommendation']
    assert sha(R/old['path']) == old['sha256']
    texts['prior-recommendation'] = ' '.join((R/old['path']).read_text().split())
    for a in d['anchors']:
        first,last = a['normalized_character_span']
        assert texts[a['source']][first:last] == a['quote'], a['id']
    assert d['suite']['status'] == 'not_requested_members_only_listing'
    assert d['suite']['url'] in d['sources'][0]['links']
    assert all('conformance/' not in load(R/s['receipt'])['url'] for s in d['sources'])
    examples = load(U/'exact-examples.json')
    assert examples['actual_sum'] == 12141123+45441321 == 57582444
    assert Fraction(examples['rounded_sum_millions']) == Fraction(121+454,10)
    assert [Fraction(x) for x in examples['calculated_interval_millions']] == [Fraction(5740,100),Fraction(5760,100)]
    assert [Fraction(x) for x in examples['overlap_millions']] == [Fraction(5755,100),Fraction(5760,100)]
    assert examples['finer_interval'] == ['5450','5550']
    assert examples['intersection'] == ['5450','5500']
    assert examples['authored_exact_total'] == 5525
    assert examples['finest_only_accepts'] and not examples['intersection_accepts']
    assert 5450 <= 5525 <= 5550 and not 5450 <= 5525 <= 5500
    a,o = load(REVIEW/'assessment-successor.json'),load(REVIEW/'operation-successor.json')
    assert (len(a['rows']),len(a['interactions']),len(o['rows'])) == (53,6,46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    return p, {'sources':3,'anchors':18,'claims':6,'suite_tests_read':0,
               'exact_source_arithmetic':'passed','protected_files':len(p['protected']),
               'tracked_dirty_paths':len(rows),'whole_rows_closed':0,'readiness':'not_ready'}


def record(p, checks):
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (U/'completion.json').exists() and not SUPPLEMENT.exists()
    assert not (U/'run-manifest.json').exists()
    replacement = '''The bounded official Calculations 1.1 inquiry is complete at
data/accounting-master/r06-calc11-conformance-source-20261022/: three public
documents and 18 anchors preserve a members-only suite listing (no suite was
requested or read). The complete 2022 requirements support same-context
alignment, without correcting Recommendation 5.1. Their most-precise duplicate
instruction differs from the final interval-intersection rule; exact source
examples expose the difference. Section 5.4 remains unresolved. The title/URL
date25May2022 differs from the indexes'22May. No policy or manuscript changes.
Read-only replay: verify.py without flags. No whole row closes.

Next: inspect the newly linked public Calculations 2.0 requirements for the
scope and prerequisites of cross-context calculations, under a bounded audited
source plan. This is design preparation, not adoption of a draft standard.
Other ready R03–R06 work remains eligible. Preserve exhausted source routes
and completed finite checks; do not restart the completed manuscript review.

'''
    edits = []
    for name in p['controls']:
        before = (R/name).read_text()
        start = before.index('Next: continue the ready internal R03–R06 source/method preparation after a')
        end = before.index('Completed review evidence:',start)
        edits.append((name,before[:start]+replacement+before[end:]))
    write(U/'checks.json',checks)
    receipts = [load(R/s['receipt']) for s in load(U/'source-ledger.json')['sources']]
    write(U/'run-manifest.json',{
        'git_commit':p['head'],'branch':p['branch'],'environment':sys.executable,
        'python':platform.python_version(),'cpu_gpu':'CPU only; GPU devices intentionally hidden; standard library only',
        'data_version':'Three exact official responses and retained corrected Recommendation; see source-ledger.json',
        'seeds':'N/A deterministic documentary comparison and exact rational examples',
        'first_acquisition_start_utc':receipts[0]['started_utc'],
        'recorded_utc':datetime.now(timezone.utc).isoformat(),
        'wall_time':'Not measured as a continuous inquiry; curl request durations preserved separately',
        'request_seconds':[x['metrics']['time_total'] for x in receipts],
        'timestamp_qualification':'protection.json started_utc is inherited from the predecessor review, not this inquiry start',
        'commands':[x['command'] for x in receipts]+[
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'prepare.py'),
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'build_records.py'),
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'verify.py')+' --record',
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'verify.py')],
        'plan':rel(PLAN),'result':rel(U/'result.md'),'output':rel(U)})
    write(SUPPLEMENT,{
        'scope':'Public Calculations 1.1 requirements and suite access listing; source-only',
        'candidate_version':'3.48','candidate_pdf':bind(R/'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment':bind(REVIEW/'assessment-successor.json'),
        'protected_operations':bind(REVIEW/'operation-successor.json'),
        'completed_author_review':bind(REVIEW/'regression/completion.json'),
        'all_original_obligations':53,'interactions':6,'operations':46,'whole_rows_closed':0,'readiness':'not_ready',
        'plan':bind(PLAN),'result':bind(U/'result.md'),'review':bind(U/'review.md'),'checks':checks,
        'manuscript_changed':False,'runtime_admitted':False,'independent_human_acceptance':'pending'})
    for name,after in edits:
        (R/name).write_text(after)
        target=U/'controls-after'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x') as stream:
            stream.write(after)
    check()
    files=[path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    files += [PLAN,SUPPLEMENT]
    write(U/'completion.json',{'status':'complete_source_inquiry_no_policy_promotion',
        'checks':checks,'bindings':{rel(path):sha(path) for path in sorted(files)},
        'control_replay_policy':'Immutable before/after snapshots; live controls may advance in successor units'})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--record',action='store_true')
    args=parser.parse_args()
    p,checks=check()
    if args.record:
        record(p,checks)
    c=load(U/'completion.json')
    for name,digest in c['bindings'].items():
        assert sha(R/name)==digest,name
    assert load(U/'checks.json')==c['checks']==checks
    print(json.dumps({'status':'recorded and verified' if args.record else 'read-only replay passed',**checks}))


if __name__=='__main__':
    main()
