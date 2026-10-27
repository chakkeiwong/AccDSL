"""Bounded audit of the preserved guarded requirement engine."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v3 as guarded
core=guarded.v1
def main():
    assert not (HERE/'guard-audit.json').exists(),'audit_already_recorded'
    definition={'profile':guarded.PROFILE,'method_id':'query.guard.audit','version':'1',
      'inputs':{key:{'type':core.BOOL,'role':'state','source_ref':'explicit truth-table input'} for key in ('condition','body')},
      'requirements':[{'id':'relation','guard':{'op':'ref','id':'condition'},'guard_requires':['condition'],
        'predicate':{'op':'ref','id':'body'},'requires':['body'],'admission_refs':[],
        'on_false':'invalid','on_unknown':'unresolved'}],
      'required_known':[],'capabilities':[],'residual_prerequisites':['Scalar truth-table audit only']}
    cases=[]
    for g in (True,False,None):
      for b in (True,False,None):
       for require in (False,True):
        d=deepcopy(definition);d['required_known']=['body'] if require else []
        values={k:({'status':'unknown','reason':'audit unknown'} if v is None else {'status':'known','value':v}) for k,v in [('condition',g),('body',b)]}
        h=core.digest(d);actual=guarded.assess({h:d},h,values,[])
        activation='unknown' if g is None else 'active' if g else 'inactive'
        consequence='unresolved' if g is None or (g and b is None) else 'not_applicable' if not g else 'satisfied' if b else 'invalid'
        status='unresolved' if require and b is None else consequence
        status={'satisfied':'requirements_satisfied','not_applicable':'no_active_requirements'}.get(status,status)
        assert actual['status']==status,(g,b,require,actual)
        finding=actual['findings'][0]
        assert (finding['activation'],finding['consequence'])==(activation,consequence)
        assert not actual['executed'] and not actual['method_eligible']
        cases.append({'guard':g,'body':b,'required_known':require,'expected_status':status,
          'expected_activation':activation,'expected_consequence':consequence,'actual':actual})
    paths=[Path(module.__file__).resolve() for module in (guarded,guarded.v1,guarded.v2)]
    output={'passed':True,'cases':cases,'source_hashes':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}}
    (HERE/'guard-audit.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'passed':True,'truth_table_cases':len(cases),'findings':'False guard is inactive; required_known remains independent'}))
if __name__=='__main__':main()
