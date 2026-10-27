"""Explicit typed affine histories and declared per-state constraints only."""
from copy import deepcopy
from fractions import Fraction as Q
import z3
import conditional_history_family_v1 as prior

joint, core = prior.joint, prior.core
PROFILE = 'TypedAffineHistory/1'
BOUNDARY = {**prior.BOUNDARY, 'scope':'authored_typed_affine_history_only'}
identifier, rat = prior.identifier, prior.rat
MAX_TERMS = 4096


def validate_and_lower(definition, budget):
    core.need(len(core.canonical(definition)) <= core.MAX_BYTES, 'definition_size_limit')
    core.closed(definition, ['profile','scope','value_type','opening_date','dates',
        'accounts','memory','balance_premise','templates','events','measurements',
        'obligations','state_constraints'], 'typed_history_definition')
    core.need(definition['profile'] == PROFILE, 'profile')
    money = joint.types.typed(definition['value_type'])
    core.need(money['kind'] == 'rational' and len(money['dimensions']) == 1 and
              all(k.startswith('currency:') and len(k)>len('currency:') and v==1
                  for k,v in money['dimensions'].items()), 'single_named_monetary_dimension')
    count = [0]

    def numeric(typ):
        joint.types.typed(typ)
        core.need(typ['kind'] == 'rational', 'numeric_type')
        joint.rational(typ['scale'])
        core.need(typ['context'] == money['context'], 'book_context_mismatch')
        return typ

    numeric(money)
    core.need(type(definition['accounts']) is dict and bool(definition['accounts']), 'accounts')
    fields = {'account':{k:money for k in definition['accounts']}, 'memory':{}}
    lower = deepcopy(definition)
    lower['profile'] = prior.PROFILE
    lower.pop('state_constraints')
    core.need(type(definition['memory']) is dict, 'memory')
    for name, item in definition['memory'].items():
        core.closed(item, ['type','domain'], 'typed_memory')
        fields['memory'][name] = numeric(item['type'])
        lower['memory'][name] = deepcopy(item['domain'])

    def coefficient(item, operand, target, nonzero=False):
        count[0] += 1
        core.need(count[0] <= MAX_TERMS, 'typed_term_limit')
        core.closed(item, ['value','type'], 'typed_coefficient')
        value = joint.rational(item['value'])
        core.need(not nonzero or value != 0, 'explicit_nonzero_incidence')
        numeric(item['type'])
        core.need(joint.types.product_type(item['type'], operand) == target,
                  'coefficient_product_type_mismatch')
        return item['value']

    core.need(type(definition['templates']) is dict, 'templates')
    for name, template in definition['templates'].items():
        core.closed(template, ['event_type','postings','memory','premise','provenance'], 'typed_template')
        event_type = numeric(template['event_type'])
        lower['templates'][name].pop('event_type')
        for group, kind in [('postings','account'),('memory','memory')]:
            core.need(type(template[group]) is dict and set(template[group]) <= set(fields[kind]),
                      'undeclared_incidence_field')
            lower['templates'][name][group] = {
                key:coefficient(value, event_type, fields[kind][key], True)
                for key, value in template[group].items()}

    def terms(row):
        target = numeric(row['value_type'])
        core.need(type(row['terms']) is list and bool(row['terms']), 'typed_terms')
        result = []
        for term in row['terms']:
            core.closed(term, ['kind','field','coefficient'], 'typed_term')
            kind, name = term['kind'], term['field']
            core.need(type(kind) is str and kind in fields, 'field_kind')
            core.text(name, 'field_name')
            core.need(name in fields[kind], 'undeclared_field')
            result.append({'kind':kind, 'field':name,
                'coefficient':coefficient(term['coefficient'], fields[kind][name], target)})
        return result

    core.need(type(definition['measurements']) is list, 'measurements')
    for i, row in enumerate(definition['measurements']):
        core.closed(row, ['id','date','value_type','terms','domain'], 'typed_measurement')
        lower['measurements'][i].pop('value_type')
        lower['measurements'][i]['terms'] = terms(row)
    domains, premises, missing, limit = prior.validate(lower, budget)
    constraints = definition['state_constraints']
    core.need(type(constraints) is list and len(constraints) <= prior.MAX_ENTRIES,
              'state_constraint_limit')
    core.need(len(constraints)*(len(definition['events'])+1) <= MAX_TERMS,
              'state_constraint_instance_limit')
    ids, lowered_constraints = set(), []
    for row in constraints:
        core.closed(row, ['id','value_type','terms','domain'], 'state_constraint')
        core.text(row['id'], 'constraint_id')
        core.need(row['id'] not in ids, 'duplicate_state_constraint')
        ids.add(row['id'])
        numeric_terms = terms(row)
        domain = row['domain']
        core.closed(domain, ['interval','premise','source_ref'], 'constraint_domain')
        core.text(domain['source_ref'], 'source_ref')
        premise = domain['premise']
        joint.premise(premise)
        if premise is None:
            missing.append('state_constraint:'+row['id'])
        elif premise['id'] in premises:
            core.need(premises[premise['id']] == premise, 'conflicting_premise_identity')
        else:
            premises[premise['id']] = deepcopy(premise)
        interval = domain['interval']
        core.closed(interval, ['lower','upper','lower_inclusive','upper_inclusive'], 'interval')
        lo, hi = joint.rational(interval['lower']), joint.rational(interval['upper'])
        core.need(type(interval['lower_inclusive']) is bool and
                  type(interval['upper_inclusive']) is bool, 'endpoint_inclusion')
        core.need(lo < hi or lo == hi and interval['lower_inclusive'] and
                  interval['upper_inclusive'], 'nonempty_domain')
        lowered_constraints.append({'id':row['id'],'terms':numeric_terms,'domain':deepcopy(domain)})
    core.need(sum(len(row['terms']) for row in constraints)*(len(definition['events'])+1)
              <= MAX_TERMS, 'state_constraint_expansion_limit')
    return lower, lowered_constraints, domains, premises, missing, limit, fields


def build_problem(definition, budget):
    lower, constraints, domains, premises, missing, limit, fields = validate_and_lower(definition, budget)
    problem, _, _, _ = prior.build_problem(lower, budget)
    problem.evidence_view = 'explicit_authored_typed_affine_history'
    state = {kind:{name:problem.variables[identifier('opening_'+kind,name)]
                   for name in names} for kind,names in fields.items()}

    def constrain_state(index):
        for row in constraints:
            expression = joint.solver.q(0)
            for term in row['terms']:
                kind, name = term['kind'], term['field']
                expression += joint.solver.q(joint.rational(term['coefficient']))*state[kind][name]
            interval = row['domain']['interval']
            label = core.canonical(['state',row['id'],index]).decode()
            problem.add(label, joint.solver.domain_formula(expression, {
                'lower':interval['lower'], 'upper':interval['upper'],
                'lower_closed':interval['lower_inclusive'], 'upper_closed':interval['upper_inclusive']}))
    constrain_state(0)
    for index,event in enumerate(lower['events'],1):
        template = lower['templates'][event['template']]
        amount = problem.variables[identifier('event_amount',event['id'])]
        for group,kind in [('postings','account'),('memory','memory')]:
            for name,incidence in template[group].items():
                state[kind][name] = state[kind][name] + joint.solver.q(joint.rational(incidence))*amount
        constrain_state(index)
    problem.provenance = {'definition_sha256':core.digest(definition),
        'typed_fields':deepcopy(fields), 'premises':deepcopy(premises),
        'target_obligations':deepcopy(definition['obligations']),
        'numeric_lowering_sha256':core.digest({'history':lower,'state_constraints':constraints})}
    return problem, limit, premises, missing


def replay_witness(definition, budget, witness):
    _, _, domains, _, missing, _, fields = validate_and_lower(definition, budget)
    core.need(not missing, 'unresolved_premise')
    core.need(type(witness) is dict and set(witness) == set(domains), 'complete_history_witness')
    values = {k:joint.rational(v) for k,v in witness.items()}
    for name, interval in domains.items():
        core.need(prior.in_domain(values[name], interval), 'witness_domain:'+name)
    accounts = {k:values[identifier('opening_account',k)] for k in definition['accounts']}
    memory = {k:values[identifier('opening_memory',k)] for k in definition['memory']}

    def state():
        return {'accounts':{k:rat(v) for k,v in accounts.items()},
                'memory':{k:rat(v) for k,v in memory.items()}}

    def measure(terms, current):
        return sum((joint.rational(t['coefficient']['value'])*
                    joint.rational(current['accounts' if t['kind']=='account' else 'memory'][t['field']])
                    for t in terms), Q(0))

    checked = []

    def check_state(index, event_id):
        core.need(sum(accounts.values(), Q(0)) == 0, 'unbalanced_state')
        current = state()
        for row in definition['state_constraints']:
            value = measure(row['terms'], current)
            core.need(prior.in_domain(value, row['domain']['interval']),
                      'state_constraint:'+row['id']+':'+str(index))
            checked.append({'id':row['id'],'state_index':index,'after_event':event_id,
                            'value':rat(value),'type':deepcopy(row['value_type'])})

    check_state(0, None)
    opening = state()
    trace = []
    for i, event in enumerate(definition['events'], 1):
        template = definition['templates'][event['template']]
        amount = values[identifier('event_amount',event['id'])]
        before = state()
        postings = {name:joint.rational(c['value'])*amount for name,c in template['postings'].items()}
        effects = {name:joint.rational(c['value'])*amount for name,c in template['memory'].items()}
        core.need(sum(postings.values(), Q(0)) == 0, 'unbalanced_event')
        for name, value in postings.items(): accounts[name] += value
        for name, value in effects.items(): memory[name] += value
        check_state(i, event['id'])
        trace.append({'event_id':event['id'], 'date':event['date'], 'template':event['template'],
            'amount':rat(amount), 'event_type':deepcopy(template['event_type']), 'before':before,
            'postings':{k:rat(v) for k,v in postings.items()},
            'memory_effects':{k:rat(v) for k,v in effects.items()}, 'after':state()})
    snapshots = {definition['opening_date']:opening}
    for date in definition['dates']:
        selected = [row for row in trace if row['date'] <= date]
        snapshots[date] = deepcopy(selected[-1]['after'] if selected else opening)
    measured = {}
    for row in definition['measurements']:
        value = measure(row['terms'], snapshots[row['date']])
        core.need(prior.in_domain(value, row['domain']['interval']), 'measurement:'+row['id'])
        measured[row['id']] = {'value':rat(value),'type':deepcopy(row['value_type'])}
    return {'opening':opening,'events':trace,'snapshots':snapshots,'measurements':measured,
            'field_types':deepcopy(fields),'state_constraints':checked,'checked_exactly':True,
            'declared_state_constraints_checked':bool(definition['state_constraints']),
            'operational_preconditions_checked':False}


def assess(definition,budget):
    try:
        problem,limit,premises,missing=build_problem(definition,budget)
        complete=not definition['obligations'] and not missing
        base={'profile':PROFILE,**BOUNDARY,'definition':deepcopy(definition),'definition_sha256':core.digest(definition),
              'budget':deepcopy(budget),'premises':premises,'missing_premises':missing,
              'numeric_lowering_sha256':problem.provenance['numeric_lowering_sha256'],
              'typed_fields':deepcopy(problem.provenance['typed_fields']),
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
