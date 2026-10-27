"""Record the bounded EU source inquiry and its next dependency once."""
from datetime import datetime,timezone
import json
import platform
import sys
from verify import U,R,sha,load,check

PLAN=R/'docs/plans/accounting-r05-eu-ifrs18-20261023.md'
SUPPLEMENT=R/'data/accounting-master/readability-repair-20261022-theta/r05-eu-ifrs18-supplement.json'
rel=lambda p:str(p.relative_to(R))
HEADER='''## 23 October 2026 — E3 EU legal-text source resolved

Current question: future OCF predictive accuracy for the same nine companies,
next full fiscal year, pre-start cutoff and equal company weights. Annual and
interim asset candidates are mapped. The official EU2026/338 regulation is now
retained and its relevant IFRS18/IAS7 passages inspected; issuer elections
remain open. Next: exact-version release evidence and prospective timing.
All192 historical admissions remain false. Q, time weights, refit/service,
inference and resources remain open. No user question is pending.

'''
FRONTIER='''The EU source inquiry is complete at
data/accounting-master/r05-eu-ifrs18-20261023/: nine distinct requests recovered
the official105-page regulation through the Publications Office metadata/item
chain. Articles1-3, IFRS18 B30-B41/C1-C6 and IAS7 amendments were inspected;
23 source anchors retain the selected text. Publication16February2026,
entry8March2026 and required first-year start1January2027 are distinct.
IAS7.34B-D still requires issuer facts and elections. Full-annex equivalence
and issuer cash-flow effects are not established.

Next E3 dependency: investigate concrete exact-version release leads and
separate historical-vintage requirements from genuinely prospective inputs.
Future Q, time weights, refit/service, inference and resources remain open.
All192 historical admissions stay false. No whole row closes. Safe replay:
data/accounting-master/r05-eu-ifrs18-20261023/verify.py. No user question is
pending or global continuation veto active. Completed records are immutable.

'''

def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    assert not (U/'completion.json').exists() and not (U/'run-manifest.json').exists()
    assert not SUPPLEMENT.exists()
    checks=check();start=load(U/'start.json');edits=[]
    for name in start['controls']:
        raw=(U/'controls-before'/name).read_bytes();assert (R/name).read_bytes()==raw,name
        before=raw.decode();marker='Next E3 dependency: inspect the EU regulation using a distinct official lead,\n'
        assert before.count(marker)==1
        a=before.index(marker);b=before.index('Completed review evidence:',a)
        after=before[:a]+FRONTIER+before[b:]
        a=after.index('## 23 October 2026 — E3 interim asset candidates checked');b=after.index('## 22 October 2026',a)
        edits.append((name,after[:a]+HEADER+after[b:]))
    data=load(U/'source-record.json');commands=[]
    for i,q in enumerate(data['requests']):
        args=['curl']+([] if i==0 else ['-sS'])+['-L','--connect-timeout','10','--max-time','45','--max-filesize','20000000']
        for key,value in q.get('headers',{}).items():args+=['-H',key+': '+value]
        args+=['-D',q['response_headers']['path'],'-o',q['body']['path'],'-w',
               '%{json}' if i==0 else '%{http_code} %{size_download} %{time_total} %{url_effective}',q['requested_url']]
        commands.append(args)
    prefix=['env','CUDA_VISIBLE_DEVICES=-1','/home/chakwong/miniconda3/envs/tfgpu/bin/python3','-B']
    commands += [prefix+[rel(U/n)] for n in ('prepare.py','record_sources.py','verify.py','finish.py')]
    commands += [prefix+['data/accounting-master/r05-ifrs18-adoption-20261023/extract_html.py',rel(U/'sources/efrag-update59.html')],
                 ['pdftotext','-layout',rel(U/'sources/eu-regulation.pdf'),rel(U/'sources/eu-regulation.txt')],
                 ['pdfinfo',rel(U/'sources/eu-regulation.pdf')]]
    now=datetime.now(timezone.utc)
    write(U/'run-manifest.json',{'git_commit':start['head'],'branch':start['branch'],
        'environment':sys.executable,'python':platform.python_version(),
        'cpu_gpu':'CPU only; GPU intentionally hidden; standard-library helpers and Poppler',
        'data_version':'Official EU2026/338; source-record.json exact bindings',
        'random_seeds':'N/A; documentary inspection and exact calendar calculation',
        'started_utc':start['started_utc'],'completed_utc':now.isoformat(),
        'wall_time_seconds':(now-datetime.fromisoformat(start['started_utc'])).total_seconds(),
        'wall_time_scope':'Snapshot to completion; initial EFRAG request preceded snapshot',
        'sum_request_seconds':sum(q['seconds'] for q in data['requests']),
        'command_argv':commands,'plan':rel(PLAN),'result':rel(U/'result.md'),
        'output_paths':[rel(U),rel(SUPPLEMENT)],'full_annex_reading':False})
    write(SUPPLEMENT,{'scope':'EU IFRS18/IAS7 selected technical source','result':rel(U/'result.md'),
        'result_sha256':sha(U/'result.md'),'checks':checks,'candidate_version':'3.48',
        'readiness':'not_ready','whole_rows_closed':0})
    for name,after in edits:
        target=U/'controls-after'/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x') as f:f.write(after)
        (R/name).write_text(after)
    paths=[p for p in U.rglob('*') if p.is_file()]+[PLAN,SUPPLEMENT]
    write(U/'completion.json',{'status':'complete_selected_EU_technical_source','checks':checks,
        'bindings':{rel(p):sha(p) for p in sorted(paths)},'replay':'verify.py; read only'})
    assert check()==checks
    print(json.dumps({'status':'completed and verified',**checks}))

if __name__=='__main__':main()
