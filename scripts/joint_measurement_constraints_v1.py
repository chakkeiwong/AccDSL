"""Conditional exact measurement consistency, never historical reconstruction."""
from copy import deepcopy
from fractions import Fraction as Q
import re
import z3
import method_requirements_v1 as core
import method_requirements_v2 as types
import rational_solver_v1 as solver

PROFILE='JointMeasurementConstraints/1'
MAX_ENTRIES=256
MAX_TERMS=4096
MAX_BITS=4096
BOUNDARY={'executed':False,'source_admission':False,'accounting_admission':False,
          'actual_history':'unknown','executable_opening':None,
          'scope':'conditional_joint_measurement_constraints_only'}
BUDGET_FIELDS=['max_slots','max_formula_nodes','max_integer_assignments','max_cells',
               'elapsed_ms','solver_timeout_ms','solver_rlimit']


def rational(value):
    result=core.scalar(value,'rational')
    core.need(max(abs(result.numerator).bit_length(),result.denominator.bit_length())<=MAX_BITS,'rational_bit_limit')
    return result


def premise(value):
    if value is None:return
    core.closed(value,['id','status','meaning'],'premise')
    core.text(value['id'],'premise_id');core.text(value['meaning'],'premise_meaning')
    core.need(value['status']=='proposed','premise_requires_explicit_proposed_status')


def validate(definition,budget):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','observations','equations'],'joint_definition')
    core.need(definition['profile']==PROFILE,'profile')
    observations=definition['observations'];equations=definition['equations']
    core.need(type(observations) is dict and len(observations)<=MAX_ENTRIES,'observation_limit')
    core.need(type(equations) is list and 0<len(equations)<=MAX_ENTRIES,'equation_limit')
    premises={};missing=[]
    def remember(value,where):
        premise(value)
        if value is None:missing.append(where)
        elif value['id'] in premises:core.need(premises[value['id']]==value,'conflicting_premise_identity')
        else:premises[value['id']]=deepcopy(value)
    for key,item in observations.items():
        core.text(key,'observation_id')
        core.closed(item,['type','interval','interval_premise','source_ref'],'observation')
        types.typed(item['type']);core.need(item['type']['kind']=='rational','numeric_observation')
        rational(item['type']['scale']);core.text(item['source_ref'],'source_ref')
        remember(item['interval_premise'],'interval_premise:'+key)
        interval=item['interval']
        if interval is None:missing.append('interval:'+key)
        else:
            core.closed(interval,['lower','upper','lower_inclusive','upper_inclusive'],'interval')
            low,high=rational(interval['lower']),rational(interval['upper'])
            core.need(type(interval['lower_inclusive']) is bool and type(interval['upper_inclusive']) is bool,'endpoint_inclusion')
            core.need(low<high or (low==high and interval['lower_inclusive'] and interval['upper_inclusive']),'empty_observation_interval')
    ids,used,normalized=set(),set(),[];count=0
    for row in equations:
        core.closed(row,['id','type','terms','rhs','identity_premise'],'equation')
        core.text(row['id'],'equation_id');core.need(row['id'] not in ids,'duplicate_equation');ids.add(row['id'])
        types.typed(row['type']);core.need(row['type']['kind']=='rational','numeric_equation')
        rational(row['type']['scale']);rational(row['rhs'])
        remember(row['identity_premise'],'identity_premise:'+row['id'])
        core.need(type(row['terms']) is list,'equation_terms');coefficients={}
        count+=len(row['terms']);core.need(count<=MAX_TERMS,'term_limit')
        for term in row['terms']:
            core.closed(term,['observation','coefficient'],'term');key=term['observation']
            core.text(key,'term_observation');core.need(key in observations,'undeclared_observation')
            core.need(observations[key]['type']==row['type'],'equation_context_type_mismatch')
            coefficient=rational(term['coefficient']);used.add(key)
            coefficients[key]=coefficients.get(key,Q(0))+coefficient
            core.need(max(abs(coefficients[key].numerator).bit_length(),coefficients[key].denominator.bit_length())<=MAX_BITS,'combined_coefficient_limit')
        normalized.append({k:v for k,v in coefficients.items() if v})
    core.need(used==set(observations),'unused_observation')
    core.closed(budget,BUDGET_FIELDS,'budget')
    result=solver.Budget(**budget)
    # This adapter executes one conjunction with no slots, choices or objectives.
    core.need(result.max_cells<=1 and result.max_integer_assignments<=1 and result.max_slots==0,'single_conjunction_budget')
    core.need(result.elapsed_ms<=60000 and result.solver_timeout_ms<=10000 and result.solver_rlimit<=10000000,'reference_runtime_limit')
    return normalized,missing,premises,result


def check_witness(definition,witness):
    core.need(type(witness) is dict and set(witness)==set(definition['observations']),'complete_witness_required')
    values={key:rational(value) for key,value in witness.items()}
    for key,item in definition['observations'].items():
        interval=item['interval'];core.need(interval is not None,'unresolved_witness_domain')
        lo,hi=rational(interval['lower']),rational(interval['upper']);value=values[key]
        core.need((value>=lo if interval['lower_inclusive'] else value>lo) and
                  (value<=hi if interval['upper_inclusive'] else value<hi),'witness_bound_violation:'+key)
    for equation in definition['equations']:
        value=sum((rational(term['coefficient'])*values[term['observation']] for term in equation['terms']),Q(0))
        core.need(value==rational(equation['rhs']),'witness_equation_violation:'+equation['id'])
    return True


def assess(definition,budget):
    try:
        coefficients,missing,premises,limit=validate(definition,budget)
        base={**BOUNDARY,'profile':PROFILE,'definition_sha256':core.digest(definition),
              'budget':deepcopy(budget),'premises':premises,'missing':missing}
        if missing:return {**base,'status':'unresolved'}
        variables={key:z3.Real('measurement.'+str(i)) for i,key in enumerate(definition['observations'])}
        problem=solver.Problem('selected_conditional_measurements','explicit_input_definition',variables=variables)
        problem.provenance={'definition_sha256':core.digest(definition),'premises':deepcopy(premises)}
        for key,item in definition['observations'].items():
            interval=item['interval']
            problem.add('domain:'+key,solver.domain_formula(variables[key],{
                'lower':interval['lower'],'upper':interval['upper'],
                'lower_closed':interval['lower_inclusive'],'upper_closed':interval['upper_inclusive']}))
        for row,terms in zip(definition['equations'],coefficients):
            expression=sum((solver.q(a)*variables[k] for k,a in terms.items()),solver.q(0))
            problem.add('equation:'+row['id'],expression==solver.q(row['rhs']))
        result=solver.solve(problem,limit)
        common={**base,'solver_status':result['status'],'solver_feasibility':result['feasibility'],
                'solver_version':z3.get_version_string(),'coverage':deepcopy(result['coverage']),
                'generated_constraints':deepcopy(result['generated_constraints']),
                'solver_wall_seconds':result.get('wall_seconds')}
        if result['status']=='UnsupportedFragment':
            return {**common,'status':'unsupported','reason':result.get('reason')}
        if result['feasibility']=='Feasible':
            cells=[c for c in result['cells'] if c['feasibility']=='sat']
            core.need(bool(cells),'feasible_without_witness')
            witness={k:f'{Q(v).numerator}/{Q(v).denominator}' for k,v in cells[0]['witness'].items()}
            check_witness(definition,witness)
            return {**common,'status':'conditionally_feasible','witness':witness,'witness_checked_exactly':True,
                    'meaning':'one assignment satisfies the declared measurement system; actual history remains unknown'}
        if result['feasibility']=='Infeasible':
            core.need(result['coverage']['complete'] and all(c['conflict']['rechecked']=='unsat' for c in result['cells']),'unverified_infeasibility')
            return {**common,'status':'conditionally_infeasible',
                    'conflicts':[deepcopy(c['conflict']) for c in result['cells']],
                    'meaning':'no assignment to this declared system according to the exact solver and core recheck; no accounting-history verdict'}
        return {**common,'status':'unknown','reason':result.get('reason') or 'solver_or_resource_unknown'}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError,z3.Z3Exception) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}
