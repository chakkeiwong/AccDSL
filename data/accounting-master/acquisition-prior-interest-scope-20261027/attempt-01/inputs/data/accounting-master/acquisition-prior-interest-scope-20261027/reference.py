from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-prior-interest-20261027'
spec=importlib.util.spec_from_file_location('prior_equity_v1',S/'reference.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
h=base.h;FLAGS=base.FLAGS;PROFILE='ConditionalPriorEquityExpressions/2'
def derive(body):
    try:
        h.need(len(json.dumps(body,allow_nan=False))<600000,'request_size');h.fields(body,['profile','payload','expected_payload_sha256'],'envelope');h.need(body['profile']==PROFILE,'profile');p=body['payload'];h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['prior_request','prior_result_sha256','source_lock_sha256','relationship','source'],'payload')
        lock=H/'predecessor-lock.json';h.need(sha256(lock.read_bytes()).hexdigest()==p['source_lock_sha256'],'source_lock_binding')
        for name,d in json.loads(lock.read_text()).items():h.need(sha256((R/name).read_bytes()).hexdigest()==d,'protected_dependency:'+name)
        old=base.derive(p['prior_request']);h.need(old['status'] in ['conditional_prior_expressions','unresolved'],'prior_status');h.need(h.digest(old)==p['prior_result_sha256'],'prior_result_binding')
        bp=p['prior_request']['payload']['base_request']['payload'];hr=bp['scope_request']['history_request'];source=p['source'];relation=p['relationship']
        h.fields(source,['text','subject','actor','available_at'],'source');h.text(source['text']);h.need(source['subject']==hr['subject'] and source['actor']==hr['actor'],'source_context')
        h.fields(relation,['significant_influence','joint_control','at','basis','rationale','evidence_sha256'],'relationship')
        h.need(relation['evidence_sha256']==h.digest(source),'relationship_source_binding');h.need(h.moment(relation['at'])==h.moment(bp['acquisition']['at']),'relationship_date')
        h.need(relation['basis']=='immediately_before_control','relationship_basis');h.text(relation['rationale'])
        deps=[]
        for key in ['significant_influence','joint_control']:
            h.need(relation[key] in ['yes','no','unknown'],'relationship_status:'+key)
            if relation[key]!='no':deps.append('prior_relationship_method:'+key+':'+relation[key])
        if source['available_at'] is None:deps.append('relationship_source_availability_unknown')
        elif h.moment(source['available_at'])>h.moment(hr['cutoff']):deps.append('relationship_source_after_cutoff')
        if old['status']=='unresolved':deps.extend(old['dependencies'])
        result=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(body),prior_result=deepcopy(old),relationship=deepcopy(relation),source=deepcopy(source),scope_assessment='supplied_assertions_only')
        if deps:return dict(result,status='unresolved',dependencies=sorted(set(deps)),expressions={})
        return dict(result,status='conditional_prior_expressions',dependencies=deepcopy(old['dependencies']),expressions=deepcopy(old['expressions']),scope='Conditional no-significant-influence/no-joint-control assertions; no actual classification,legal postings,tax or measured report.')
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
