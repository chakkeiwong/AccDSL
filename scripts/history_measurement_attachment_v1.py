"""Conjoin complete conditional measurement and history families explicitly."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as Q
import z3
import conditional_history_family_v1 as history
import temporal_measurement_constraints_v1 as temporal

joint=history.joint;core=history.core
PROFILE='HistoryMeasurementAttachment/1'
BOUNDARY={**history.BOUNDARY,'scope':'explicit_conditional_history_measurement_attachment_only'}


def key(kind,name):return core.canonical([kind,name]).decode()
def measurement_budget(budget):return {**budget,'max_slots':0}


def prepare(definition,budget):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','history','measurements','bindings','obligations'],'attachment_definition')
    core.need(definition['profile']==PROFILE,'profile')
    h=definition['history'];m=definition['measurements'];bindings=definition['bindings']
    hp,limit,hpremises,hmissing=history.build_problem(h,budget)
    numeric,lowering=temporal.lower(m,measurement_budget(budget))
    _,mmissing,mpremises,_=joint.validate(numeric,measurement_budget(budget))
    core.need(type(bindings) is dict and set(bindings)<=set(m['observations']),'binding_observation_keys')
    count=0;missing=['history:'+x for x in hmissing]+['measurements:'+x for x in mmissing]
    premises={}
    def remember(p,where):
        joint.premise(p)
        if p is None:missing.append(where)
        elif p['id'] in premises:core.need(premises[p['id']]==p,'conflicting_premise_identity')
        else:premises[p['id']]=deepcopy(p)
    for p in [*hpremises.values(),*mpremises.values()]:remember(p,'parent_premise')
    for name,binding in bindings.items():
        core.closed(binding,['kind','quantity','terms','premise'],'measurement_binding')
        core.need(binding['kind'] in ['snapshot','movement'],'mapping_kind')
        core.text(binding['quantity'],'mapping_quantity');obs=m['observations'][name];typ=obs['type']
        core.need(binding['quantity']==typ['quantity'],'mapping_quantity_mismatch')
        core.need(typ['value_type']==h['value_type'],'mapping_value_type_mismatch')
        remember(binding['premise'],'mapping:'+name)
        when=typ['time']
        if binding['kind']=='snapshot':
            core.need(when['kind']=='instant' and when['at'] in [h['opening_date'],*h['dates']],'mapping_snapshot_time')
        else:
            core.need(when['kind']=='period','mapping_period_required')
            start=(temporal.day(when['start'])-timedelta(days=1)).isoformat()
            end=(temporal.day(when['end_exclusive'])-timedelta(days=1)).isoformat()
            core.need(start in [h['opening_date'],*h['dates']] and end in h['dates'],'mapping_period_endpoints')
        terms=binding['terms'];core.need(type(terms) is list and bool(terms),'mapping_terms')
        count+=len(terms);core.need(count<=4096,'mapping_term_limit')
        for term in terms:
            core.closed(term,['kind','field','coefficient'],'mapping_term')
            core.need(term['kind'] in ['account','memory'],'mapping_field_kind')
            core.text(term['field'],'mapping_field');joint.rational(term['coefficient'])
            core.need(term['field'] in h['accounts' if term['kind']=='account' else 'memory'],'mapping_unknown_field')
    obligations=definition['obligations'];core.need(type(obligations) is list and len(obligations)<=256,'obligation_limit')
    ids=set()
    for row in obligations:
        core.closed(row,['id','meaning','affects'],'attachment_obligation')
        core.text(row['id'],'obligation_id');core.need(row['id'] not in ids,'duplicate_obligation');ids.add(row['id'])
        core.text(row['meaning'],'obligation_meaning');core.identifiers(row['affects'],'affects',nonempty=True)
    unresolved=[{'origin':'history','obligation':deepcopy(row)} for row in h['obligations']]
    unresolved.extend({'origin':'attachment','obligation':deepcopy(row)} for row in obligations)
    unmapped=[name for name in m['observations'] if name not in bindings]
    unresolved.extend({'origin':'unmapped_measurement','observation':name,
                       'meaning':'No explicit history mapping was supplied.'} for name in unmapped)
    core.need(len(hp.variables)+len(numeric['observations'])<=256,'combined_variable_limit')
    meta={'history_definition_sha256':core.digest(h),'measurement_definition_sha256':core.digest(m),
          'numeric_measurement_definition':numeric,'measurement_lowering':lowering,
          'missing_premises':missing,'premises':premises,'target_obligations':unresolved,
          'unmapped_observations':unmapped}
    if missing:return None,limit,meta
    hv={name:z3.Real('attachment.history.'+str(i)) for i,name in enumerate(hp.variables)}
    mv={name:z3.Real('attachment.measurement.'+str(i)) for i,name in enumerate(numeric['observations'])}
    variables={key('history',name):value for name,value in hv.items()}
    variables.update({key('measurement',name):value for name,value in mv.items()})
    p=joint.solver.Problem(h['scope']['name']+':measurement_attachment','explicit_conditional_attachment',
        variables=variables,slots=len(h['events']),exclusions=deepcopy(h['scope']['exclusions']))
    substitutions=[(hp.variables[name],hv[name]) for name in hv]
    for label,formula in hp.constraints:p.add('history:'+label,z3.substitute(formula,*substitutions))
    for name,item in numeric['observations'].items():
        interval=item['interval']
        p.add('measurement_domain:'+name,joint.solver.domain_formula(mv[name],{
            'lower':interval['lower'],'upper':interval['upper'],
            'lower_closed':interval['lower_inclusive'],'upper_closed':interval['upper_inclusive']}))
    for equation in numeric['equations']:
        expression=sum((joint.solver.q(joint.rational(t['coefficient']))*mv[t['observation']]
                        for t in equation['terms']),joint.solver.q(0))
        p.add('measurement_equation:'+equation['id'],expression==joint.solver.q(joint.rational(equation['rhs'])))
    for name,binding in bindings.items():
        when=m['observations'][name]['type']['time'];expression=joint.solver.q(0)
        for term in binding['terms']:
            if binding['kind']=='snapshot':
                value=hv[history.identifier('opening_'+term['kind'],term['field'])]
                selected=[e for e in h['events'] if e['date']<=when['at']]
            else:
                value=joint.solver.q(0)
                selected=[e for e in h['events'] if when['start']<=e['date']<when['end_exclusive']]
            for event in selected:
                template=h['templates'][event['template']]
                incidence=joint.rational(template['postings' if term['kind']=='account' else 'memory'].get(term['field'],'0/1'))
                value=value+joint.solver.q(incidence)*hv[history.identifier('event_amount',event['id'])]
            expression=expression+joint.solver.q(joint.rational(term['coefficient']))*value
        p.add('mapping:'+name,mv[name]==expression)
    p.provenance={'attachment_sha256':core.digest(definition),**deepcopy(meta)}
    return p,limit,meta


def replay_witness(definition,budget,witness):
    problem,_,meta=prepare(definition,budget)
    core.need(problem is not None,'unresolved_attachment_premise')
    core.need(type(witness) is dict and set(witness)==set(problem.variables),'complete_attachment_witness')
    hnames=history.validate(definition['history'],budget)[0]
    hw={name:witness[key('history',name)] for name in hnames}
    mw={name:witness[key('measurement',name)] for name in definition['measurements']['observations']}
    replay=history.replay_witness(definition['history'],budget,hw)
    temporal.check_witness(definition['measurements'],measurement_budget(budget),mw)
    checks={}
    for name,binding in definition['bindings'].items():
        when=definition['measurements']['observations'][name]['type']['time'];value=Q(0)
        for term in binding['terms']:
            if binding['kind']=='snapshot':
                state=replay['snapshots'][when['at']]
                component=Q(state['accounts' if term['kind']=='account' else 'memory'][term['field']])
            else:
                component=sum((Q(e['postings' if term['kind']=='account' else 'memory_effects'].get(term['field'],'0/1'))
                    for e in replay['events'] if when['start']<=e['date']<when['end_exclusive']),Q(0))
            value+=joint.rational(term['coefficient'])*component
        core.need(value==joint.rational(mw[name]),'mapping_witness_mismatch:'+name)
        checks[name]=history.rat(value)
    return {'history':replay,'measurement_witness':mw,'mapping_values':checks,
            'both_parent_constraints_checked':True,'all_supplied_mappings_checked':True}


def assess(definition,budget):
    try:
        problem,limit,meta=prepare(definition,budget)
        complete=not meta['target_obligations'] and not meta['missing_premises']
        base={'profile':PROFILE,**BOUNDARY,'definition':deepcopy(definition),'definition_sha256':core.digest(definition),
              'budget':deepcopy(budget),**meta,'formulation_complete':complete,
              'economic_scope':'explicitly_limited' if complete else 'unresolved',
              'target_existence':'unknown','declared_search':'not_started'}
        if problem is None:return {**base,'status':'unresolved','candidate_feasibility':'unresolved'}
        result=joint.solver.solve(problem,limit)
        common={**base,'solver_status':result['status'],'solver_version':z3.get_version_string(),
            'coverage':deepcopy(result['coverage']),'generated_constraints':deepcopy(result['generated_constraints']),
            'solver_wall_seconds':result.get('wall_seconds'),
            'declared_search':'complete' if result['coverage'].get('complete',False) else 'partial'}
        if result['feasibility']=='Feasible':
            cells=[c for c in result['cells'] if c['feasibility']=='sat'];core.need(bool(cells),'missing_witness')
            witness={k:history.rat(Q(v)) for k,v in cells[0]['witness'].items()}
            replay=replay_witness(definition,budget,witness)
            return {**common,'status':'conditional_attachment_witness' if complete else 'candidate_attachment_with_unresolved_obligations',
                'candidate_feasibility':'conditionally_feasible','target_existence':'conditional_witness' if complete else 'unknown',
                'witness':witness,'replay':replay}
        if result['feasibility']=='Infeasible':
            core.need(result['coverage']['complete'] and all(c['conflict']['rechecked']=='unsat' for c in result['cells']),
                      'unverified_infeasibility')
            return {**common,'status':'conditionally_infeasible','candidate_feasibility':'conditionally_infeasible',
                'target_existence':'conditionally_empty' if complete else 'unknown',
                'conflicts':[deepcopy(c['conflict']) for c in result['cells']]}
        return {**common,'status':'unsupported' if result['status']=='UnsupportedFragment' else 'unknown',
                'candidate_feasibility':'unknown','reason':result.get('reason') or 'solver_or_resource_unknown'}
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}


def verify_result(definition,budget,result):
    try:
        current=assess(definition,budget)
        if current['status']=='invalid':return result==current
        core.need(type(result) is dict and set(result)==set(current),'result_fields')
        for name in current:
            if name not in ['witness','replay','conflicts','solver_wall_seconds']:
                core.need(result[name]==current[name],'result_changed:'+name)
        if 'witness' in result:core.need(result['replay']==replay_witness(definition,budget,result['witness']),'replay_changed')
        if 'conflicts' in result:
            problem,_,_=prepare(definition,budget);formulas=dict(problem.constraints)
            core.need(type(result['conflicts']) is list and len(result['conflicts'])==1,'conflict_scope')
            for conflict in result['conflicts']:
                core.closed(conflict,['labels','rechecked','minimal'],'conflict')
                core.identifiers(conflict['labels'],'conflict_labels',nonempty=True)
                core.need(set(conflict['labels'])<=set(formulas),'unknown_conflict_label')
                core.need(conflict['rechecked']=='unsat' and conflict['minimal'] is False,'conflict_claim')
                core.need(budget['solver_timeout_ms']>0 and budget['solver_rlimit']>0,'core_budget')
                engine=z3.Solver();engine.set(timeout=budget['solver_timeout_ms'],rlimit=budget['solver_rlimit'])
                engine.add(*(formulas[k] for k in conflict['labels']))
                core.need(engine.check()==z3.unsat,'conflict_not_unsat')
        if 'solver_wall_seconds' in result:
            wall=result['solver_wall_seconds'];core.need(wall is None or type(wall) in [int,float] and 0<=wall<float('inf'),'invalid_timing')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception):return False
