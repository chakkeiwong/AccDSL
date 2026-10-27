"""Finite documentary conformance helper, not a production simulator."""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
import re

INFORMATION = {'schema':'ObservableHistory/1',
               'initial':['observation','current_output'],
               'step':['action','observation','output','current_output']}

class Refusal(ValueError):
    def __init__(self, code, detail=None):
        self.code, self.detail = code, detail
        super().__init__(code + (':' + str(detail) if detail is not None else ''))

def require(condition, code, detail=None):
    if not condition: raise Refusal(code, detail)

def exact_json(value):
    if value is None or type(value) in (str, int, bool): return
    if type(value) is list:
        for child in value: exact_json(child)
        return
    if type(value) is dict and all(type(k) is str for k in value):
        for child in value.values(): exact_json(child)
        return
    raise Refusal('non_exact_json')

def key(value):
    exact_json(value)
    return json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=False)

def digest(value): return sha256(key(value).encode()).hexdigest()

def fields(value, names, code):
    require(type(value) is dict and set(value) == set(names), code)

def names(value, code, nonempty=True):
    require(type(value) is list and (bool(value) or not nonempty), code)
    require(all(type(x) is str and bool(x) for x in value), code)
    require(len(set(value)) == len(value), code)

def mass(value):
    require(type(value) is str and re.fullmatch(r'[0-9]+(?:/[1-9][0-9]*)?',value) is not None, 'invalid_mass')
    f = Fraction(value)
    require(f > 0, 'nonpositive_mass')
    return f

def validate(model, partition):
    exact_json(model); exact_json(partition)
    fields(model, ['schema','mode','horizon','scenarios','information','requested_outputs','dates','initial'], 'model_fields')
    require(model['schema'] == 'FiniteCompanyModel/1', 'model_schema')
    require(model['mode'] in ('probability','relation'), 'model_mode')
    h = model['horizon']
    require(type(h) is int and h >= 0, 'invalid_horizon')
    names(model['scenarios'], 'invalid_scenarios')
    require(key(model['information']) == key(INFORMATION), 'unsupported_information')
    fields(model['requested_outputs'], ['current','step'], 'output_interface')
    for n in ('current','step'): names(model['requested_outputs'][n], 'output_names', nonempty=False)
    require(type(model['dates']) is list and len(model['dates']) == h+1, 'date_coverage')
    require(type(partition) is list and len(partition) == h+1, 'partition_dates')
    states, kernels = [], []
    for t,date in enumerate(model['dates']):
        fields(date, ['states','transitions'], 'date_fields')
        require(type(date['states']) is list and bool(date['states']), 'empty_states')
        sm = {}
        for state in date['states']:
            fields(state, ['id','actions','current'], 'state_fields')
            x = state['id']; require(type(x) is str and bool(x) and x not in sm, 'state_identity')
            names(state['actions'], 'invalid_actions', nonempty=t<h)
            if t == h: require(not state['actions'], 'terminal_action')
            fields(state['current'], model['requested_outputs']['current'], 'current_output_interface')
            sm[x] = state
        require(type(partition[t]) is dict and set(partition[t]) == set(sm), 'partition_coverage')
        require(all(type(b) is str and bool(b) for b in partition[t].values()), 'partition_block')
        states.append(sm)
    weighted = model['mode'] == 'probability'
    for t,date in enumerate(model['dates']):
        require(type(date['transitions']) is list, 'transition_type')
        km = {}
        expected = {(x,a,s) for x,st in states[t].items() for a in st['actions'] for s in model['scenarios']}
        for transition in date['transitions']:
            fields(transition, ['state','action','scenario','outcomes'], 'transition_fields')
            triple = (transition['state'],transition['action'],transition['scenario'])
            require(all(type(v) is str for v in triple), 'transition_identity')
            require(triple in expected and triple not in km, 'transition_coverage', triple)
            outcomes = transition['outcomes']
            require(type(outcomes) is list and bool(outcomes), 'empty_kernel')
            seen, total = set(), Fraction(0)
            for out in outcomes:
                fields(out, ['next','observation','output'] + (['probability'] if weighted else []), 'outcome_fields')
                require(type(out['next']) is str and out['next'] in states[t+1], 'successor_coverage')
                fields(out['output'], model['requested_outputs']['step'], 'step_output_interface')
                ident = key([out['next'],out['observation'],out['output']])
                require(ident not in seen, 'duplicate_outcome'); seen.add(ident)
                if weighted: total += mass(out['probability'])
            if weighted: require(total == 1, 'kernel_mass', triple)
            km[triple] = outcomes
        require(set(km) == expected, 'missing_kernel', sorted(expected-set(km)))
        kernels.append(km)
    require(type(model['initial']) is list and bool(model['initial']), 'empty_initial')
    seen, total = set(), Fraction(0)
    for init in model['initial']:
        fields(init, ['state','observation'] + (['probability'] if weighted else []), 'initial_fields')
        require(type(init['state']) is str and init['state'] in states[0], 'initial_state')
        ident = key([init['state'],init['observation']])
        require(ident not in seen, 'duplicate_initial'); seen.add(ident)
        if weighted: total += mass(init['probability'])
    if weighted: require(total == 1, 'initial_mass')
    return states, kernels

def bindings(model, partition):
    return {name:digest(value) for name,value in {
        'model':model, 'partition':partition, 'information':model['information'],
        'requested_outputs':model['requested_outputs'], 'horizon':model['horizon']}.items()}

def push(outcomes, next_partition, weighted):
    grouped = defaultdict(Fraction) if weighted else set()
    for out in outcomes:
        k = key([next_partition[out['next']],out['observation'],out['output']])
        if weighted: grouped[k] += mass(out['probability'])
        else: grouped.add(k)
    return dict(grouped) if weighted else grouped

def display(pushed, weighted):
    return [{'triple':json.loads(k), **({'probability':str(pushed[k])} if weighted else {})} for k in sorted(pushed)]

def check(model, partition, max_obligations=None):
    states,kernels = validate(model,partition)
    require(max_obligations is None or type(max_obligations) is int and max_obligations>=0, 'invalid_budget')
    weighted = model['mode'] == 'probability'
    grouped = []
    tasks = []
    for t,sm in enumerate(states):
        blocks = defaultdict(list)
        for x in sorted(sm): blocks[partition[t][x]].append(x)
        grouped.append(dict(blocks))
        for b,xs in sorted(blocks.items()):
            rep = xs[0]
            for x in xs:
                tasks.append({'date':t,'block':b,'reference':rep,'state':x,'component':'actions'})
                tasks.append({'date':t,'block':b,'reference':rep,'state':x,'component':'current'})
                if t < model['horizon']:
                    for a in sorted(states[t][rep]['actions']):
                        for s in sorted(model['scenarios']):
                            tasks.append({'date':t,'block':b,'reference':rep,'state':x,'component':'joint_kernel','action':a,'scenario':s})
    bound = bindings(model,partition)
    for i,task in enumerate(tasks):
        if max_obligations is not None and i >= max_obligations:
            return {'status':'unknown','bindings':bound,'checked':i,'frontier':tasks[i:]}
        t,rep,x = task['date'],task['reference'],task['state']
        part = task['component']
        if part == 'actions':
            left,right = sorted(states[t][rep]['actions']),sorted(states[t][x]['actions'])
        elif part == 'current':
            left,right = states[t][rep]['current'],states[t][x]['current']
        else:
            # An action mismatch must be reported before accessing a missing kernel.
            if set(states[t][rep]['actions']) != set(states[t][x]['actions']):
                return {'status':'rejected','bindings':bound,'checked':i,'witness':{**task,'component':'actions'}}
            a,s=task['action'],task['scenario']
            left=display(push(kernels[t][rep,a,s],partition[t+1],weighted),weighted)
            right=display(push(kernels[t][x,a,s],partition[t+1],weighted),weighted)
        if key(left) != key(right):
            return {'status':'rejected','bindings':bound,'checked':i+1,'witness':{**task,'left':left,'right':right}}
    quotient = {k:json.loads(key(model[k])) for k in ('schema','mode','horizon','scenarios','information','requested_outputs')}
    quotient['dates'] = []
    for t,blocks in enumerate(grouped):
        date={'states':[],'transitions':[]}
        for b,xs in sorted(blocks.items()):
            rep=xs[0]; st=states[t][rep]
            date['states'].append({'id':b,'actions':sorted(st['actions']),'current':json.loads(key(st['current']))})
            if t == model['horizon']: continue
            for a in sorted(st['actions']):
                for s in model['scenarios']:
                    values=push(kernels[t][rep,a,s],partition[t+1],weighted)
                    outs=[]
                    for k in sorted(values):
                        nxt,o,y=json.loads(k)
                        out={'next':nxt,'observation':o,'output':y}
                        if weighted: out['probability']=str(values[k])
                        outs.append(out)
                    date['transitions'].append({'state':b,'action':a,'scenario':s,'outcomes':outs})
        quotient['dates'].append(date)
    initial=defaultdict(Fraction) if weighted else set()
    for init in model['initial']:
        k=key([partition[0][init['state']],init['observation']])
        if weighted: initial[k]+=mass(init['probability'])
        else: initial.add(k)
    quotient['initial']=[]
    for k in sorted(initial):
        b,o=json.loads(k); init={'state':b,'observation':o}
        if weighted: init['probability']=str(initial[k])
        quotient['initial'].append(init)
    return {'status':'accepted','bindings':bound,'checked':len(tasks),'frontier':[], 'quotient':quotient}

def reuse(certificate, model, partition):
    validate(model,partition)
    require(type(certificate) is dict and certificate.get('status')=='accepted','not_accepted_certificate')
    require(certificate.get('bindings')==bindings(model,partition),'stale_binding')
    fresh=check(model,partition)
    require(key(certificate)==key(fresh),'certificate_mismatch')
    return fresh['quotient']
