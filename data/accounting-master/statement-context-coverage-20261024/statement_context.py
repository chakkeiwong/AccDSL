"""Finite full-statement context binding; source observations remain immutable."""
from copy import deepcopy
from datetime import date,timedelta
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import json,re,sys
from jsonschema import Draft202012Validator,FormatChecker
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
RELATIONS=HERE.parent/'source-relations-20261024';sys.path.insert(0,str(RELATIONS))
import relations as prior
state=prior.state;readiness=state.prior
from relations import canonical,digest,closed,OPS,COMPOSED
PROFILE='RetainedStatementContextDraft/1'
KINDS=['snapshot_sum','period_sum','stock_flow_bridge','same_date_endpoint',
    'same_period_measurement','displayed_population_comparison','endpoint_difference',
    'derived_subtotal','explanatory_difference','cross_period_endpoint']
DERIVED={'other_equity_movements','operating_reconciliation_adjustments','operating_asset_liability_adjustments'}
BRIDGES={'capital','retained','aoci','whole_equity_bridge','cash_closing'}

def rat(x):return f'{x.numerator}/{x.denominator}'
def schema():
    text={'type':'string','minLength':1};h={'type':'string','pattern':'^[0-9a-f]{64}$'}
    day={'type':'string','format':'date','pattern':r'^\d{4}-\d{2}-\d{2}$'}
    ref=closed({'kind':text,'schema':text,'digest':h})
    term=closed({'alias':text,'coefficient':{'type':'string','pattern':r'^(?:0|-?[1-9][0-9]*)/[1-9][0-9]*$'}})
    time={'oneOf':[closed({'kind':{'const':'instant'},'at':day}),
        closed({'kind':{'const':'period'},'start':day,'end_exclusive':day})]}
    obs=closed({'alias':text,'collection':{'enum':list(readiness.GROUPS)},'observation_ref':ref,
        'measurement_time':time,'unit':text})
    relation=closed({'id':text,'group':{'enum':['annual','interim']},'source_pointer':text,
        'source_record_sha256':h,'kind':{'enum':KINDS},
        'lhs':{'type':'array','minItems':1,'items':term},'rhs':{'type':'array','items':term},
        'comparison':{'enum':['zero','terms','derived_only']},
        'omitted_source_rows':{'type':'array','items':text}})
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**closed({
        'profile':{'const':PROFILE},'name':text,
        'source':closed({'target':{'enum':[OPS,COMPOSED]},'view':{'enum':['annual','interim','combined']},
            'request_sha256':h,'result_sha256':h}),
        'observations':{'type':'array','minItems':1,'items':obs},
        'relations':{'type':'array','minItems':1,'items':relation},
        'requirement_ids':{'type':'array','minItems':1,'items':text}})}

def get_pointer(value,pointer):
    for part in pointer.split('/')[1:]:
        part=part.replace('~1','/').replace('~0','~')
        value=value[int(part)] if isinstance(value,list) else value[part]
    return value

def evidence(target,view):
    request=readiness.fixture(target,view);result=readiness.evaluate(request)
    packet=readiness.load_packet();out={};cache={}
    for collection in readiness.GROUPS:
        group='annual' if collection.startswith('annual') else 'interim'
        for o in result['known_evidence'][collection]:
            b=o['record']['body'];rid=b['row_id']
            alias=group+'.'+(rid.replace('opening.balance.','opening.',1) if rid.startswith('opening.balance.') else rid)
            file=readiness.record(packet,b['reading_file_ref'])['body']['blob'];h=file['digest']
            if h not in cache:
                path=ROOT/packet['blobs'][h]['path'];raw=path.read_bytes()
                if sha256(raw).hexdigest()!=h:raise ValueError('reading source bytes changed')
                cache[h]=json.loads(raw)
            reading=get_pointer(cache[h],b['pointer'])
            if b['literal']!=reading['literal']:raise ValueError('reading pointer literal')
            if o['context']['measurement_kind']=='instant balance':
                instant=reading.get('measurement_date',reading.get('date',reading.get('period')))
                date.fromisoformat(instant);timing={'kind':'instant','at':instant}
            else:
                match=re.fullmatch(r'.+: (\d{4}-\d{2}-\d{2}) through (\d{4}-\d{2}-\d{2})',o['context']['period'])
                if not match:raise ValueError('unsupported source interval')
                start,last=match.groups();timing={'kind':'period','start':start,
                    'end_exclusive':(date.fromisoformat(last)+timedelta(days=1)).isoformat()}
            if alias in out:raise ValueError('ambiguous alias')
            out[alias]={'declaration':{'alias':alias,'collection':collection,'observation_ref':o['ref'],
                'measurement_time':timing,'unit':o['context']['unit']},
                'observation':deepcopy(o),'reading_pointer':b['pointer'],'reading_file_ref':b['reading_file_ref'],
                'measurement_time_source':deepcopy(reading)}
    return request,result,out

def classify(key):
    if key.startswith('annual_to_quarter:'):return 'cross_period_endpoint'
    if key in DERIVED:return 'derived_subtotal'
    if key.startswith('diagnostic:'):return 'explanatory_difference'
    if key=='balance_changes':return 'endpoint_difference'
    if key.startswith(('balance:','opening:')) or key in ['equity_opening','equity_closing']:return 'snapshot_sum'
    if key.startswith('equity_to_balance:'):return 'same_date_endpoint'
    if key=='closing_cash_population_match':return 'displayed_population_comparison'
    if key.startswith('income_to:') or key=='oci_to_equity':return 'same_period_measurement'
    if key in BRIDGES:return 'stock_flow_bridge'
    return 'period_sum'

def fixture(target=OPS,view='combined'):
    request,result,observations=evidence(target,view)
    rows=[]
    for group in ['annual','interim']:
        if not result['known_evidence'][group+'_refs']:continue
        for i,r in enumerate(prior.load_ledger(group)['relations']):
            kind=classify(r['id']);rhs=[];comparison='terms'
            if kind=='cross_period_endpoint':
                lhs=[{'alias':'annual.'+r['annual_row'],'coefficient':'1/1'}]
                rhs=[{'alias':'interim.'+r['interim_row'],'coefficient':'1/1'}]
            else:
                lhs=[{'alias':group+'.'+t['row'],'coefficient':rat(Q(t['coefficient']))} for t in r['terms']]
                if kind=='derived_subtotal':comparison='derived_only'
                elif kind=='explanatory_difference':comparison='zero'
                elif kind=='endpoint_difference':rhs=[{'alias':group+'.balance.equity','coefficient':'1/1'},{'alias':group+'.opening.equity','coefficient':'-1/1'}]
                else:rhs=[{'alias':group+'.'+r['target'],'coefficient':'1/1'}]
            rows.append({'id':group+'.'+r['id'],'group':group,'source_pointer':'/relations/'+str(i),
                'source_record_sha256':digest(r),'kind':kind,'lhs':lhs,'rhs':rhs,'comparison':comparison,
                'omitted_source_rows':deepcopy(r.get('removed_annual_rows',[]))})
    return {'profile':PROFILE,'name':'Apple complete retained statement contexts',
        'source':{'target':target,'view':view,'request_sha256':digest(request),'result_sha256':digest(result)},
        'observations':[v['declaration'] for v in observations.values()],
        'relations':rows,'requirement_ids':[d['id'] for d in result['dependencies']]}

def validate(body):
    Draft202012Validator(schema(),format_checker=FormatChecker()).validate(body)
    def strings(x):
        if isinstance(x,dict):
            for k,v in x.items():strings(k);strings(v)
        elif isinstance(x,list):
            for v in x:strings(v)
        elif isinstance(x,str):
            x.encode('utf-8',errors='strict')
            if any(ord(c)<32 or ord(c)==127 or c in '\x85\u2028\u2029' for c in x):raise ValueError('single-line scalar')
    strings(body)
    for field,key in [('observations','alias'),('relations','id')]:
        ids=[r[key] for r in body[field]]
        if len(set(ids))!=len(ids):raise ValueError('duplicate '+field)
    if len(body['requirement_ids'])!=len(set(body['requirement_ids'])):raise ValueError('duplicate requirement')
    for o in body['observations']:
        t=o['measurement_time']
        if t['kind']=='period' and t['start']>=t['end_exclusive']:raise ValueError('reversed period')
    return body

def context_check(relation,observations):
    terms=relation['lhs']+relation['rhs'];missing=[t['alias'] for t in terms if t['alias'] not in observations]
    if missing:return {'status':'unresolved_view','missing_aliases':sorted(set(missing))}
    os=[observations[t['alias']] for t in terms]
    contexts=[o['observation']['context'] for o in os]
    for field in ['issuer','perimeter','unit']:
        if len({c[field] for c in contexts})!=1:raise ValueError('incompatible '+field)
    if contexts[0]['unit']!='USD million':raise ValueError('unsupported relation unit')
    kind=relation['kind'];times=[o['declaration']['measurement_time'] for o in os]
    if kind!='cross_period_endpoint':
        if len({c['basis'] for c in contexts})!=1:raise ValueError('incompatible basis')
        if len({o['observation']['record']['body']['source_ref']['digest'] for o in os})!=1:raise ValueError('incompatible source')
    if kind in ['snapshot_sum','same_date_endpoint','displayed_population_comparison','cross_period_endpoint']:
        if any(t['kind']!='instant' for t in times) or any(t!=times[0] for t in times):raise ValueError('incompatible instant')
    elif kind in ['period_sum','same_period_measurement','derived_subtotal']:
        if any(t['kind']!='period' for t in times) or any(t!=times[0] for t in times):raise ValueError('incompatible interval')
    elif kind in ['stock_flow_bridge','endpoint_difference','explanatory_difference']:
        # Exact bound relation roles admit documented endpoint/flow differences.
        group=relation['group'];anchor=observations[group+'.operations.net_income']['declaration']['measurement_time']
        beginning=(date.fromisoformat(anchor['start'])-timedelta(days=1)).isoformat()
        end=(date.fromisoformat(anchor['end_exclusive'])-timedelta(days=1)).isoformat()
        for t in times:
            if t['kind']=='period' and t!=anchor:raise ValueError('bridge flow interval')
            if t['kind']=='instant' and t['at'] not in [beginning,end]:raise ValueError('bridge endpoint')
    return {'status':'compatible_for_declared_displayed_relation','kind':kind,
        'cross_basis_comparison':kind=='cross_period_endpoint',
        'limit':'Context permits this declared displayed comparison; no exact latent equality or cash-population equivalence is admitted.'}

def compute(terms,observations):
    missing=[];total=Q(0)
    for t in terms:
        o=observations.get(t['alias'])
        if o is None:missing.append(t['alias']);continue
        v=o['observation']['record']['body']['value']
        if v['tag']!='known_displayed':missing.append(t['alias']);continue
        total+=Q(t['coefficient'])*Q(int(v['amount']['n']),int(v['amount']['d']))
    return {'status':'unresolved','missing':sorted(set(missing))} if missing else {'status':'known_displayed_arithmetic','value':rat(total)}

def evaluate(body):
    validate(body);expected=fixture(body['source']['target'],body['source']['view'])
    comparison=deepcopy(body);comparison['name']=expected['name']
    if comparison!=expected:raise ValueError('source or relation binding mismatch')
    _,readiness_result,observations=evidence(body['source']['target'],body['source']['view'])
    rows=[];ledgers={}
    for r in body['relations']:
        group=r['group']
        if group not in ledgers:ledgers[group]=prior.load_ledger(group)
        original=get_pointer(ledgers[group],r['source_pointer'])
        if digest(original)!=r['source_record_sha256']:raise ValueError('ledger row hash')
        context=context_check(r,observations);lhs=compute(r['lhs'],observations)
        rhs=compute(r['rhs'],observations) if r['comparison']=='terms' else None
        if r['comparison']=='derived_only':arithmetic={'status':'derived_subtotal','subtotal':lhs,'independent_residual':None}
        elif context['status']=='unresolved_view' or lhs['status']=='unresolved' or rhs and rhs['status']=='unresolved':
            arithmetic={'status':'unresolved','lhs':lhs,'rhs':rhs,'residual':None}
        else:
            difference=Q(lhs['value'])-(Q(rhs['value']) if rhs else Q(0))
            arithmetic={'status':'displayed_difference','lhs':lhs,'rhs':rhs,'residual':rat(difference),
                'zero':difference==0,'role':'explanatory_only' if r['kind']=='explanatory_difference' else 'displayed_check_only'}
        disposition={'id':r['id'],'original_record':deepcopy(original),'kind':r['kind'],
            'context_check':context,'arithmetic':arithmetic,'omitted_source_rows':r['omitted_source_rows'],
            'next':'Gross events, source admission and latent-state consistency require separate evidence.'}
        if r['kind']=='derived_subtotal':disposition['role_correction']='No independent observed target; original fixed/derived subtotal preserved for provenance only.'
        if r['omitted_source_rows']:disposition['omission_limit']='Listed interim rows only; omitted annual concepts are not zero facts.'
        rows.append(disposition)
    return {'profile':PROFILE,'request_sha256':digest(body),'status':'displayed_statement_description',
        'observations':observations,'relations':rows,'preserved_ledgers':ledgers,
        'requirements':deepcopy(readiness_result['dependencies']),
        'actual_history':'unknown','joint_latent_feasibility':'uncomputed','executable_opening':None,'executed':False}

def verify_result(body,result):
    try:return canonical(evaluate(body))==canonical(result)
    except Exception:return False
