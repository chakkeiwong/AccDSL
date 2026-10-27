"""One-shot author diagnostic of specified JSON examples; not a product evaluator.
Run from repository root with --output pointing to a fresh JSON report.
Only standard-library arithmetic and document consistency are checked.
"""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
from datetime import datetime, timezone

BASE = Path('docs/design/proposal/architecture')
FIXTURE = BASE / 'uncertainty-measure-attachment-fixtures-v2.json'
SPEC = BASE / 'uncertainty-measure-attachment-contract-v2.md'
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
a = p.parse_args()
out = Path(a.output)
if out.exists():
    raise SystemExit('Refusing to overwrite evidence: ' + str(out))
checks = []
observations = []
def check(name, passed, detail=None):
    checks.append(dict(id=name, passed=bool(passed), **({'detail': detail} if detail is not None else {})))
def unique_object(pairs):
    d = {}
    for k, v in pairs:
        check('JSON key is unique: '+k, k not in d) if k in d else None
        d[k] = v
    return d
f = json.loads(FIXTURE.read_text(), object_pairs_hook=unique_object)
r = f['records']
cases = [c for g in f['groups'] for c in g['cases']]
request_keys = {c['input']['request_id']+'@'+str(c['input']['version']) for c in cases}
check('Unique case and request identities', len({c['id'] for c in cases}) == len(request_keys) == len(cases))
result_keys = {c['expected']['result_id']+'@'+str(c['expected']['version']) for c in cases}
check('Unique result identities', len(result_keys) == len(cases))
known = set(r) | request_keys
req_fields = set('request_id version predecessor operation family_ref view_ref model_ref coordinates sample_space measure_kind purpose mass_or_density dependence support_restrictions event_representation provenance justification information_cutoff evidence_cutoff dependencies'.split())
res_fields = set('result_id version request_ref operation old_view proposed_view disposition reason_codes preserved_records support_references unresolved_obligations structural_validity attachment_status mathematical_status mathematical_obligations empirical_justification capability_status computation_status next_permissible_operations future_dependencies family_effect attachment_ref probability observations'.split())
ref_keys = {'family_ref','view_ref','model_ref','time_ref','admission_ref','attachment_ref','justification','coordinate','left','right'}
ref_lists = {'coordinates','provenance','dependencies','event_refs','source_coordinates','target_coordinates','lost_coordinates'}
def refs(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in ref_keys and isinstance(v,str):yield v
            elif k in ref_lists and isinstance(v,list):
                yield from (z for z in v if isinstance(z,str))
            else:yield from refs(v)
    elif isinstance(obj,list):
        for v in obj:yield from refs(v)
for key, value in r.items():
    check('Immutable record identity '+key, key == value['id']+'@'+str(value['version']))
    check('Record references resolve '+key, all(x in r for x in refs(value)))
    if value['kind']=='coordinate':
        check('Typed coordinate '+key, all(k in value for k in ['concept','entity','perimeter','dimensions','unit','economic_time','value_type']))
    if value['kind']=='history_family' and value['sample_space']['kind']=='finite':
        s=value['sample_space']['outcomes'];cn=[r[x]['concept'] for x in value['coordinates']]
        check('Family assignment coverage '+key, set(s)==set(value['assignments']) and all(set(v)==set(cn) for v in value['assignments'].values()))
        check('Distinct elementary assignments '+key, len({json.dumps(v,sort_keys=True) for v in value['assignments'].values()})==len(s))
        for ass in value['assignments'].values():
            for cr in value['coordinates']:
                cd=r[cr];check('Coordinate value domain '+key+'/'+cd['concept'], cd['domain'] is None or ass[cd['concept']] in cd['domain'])
    if value['kind']=='measure_model':
        fam=r[value['family_ref']]
        check('Model family/view/coordinate binding '+key, r[value['view_ref']]['family_ref']==value['family_ref'] and value['coordinates']==fam['coordinates'])
        # The malformed duplicate-ID submission intentionally has a non-set representation.
        sp=value['sample_space'];fsp=fam['sample_space']
        compatible=(set(sp['outcomes'])==set(fsp['outcomes'])) if sp['kind']=='finite' else sp==fsp
        check('Model domain membership '+key, compatible)
    if value['kind']=='event':
        model=r[value['model_ref']]
        check('Event model/family/view binding '+key, all(value[k]==model[k] for k in ['family_ref','view_ref','coordinates']))
    if value['kind']=='measure_attachment':
        model=r[value['model_ref']]
        check('Attachment model/family/view/purpose binding '+key, all(value[k]==model[k] for k in ['family_ref','view_ref','purpose']))
        if value['status']=='attached_assumption':
            sp=model['sample_space']['outcomes'];mass={k:Q(v) for k,v in model['mass_or_density']['masses'].items()}
            check('Admitted synthetic precondition is a law '+key, len(sp)==len(set(sp)) and set(mass)==set(sp) and all(x>=0 for x in mass.values()) and sum(mass.values())==1)

def evaluate(q):
    """Compute finite observations and diagnostic dispositions from input records."""
    observation={};codes=[];struct='valid';math='unresolved'
    m=r[q['model_ref']] if q['model_ref'] else None
    if q['operation']=='infer_from_branch_count':
        return 'REQUEST_INVALID',['COUNT_IS_NOT_A_MEASURE'],observation,None,struct,math
    if m is None:
        code='JOINT_DEPENDENCE_UNSPECIFIED' if q['dependence']['kind']=='marginals_only' else 'NO_MEASURE_PROVIDED'
        return 'RETAINED_ONLY',[code],observation,None,struct,math
    attached=r[q['attachment_ref']] if q.get('attachment_ref') else None
    if attached:
        if q['family_ref']!=attached['family_ref']:
            codes.append('FAMILY_VERSION_MISMATCH')
            if q['sample_space']!=r[attached['family_ref']]['sample_space']:codes.append('SUPPORT_CHANGED')
        if q['purpose']!=attached['purpose']:codes.append('MEASURE_PURPOSE_MISMATCH')
        if codes:return 'REQUEST_INVALID',codes,observation,None,'invalid',math
        if q['model_ref']!=attached['model_ref']:
            return 'RETAINED_ONLY',['MODEL_VERSION_STALE'],observation,None,'invalid',math
    if q['measure_kind']!='finite_joint':
        observation={'preserved_expression':q['mass_or_density'],'preserved_event':r[q['event_refs'][0]]['selector']}
        if q['measure_kind']=='continuous_joint':
            codes=['CONTINUOUS_EVALUATOR_UNAVAILABLE']
            if q['mass_or_density']['normalization_proof'] is None:codes.append('NORMALIZATION_UNPROVEN')
        else:codes=['MIXED_MEASURE_REPRESENTATION_UNSUPPORTED']
        return 'UNSUPPORTED',codes,observation,None,struct,math
    s=q['sample_space']['outcomes']
    if len(s)!=len(set(s)):return 'REQUEST_INVALID',['DUPLICATE_ELEMENTARY_ID'],{},None,'invalid',math
    mass={k:Q(v) for k,v in q['mass_or_density']['masses'].items()}
    if set(s)!=set(mass):return 'REQUEST_INVALID',['MASS_COVERAGE_MISMATCH'],{},None,'invalid',math
    total=sum(mass.values(),Q(0))
    if any(x<0 for x in mass.values()):codes.append('NEGATIVE_MASS')
    if total!=1:codes.append('NON_UNIT_MASS')
    if codes:return 'REQUEST_INVALID',codes,{'candidate_mass_total':str(total)},None,struct,'failed'
    math='satisfied';positive=[x for x in s if mass[x]>0];zeros=[x for x in s if mass[x]==0]
    if q['operation']=='attach_measure':
        return 'ATTACHED_ASSUMPTION',[],dict(probability_total=str(total),positive_mass_support=positive,zero_mass_outcomes=zeros),None,struct,math
    def probability(ids):
        assert set(ids)<=set(s), 'event outside declared space'
        return sum((mass[x] for x in set(ids)),Q(0))
    events=[r[e] for e in dict.fromkeys(q['event_refs'])]
    if q['query']=='overlap':
        A,B=[set(e['selector']) for e in events]
        observation=dict(event_a_probability=str(probability(A)),event_b_probability=str(probability(B)),intersection_probability=str(probability(A&B)),union_probability=str(probability(A|B)))
        check('Inclusion-exclusion '+q['request_id'],probability(A|B)==probability(A)+probability(B)-probability(A&B))
    elif q['query']=='partition':
        cells=[set(c) for c in events[0]['selector']];covered=set().union(*cells)
        disjoint=all(not cells[i]&cells[j] for i in range(len(cells)) for j in range(i))
        observation={'missing_outcomes':[x for x in s if x not in covered],'disjoint':disjoint}
        if covered!=set(s):codes.append('PARTITION_COVERAGE_UNPROVEN')
        if not disjoint:codes.append('PARTITION_NOT_DISJOINT')
        if codes:return 'REQUEST_INVALID',codes,observation,None,struct,'failed'
    elif q['query']=='projection':
        projection=events[0]['projection'];mapping=projection['mapping'];famil=r[q['family_ref']]
        check('Projection covers sample space '+q['request_id'],set(mapping)==set(s))
        values={}
        for x in s:
            projected=mapping[x]
            check('Projection agrees with source assignment '+x, all(famil['assignments'][x][k]==v for k,v in projected.items()))
            label=','.join(k+'='+v for k,v in projected.items());values[label]=values.get(label,Q(0))+mass[x]
        observation={'projected_probabilities':{k:str(v) for k,v in values.items()},'elementary_outcomes_preserved':s}
        if len(values)<len(s):codes=['PROJECTION_COLLISION_RETAINED']
    else:
        event=events[0]
        if event['selector_kind']=='coordinate_equality':
            assignments=r[q['family_ref']]['assignments'];left=r[event['selector']['left']]['concept'];right=r[event['selector']['right']]['concept']
            selected=[x for x in s if assignments[x][left]==assignments[x][right]]
            marginals={}
            for cr in q['coordinates']:
                vals={};name=r[cr]['concept']
                for x in s:
                    value=str(assignments[x][name]);vals[value]=vals.get(value,Q(0))+mass[x]
                marginals[cr]={k:str(v) for k,v in vals.items()}
            observation={'marginals':marginals,'positive_mass_support':positive,'zero_mass_outcomes':zeros}
        else:
            selected=event['selector']
            if len(events)<len(q['event_refs']):codes=['IDEMPOTENT_EVENT_REFERENCE'];observation={'unique_event_references':len(events)}
        return 'EVALUATED',codes,observation,str(probability(selected)),struct,math
    return 'EVALUATED',codes,observation,None,struct,math

for c in cases:
    cid=c['id'];q=c['input'];e=c['expected']
    check(cid+' complete request', req_fields<=q.keys())
    check(cid+' complete result', res_fields<=e.keys())
    check(cid+' all request references resolve',all(x in r for x in refs(q)))
    check(cid+' preserved/support references resolve',all(x in known for x in e['preserved_records']+e['support_references']))
    check(cid+' dependency closure',set(refs({k:v for k,v in q.items() if k!='dependencies'}))<=set(q['dependencies']))
    check(cid+' result references request',e['request_ref']==q['request_id']+'@'+str(q['version']) and e['operation']==q['operation'])
    family=r[q['family_ref']]
    check(cid+' request coordinates and family view',q['coordinates']==family['coordinates'] and r[q['view_ref']]['family_ref']==q['family_ref'])
    check(cid+' cutoffs explicit and consistent',q['information_cutoff']==r['time:fixture@1']['information_cutoff'] and q['evidence_cutoff']==r['time:fixture@1']['evidence_cutoff'])
    check(cid+' source available by cutoff',all(r[x]['available_at']<=q['evidence_cutoff'] for x in q['provenance']))
    if q['model_ref']:
        model=r[q['model_ref']]
        check(cid+' law bytes match immutable model',all(q[k]==model[k] for k in ['mass_or_density','measure_kind','dependence','coordinates']))
        # Cross-version/domain/purpose mismatches must be rejected below, not waived.
        binding=all(q[k]==model[k] for k in ['family_ref','view_ref','sample_space','purpose'])
    else:binding=q['sample_space']==family['sample_space']
    if q['operation']=='evaluate_event':
        check(cid+' complete event request',all(k in q for k in ['attachment_ref','event_refs','query']))
        event_binding=all(all(r[x][k]==q[k] for k in ['family_ref','view_ref','model_ref','coordinates']) for x in q['event_refs'])
    else:event_binding=True
    disposition,codes,obs,prob,struct,math=evaluate(q)
    if not binding or not event_binding:
        check(cid+' incompatible binding never evaluated',disposition in ['REQUEST_INVALID','RETAINED_ONLY'])
    check(cid+' disposition and reasons from inputs',(disposition,codes)==(e['disposition'],e['reason_codes']))
    check(cid+' independently computed observations',obs==e['observations'],dict(computed=obs,expected=e['observations']) if obs!=e['observations'] else None)
    check(cid+' probability from inputs',prob==e['probability'])
    check(cid+' separate validity dimensions',(struct,math)==(e['structural_validity'],e['mathematical_status']))
    check(cid+' empirical and capability boundary',e['empirical_justification']=='not_established' and e['capability_status']==('outside_proposed_evaluator' if disposition=='UNSUPPORTED' else 'specified_only_no_runtime'))
    check(cid+' permitted operations exclude future features',set(e['next_permissible_operations'])<= {'revise_request','attach_measure','evaluate_event','retain_symbolic'} and not set(e['next_permissible_operations']) & set(e['future_dependencies']))
    check(cid+' unsupported/rejected probability absent',disposition=='EVALUATED' or e['probability'] is None)
    check(cid+' unresolved mathematical obligations retained', math=='satisfied' or bool(e['mathematical_obligations']))
    old=r[q['attachment_ref']]['view_ref'] if q.get('attachment_ref') else q['view_ref']
    check(cid+' old family view preserved',e['old_view']==e['proposed_view']==old)
    observations.append(dict(case=cid,disposition=disposition,reason_codes=codes,computed_observations=obs,probability=prob,structural_validity=struct,mathematical_status=math))
diag=next(x for x in observations if x['case']=='MA04c');anti=next(x for x in observations if x['case']=='MA04d')
check('Same marginals give distinct equality probabilities',diag['computed_observations']['marginals']==anti['computed_observations']['marginals'] and diag['probability']=='1' and anti['probability']=='0')
inputs=[FIXTURE,SPEC,Path(__file__),BASE/'uncertainty-measure-attachment-contract-v1.md',BASE/'uncertainty-measure-attachment-fixtures-v1.json',Path('docs/design/spec/core-contract.md'),Path('scripts/reconstruction_v1.py'),Path('data/accounting-master/deliverables/P15/coverage.json')]
report=dict(schema_version='accdsl.proposal.measure_attachment.consistency.v1',measured_at=datetime.now(timezone.utc).isoformat(),passed=all(x['passed'] for x in checks),scope='Bounded specified-example consistency only; no runtime implementation, statistical comparison, accounting validity or human acceptance.',command='PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__))+' --output '+str(out),environment='Python standard library; no framework imports; CPU arithmetic; GPU not queried',input_hashes={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in inputs},groups=len(f['groups']),cases=len(cases),registry_records=len(r),checks=checks,observations=observations,failures=[x for x in checks if not x['passed']],manual_review='See uncertainty-measure-attachment-result-v1.md for author reconciliation and explicit deferred failures; independent review pending.')
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['passed','groups','cases','registry_records','failures']}))
print('assertions',len(checks))
raise SystemExit(0 if report['passed'] else 1)
