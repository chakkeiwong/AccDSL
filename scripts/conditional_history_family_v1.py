"""Finite authored linear monetary histories; never actual-company admission."""
from copy import deepcopy
from fractions import Fraction as Q
import z3
import joint_measurement_constraints_v1 as joint
from temporal_measurement_constraints_v1 import day, TEMPORAL_KEYS

core=joint.core
PROFILE='ConditionalMonetaryHistory/1'
MAX_ENTRIES=256
BOUNDARY={'executed':False,'source_admission':False,'accounting_admission':False,
          'actual_history':'unknown','executable_opening':None,
          'scope':'authored_conditional_linear_monetary_history_only'}


def identifier(kind,key):return core.canonical([kind,key]).decode()
def rat(value):return f'{value.numerator}/{value.denominator}'


def validate(definition,budget):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','scope','value_type','opening_date','dates','accounts','memory',
        'balance_premise','templates','events','measurements','obligations'],'history_definition')
    core.need(definition['profile']==PROFILE,'profile')
    scope=definition['scope'];core.closed(scope,['name','exclusions'],'declared_scope')
    core.text(scope['name'],'scope_name');core.identifiers(scope['exclusions'],'exclusions')
    typ=joint.types.typed(definition['value_type'])
    core.need(typ['kind']=='rational' and len(typ['dimensions'])==1
              and all(k.startswith('currency:') and v==1 for k,v in typ['dimensions'].items()),'single_monetary_dimension')
    core.need(not set(typ['context'])&TEMPORAL_KEYS,'time_declared_separately')
    opening=day(definition['opening_date']);dates=definition['dates']
    core.identifiers(dates,'snapshot_dates',nonempty=True)
    parsed=[day(x) for x in dates]
    core.need(len(dates)<=MAX_ENTRIES and parsed==sorted(parsed) and opening<parsed[0], 'chronological_snapshot_dates')
    accounts,memory=definition['accounts'],definition['memory']
    core.need(type(accounts) is dict and 0<len(accounts)<=MAX_ENTRIES,'account_limit')
    core.need(type(memory) is dict and len(memory)<=MAX_ENTRIES,'memory_limit')
    premises,missing,domains={},[],{}
    def remember(value,where):
        joint.premise(value)
        if value is None:missing.append(where)
        elif value['id'] in premises:core.need(premises[value['id']]==value,'conflicting_premise_identity')
        else:premises[value['id']]=deepcopy(value)
    def domain(value,where,nonnegative=False):
        core.closed(value,['interval','premise','source_ref'],'quantity_domain')
        core.text(value['source_ref'],'source_ref');remember(value['premise'],'domain:'+where)
        interval=value['interval']
        core.closed(interval,['lower','upper','lower_inclusive','upper_inclusive'],'interval')
        low,high=joint.rational(interval['lower']),joint.rational(interval['upper'])
        core.need(type(interval['lower_inclusive']) is bool and type(interval['upper_inclusive']) is bool,'endpoint_inclusion')
        core.need(low<high or low==high and interval['lower_inclusive'] and interval['upper_inclusive'],'nonempty_domain')
        core.need(not nonnegative or low>=0,'nonnegative_event_domain')
    for kind,fields in [('account',accounts),('memory',memory)]:
        for key,value in fields.items():
            core.text(key,'field_name');name=identifier('opening_'+kind,key)
            domain(value,name);domains[name]=deepcopy(value['interval'])
    remember(definition['balance_premise'],'opening_balance')
    templates=definition['templates'];events=definition['events'];measurements=definition['measurements']
    core.need(type(templates) is dict and len(templates)<=MAX_ENTRIES,'template_limit')
    core.need(type(events) is list and len(events)<=MAX_ENTRIES,'event_limit')
    core.need(type(measurements) is list and 0<len(measurements)<=MAX_ENTRIES,'measurement_limit')
    count=0
    for key,template in templates.items():
        core.text(key,'template_id')
        core.closed(template,['postings','memory','premise','provenance'],'template')
        remember(template['premise'],'template:'+key);core.text(template['provenance'],'template_provenance')
        for group,allowed in [('postings',accounts),('memory',memory)]:
            incidence=template[group];core.need(type(incidence) is dict,'incidence_map')
            core.need(set(incidence)<=set(allowed),'undeclared_incidence_field')
            count+=len(incidence);core.need(count<=4096,'incidence_term_limit')
            for value in incidence.values():core.need(joint.rational(value)!=0,'explicit_nonzero_incidence')
        core.need(bool(template['postings']) or bool(template['memory']),'empty_template')
        core.need(sum((joint.rational(v) for v in template['postings'].values()),Q(0))==0,'unbalanced_template')
    event_ids,used=set(),set();previous=opening
    for event in events:
        core.closed(event,['id','date','template','amount'],'event')
        key=event['id'];core.text(key,'event_id');core.need(key not in event_ids,'duplicate_event');event_ids.add(key)
        when=day(event['date']);core.need(opening<when<=parsed[-1] and when>=previous,'chronological_events');previous=when
        core.text(event['template'],'template_id');core.need(event['template'] in templates,'undeclared_template');used.add(event['template'])
        name=identifier('event_amount',key);domain(event['amount'],name,True);domains[name]=deepcopy(event['amount']['interval'])
    core.need(used==set(templates),'unused_template')
    core.need(len(domains)<=MAX_ENTRIES,'total_variable_limit')
    measurement_ids=set()
    for measurement in measurements:
        core.closed(measurement,['id','date','terms','domain'],'measurement')
        key=measurement['id'];core.text(key,'measurement_id');core.need(key not in measurement_ids,'duplicate_measurement');measurement_ids.add(key)
        day(measurement['date']);core.need(measurement['date'] in [definition['opening_date'],*dates],'measurement_snapshot_date')
        terms=measurement['terms'];core.need(type(terms) is list and bool(terms),'measurement_terms')
        count+=len(terms);core.need(count<=4096,'incidence_term_limit')
        for term in terms:
            core.closed(term,['kind','field','coefficient'],'measurement_term')
            core.need(term['kind'] in ['account','memory'],'measurement_field_kind')
            core.text(term['field'],'measurement_field')
            core.need(term['field'] in (accounts if term['kind']=='account' else memory),'undeclared_measurement_field')
            joint.rational(term['coefficient'])
        domain(measurement['domain'],'measurement:'+key)
    obligations=definition['obligations'];core.need(type(obligations) is list and len(obligations)<=MAX_ENTRIES,'obligation_limit')
    obligation_ids=set()
    for row in obligations:
        core.closed(row,['id','meaning','affects'],'obligation')
        core.text(row['id'],'obligation_id');core.need(row['id'] not in obligation_ids,'duplicate_obligation');obligation_ids.add(row['id'])
        core.text(row['meaning'],'obligation_meaning');core.identifiers(row['affects'],'obligation_affects',nonempty=True)
    core.closed(budget,joint.BUDGET_FIELDS,'budget');limit=joint.solver.Budget(**budget)
    core.need(limit.max_slots<=MAX_ENTRIES and limit.max_cells<=1 and limit.max_integer_assignments<=1,'single_continuous_family_budget')
    core.need(limit.elapsed_ms<=60000 and limit.solver_timeout_ms<=10000 and limit.solver_rlimit<=10000000,'reference_runtime_limit')
    return domains,premises,missing,limit


def in_domain(value,interval):
    low,high=joint.rational(interval['lower']),joint.rational(interval['upper'])
    return (value>=low if interval['lower_inclusive'] else value>low) and (value<=high if interval['upper_inclusive'] else value<high)


def replay_witness(definition,budget,witness):
    domains,_,missing,_=validate(definition,budget)
    core.need(not missing,'unresolved_premise')
    core.need(type(witness) is dict and set(witness)==set(domains),'complete_history_witness')
    values={k:joint.rational(v) for k,v in witness.items()}
    for key,interval in domains.items():core.need(in_domain(values[key],interval),'witness_domain:'+key)
    accounts={k:values[identifier('opening_account',k)] for k in definition['accounts']}
    memory={k:values[identifier('opening_memory',k)] for k in definition['memory']}
    core.need(sum(accounts.values(),Q(0))==0,'opening_balance_violation')
    def snapshot():return {'accounts':{k:rat(v) for k,v in accounts.items()},'memory':{k:rat(v) for k,v in memory.items()}}
    snapshots={definition['opening_date']:snapshot()};trace=[];index=0
    for when in definition['dates']:
        while index<len(definition['events']) and definition['events'][index]['date']<=when:
            event=definition['events'][index];template=definition['templates'][event['template']]
            amount=values[identifier('event_amount',event['id'])]
            postings={k:joint.rational(v)*amount for k,v in template['postings'].items()}
            effects={k:joint.rational(v)*amount for k,v in template['memory'].items()}
            core.need(sum(postings.values(),Q(0))==0,'journal_balance_violation')
            for key,value in postings.items():accounts[key]+=value
            for key,value in effects.items():memory[key]+=value
            core.need(sum(accounts.values(),Q(0))==0,'state_balance_violation')
            trace.append({'event_id':event['id'],'date':event['date'],'amount':rat(amount),
                'postings':{k:rat(v) for k,v in postings.items()},'memory_effects':{k:rat(v) for k,v in effects.items()},
                'after':snapshot()});index+=1
        snapshots[when]=snapshot()
    measured={}
    for item in definition['measurements']:
        state=snapshots[item['date']];value=sum((joint.rational(t['coefficient'])*
            Q(state['accounts' if t['kind']=='account' else 'memory'][t['field']]) for t in item['terms']),Q(0))
        core.need(in_domain(value,item['domain']['interval']),'measurement_violation:'+item['id'])
        measured[item['id']]=rat(value)
    return {'opening':snapshots[definition['opening_date']],'events':trace,'snapshots':snapshots,
            'measurements':measured,'checked_exactly':True,'operational_preconditions_checked':False}


def build_problem(definition,budget):
    domains,premises,missing,limit=validate(definition,budget)
    variables={key:z3.Real('history.'+str(i)) for i,key in enumerate(domains)}
    p=joint.solver.Problem(definition['scope']['name'],'explicit_authored_conditional_history',
        variables=variables,slots=len(definition['events']),exclusions=deepcopy(definition['scope']['exclusions']))
    p.provenance={'definition_sha256':core.digest(definition),'premises':deepcopy(premises),
                  'target_obligations':deepcopy(definition['obligations'])}
    for key,interval in domains.items():
        p.add('domain:'+key,joint.solver.domain_formula(variables[key],{
            'lower':interval['lower'],'upper':interval['upper'],
            'lower_closed':interval['lower_inclusive'],'upper_closed':interval['upper_inclusive']}))
    p.add('opening_balance',sum((variables[identifier('opening_account',k)] for k in definition['accounts']),joint.solver.q(0))==0)
    for item in definition['measurements']:
        expression=joint.solver.q(0)
        for term in item['terms']:
            value=variables[identifier('opening_'+term['kind'],term['field'])]
            for event in definition['events']:
                if event['date']<=item['date']:
                    template=definition['templates'][event['template']]
                    incidence=template['postings' if term['kind']=='account' else 'memory'].get(term['field'],'0/1')
                    value=value+joint.solver.q(joint.rational(incidence))*variables[identifier('event_amount',event['id'])]
            expression=expression+joint.solver.q(joint.rational(term['coefficient']))*value
        interval=item['domain']['interval']
        p.add('measurement:'+item['id'],joint.solver.domain_formula(expression,{
            'lower':interval['lower'],'upper':interval['upper'],
            'lower_closed':interval['lower_inclusive'],'upper_closed':interval['upper_inclusive']}))
    return p,limit,premises,missing


def assess(definition,budget):
    try:
        problem,limit,premises,missing=build_problem(definition,budget)
        complete=not definition['obligations'] and not missing
        base={'profile':PROFILE,**BOUNDARY,'definition':deepcopy(definition),'definition_sha256':core.digest(definition),
              'budget':deepcopy(budget),'premises':premises,'missing_premises':missing,
              'target_obligations':deepcopy(definition['obligations']),'formulation_complete':complete,
              'economic_scope':'explicitly_limited' if complete else 'unresolved',
              'target_existence':'unknown','declared_search':'not_started',
              'family_representation':'complete_supplied_formula_retained; a witness is one member, not enumeration'}
        if missing:return {**base,'status':'unresolved','candidate_feasibility':'unresolved'}
        result=joint.solver.solve(problem,limit)
        common={**base,'solver_status':result['status'],'solver_version':z3.get_version_string(),
                'coverage':deepcopy(result['coverage']),'generated_constraints':deepcopy(result['generated_constraints']),
                'solver_wall_seconds':result.get('wall_seconds'),
                'declared_search':'complete' if result['coverage'].get('complete',False) else 'partial'}
        if result['feasibility']=='Feasible':
            cells=[c for c in result['cells'] if c['feasibility']=='sat'];core.need(bool(cells),'missing_witness')
            witness={k:rat(Q(v)) for k,v in cells[0]['witness'].items()}
            replay=replay_witness(definition,budget,witness)
            return {**common,'status':'conditional_family_witness' if complete else 'candidate_witness_with_unresolved_obligations',
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
        for key in current:
            if key not in ['witness','replay','conflicts','solver_wall_seconds']:
                core.need(result[key]==current[key],'result_changed:'+key)
        if 'witness' in result:
            core.need(result['replay']==replay_witness(definition,budget,result['witness']),'replay_changed')
        if 'conflicts' in result:
            problem,_,_,missing=build_problem(definition,budget)
            core.need(not missing and type(result['conflicts']) is list and len(result['conflicts'])==1,'conflict_scope')
            formulas=dict(problem.constraints)
            for conflict in result['conflicts']:
                core.closed(conflict,['labels','rechecked','minimal'],'conflict')
                core.identifiers(conflict['labels'],'conflict_labels',nonempty=True)
                core.need(set(conflict['labels'])<=set(formulas),'unknown_conflict_label')
                core.need(conflict['rechecked']=='unsat' and conflict['minimal'] is False,'conflict_claim')
                core.need(budget['solver_timeout_ms']>0 and budget['solver_rlimit']>0,'conflict_budget')
                engine=z3.Solver();engine.set(timeout=budget['solver_timeout_ms'],rlimit=budget['solver_rlimit'])
                engine.add(*(formulas[k] for k in conflict['labels']))
                core.need(engine.check()==z3.unsat,'conflict_not_unsat')
        if 'solver_wall_seconds' in result:
            wall=result['solver_wall_seconds']
            core.need(wall is None or type(wall) in [int,float] and 0<=wall<float('inf'),'invalid_timing')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception):return False
