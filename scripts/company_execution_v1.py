"""Bounded DemoCorporate/1 economic execution. No expected-result fixture is read."""
from __future__ import annotations
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = 'docs/design/fixtures/p05-economic-inputs-v1.json'
TEMP = ('revenue', 'cost_of_sales', 'payroll', 'depreciation', 'interest', 'tax')
ASSETS = ('cash','receivables','inventory','plant_cost','accum_depreciation','tax_prepaid')
LIABILITIES = ('payables','debt','interest_payable','tax_payable','payroll_payable','plant_payable','dividend_payable')
ACCOUNTS = ASSETS + LIABILITIES + ('capital','retained') + TEMP
CASH_CLASS = {'collect':'operating','supplier_pay':'operating','payroll_pay':'operating',
              'interest_pay':'operating','tax_pay':'operating','plant_pay':'investing',
              'dividend_pay':'financing','equity_issue':'financing','debt_issue':'financing','debt_redeem':'financing'}
PARAMS = {'purchase':{'units'}, 'deliver':{'units','consideration'}, 'collect':{'amount'},
          'supplier_pay':{'amount'}, 'payroll_accrue':{'amount'}, 'payroll_pay':{'amount'},
          'plant_acquire':{'amount','life_years'}, 'plant_pay':{'amount'}, 'depreciate':{'years','start'},
          'interest_accrue':{'rate','years'}, 'interest_pay':{'amount'}, 'tax_accrue':{'rate'},
          'tax_pay':{'amount'}, 'dividend_declare':{'amount'}, 'dividend_pay':{'amount'},
          'equity_issue':{'shares','price'}, 'debt_issue':{'amount'}, 'debt_redeem':{'amount'}, 'close':set()}


def exact(x):
    if isinstance(x, bool) or not isinstance(x, (str,int,F)):
        raise ValueError('exact rational string/integer required')
    return F(x)


def day(x):
    if not isinstance(x,str) or date.fromisoformat(x).isoformat()!=x:
        raise ValueError('ISO date required')
    return date.fromisoformat(x)


def serial(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {k:serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [serial(v) for v in x]
    return x


def canonical(x):
    return json.dumps(serial(x),sort_keys=True,separators=(',',':'),allow_nan=False)


def fingerprint(x): return hashlib.sha256(canonical(x).encode()).hexdigest()


def information(record, role, at, scenario='historical'):
    """Both measurement and behaviour consumers call this before reading values."""
    when=day(at)
    if not isinstance(record,dict) or record.get('kind') not in ('stress','disclosure','realized'):
        raise ValueError('supported information record required')
    if not isinstance(record.get('roles'),list) or role not in ('behaviour','measurement') or role not in record['roles']:
        raise ValueError('role denied')
    if record.get('kind')=='stress':
        if scenario!='exogenous_stress' or record.get('scenario')!=scenario:
            raise ValueError('stress input requires explicit exogenous scenario')
        if day(record['declared_at'])>when: raise ValueError('future stress declaration')
    else:
        for name in ('economic_date','published','ingested'):
            if record.get(name) is None: raise ValueError('unknown historical availability')
            if day(record[name])>when: raise ValueError('future information: '+name)
    return exact(record['value'])


def compatible_difference(annual, interim, at):
    if annual['revision_group']!=interim['revision_group']:
        raise ValueError('incompatible revision groups')
    return information({**annual,'value':annual['revenue']},'measurement',at)-information({**interim,'value':interim['revenue']},'measurement',at)


class Engine:
    def __init__(self, spec, *, opening=None, assets=None, before_commit=None):
        self.context=deepcopy(spec['context']); self.unit_cost=exact(spec['inventory_unit_cost'])
        if self.unit_cost<=0: raise ValueError('positive inventory cost required')
        self.period_bounds={p['id']:(p['start'],p['date']) for p in spec.get('periods',[])}
        self.balances={k:F(0) for k in ACCOUNTS}
        for k,v in (spec['opening'] if opening is None else opening).items():
            if k not in self.balances: raise ValueError('unknown opening account')
            self.balances[k]=exact(v)
        if sum(self.balances.values())!=0: raise ValueError('unbalanced opening')
        self.assets=deepcopy(spec['assets'] if assets is None else assets)
        for a in self.assets:
            a['cost']=exact(a['cost']); a['life_years']=exact(a['life_years']); a['accumulated']=exact(a['accumulated'])
            if a['life_years']<=0 or not 0<=a['accumulated']<=a['cost']: raise ValueError('invalid asset')
            day(a['in_service'])
        if sum((a['cost'] for a in self.assets),F(0))!=self.balances['plant_cost'] or sum((a['accumulated'] for a in self.assets),F(0))!=-self.balances['accum_depreciation']:
            raise ValueError('asset cohorts disagree with opening')
        self.journals=[]; self.applied={}; self.closed=set(); self.last_date=None
        self.before_commit=before_commit

    def snapshot(self):
        return serial({'balances':self.balances,'assets':self.assets,'journals':self.journals,
                       'applied':self.applied,'closed':sorted(self.closed),'last_date':self.last_date})

    def fork(self):
        result=deepcopy(self); result.before_commit=None; return result

    def apply(self,e):
        """Stage all changes; rejected/default/internal failures commit nothing."""
        ident=e.get('id') if isinstance(e,dict) else None
        result={'id':ident,'status':'Rejected'}
        try:
            if not isinstance(ident,str) or not ident: raise ValueError('event identity required')
            token=fingerprint(e)
            if ident in self.applied:
                if token!=self.applied[ident]['input_sha256']: raise ValueError('conflicting event identity')
                return {**deepcopy(self.applied[ident]),'status':'Duplicate','original_status':'Applied'}
            if set(e)!={'id','op','date','period','context','depends','params','decision_at','scenario','provenance'}:
                raise ValueError('unexpected/missing event fields')
            if e['context']!=self.context: raise ValueError('context mismatch')
            when=day(e['date']); decision=day(e['decision_at'])
            if decision>when: raise ValueError('decision after economic event')
            if self.last_date and when<day(self.last_date): raise ValueError('backdated event')
            if not isinstance(e['period'],str) or not e['period']: raise ValueError('period required')
            if e['period'] in self.closed: raise ValueError('period already closed')
            if e['period'] in self.period_bounds:
                start,end=self.period_bounds[e['period']]
                if not day(start)<=when<=day(end): raise ValueError('event outside declared period')
            if e['scenario'] not in ('historical','exogenous_stress','conditioning'):
                return {**result,'status':'Unsupported','reason':'unsupported scenario mode'}
            if not isinstance(e['depends'],list) or len(set(e['depends']))!=len(e['depends']) or any(d not in self.applied for d in e['depends']):
                raise ValueError('uncommitted or duplicate dependency')
            if not isinstance(e['provenance'],list) or not e['provenance']: raise ValueError('provenance required')
            for source in e['provenance']:
                if isinstance(source,dict) and 'information_inputs' in source:
                    for record in source['information_inputs'].values():
                        information(record,'measurement',e['decision_at'],e['scenario'])
            op=e['op']
            if op not in PARAMS: return {**result,'status':'Unsupported','reason':'unsupported operation: '+str(op)}
            if set(e['params'])!=PARAMS[op]: raise ValueError('operation parameter mismatch')
            p={}
            for k,v in e['params'].items():
                if k=='start': day(v); p[k]=v
                else:
                    p[k]=information(v,'measurement',e['decision_at'],e['scenario']) if isinstance(v,dict) else exact(v)
                    if p[k]<0: raise ValueError('negative parameter')
            b=deepcopy(self.balances); assets=deepcopy(self.assets); lines=[]
            def post(a,v):
                if v: lines.append({'account':a,'signed_amount':v}); b[a]+=v
            def pair(a,c,v): post(a,v);post(c,-v)
            def settle(account):
                if p['amount']>-b[account]: raise ValueError('settlement exceeds obligation')
                pair(account,'cash',p['amount'])
            if op=='purchase': pair('inventory','payables',p['units']*self.unit_cost)
            elif op=='deliver':
                cost=p['units']*self.unit_cost
                if cost>b['inventory']: raise ValueError('insufficient inventory')
                pair('receivables','revenue',p['consideration']); pair('cost_of_sales','inventory',cost)
            elif op=='collect':
                if p['amount']>b['receivables']: raise ValueError('collection exceeds receivable')
                pair('cash','receivables',p['amount'])
            elif op=='supplier_pay': settle('payables')
            elif op=='payroll_accrue': pair('payroll','payroll_payable',p['amount'])
            elif op=='payroll_pay': settle('payroll_payable')
            elif op=='plant_acquire':
                if p['life_years']<=0: raise ValueError('positive asset life required')
                pair('plant_cost','plant_payable',p['amount'])
                assets.append({'id':ident,'cost':p['amount'],'life_years':p['life_years'],
                               'in_service':(when+timedelta(days=1)).isoformat(),'accumulated':F(0)})
            elif op=='plant_pay': settle('plant_payable')
            elif op=='depreciate':
                if day(p['start'])>when: raise ValueError('accrual starts after event')
                for a in assets:
                    if day(a['in_service'])<=day(p['start']):
                        dep=min(a['cost']-a['accumulated'],a['cost']/a['life_years']*p['years'])
                        a['accumulated']+=dep; pair('depreciation','accum_depreciation',dep)
            elif op=='interest_accrue': pair('interest','interest_payable',-b['debt']*p['rate']*p['years'])
            elif op=='interest_pay': settle('interest_payable')
            elif op=='tax_accrue':
                charge=max(F(0),-sum(b[a] for a in TEMP if a!='tax'))*p['rate']
                use=min(b['tax_prepaid'],charge); post('tax',charge); post('tax_prepaid',-use);post('tax_payable',-(charge-use))
            elif op=='tax_pay':
                owed=-b['tax_payable']; use=min(owed,p['amount'])
                post('tax_payable',use);post('tax_prepaid',p['amount']-use);post('cash',-p['amount'])
            elif op=='dividend_declare': pair('retained','dividend_payable',p['amount'])
            elif op=='dividend_pay': settle('dividend_payable')
            elif op=='equity_issue': pair('cash','capital',p['shares']*p['price'])
            elif op=='debt_issue': pair('cash','debt',p['amount'])
            elif op=='debt_redeem': settle('debt')
            elif op=='close':
                for a in TEMP: pair(a,'retained',-b[a])
            if b['cash']<0:
                return {**result,'status':'EconomicFundingDefault','reason':'no borrowing policy',
                        'cash_available':str(self.balances['cash']),'cash_shortfall':str(-b['cash']),
                        'unpaid_obligation':str(-sum(x['signed_amount'] for x in lines if x['account']=='cash')),
                        'last_committed_sha256':fingerprint(self.snapshot()),'outputs_available':False}
            if sum(x['signed_amount'] for x in lines)!=0 or sum(b.values())!=0: raise RuntimeError('posting invariant failed')
            if any(b[a]<0 for a in ('cash','receivables','inventory','tax_prepaid')) or any(b[a]>0 for a in LIABILITIES):
                raise ValueError('invalid account sign')
            journal={'event_id':ident,'op':op,'date':e['date'],'period':e['period'],'postings':lines,
                     'cash_class':CASH_CLASS.get(op),'input_sha256':token,'provenance':deepcopy(e['provenance'])}
            if self.before_commit:
                # A validation/storage hook may fail, but cannot rewrite the
                # journal independently of the already staged economic state.
                candidate=deepcopy(journal)
                self.before_commit(candidate)
                if candidate!=journal: raise RuntimeError('staged journal mutation')
            result={**result,'status':'Applied','input_sha256':token,'journal_index':len(self.journals)}
            self.balances=b; self.assets=assets; self.journals.append(journal)
            self.last_date=e['date']; self.applied[ident]=deepcopy(result)
            if op=='close': self.closed.add(e['period'])
            return result
        except (ValueError,KeyError,TypeError,ZeroDivisionError,OverflowError) as exc:
            return {**result,'reason':str(exc)}
        except Exception as exc:
            return {**result,'status':'InternalFailure','reason':type(exc).__name__+': '+str(exc)}

    def run(self,events):
        try:
            ids=[e['id'] for e in events]
            if len(ids)!=len(set(ids)): raise ValueError('duplicate IDs within schedule')
            pending={e['id']:e for e in events}; order=[]; known=set(self.applied)
            while pending:
                ready=[e for e in pending.values() if set(e['depends'])<=known]
                if not ready: raise ValueError('dependency cycle or missing dependency')
                e=min(ready,key=lambda x:(x['date'],x['id'])); order.append(e);known.add(e['id']);del pending[e['id']]
            dates=[e['date'] for e in order]
            if dates!=sorted(dates): raise ValueError('dependency date inversion')
        except (ValueError,KeyError,TypeError) as exc:
            return {'status':'Rejected','reason':str(exc),'events':[],'statements':None}
        outcomes=[]
        for i,e in enumerate(order):
            r=self.apply(e);outcomes.append(r)
            if r['status'] not in ('Applied','Duplicate'):
                return {'status':r['status'],'events':outcomes,'unexecuted':[x['id'] for x in order[i+1:]],
                        'last_committed_state':self.snapshot(),'statements':None}
        return {'status':'Complete','events':outcomes}


def event(spec, ident, op, params, *, period='test', date_='2024-06-30', depends=(), decision_at=None, scenario='historical'):
    return {'id':ident,'op':op,'params':params,'date':date_,'period':period,'context':deepcopy(spec['context']),
            'depends':list(depends),'decision_at':decision_at or date_,'scenario':scenario,'provenance':[spec['source']]}


def period_events(spec,p):
    result=[]
    def add(op,params):
        result.append(event(spec,p['id']+'.'+op,op,params,period=p['id'],date_=p['date'],
                            depends=[result[-1]['id']] if result else (),decision_at=p.get('decision_at'),scenario=p.get('scenario','historical')))
        if 'information_inputs' in p:
            result[-1]['provenance'].append({'information_inputs':deepcopy(p['information_inputs'])})
    add('purchase',{'units':p['purchase_units']});add('deliver',{'units':p['delivery_units'],'consideration':p['sales_consideration']})
    add('collect',{'amount':p['collections']}); add('supplier_pay',{'amount':p['supplier_payment']})
    add('payroll_accrue',{'amount':p['payroll']});add('payroll_pay',{'amount':p['payroll']})
    add('plant_acquire',{'amount':p['capex'],'life_years':p['capex_life']});add('plant_pay',{'amount':p['capex']})
    add('depreciate',{'start':p['start'],'years':p['years']});add('interest_accrue',{'rate':p['interest_rate'],'years':p['years']})
    # Settlement is resolved from committed obligations by execute_period.
    add('interest_pay',{'amount':'0'});add('tax_accrue',{'rate':p['tax_rate']});add('tax_pay',{'amount':p.get('tax_payment','0')})
    add('dividend_declare',{'amount':p['dividend']});add('dividend_pay',{'amount':p['dividend']});add('close',{})
    return result


def statements(opening, journals):
    b={k:exact(opening.get(k,0)) for k in ACCOUNTS}; income={k:F(0) for k in TEMP}; cf={k:F(0) for k in ('operating','investing','financing')}
    dividends=F(0); issues=F(0); debt_issue=F(0); debt_redeem=F(0)
    for j in journals:
        for row in j['postings']:
            a=row['account'];v=exact(row['signed_amount']);b[a]+=v
            if j['op']!='close' and a in income:income[a]+=v
            if a=='cash' and j['cash_class']:cf[j['cash_class']]+=v
            if j['op']=='dividend_declare' and a=='retained':dividends+=v
            if j['op']=='equity_issue' and a=='capital':issues-=v
            if j['op']=='debt_issue' and a=='debt':debt_issue-=v
            if j['op']=='debt_redeem' and a=='debt':debt_redeem+=v
    o={k:exact(opening.get(k,0)) for k in ACCOUNTS}; profit=-sum(income.values()); equity=-b['capital']-b['retained']
    indirect=profit+income['depreciation']-sum(b[a]-o[a] for a in ('receivables','inventory','tax_prepaid'))-sum(b[a]-o[a] for a in ('payables','payroll_payable','interest_payable','tax_payable'))
    flat={k:b[k] for k in ('cash','receivables','inventory','tax_prepaid')}
    flat.update(plant_net=b['plant_cost']+b['accum_depreciation'],assets=sum(b[a] for a in ASSETS),
                payables=-b['payables'],debt=-b['debt'],equity=equity,revenue=-income['revenue'],profit=profit,
                interest=income['interest'],tax=income['tax'],operating_cash=cf['operating'],investing_cash=cf['investing'],financing_cash=cf['financing'],cash_change=b['cash']-o['cash'])
    return serial({'flat':flat,'balance_sheet':{'accounts':b,'assets':flat['assets'],'liabilities':-sum(b[a] for a in LIABILITIES),'equity':equity},
                   'income':{**{a:(-v if a=='revenue' else v) for a,v in income.items()},'profit':profit,'oci':F(0),'comprehensive_income':profit},
                   'cash_flow':{'direct':cf,'indirect_operating':indirect,'opening':o['cash'],'closing':b['cash']},
                   'equity':{'opening':-o['capital']-o['retained'],'profit':profit,'oci':F(0),'issues':issues,'dividends':dividends,'closing':equity},
                   'debt':{'opening':-o['debt'],'issued':debt_issue,'redeemed':debt_redeem,'closing':-b['debt']},
                   'plant':{'opening_cost':o['plant_cost'],'additions':b['plant_cost']-o['plant_cost'],'closing_cost':b['plant_cost'],
                            'opening_accumulated':-o['accum_depreciation'],'depreciation':income['depreciation'],'closing_accumulated':-b['accum_depreciation']}})


def execute_period(engine,spec,p):
    opening=deepcopy(engine.balances); start=len(engine.journals); outcomes=[]; actual=[]
    scheduled=period_events(spec,p)
    for i,e in enumerate(scheduled):
        if e['op']=='interest_pay':e['params']['amount']=str(-engine.balances['interest_payable'])
        if e['op']=='tax_pay' and 'tax_payment' not in p:e['params']['amount']=str(-engine.balances['tax_payable'])
        actual.append(deepcopy(e)); r=engine.apply(e);outcomes.append(r)
        if r['status']!='Applied':
            return serial({'status':r['status'],'inputs':actual,'events':outcomes,'opening':opening,'journals':engine.journals[start:],
                           'last_committed_state':engine.snapshot(),'statements':None,'unexecuted':[x['id'] for x in scheduled[i+1:]]})
    return serial({'status':'Complete','inputs':actual,'events':outcomes,'opening':opening,'journals':engine.journals[start:],
                   'closing':engine.snapshot(),'statements':statements(opening,engine.journals[start:])})


def stress_record(value, at='2025-01-01'):
    return {'value':str(value),'roles':['behaviour','measurement'],'kind':'stress','scenario':'exogenous_stress','declared_at':at}


def forecast_period(engine,spec,fixed_fraction,drivers=None):
    f=deepcopy(spec['forecast']); records=drivers if drivers is not None else {k:stress_record(v,f['start']) for k,v in f.items() if k not in ('start','date')}
    if day(f['start'])>day(f['date']):raise ValueError('forecast interval reversed')
    if engine.last_date and day(engine.last_date)>day(f['start']):
        raise ValueError('future economic state at forecast origin')
    vals={k:information(v,'behaviour',f['start'],'exogenous_stress') for k,v in records.items()}
    required=set(f)-{'start','date'}
    if set(vals)!=required: raise ValueError('forecast requires complete explicit driver set')
    # These drivers also determine recognised quantities and amounts. Passing
    # the behaviour check never grants a missing measurement permission.
    for record in records.values():information(record,'measurement',f['start'],'exogenous_stress')
    alpha=exact(fixed_fraction)
    if not 0<=alpha<=1:raise ValueError('fixed fraction outside unit interval')
    units=vals['demand_units']; purchase=max(F(0),units+vals['target_inventory_units']-engine.balances['inventory']/engine.unit_cost)
    revenue=units*vals['price'];rate=alpha*vals['fixed_rate']+(1-alpha)*vals['floating_rate']
    return {'id':'2025','start':f['start'],'date':f['date'],'decision_at':f['start'],'scenario':'exogenous_stress',
            'years':str(vals['years']),'purchase_units':str(purchase),'delivery_units':str(units),'sales_consideration':str(revenue),
            'collections':str(vals['legacy_collections']+revenue*vals['collection_fraction']),
            'interest_rate':stress_record(rate,f['start']),'tax_rate':stress_record(vals['tax_rate'],f['start']),
            'information_inputs':deepcopy(records),
            **{k:str(vals[k]) for k in ('supplier_payment','payroll','capex','capex_life','dividend')}}


def run_northstar(spec=None):
    spec=deepcopy(spec or json.loads((ROOT/INPUT).read_text())); engine=Engine(spec); periods={}
    for p in spec['periods']:
        periods[p['id']]=execute_period(engine,spec,p)
        if periods[p['id']]['status']!='Complete':return {'periods':periods,'status':'Incomplete'}
    periods['2024FY']={'status':'Complete','opening':spec['opening'],'journals':serial(engine.journals),'statements':statements(spec['opening'],engine.journals)}
    for name,alpha in [('2025_fixed','1'),('2025_floating','0')]:
        branch=engine.fork();periods[name]=execute_period(branch,spec,forecast_period(branch,spec,alpha))
    return {'status':'Complete' if all(p['status']=='Complete' for p in periods.values()) else 'Incomplete',
            'periods':periods,'historical_engine':engine}


def branch_family(engine,spec,atoms,mode='exogenous_stress',likelihood=None):
    from reconstruction_v1 import FiniteMeasure
    if mode not in ('exogenous_stress','conditioning'):return {'status':'Unsupported','mode':mode}
    # Invalid laws cannot define a family. Validate weights, identities and
    # joint coordinates before executing any branch; execution failures below
    # retain their original mass within an otherwise valid law.
    FiniteMeasure(atoms,'Explicit illustrative joint law; not inferred probabilities')
    rows=[]
    for a in atoms:
        branch=engine.fork();h=a['hypothesis']
        if h.get('operation')!='supported':r={'status':'Unsupported','statements':None}
        else:
            try:
                f=spec['forecast']
                drivers={k:stress_record(v,f['start']) for k,v in f.items() if k not in ('start','date')}
                drivers['payroll']=stress_record(h['payroll'],f['start'])
                p=forecast_period(branch,spec,h['fixed_fraction'],drivers)
            except (ValueError,KeyError,TypeError,ZeroDivisionError,OverflowError) as exc:
                r={'status':'Rejected','reason':str(exc),'statements':None,
                   'inputs':[],'events':[],'journals':[],
                   'last_committed_state':branch.snapshot()}
            else:
                r=execute_period(branch,spec,p)
        rows.append({**deepcopy(a),'status':r['status'],'outcome':r['statements']['flat']['cash'] if r['statements'] else None,'execution':r})
    measure=FiniteMeasure(rows,'Explicit illustrative joint law; not inferred probabilities')
    if mode=='conditioning':measure=measure.update(likelihood,['declared-synthetic-observation'])
    return {'status':'Retained','mode':mode,'atoms':serial(measure.atoms),'summary':measure.summary()}


def p03_family(ir, bindings):
    """Structural adapter only: no transfer of Acme dates/evidence to Northstar."""
    from reconstruction_v1 import from_p03
    from rational_solver_v1 import solve, Budget, q
    p=from_p03(ir,bindings,{'DemoDebt@1/DebtMix':'fixed-floating-amounts-v1'})
    if p.unsupported: raise ValueError('unsupported P03 family')
    budget=Budget(10,10000,100,100,10000,1000,1000000)
    joint=solve(p,budget,p.outputs['interest'])
    endpoints=[]
    for fixed in (F(0),F(100)):
        r=solve(p,budget,p.outputs['interest'],extra=(p.outputs['fixed']==q(fixed),p.outputs['principal']==q(100)))
        if not any(c['feasibility']=='sat' for c in r.get('cells',[])): raise ValueError('Northstar endpoint not admitted')
        endpoints.append({'fixed_fraction':str(fixed/100),'fixed':str(fixed),'floating':str(100-fixed),'solver':r})
    return {'provenance':p.provenance,'joint':joint,'endpoints':endpoints,
            'scope':'Explicit structural mapping of principal-100 debt fractions; Acme evidence dates do not establish Northstar facts',
            'probabilities':None,'continuous_interior':'Preserved by the P04 parent family; endpoint executions are not exhaustive histories'}


def apple_conditional(exposure='14575000000'):
    case=json.loads((ROOT/'data/accounting-master/deliverables/P02/case.json').read_text())
    ids=['annual.bs.2024-09-28.cash','annual.debt.2024-09-28.principal','annual.debt.2024-09-28.carrying','annual.notional.2024']
    obs={x['id']:x for x in case['observations'] if x['id'] in ids}
    if set(obs)!=set(ids):raise ValueError('P02 observations missing')
    cash=exact(obs[ids[0]]['value_usd']); exposure=exact(exposure)
    if exposure<0:raise ValueError('negative conditional exposure')
    spec={'context':{'entity':'0000320193','basis':'conditional marginal stress','currency':'USD','unit':'USD','calendar':'13/52 convention'},
          'source':'data/accounting-master/deliverables/P02/case.json','inventory_unit_cost':'1','assets':[],
          'opening':{'cash':str(cash),'capital':str(-cash+exposure),'debt':str(-exposure)}}
    e=Engine(spec); opening=deepcopy(e.balances); results=[];inputs=[]
    for i,op,params in [('accrue','interest_accrue',{'rate':stress_record('0.02','2026-10-03'),'years':'13/52'}),
                        ('pay','interest_pay',{'amount':str(exposure*F(1,50)*F(13,52))}),('close','close',{})]:
        supplied=event(spec,i,op,params,date_='2026-10-03',scenario='exogenous_stress',depends=[results[-1]['id']] if results else ())
        inputs.append(deepcopy(supplied));results.append(e.apply(supplied))
        if results[-1]['status']!='Applied': break
    completed=all(r['status']=='Applied' for r in results) and len(results)==3
    reported=statements(opening,e.journals) if completed else None
    deltas={'cash':reported['flat']['cash_change'],'profit':reported['income']['profit'],
            'equity':str(exact(reported['equity']['closing'])-exact(reported['equity']['opening']))} if completed else None
    return {'status':'ConditionalCalculation' if completed else results[-1]['status'],'assumed_effective_floating_exposure_usd':str(exposure),
            'exposure_is_not_inferred_from_notional':True,'assumptions':['+200 basis points','13/52 year','immediate settlement','no tax','no other changes'],
            'source_observations':list(obs.values()),'source_pins':case['source_pins'],'availability':case['filing_availability'],
            'historical_availability':'Unknown; retrospective calculation only','unresolved_operations':case['unidentified_histories'],
            'opening':serial(opening),'inputs':inputs,'journals':serial(e.journals),'events':results,'statements':reported,
            'closing':e.snapshot() if completed else None,'last_committed_state':e.snapshot(),'delta_usd':deltas,
            'scope':'Marginal journal illustration; opening balancing capital is computational, not reported Apple equity; no full-company statements or forecast accuracy'}
