"""Attach existing partial collections to source-constrained observations."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'data/accounting-master/source-constrained-state-20261024'))
import partial_state
import method_collections_v1 as collections

PROFILE='SourceClaimPopulationView/1'
core=collections.core

def unknown(reason):return {'status':'unknown','reason':reason}
def known(value):return {'status':'known','value':value}

def definition(context):
    core.closed(context,['entity','scope','currency','scale'],'population_context')
    for name in ['entity','scope','currency']:core.text(context[name],name)
    core.need(core.scalar(context['scale'],'rational')>0,'population_scale')
    type_context={k:context[k] for k in ['entity','scope']}
    types={'id':{'kind':'text','context':type_context},
        'due':{'kind':'date','context':type_context},
        'remaining':{'kind':'rational','context':type_context,
            'dimensions':{'currency:'+context['currency']:1},'scale':context['scale']}}
    return {'profile':collections.PROFILE,'method_id':'claim.population.query','version':'1','inputs':{},
        'collections':{'claims':{'fields':{k:{'type':v,'role':'state',
            'source_ref':'Caller-supplied population; completeness requires separate evidence'} for k,v in types.items()}}},
        'constraints':[{'id':'unique_claims','op':'unique','collection':'claims','field':'id'}],
        'residual_prerequisites':['Completeness, gross/net mapping, recognition and behavioral timing require separate support.']}

def inspect(context,population):
    try:
        d=definition(context);values={'globals':{},'collections':{'claims':deepcopy(population)}}
        assessment=collections.assess(d,values,[])
        core.need(assessment['status']!='invalid','collection_invalid:'+assessment.get('reason',str(assessment.get('findings'))))
        rows=population['rows'];complete=population['status']=='complete'
        unique=assessment['status']=='collection_requirements_satisfied'
        amounts=[];terms=[];all_amounts=True;all_terms=True
        for row in rows:
            amount=row.get('remaining',unknown('remaining not supplied'))
            due=row.get('due',unknown('due not supplied'))
            identity=row.get('id',unknown('identity not supplied'))
            if amount['status']=='known':
                number=core.scalar(amount['value'],'rational');core.need(number>=0,'negative_remaining');amounts.append(number)
            else:all_amounts=False
            if due['status']!='known' or identity['status']!='known':all_terms=False
            terms.append({'id':deepcopy(identity),'due':deepcopy(due),'remaining':deepcopy(amount)})
        count=known(len(rows)) if complete and unique else unknown('Population completeness or unique identities unestablished')
        total=sum(amounts,Fraction())
        gross=known(str(total.numerator)+'/'+str(total.denominator)) if complete and unique and all_amounts else unknown('Complete exact gross claim amounts unestablished')
        schedule=known(terms) if complete and unique and all_terms and all_amounts else unknown('Complete identified contractual terms unestablished')
        return {'status':'population_inspected','context':deepcopy(context),'population':deepcopy(population),
            'definition':d,'native_assessment':assessment,'known_row_count':len(rows),
            'claim_count':count,'gross_remaining':gross,'contractual_due_terms':schedule,
            'future_receipts':unknown('Contractual due terms do not establish settlement behavior'),
            'executed':False,'source_admission':False,'accounting_admission':False,'posting_authorized':False}
    except Exception as exc:return {'status':'invalid','reason':str(exc)[:300],'executed':False}

def evaluate(body):
    # The retained source binder has no argument that can promote membership.
    base=partial_state.evaluate(body);populations=[]
    for constraint in base['constraints']:
        observation=constraint['observation'];row=observation['record']['body']
        if row['row_id'] not in ['balance.receivables','balance.vendor_receivables']:continue
        c=observation['context']
        core.need(c['unit']=='USD million','retained_money_unit')
        context={'entity':c['issuer'],'scope':c['perimeter'],'currency':'USD','scale':'1000000/1'}
        population={'status':'partial','rows':[],
            'reason':'No identified claim schedule bound to retained observation '+observation['ref']['digest']}
        inspected=inspect(context,population);core.need(inspected['status']=='population_inspected','population_inspection')
        populations.append({'constraint_id':constraint['id'],'source_constraint':deepcopy(constraint),
            'reported_measurement':deepcopy(row['value']),'population_view':inspected,
            'measurement_relation':{'status':'unresolved','reason':'No gross/net, allowance, offset or legal-book mapping supplied; no balancing residual computed'}})
    return {'profile':PROFILE,'request_sha256':partial_state.digest(body),'partial_state':base,'populations':populations,
        'executed':False,'source_admission':False,'accounting_admission':False,'posting_authorized':False,
        'executable_opening':None,'scope':'Source-bound population views over unchanged partial state; no new company-state model'}

def verify(body,result):
    try:return partial_state.canonical(evaluate(body))==partial_state.canonical(result)
    except Exception:return False
