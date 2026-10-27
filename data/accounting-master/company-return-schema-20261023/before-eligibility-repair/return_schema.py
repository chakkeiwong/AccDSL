"""Closed component authoring and static checks; no accounting journals execute."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
from hashlib import sha256
import json
from jsonschema import Draft202012Validator, FormatChecker

PROFILE='ReturnModuleAuthoringDraft/1'
ROLES=['cash','inventory','refund_liability','recovery_asset','revenue','cogs',
       'selling_expense','dta','dtl','current_tax','deferred_tax']
NUMBERS=['sold_units','expected_units','unit_refund','unit_cost','estimated_handling',
         'estimated_deterioration','refund','recovery']
TAX_NUMBERS=['rate','refund_tax_base','recovery_tax_base','opening_dta','opening_dtl']
FINDINGS=['rate_enacted','recovery_supported','temporary_difference_inventory_complete',
          'outside_basis_timing_control','outside_basis_no_foreseeable_reversal']
SETTLE_NUMBERS=['actual_units','unit_handling','unit_deterioration','refund_cash','handling_cash','inventory_nrv']
METHODS={'settle':'returns.settle','sell':'inventory.sell'}
def closed(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return sha256(canonical(x)).hexdigest()
def rational(value):
    if type(value) is not str:raise ValueError('exact rational string required')
    q=Q(value)
    if value!=str(q.numerator)+'/'+str(q.denominator):raise ValueError('canonical n/d required')
    return q


def schema():
    text={'type':'string','minLength':1}; ident={'type':'string','pattern':r'^[A-Za-z][A-Za-z0-9_-]*$','not':{'const':'unknown'}}
    h={'type':'string','pattern':'^[0-9a-f]{64}$'}
    num={'type':'string','pattern':r'^(unknown|-?(0|[1-9][0-9]*)/[1-9][0-9]*)$'}
    truth={'oneOf':[{'type':'boolean'},{'const':'unknown'}]}
    day={'type':'string','format':'date','pattern':r'^\d{4}-\d{2}-\d{2}$'}
    component=closed({'id':ident,'source_pointer':text,**{k:num for k in NUMBERS},'settled':truth})
    lot=closed({'id':ident,'component_id':ident,'units':num,'carrying':num,'tax_base':num,'acquired':day})
    settle=closed({'id':ident,'kind':{'const':'settle'},'method':{'const':METHODS['settle']},
        'date':day,'source_pointer':text,'component_id':ident,'lot_id':ident,
        **{k:num for k in SETTLE_NUMBERS},'all_rights_closed':truth,'handling_is_selling_cost':truth})
    sale=closed({'id':ident,'kind':{'const':'sell'},'method':{'const':METHODS['sell']},
        'date':day,'source_pointer':text,'lot_id':ident,'fraction':num,'proceeds':num,'performance_complete':truth})
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**closed({
        'profile':{'const':PROFILE},'name':text,
        'source':closed({'packet_sha256':h,'opening_sha256':h,'meaning':{'const':'retained_synthetic_case'}}),
        'context':closed({'entity':text,'book_role':{'const':'legal'},'currency':text,'case_id':ident}),
        'period':closed({'start':day,'end_exclusive':day}),
        'accounts':closed({k:{'const':k} for k in ROLES}),
        'component':component,
        'tax':closed({'method':{'const':'refund_and_recovered_stock_on_settlement'},
            'source_pointer':text,'opening_source_pointer':text,
            **{k:num for k in TAX_NUMBERS},**{k:truth for k in FINDINGS}}),
        'lots':{'type':'array','items':lot},'events':{'type':'array','minItems':1,'items':{'oneOf':[settle,sale]}}})}


def validate(body):
    rule=schema();Draft202012Validator(rule,format_checker=FormatChecker()).validate(body)
    def walk(value,shape):
        if 'oneOf' in shape:
            valid=[r for r in shape['oneOf'] if Draft202012Validator(r).is_valid(value)]
            if len(valid)!=1:raise ValueError('ambiguous typed field')
            return walk(value,valid[0])
        if type(value) is dict:
            for k,v in value.items():walk(v,shape['properties'][k])
        elif type(value) is list:
            for v in value:walk(v,shape['items'])
        elif shape.get('pattern','').startswith('^(unknown|') and value!='unknown':
            if rational(value)<0:raise ValueError('negative quantity outside subset')
        elif type(value) is str:value.encode('utf-8',errors='strict')
    walk(body,rule)
    start,end=[date.fromisoformat(body['period'][k]) for k in ['start','end_exclusive']]
    if start>=end:raise ValueError('nonpositive period')
    component=body['component'];lots=body['lots'];events=body['events']
    for values in [[l['id'] for l in lots],[e['id'] for e in events]]:
        if len(values)!=len(set(values)):raise ValueError('duplicate identity')
    if any(l['component_id']!=component['id'] for l in lots):raise ValueError('lot component reference')
    if any(l['acquired']>body['period']['start'] for l in lots):raise ValueError('opening lot acquired after opening')
    dates=[e['date'] for e in events]
    if dates!=sorted(dates) or any(not start<=date.fromisoformat(d)<end for d in dates):raise ValueError('event chronology')
    known_lots={l['id'] for l in lots};settlements=0;sold=set()
    for event in events:
        if event['kind']=='settle':
            settlements+=1
            if settlements>1:raise ValueError('duplicate complete settlement')
            if event['component_id']!=component['id']:raise ValueError('event component reference')
            if event['lot_id'] in known_lots:raise ValueError('duplicate recovered lot')
            known_lots.add(event['lot_id'])
        else:
            if event['lot_id'] not in known_lots:raise ValueError('sale before lot exists')
            if event['lot_id'] in sold:raise ValueError('whole lot sold twice')
            sold.add(event['lot_id'])
    if not component['source_pointer'].startswith('/record_registry/'):raise ValueError('component source pointer')
    if any(not e['source_pointer'].startswith('/record_registry/') for e in events):raise ValueError('event source pointer')
    if any(not body['tax'][k].startswith('/record_registry/') for k in ['source_pointer','opening_source_pointer']):raise ValueError('tax source pointer')
    return body


def assess(body):
    try:
        validate(body)
        unknown=[]
        def visit(x,rule,p=''):
            if 'oneOf' in rule:
                matches=[r for r in rule['oneOf'] if Draft202012Validator(r).is_valid(x)]
                return visit(x,matches[0],p)
            if type(x) is dict:
                for k,v in x.items():visit(v,rule['properties'][k],p+'/'+k)
            elif type(x) is list:
                for i,v in enumerate(x):visit(v,rule['items'],p+'/'+str(i))
            elif x=='unknown' and (rule.get('const')=='unknown' or rule.get('pattern','').startswith('^(unknown|')):unknown.append(p)
        visit(body,schema())
        if unknown:return {'status':'unresolved','missing':unknown,'executed':False}
        c,t=body['component'],body['tax'];number=lambda d,k:rational(d[k])
        for key in FINDINGS:
            if t[key] is False:return {'status':'unsupported','reason':'finding:'+key,'executed':False}
        if number(t,'rate')>1:raise ValueError('tax rate exceeds one')
        if number(c,'expected_units')>number(c,'sold_units'):raise ValueError('expected returns exceed units sold')
        if number(c,'estimated_handling')+number(c,'estimated_deterioration')>number(c,'unit_cost'):
            return {'status':'unsupported','reason':'negative_recovery_estimate','executed':False}
        if not c['settled']:
            if number(c,'refund')!=number(c,'expected_units')*number(c,'unit_refund'):raise ValueError('refund allocation')
            if number(c,'recovery')!=number(c,'expected_units')*(number(c,'unit_cost')-number(c,'estimated_handling')-number(c,'estimated_deterioration')):raise ValueError('recovery allocation')
        elif number(c,'refund') or number(c,'recovery'):
            raise ValueError('settled component has outstanding rights')
        if number(t,'refund_tax_base')!=0 or number(t,'recovery_tax_base')!=0:
            return {'status':'unsupported','reason':'tax_basis_outside_selected_method','executed':False}
        if number(t,'opening_dta')!=number(c,'refund')*number(t,'rate'):raise ValueError('opening deferred asset correspondence')
        if number(t,'opening_dtl')!=number(c,'recovery')*number(t,'rate'):raise ValueError('opening deferred liability correspondence')
        if not c['settled'] and body['lots']:raise ValueError('opening recovered lot before complete settlement')
        for lot in body['lots']:
            if number(lot,'units')<=0:raise ValueError('empty recovered lot')
            if number(lot,'tax_base')!=number(lot,'carrying'):
                return {'status':'unsupported','reason':'recovered_tax_cost_outside_method','executed':False}
        for event in body['events']:
            if event['kind']=='settle':
                if c['settled']:raise ValueError('settlement already completed')
                for key in ['all_rights_closed','handling_is_selling_cost']:
                    if event[key] is False:return {'status':'unsupported','reason':'finding:'+key,'executed':False}
                if number(event,'actual_units')>number(c,'sold_units') or number(event,'unit_deterioration')>number(c,'unit_cost'):raise ValueError('settlement quantity domain')
                if number(event,'refund_cash')!=number(event,'actual_units')*number(c,'unit_refund'):raise ValueError('refund cash correspondence')
                if number(event,'handling_cash')!=number(event,'actual_units')*number(event,'unit_handling'):raise ValueError('handling cash correspondence')
            else:
                if event['performance_complete'] is False:return {'status':'unsupported','reason':'performance_incomplete','executed':False}
                if number(event,'fraction')!=1:return {'status':'unsupported','reason':'whole_lot_sale_only','executed':False}
        return {'status':'statically_eligible','executed':False,'accounting_admission':False,
                'source_admission':False,'profile':PROFILE,'draft_sha256':digest(body)}
    except Exception as exc:
        return {'status':'invalid','reason':type(exc).__name__+': '+str(exc).splitlines()[0][:250],'executed':False}
