from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone
import os,sys,json,time,platform,subprocess,resource,traceback,fitz
import reference as m
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-prior-interest-20261027'
SAVED=json.loads((S/'attempt-01/cases.json').read_text())
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def bind(b):b['payload']['relationship']['evidence_sha256']=digest(b['payload']['source']);b['expected_payload_sha256']=digest(b['payload']);return b
def fixture(old):
    src=dict(text='Synthetic assertion: no board participation,policy participation,material transactions,management interchange,essential technical dependence,joint-control arrangement or relevant potential rights before acquisition; not an actual fact',subject=['P','S'],actor='manager',available_at='2025-01-01T00:00:00Z')
    return bind(dict(profile=m.PROFILE,payload=dict(prior_request=deepcopy(old['request']),prior_result_sha256=digest(old['result']),source_lock_sha256=sha256((H/'predecessor-lock.json').read_bytes()).hexdigest(),relationship=dict(significant_influence='no',joint_control='no',at='2025-07-01T00:00:00Z',basis='immediately_before_control',rationale='Supplied synthetic absence of participation and joint arrangement despite20% voting power; actual determination is not admitted',evidence_sha256=''),source=src),expected_payload_sha256=''))
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(110,110));out=H/sys.argv[1];out.mkdir(exist_ok=False);clock=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];cases=[];controls=[]
    files={R/p for p in json.loads((H/'predecessor-lock.json').read_text())};files.update(H/p for p in ['reference.py','verify.py','prepare.py','contract.md','predecessor-lock.json']);files.add(R/'docs/plans/accounting-prior-interest-worksheet-20261027.md')
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def ck(n,a,b=True):
        checks.append(dict(name=n,passed=a==b))
        if a!=b:raise AssertionError(n+': '+repr(a)[:220]+' != '+repr(b)[:220])
    def run(n,b,old,extra=[]):
        bind(b);before=deepcopy(b);r=m.derive(b);deps=sorted(set(extra+(old['result']['dependencies'] if old['result']['status']=='unresolved' else [])));unresolved=bool(deps)
        ck(n+'/status',r['status'],'unresolved' if unresolved else 'conditional_prior_expressions');ck(n+'/immutable',b,before)
        ck(n+'/expressions',r['expressions'],{} if unresolved else old['result']['expressions']);ck(n+'/dependencies',r['dependencies'],deps if unresolved else old['result']['dependencies'])
        ck(n+'/prior_retained',r['prior_result'],old['result']);ck(n+'/relationship_retained',r['relationship'],b['payload']['relationship']);ck(n+'/source_retained',r['source'],b['payload']['source']);ck(n+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));ck(n+'/no_report','report' not in r);ck(n+'/scope',r['scope_assessment'],'supplied_assertions_only');cases.append(dict(id=n,request=b,result=r))
    def reject(n,b,reason,rehash=True):
        if rehash:b['expected_payload_sha256']=digest(b['payload'])
        before=deepcopy(b);r=m.derive(b);ck(n+'/status',r['status'],'invalid');ck(n+'/reason',r['reason'],reason);ck(n+'/immutable',b,before);ck(n+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));ck(n+'/no_report','report' not in r);controls.append(dict(id=n,request=b,result=r))
    try:
        source=S/'source-inspection-02/aasb128-nov2024-jan2025.pdf';doc=fitz.open(source)
        ck('source/influence','presumed that the entity has significant influence' in ' '.join(doc[5].get_text().split()));ck('source/exception','venture capital organisation' in ' '.join(doc[7].get_text().split()))
        for old in SAVED:run('preserved/'+old['id'],fixture(old),old)
        old=SAVED[0]
        for key in ['significant_influence','joint_control']:
            for status in ['yes','unknown']:
                b=fixture(old);b['payload']['relationship'][key]=status;run(key+'/'+status,b,old,['prior_relationship_method:'+key+':'+status])
        for value,dep in [(None,'relationship_source_availability_unknown'),('2027-01-01T00:00:00Z','relationship_source_after_cutoff')]:
            b=fixture(old);b['payload']['source']['available_at']=value;run(dep,b,old,[dep])
        b=fixture(old);b['payload']['relationship']['significant_influence']='yes';reject('stale_payload',b,'payload_binding',False)
        for field,reason in [('prior_result_sha256','prior_result_binding'),('source_lock_sha256','source_lock_binding')]:b=fixture(old);b['payload'][field]='0'*64;reject(field,b,reason)
        for key,value,reason in [('significant_influence','automatic_no','relationship_status:significant_influence'),('joint_control',False,'relationship_status:joint_control'),('at','2025-07-02T00:00:00Z','relationship_date'),('basis','percentage_only','relationship_basis'),('evidence_sha256','0'*64,'relationship_source_binding')]:
            b=fixture(old);b['payload']['relationship'][key]=value;reject('relationship/'+key,b,reason)
        b=fixture(old);b['payload']['source']['actor']='analyst';bind(b);reject('wrong_actor',b,'source_context')
        b=fixture(old);b['payload']['relationship']['extra']=True;reject('open_schema',b,'relationship_fields')
        b=fixture(old);del b['payload']['relationship']['significant_influence'];reject('missing_influence',b,'relationship_fields')
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for n,v in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]: (out/n).write_text(json.dumps(v,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU;GPU intentionally hidden',random_seeds='N/A deterministic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-prior-interest-worksheet-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
