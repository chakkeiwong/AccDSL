"""Draft authored operations; no imported forecast journals or persistent writes."""
from copy import deepcopy
from datetime import date, datetime
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import sys
from jsonschema import Draft202012Validator, FormatChecker

YEAR = Path(__file__).resolve().parent.parent/'company-inputs-20261023'
sys.path.insert(0,str(YEAR))
from authoring import closed, q, schema as annual_schema
from semantics import ACCOUNTS, ASSETS, TEMPORARY, record_digest

SINGLE = ['facility_draw','facility_interest','facility_repayment','depreciation','interest','tax','close']
REPEAT = ['purchase','delivery','supplier_payment','collection','payroll','plant_addition','dividend']


def wire(x):
    if isinstance(x,Q): return f'{x.numerator}/{x.denominator}'
    if isinstance(x,dict): return {k:wire(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [wire(v) for v in x]
    return x


def canonical(x):
    return json.dumps(wire(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def schema():
    ap=annual_schema()['properties'];rat=deepcopy(ap['inventory']['properties']['price'])
    txt={'type':'string','minLength':1};day={'type':'string','format':'date','pattern':r'^\d{4}-\d{2}-\d{2}$'}
    truth={'enum':[True,False,'unknown']}
    allocation=closed({'claim_id':txt,'amount':rat})
    payloads={
        'purchase':closed({'units':rat,'claim_id':txt}),
        'delivery':closed({'units':rat,'unit_price':rat,'control_transferred':truth,'claim_id':txt}),
        'collection':closed({'allocations':{'type':'array','minItems':1,'items':allocation}}),
        'supplier_payment':closed({'allocations':{'type':'array','minItems':1,'items':allocation}}),
        'payroll':closed({'amount':rat}), 'dividend':closed({'amount':rat}),
        'plant_addition':closed({'asset_id':txt,'cost':rat,'life':rat,'in_service':day})}
    payloads.update({kind:closed({}) for kind in SINGLE})
    fields={k:deepcopy(ap[k]) for k in ['name','assumption','source','opening_digest','context',
        'period','information','assets','depreciation_method','debt','facility','loan','tax']}
    fields['profile']={'const':'CompanyOperationsDraft/1'}
    fields['inventory']=closed({'method':txt,'unit_cost':rat})
    cp=deepcopy(ap['opening_claims']['items']['properties']);cp.pop('settlement')
    fields['opening_claims']={'type':'array','minItems':1,'items':closed(cp)}
    fields['operations']={'type':'array','minItems':1,'items':{'oneOf':[closed({
        'id':txt,'kind':{'const':kind},'at':deepcopy(ap['events']['items']['properties']['at']),
        'payload':payload}) for kind,payload in payloads.items()]}}
    out=closed(fields);out['$schema']='https://json-schema.org/draft/2020-12/schema'
    return out


def lower_annual(body, opening_units):
    """Lower authored economics, without consulting an annual run or projection."""
    out={k:deepcopy(v) for k,v in body.items() if k not in ['profile','events','inventory','trade','cash','opening_claims']}
    out['profile']='CompanyOperationsDraft/1'
    out['inventory']={k:body['inventory'][k] for k in ['method','unit_cost']}
    out['opening_claims']=[{k:v for k,v in c.items() if k!='settlement'} for c in body['opening_claims']]
    inv,trade,cash=body['inventory'],body['trade'],body['cash']
    purchase=q(inv['demand_units'])+q(inv['target_units'])-opening_units
    sales=q(inv['demand_units'])*q(inv['price'])
    payloads={'purchase':{'units':wire(purchase),'claim_id':trade['purchase_claim_id']},
        'delivery':{'units':inv['demand_units'],'unit_price':inv['price'],
            'control_transferred':inv['control_transferred'],'claim_id':trade['sales_claim_id']},
        'payroll':{'amount':cash['payroll']},'dividend':{'amount':cash['dividend']},
        'plant_addition':{'asset_id':cash['capex_id'],'cost':cash['capex'],
            'life':cash['capex_life'],'in_service':cash['capex_service']}}
    for kind,ledger,cid,amount in [('collection','receivable',trade['sales_claim_id'],sales*q(trade['collection_fraction'])),
            ('supplier_payment','payable',trade['purchase_claim_id'],q(trade['supplier_payment']))]:
        payloads[kind]={'allocations':[{'claim_id':c['id'],'amount':c['settlement']} for c in body['opening_claims'] if c['ledger']==ledger]+[{'claim_id':cid,'amount':wire(amount)}]}
    out['operations']=[{'id':e['kind']+'-1','kind':e['kind'],'at':e['at'],
        'payload':deepcopy(payloads.get(e['kind'],{}))} for e in body['events']]
    return out


def result(status,**fields):
    return {'status':status,'committed':False,'conditional_state':True,**fields}


def unknowns(value,rule,path=''):
    if isinstance(value,dict):
        return sum((unknowns(v,rule['properties'][k],path+'/'+k) for k,v in value.items()),[])
    if isinstance(value,list):
        return sum((unknowns(v,rule['items'],path+'/'+str(i)) for i,v in enumerate(value)),[])
    admits=rule.get('pattern','').startswith('^(unknown|') or 'unknown' in rule.get('enum',[])
    return [path] if value=='unknown' and admits else []


def inspect_rationals(value,rule):
    if isinstance(value,dict):
        for k,v in value.items(): inspect_rationals(v,rule['properties'][k])
    elif isinstance(value,list):
        for v in value: inspect_rationals(v,rule['items'])
    elif rule.get('pattern','').startswith('^(unknown|') and value!='unknown':
        if q(value)<0: raise ValueError('negative amount')


def validate(body,source):
    errors=list(Draft202012Validator(schema(),format_checker=FormatChecker()).iter_errors(body))
    if errors:return result('invalid',reason='schema',path=list(errors[0].path))
    if hashlib.sha256(source).hexdigest()!=body['source']['sha256']:
        return result('invalid',reason='source_digest')
    try:
        registry=json.loads(source)['record_registry'];entry=registry[body['opening_digest']]
        if entry['kind']!='CompanyState' or record_digest(entry)!=body['opening_digest']:
            return result('invalid',reason='opening_record')
        ctx_ref=entry['body']['context_ref'];context=registry[ctx_ref['digest']]
        if context['kind']!='Context' or record_digest(context)!=ctx_ref['digest']:
            return result('invalid',reason='context_record')
        cb=context['body'];opening=entry['body']
        balances={k:Q(v['n'])/Q(v['d']) for k,v in opening['balances'].items()}
        units=Q(opening['inventory_units']['n'])/Q(opening['inventory_units']['d'])
    except (ValueError,KeyError,TypeError,ZeroDivisionError):
        return result('invalid',reason='source_structure')
    if any(body['context'][k]!=cb[k] for k in body['context']) or cb['period_end_exclusive']!=body['period']['start']:
        return result('invalid',reason='opening_context')
    start,end=[date.fromisoformat(body['period'][k]) for k in ['start','end_exclusive']]
    if start.month!=1 or start.day!=1 or end!=date(start.year+1,1,1):
        return result('unsupported',reason='full_calendar_year_required')
    if set(balances)!=set(ACCOUNTS) or sum(balances.values(),Q(0)) or any(balances[k] for k in TEMPORARY):
        return result('invalid',reason='opening_accounts')
    global_body={k:v for k,v in body.items() if k!='operations'}
    missing=unknowns(global_body,schema())
    if missing:return result('unresolved',obligations=['supply:'+p for p in missing])
    methods=[(body['inventory']['method'],'homogeneous_cost'),(body['depreciation_method'],'straight_line_full_year'),
        (body['loan']['day_count'],'ACT365_calendar'),(body['loan']['interest_cash_class'],'operating'),(body['tax']['method'],'immediate_deductible')]
    if any(a!=b for a,b in methods):return result('unsupported',reason='method')
    try:
        for k,v in global_body.items():inspect_rationals(v,schema()['properties'][k])
    except (ValueError,ZeroDivisionError):return result('invalid',reason='rational')
    cost=q(body['inventory']['unit_cost']);debt=body['debt'];facility=body['facility'];loan=body['loan']
    if cost<=0 or units<0 or cost*units!=balances['inventory']:return result('invalid',reason='inventory_control')
    if q(debt['floating_share'])>1 or q(body['tax']['rate'])>1:return result('invalid',reason='fraction_domain')
    if q(debt['coupon_years'])!=1:return result('unsupported',reason='annual_coupon_only')
    if q(debt['principal'])+q(facility['drawn'])!=-balances['debt']:return result('invalid',reason='debt_control')
    if q(facility['drawn'])!=0:return result('unsupported',reason='opening_facility_accrual')
    if loan['facility_id']!=facility['id'] or q(facility['reserved'])>q(facility['limit']):return result('invalid',reason='facility_control')
    if q(loan['fee'])!=0:return result('unsupported',reason='loan_fee')
    claims=body['opening_claims'];assets=body['assets']
    if len({c['id'] for c in claims})!=len(claims):return result('invalid',reason='duplicate_claim')
    if any(sum((q(c['amount']) for c in claims if c['ledger']==l),Q(0))!=s*balances[a] for l,a,s in [('receivable','receivables',1),('payable','payables',-1)]):return result('invalid',reason='claim_control')
    if len({a['id'] for a in assets})!=len(assets):return result('invalid',reason='duplicate_asset')
    if sum(q(a['cost']) for a in assets)!=balances['plant_cost'] or sum(q(a['accumulated']) for a in assets)!=-balances['accum_depreciation']:return result('invalid',reason='asset_control')
    if any(q(a['life'])<=0 or q(a['accumulated'])>q(a['cost']) for a in assets):return result('invalid',reason='asset_domain')
    if any(start<date.fromisoformat(a['in_service'])<end for a in assets):return result('unsupported',reason='midyear_service_fraction')
    if any(date.fromisoformat(a['in_service'])>start and q(a['accumulated']) for a in assets):return result('invalid',reason='unserved_asset_accumulation')
    ops=body['operations'];ids=[o['id'] for o in ops];kinds=[o['kind'] for o in ops]
    if len(set(ids))!=len(ids):return result('invalid',reason='duplicate_operation_id')
    if any(kinds.count(k)!=1 for k in SINGLE):return result('invalid',reason='single_operation_count')
    if any(o['at']=='unknown' for o in ops):return result('unresolved',obligations=['supply:operation_instants'])
    times=[datetime.fromisoformat(o['at'].replace('Z','+00:00')) for o in ops]
    if times!=sorted(times) or any(not start<=t.date()<end for t in times):return result('invalid',reason='chronology')
    pos={k:kinds.index(k) for k in SINGLE}
    if not pos['facility_draw']<pos['facility_interest']<pos['facility_repayment'] or pos['close']!=len(ops)-1:return result('invalid',reason='annual_dependencies')
    if any(i>pos['tax'] for i,k in enumerate(kinds) if k not in ['tax','close','dividend']):return result('invalid',reason='tax_before_operations')
    if any(i>pos['depreciation'] for i,k in enumerate(kinds) if k=='plant_addition'):return result('invalid',reason='late_asset_addition')
    if any(times[pos[k]].date()!=date(start.year,12,31) for k in ['depreciation','interest','tax','close']):return result('unsupported',reason='annual_tail_date')
    if times[pos['facility_interest']].date()!=times[pos['facility_repayment']].date():return result('unsupported',reason='bridge_repayment_date')
    days=(times[pos['facility_repayment']].date()-times[pos['facility_draw']].date()).days
    return result('validated',opening=balances,units=units,bridge_interest=q(loan['principal'])*q(loan['annual_rate'])*Q(days,365))


def _execute(body, source):
    checked=validate(body,source)
    if checked['status']!='validated':return checked
    b=checked['opening'].copy();initial=b.copy();units=checked['units']
    cost=q(body['inventory']['unit_cost']);drawn=q(body['facility']['drawn'])
    assets=deepcopy(body['assets'])
    claims={c['id']:{'ledger':c['ledger'],'recognised':q(c['amount']),
        'settled':Q(0),'outstanding':q(c['amount'])} for c in body['opening_claims']}
    applied=[];flows={k:Q(0) for k in ['operating','investing','financing']}
    minimum=b['cash'];capex=Q(0);dividends=Q(0)
    payload_rules={r['properties']['kind']['const']:r['properties']['payload'] for r in schema()['properties']['operations']['items']['oneOf']}

    def halted(status,reason,op,**extra):
        return result(status,reason=reason,event=op['id'],event_kind=op['kind'],
            balances=b.copy(),claims=deepcopy(claims),assets=deepcopy(assets),
            inventory_units=units,facility_drawn=drawn,flows=flows.copy(),
            applied=deepcopy(applied),**extra)

    for i,op in enumerate(body['operations']):
        kind,p=op['kind'],op['payload'];rule=payload_rules[kind]
        missing=unknowns(p,rule,'/operations/'+str(i)+'/payload')
        if missing:return halted('unresolved','operation_inputs',op,obligations=['supply:'+x for x in missing])
        try:inspect_rationals(p,rule)
        except (ValueError,ZeroDivisionError):return halted('invalid','operation_rational',op)
        nc,na,nu,nd=deepcopy(claims),deepcopy(assets),units,drawn
        cc=None;new_capex,new_dividend=Q(0),Q(0)
        if kind in ['purchase','delivery']:
            if p['claim_id'] in claims:return halted('invalid','duplicate_claim',op)
            qty=q(p['units'])
            if kind=='purchase':
                amount=qty*cost;lines={'inventory':amount,'payables':-amount};nu+=qty
                ledger='payable'
            else:
                if not p['control_transferred']:return halted('unsupported','control_not_transferred_method',op)
                if qty>units:return halted('economic_failure','inventory_shortfall',op,shortfall=qty-units)
                amount=qty*q(p['unit_price']);lines={'receivables':amount,'revenue':-amount,'cost_of_sales':qty*cost,'inventory':-qty*cost}
                nu-=qty;ledger='receivable'
            nc[p['claim_id']]={'ledger':ledger,'recognised':amount,'settled':Q(0),'outstanding':amount}
        elif kind in ['collection','supplier_payment']:
            ledger='receivable' if kind=='collection' else 'payable'
            allocations=p['allocations'];ids=[a['claim_id'] for a in allocations]
            if len(set(ids))!=len(ids):return halted('invalid','duplicate_allocation',op)
            amount=Q(0)
            for a in allocations:
                key=a['claim_id'];v=q(a['amount'])
                if key not in nc:return halted('invalid','unrecognised_claim',op)
                if nc[key]['ledger']!=ledger:return halted('invalid','wrong_claim_ledger',op)
                if v>nc[key]['outstanding']:return halted('invalid','over_settlement',op)
                nc[key]['settled']+=v;nc[key]['outstanding']-=v;amount+=v
            lines={'cash':amount,'receivables':-amount} if kind=='collection' else {'payables':amount,'cash':-amount}
            cc='operating'
        elif kind=='facility_draw':
            facility=body['facility'];principal=q(body['loan']['principal'])
            if not facility['eligible']:return halted('funding_failure','known_ineligible_facility',op)
            available=q(facility['limit'])-drawn-q(facility['reserved'])
            if principal>available:return halted('funding_failure','facility_headroom',op,shortfall=principal-available)
            lines={'cash':principal,'debt':-principal};nd+=principal;cc='financing'
        elif kind=='facility_interest':
            amount=checked['bridge_interest'];lines={'interest':amount,'cash':-amount};cc='operating'
        elif kind=='facility_repayment':
            amount=q(body['loan']['principal'])
            if amount>drawn:return halted('invalid','undrawn_repayment',op)
            lines={'debt':amount,'cash':-amount};nd-=amount;cc='financing'
        elif kind=='payroll':
            amount=q(p['amount']);lines={'payroll':amount,'cash':-amount};cc='operating'
        elif kind=='plant_addition':
            if p['asset_id'] in {a['id'] for a in assets}:return halted('invalid','duplicate_asset',op)
            if q(p['life'])<=0:return halted('invalid','asset_life',op)
            service=date.fromisoformat(p['in_service']);start=date.fromisoformat(body['period']['start']);end=date.fromisoformat(body['period']['end_exclusive'])
            if service<date.fromisoformat(op['at'][:10]):return halted('invalid','service_before_acquisition',op)
            if start<service<end:return halted('unsupported','midyear_service_fraction',op)
            amount=q(p['cost']);lines={'plant_cost':amount,'cash':-amount};cc='investing';new_capex=amount
            na.append({'id':p['asset_id'],'cost':p['cost'],'life':p['life'],'accumulated':'0/1','in_service':p['in_service']})
        elif kind=='depreciation':
            amount=Q(0)
            for a in na:
                if a['in_service']<=body['period']['start']:
                    charge=min(q(a['cost'])/q(a['life']),q(a['cost'])-q(a['accumulated']))
                    a['accumulated']=wire(q(a['accumulated'])+charge);amount+=charge
            lines={'depreciation':amount,'accum_depreciation':-amount}
        elif kind=='interest':
            d=body['debt'];share=q(d['floating_share'])
            amount=q(d['principal'])*((1-share)*q(d['fixed_rate'])+share*q(d['floating_rate']))
            lines={'interest':amount,'cash':-amount};cc='operating'
        elif kind=='tax':
            pbt=-b['revenue']-sum(b[k] for k in TEMPORARY if k not in ['revenue','tax'])
            if pbt<0:return halted('unsupported','loss_tax_method',op)
            amount=pbt*q(body['tax']['rate']);lines={'tax':amount,'cash':-amount};cc='operating'
        elif kind=='dividend':
            amount=q(p['amount']);lines={'retained':amount,'cash':-amount};cc='financing';new_dividend=amount
        else:
            income={k:-b[k] if k=='revenue' else b[k] for k in TEMPORARY}
            lines={k:-b[k] for k in TEMPORARY};lines['retained']=sum(b[k] for k in TEMPORARY)
        if sum(lines.values(),Q(0)):raise AssertionError('unbalanced proposed journal')
        cash=lines.get('cash',Q(0))
        if b['cash']+cash<0:return halted('funding_failure','cash_shortfall',op,shortfall=-(b['cash']+cash))
        for k,v in lines.items():b[k]+=v
        claims,assets,units,drawn=nc,na,nu,nd
        if cash:flows[cc]+=cash
        capex+=new_capex;dividends+=new_dividend;minimum=min(minimum,b['cash'])
        assert sum(b.values(),Q(0))==0 and units*cost==b['inventory']
        assert sum(q(a['cost']) for a in assets)==b['plant_cost']
        assert sum(q(a['accumulated']) for a in assets)==-b['accum_depreciation']
        assert all(c['recognised']-c['settled']==c['outstanding'] for c in claims.values())
        for ledger,account,sign in [('receivable','receivables',1),('payable','payables',-1)]:
            assert sum((c['outstanding'] for c in claims.values() if c['ledger']==ledger),Q(0))==sign*b[account]
        applied.append({'event':op['id'],'kind':kind,'at':op['at'],'date':op['at'][:10],
            'journal':lines,'cash_class':cc,'cash_after':b['cash'],'facility_principal_after':drawn,
            'method':'northstar.company-operations.'+kind+'@draft1','input_paths':['/operations/'+str(i)+'/payload'],
            'global_method_inputs':['/inventory','/debt','/loan','/tax','/depreciation_method']})
    profit=income['revenue']-sum(income[k] for k in TEMPORARY if k!='revenue')
    a=sum(b[k] for k in ASSETS);liab=-b['payables']-b['debt'];eq=-b['capital']-b['retained']
    indirect=profit+income['depreciation']-(b['receivables']-initial['receivables'])-(b['inventory']-initial['inventory'])-(b['payables']-initial['payables'])-(b['tax_prepaid']-initial['tax_prepaid'])
    assert a==liab+eq and indirect==flows['operating']
    assert initial['cash']+sum(flows.values())==b['cash']
    assert eq==-initial['capital']-initial['retained']+profit-dividends
    assert not any(b[k] for k in TEMPORARY)
    return result('complete_conditional',closing_balances=b,claims=claims,assets=assets,inventory_units=units,
        facility_drawn=drawn,income=income,journals=applied,minimum_cash=minimum,indirect_cfo=indirect,
        dividends=dividends,plant_additions=capex,statements={'assets':a,'liabilities':liab,'equity':eq,
        'profit':profit,'cash':b['cash'],'cash_flows':flows})


def execute(body,source):
    answer=_execute(body,source)
    answer.update(input_sha256=digest(body),source_sha256=hashlib.sha256(source).hexdigest(),
        forecast_journals_imported=False)
    return answer
