from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;S=H.parent/'acquisition-revision-discovery-repair-20261027';R=H.parents[2]
assert not (H/'reference.py').exists()
assert json.loads((S/'eligibility-probe-01/finding.json').read_text())['status']=='FAIL'
code=(S/'reference.py').read_text().replace('ConditionalAcquisitionRevisionView/2','ConditionalAcquisitionRevisionView/3')
old="""if available is None:
            return dict(**common,status='unresolved_views',selected=None,reason='revision_availability_unknown',alternatives=alternatives)
        reasons=[]
        if effective!=acq:reasons.append('different_effective_date')
        if not r['provisional']:reasons.append('not_provisional')
        if discovered>=end:reasons.append('outside_measurement_period')
        if r['disposition']=='later_event':reasons.append('later_event_requires_other_method')"""
new="""reasons=[]
        if effective!=acq:reasons.append('different_effective_date')
        if not r['provisional']:reasons.append('not_provisional')
        if discovered>=end:reasons.append('outside_measurement_period')
        if r['disposition']=='later_event':reasons.append('later_event_requires_other_method')
        if available is None:
            if reasons:
                return dict(**common,status='unresolved_availability_other_method',selected='original',reason=','.join(reasons),alternatives=alternatives[:1],availability='unknown',conditional_requirement='If the actor has received this evidence, its supplied disposition requires another method; no retrospective revised worksheet is eligible.')
            return dict(**common,status='unresolved_views',selected=None,reason='revision_availability_unknown',alternatives=alternatives)"""
assert old in code;code=code.replace(old,new);(H/'reference.py').write_text(code)
code=(S/'verify.py').read_text()
needle="b=fixture();b['payload']['revision']['disposition']='unresolved';run('unknown_disposition',bind(b),'unresolved_views',None,reason='revision_disposition_unknown')"
extra=needle+"""
        for key,value,reason in [('disposition','later_event','later_event_requires_other_method'),('provisional',False,'not_provisional'),('effective_at','2025-07-02T00:00:00Z','different_effective_date'),('period_end_exclusive','2026-01-15T00:00:00Z','outside_measurement_period')]:
            b=fixture();b['payload']['revision']['available_at']['manager']=None;b['payload']['revision'][key]=value
            r=run('unknown_access/'+key,bind(b),'unresolved_availability_other_method','original',reason=reason)
            ck('unknown_access/'+key+'/availability',r['availability'],'unknown');ck('unknown_access/'+key+'/conditional_requirement',r['conditional_requirement'].startswith('If the actor'))
        """
assert needle in code;code=code.replace(needle,extra)
code=code.replace("plan='docs/plans/accounting-acquisition-revision-discovery-repair-20261027.md'","plan='docs/plans/accounting-acquisition-revision-eligibility-repair-20261027.md'")
code=code.replace("files.add(H/'predecessor-lock.json');","files.add(R/'docs/plans/accounting-acquisition-revision-eligibility-repair-20261027.md');files.add(H/'predecessor-lock.json');")
(H/'verify.py').write_text(code)
(H/'contract.md').write_text((S/'contract.md').read_text().replace('views /2','views /3')+'\nKnown retrospective disqualifiers remove the revised financial alternative even when availability is unknown. The output retains unknown availability and makes the other-method duty conditional on access, without pretending the actor has learned it.\n')
lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file() and 'inputs' not in p.parts and '__pycache__' not in p.parts}
(H/'predecessor-lock.json').write_text(json.dumps(lock,indent=2)+'\n');print('Prepared /3 with distinct knowledge and eligibility conditions.')
