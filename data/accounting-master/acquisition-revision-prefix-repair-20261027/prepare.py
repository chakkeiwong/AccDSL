from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;S=H.parent/'acquisition-revision-eligibility-repair-20261027';R=H.parents[2]
assert not (H/'reference.py').exists()
assert json.loads((S/'future-candidate-probe-01/finding.json').read_text())['status']=='FAIL'
code=(S/'reference.py').read_text().replace('ConditionalAcquisitionRevisionView/3','ConditionalAcquisitionRevisionView/4')
code=code.replace("original=w.report(original_request);revised=w.report(revised_request)","original=w.report(original_request)")
code=code.replace("        h.need(revised['status']=='conditional_worksheet','revised_worksheet:'+revised.get('reason','invalid'))\n",'')
code=code.replace("alternatives=[dict(id='original',request=original_request,result=original),dict(id='revised',request=revised_request,result=revised)]","alternatives=[dict(id='original',request=original_request,result=original)]")
needle="        if available is None:\n            if reasons:"
replacement="""if reasons and available is not None:
            return dict(**common,status='other_method_required',selected='original',reason=','.join(reasons),alternatives=alternatives)
        if not reasons:
            revised=w.report(revised_request)
            if revised['status']!='conditional_worksheet':
                return dict(**common,status='unresolved_candidate_method' if available is None else 'candidate_method_required',selected=None,reason='revised_worksheet:'+revised.get('reason','invalid'),alternatives=alternatives,held_candidate=dict(request=revised_request,result=revised),availability='unknown' if available is None else 'available',scope='Original remains preserved; no supported revised financial result is available.')
            alternatives.append(dict(id='revised',request=revised_request,result=revised))
        if available is None:
            if reasons:"""
assert needle in code;code=code.replace(needle,'        '+replacement)
(H/'reference.py').write_text(code)
code=(S/'verify.py').read_text()
needle="        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)"
extra="""        for mode,cutoff,available,status in [('future','2026-01-10T00:00:00Z','2026-02-01T00:00:00Z','original_view'),('known','2026-03-01T00:00:00Z','2026-02-01T00:00:00Z','candidate_method_required'),('unknown','2026-03-01T00:00:00Z',None,'unresolved_candidate_method')]:
            b=fixture(cutoff=cutoff);b['payload']['revision']['available_at']['manager']=available
            next(x for x in b['payload']['revised']['payload']['acquired_items'] if x['id']=='equipment')['recognised_balance']='300/1'
            next(x for x in b['payload']['revision']['dependent_adjustments'] if x['field']=='equipment')['after']='300/1'
            bind(b);before=deepcopy(b);r=m.view(b)
            ck('held/'+mode+'/status',r['status'],status);ck('held/'+mode+'/immutable',b,before)
            ck('held/'+mode+'/original_report',r['alternatives'][0]['result']['report'],next(x['result']['report'] for x in SAVED if x['id']=='proportional/cash'))
            ck('held/'+mode+'/alternative_ids',[x['id'] for x in r['alternatives']],['original']);ck('held/'+mode+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
            if mode!='future':
                ck('held/'+mode+'/no_selected_result',r['selected'],None);ck('held/'+mode+'/candidate_reason',r['held_candidate']['result']['reason'],'excess_requires_other_method');ck('held/'+mode+'/candidate_preserved',r['held_candidate']['request'],m.rebound(b['payload']['revised'],b['payload']['query']))
            cases.append(dict(id='unsupported_revision/'+mode,request=b,result=r))
"""+needle
assert needle in code;code=code.replace(needle,extra)
code=code.replace("plan='docs/plans/accounting-acquisition-revision-eligibility-repair-20261027.md'","plan='docs/plans/accounting-acquisition-revision-prefix-repair-20261027.md'")
code=code.replace("files.add(H/'predecessor-lock.json');","files.add(R/'docs/plans/accounting-acquisition-revision-prefix-repair-20261027.md');files.add(H/'predecessor-lock.json');")
(H/'verify.py').write_text(code);(H/'contract.md').write_text((S/'contract.md').read_text().replace('views /3','views /4')+'\nEvaluate a revised worksheet only if potentially available and conditionally eligible. An unsupported candidate retains the complete original and proposed request/refusal, with no selected revised result. A future or disqualified revision never erases the earlier original.\n')
lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file() and 'inputs' not in p.parts and '__pycache__' not in p.parts}
(H/'predecessor-lock.json').write_text(json.dumps(lock,indent=2)+'\n');print('Prepared /4 original-preservation and held-candidate repair.')
