"""Read-only by default; one-time completion of a bounded access inquiry."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R/'docs/plans/accounting-r05-conditional-predictive-edition-20261023.md'
REVIEW = R/'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW/'r05-conditional-predictive-edition-supplement.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def check():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    p = load(U/'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R/name) == digest, name
    assert subprocess.check_output(['git','rev-parse','HEAD'], cwd=R, text=True).strip() == p['head']
    assert sha(R/'.git/index') == p['index_sha256']
    raw = subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'], cwd=R, text=True)
    rows = [row for row in raw.split('\0') if row]
    assert all(row[:2] == ' M' for row in rows)
    assert {row[3:] for row in rows} == set(p['tracked_dirty'])
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R/name) == digest, name
    for name in p['controls']:
        assert sha(U/'controls-before'/name) == p['tracked_dirty'][name]
    body, headers = U/'sources/ucl-record.body', U/'sources/ucl-record.headers'
    assert body.stat().st_size == 5417
    html = body.read_text()
    assert '<title>Just a moment...</title>' in html and 'challenge-platform' in html
    assert re.findall(r'^HTTP/\S+\s+(\d+)', headers.read_text(), re.M)[-1] == '403'
    begin, end = load(U/'request-start.json'), load(U/'request-observed-end.json')
    assert begin['requested_url'] == 'https://discovery.ucl.ac.uk/12680/'
    assert begin['actual_curl_start_utc'] is None and end['actual_curl_end_utc'] is None
    elapsed_bracket = (datetime.fromisoformat(end['after_tool_completion_utc']) - datetime.fromisoformat(begin['before_tool_call_utc'])).total_seconds()
    assert elapsed_bracket >= 1.211079
    old = load(R/'data/accounting-master/r05-conditional-predictive-source-20261023/source-record.json')
    assert old['final_edition_equality'] == 'not_verified' and old['inference_admitted'] is False
    c = load(R/'data/accounting-master/r05-repeated-origins-20261023/choice.json')
    assert c['selected_design'] == 'repeated_origins' and c['issuer_weights']['values'] is None
    assert all(c['forecast_task'][k] is None for k in ('interval','cutoff','origin_grouping'))
    v = load(R/'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    assert len(v['rows']) == 192 and all(x['as_of_admission'] is False for x in v['rows'])
    a, o = load(REVIEW/'assessment-successor.json'), load(REVIEW/'operation-successor.json')
    assert (len(a['rows']),len(a['interactions']),len(o['rows'])) == (53,6,46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    return p, {'http_requests': 1, 'http_status': 403, 'technical_copies_acquired': 0,
               'edition_comparison': 'not_verified', 'protected_files': len(p['protected']),
               'tracked_dirty_paths': len(rows), 'vintage_admissions': 0,
               'whole_rows_closed': 0, 'readiness': 'not_ready',
               'manuscript_changed': False, 'inference_admitted': False, 'runtime_admitted': False}


def record(p, checks):
    for path in (U/'completion.json',U/'checks.json',U/'request-receipt.json',U/'run-manifest.json',SUPPLEMENT):
        assert not path.exists() and path.parent.is_dir() and os.access(path.parent,os.W_OK), path
    assert not (U/'controls-after').exists()
    replacement = '''The UCL edition follow-up is complete as bounded access evidence at
data/accounting-master/r05-conditional-predictive-edition-20261023/: one
public institutional request returned403 challenge HTML and no technical text.
No follow-up PDF links were disclosed. The2003/2006 comparison remains
unverified; do not repeat this route without a distinct new lead. Read-only
replay: verify.py without flags; one-time stages are frozen.

Next E3 decision dependency: the pending forecast-period and company-weight
objectives determine the first task. The concrete recommendations remain a
complete future fiscal year with a named cutoff before its start, and equal
company contribution after as-of asset scaling. Neither is selected by silence.
After the answers, create an additive choice record and finalise target/origin,
refit/service, availability and matching inference design in that order.
Source edition and all192 historical-vintage admissions remain unresolved.
Other internal work must follow a specific remaining obligation/new source
lead; completed manuscript diagnosis and bounded access routes stay frozen.

'''
    marker = 'Next: inspect the untried UCL institutional record already identified in the'
    edits=[]
    for name in p['controls']:
        target=R/name
        assert target.read_bytes() == (U/'controls-before'/name).read_bytes()
        assert not target.is_symlink() and os.access(target,os.W_OK)
        text=target.read_text()
        assert text.count(marker)==1
        first=text.index(marker)
        last=text.index('Completed review evidence:',first)
        edits.append((name,text[:first]+replacement+text[last:]))
    body, headers=U/'sources/ucl-record.body',U/'sources/ucl-record.headers'
    curl=['curl','--location','--silent','--show-error','--connect-timeout','10','--max-time','45',
          '--max-filesize','15000000','--dump-header',rel(headers),'--output',rel(body),
          '--write-out','%{http_code} %{size_download} %{time_total} %{url_effective}\\n',
          'https://discovery.ucl.ac.uk/12680/']
    write(U/'checks.json',checks)
    write(U/'request-receipt.json',{
        'requested_url':curl[-1],'effective_url':curl[-1],'command_argv':curl,
        'http_status':403,'curl_exit':0,'curl_seconds':'1.211079','download_bytes':5417,
        'body':bind(body),'headers':bind(headers),
        'start_observation':bind(U/'request-start.json'),'end_observation':bind(U/'request-observed-end.json'),
        'time_provenance':'Saved UTC observations bracket the tool call; actual process start/end remain unknown',
        'technical_text_acquired':False,'challenge_bypass_attempted':False,
        'original_lead':bind(R/'data/accounting-master/r05-conditional-predictive-source-20261023/sources/openalex.body')})
    prefix='env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U/'run-manifest.json',{
        'git_commit':p['head'],'branch':p['branch'],'environment':sys.executable,'python':platform.python_version(),
        'cpu_gpu':'CPU only; GPU devices intentionally hidden for Python; no framework imported',
        'data_version':'One retained UCL HTTP response; original OpenAlex lead bound in request-receipt.json',
        'seeds':'N/A access documentation','started_utc':p['started_utc'],
        'recorded_utc':datetime.now(timezone.utc).isoformat(),
        'wall_time':{'curl_seconds':'1.211079','whole_session':'Not measured; request UTC bracket is not process wall time'},
        'commands':[prefix+rel(U/'prepare.py'),curl,prefix+rel(U/'verify.py'),prefix+rel(U/'verify.py')+' --record',prefix+rel(U/'verify.py')],
        'plan':rel(PLAN),'result':rel(U/'result.md'),'output':rel(U)})
    write(SUPPLEMENT,{
        'scope':'Bounded institutional source-edition access follow-up; no new technical text',
        'candidate_version':'3.48','candidate_pdf':bind(R/'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment':bind(REVIEW/'assessment-successor.json'),
        'protected_operations':bind(REVIEW/'operation-successor.json'),
        'completed_author_review':bind(REVIEW/'regression/completion.json'),
        'all_original_obligations':53,'interactions':6,'operations':46,'whole_rows_closed':0,
        'readiness':'not_ready','plan':bind(PLAN),'result':bind(U/'result.md'),'review':bind(U/'review.md'),
        'checks':checks,'manuscript_changed':False,'runtime_admitted':False,'inference_admitted':False,
        'independent_human_acceptance':'pending'})
    for name,after in edits:
        snapshot=U/'controls-after'/name
        snapshot.parent.mkdir(parents=True,exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R/name).write_text(after)
    assert check()[1]==checks
    files=[x for x in U.rglob('*') if x.is_file() and '__pycache__' not in x.parts]+[PLAN,SUPPLEMENT]
    write(U/'completion.json',{'status':'complete_bounded_access_edition_unverified','checks':checks,
        'bindings':{rel(x):sha(x) for x in sorted(files)},
        'control_replay_policy':'Immutable before/after snapshots; live controls may advance in successor units'})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--record',action='store_true')
    args=parser.parse_args()
    p,checks=check()
    if args.record:
        record(p,checks)
    if (U/'completion.json').exists():
        c=load(U/'completion.json')
        for name,digest in c['bindings'].items():
            assert sha(R/name)==digest,name
        assert c['checks']==checks==load(U/'checks.json')
        status='recorded and verified' if args.record else 'read-only replay passed'
    else:
        status='read-only preflight passed; not yet recorded'
    print(json.dumps({'status':status,**checks}))


if __name__=='__main__':
    main()
