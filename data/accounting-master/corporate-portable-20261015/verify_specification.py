"""Independent documentary checks. Does not import the authoring builder."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from fractions import Fraction as Q
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import time
import traceback

from jsonschema import Draft202012Validator, FormatChecker

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ACCOUNTS='cash receivables inventory plant_cost accum_depreciation tax_prepaid payables debt capital retained revenue cost_of_sales payroll depreciation interest tax'.split()
TEMP='revenue cost_of_sales payroll depreciation interest tax'.split()

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def number(value):
    assert set(value)=={'n','d'}
    q=Q(int(value['n']),int(value['d']))
    assert value=={'n':str(q.numerator),'d':str(q.denominator)}
    return q

def refs(value):
    if isinstance(value,dict):
        if set(value)=={'kind','schema','digest'}: yield value
        else:
            for item in value.values():yield from refs(item)
    elif isinstance(value,list):
        for item in value:yield from refs(item)

def blobs(value):
    if isinstance(value,dict):
        if value.get('kind')=='blob':yield value
        else:
            for item in value.values():yield from blobs(item)
    elif isinstance(value,list):
        for item in value:yield from blobs(item)

def exact_values(value):
    assert not isinstance(value,float)
    if isinstance(value,dict):
        if set(value)=={'n','d'}:number(value)
        for key,item in value.items():
            assert key.isascii()
            exact_values(item)
    elif isinstance(value,list):
        for item in value:exact_values(item)
    elif isinstance(value,str):value.encode('utf-8')

def delta(lines,affine=False):
    result={k:(Q(0),Q(0)) if affine else Q(0) for k in ACCOUNTS}
    for line in lines:
        v=line['signed_amount'];k=line['account']
        if affine:result[k]=plus(result[k],(number(v['constant']),number(v['coefficient_x'])))
        else:result[k]+=number(v)
    return result

def plus(a,b):return (a[0]+b[0],a[1]+b[1])
def scale(a,k):return (a[0]*k,a[1]*k)
def lin(v):return (Q(v),Q(0))
def read_aff(v):return (number(v['constant']),number(v['coefficient_x']))

class Verification:
    def __init__(self):
        self.bundle=json.loads((OUT/'portable-exchanges.json').read_text())
        self.schemas=json.loads((OUT/'record-schemas.json').read_text())
        self.records=self.bundle['record_registry']
        self.alias=self.bundle['aliases'];self.cases={x['id']:x for x in self.bundle['exchanges']}
        self.checks=[];self.derived={}

    def body(self,r):
        if isinstance(r,str):r=self.alias[r]
        record=self.records[r['digest']]
        assert (record['kind'],record['schema'])==(r['kind'],r['schema'])
        return record['body']

    def check(self,name,ok,detail=None):
        self.checks.append({'name':name,'passed':bool(ok),'detail':detail})

    def closure(self,roots):
        found=set();active=set()
        def visit(r):
            assert r['digest'] not in active,'reference cycle'
            if r['digest'] in found:return
            self.body(r);active.add(r['digest'])
            for child in self.records[r['digest']]['dependencies']:visit(child)
            active.remove(r['digest']);found.add(r['digest'])
        for r in roots:visit(r)
        return found

    def raw(self,blob):
        path=ROOT/self.bundle['blobs'][blob['digest']]['path']
        return path.read_bytes()

    def structural(self):
        for d,r in self.records.items():
            errors=[]
            try:
                assert set(r)=={'kind','schema','key','revision','body','dependencies'}
                assert type(r['revision']) is int and r['revision']>=0
                assert r['schema']==self.schemas['schema_ids'][r['kind']]
                Draft202012Validator(self.schemas['$defs'][r['kind']],format_checker=FormatChecker()).validate(r['body'])
                exact_values(r)
                assert hashlib.sha256(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+canonical(r)).hexdigest()==d
                deps={canonical(x):x for x in refs(r['body'])}
                assert r['dependencies']==[deps[k] for k in sorted(deps)]
                for x in deps.values():self.body(x)
                for b in blobs(r):
                    raw=self.raw(b)
                    assert len(raw)==b['byte_length'] and hashlib.sha256(raw).hexdigest()==b['digest']
            except Exception as exc:errors=[str(exc)[:700]]
            self.check('record:'+r['key'],not errors,errors)
        self.check('acyclic_complete_registry',len(self.closure(list(self.alias.values())))==len(self.records))
        for r in self.alias.values():self.body(r)
        for pin in self.bundle['source_pins']:
            self.check('source_pin:'+pin['path'],hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'])
        baseline=json.loads((OUT.parent/'convergence-audit-20261015/baseline.json').read_text())
        for pin in baseline['source_manifest']:
            self.check('protected:'+pin['path'],hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'])
        index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
        self.check('unrelated_index',(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()==index)

    def sources(self):
        original=json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text())
        native=json.loads((ROOT/'docs/design/fixtures/p05-economic-inputs-v1.json').read_text());facts=self.body('economic-facts')
        assert {k:number(v) for k,v in facts['opening'].items()}=={k:Q(native['opening'].get(k,'0')) for k in ACCOUNTS}
        assert number(self.body('assumptions')['inventory_unit_cost'])==Q(native['inventory_unit_cost'])
        for new,old in zip(facts['periods'],native['periods']):
            assert new['id']==old['id'] and new['start']==old['start']
            for k,v in new.items():
                if k not in ['id','start','end_exclusive']:assert number(v)==Q(old[k])
        assert len(facts['periods'])==len(native['periods'])==2
        for k,v in facts['forecast'].items():
            if k not in ['start','end_exclusive']:assert number(v)==Q(native['forecast'][k])
        package=self.body('source-package');units={self.body(r)['unit_key']:self.body(r) for r in package['unit_refs']}
        assert set(units)=={u['id'] for u in original['coverage_units']}
        assert set(units)=={c['unit_key'] for c in package['coverage']} and package['recursive_closure']
        for u in original['coverage_units']:
            s=units[u['id']];assert s['kind']==u['kind']
            assert json.loads(self.raw(s['source_blob']))['coverage_units'][int(s['locator'].rsplit('/',1)[1])]==u
            assert s['reference_targets']==([u['target']] if 'target' in u else [])
            assert all(t in units for t in s['reference_targets'])
        for name in ['h1.original','h1.corrected','fy.corrected']:
            r=self.body(name);a=self.body(r['admission_ref']);s=self.body(r['source_ref'])
            assert a['source_ref']==r['source_ref'] and a['context_ref']==r['context_ref']
            assert a['value']==r['value'] and a['accepted_at']==s['reviewed_at']
        missing=self.body('package.missing')
        assert not missing['recursive_closure'] and len(missing['unit_refs'])==8 and len(missing['coverage'])==9
        for label,lo,hi,closed in [('all-payers',Q(1),Q(1),True),('nearest-unit',Q('99.5'),Q('100.5'),False)]:
            c=self.body('assumption.'+label);a=self.body('admitted.'+label)
            assert number(c['lower'])==lo and number(c['upper'])==hi and c['upper_included']==closed
            assert c['lower_included'] and not c['source_entails_constraint']
            i=self.body(a['interpretation_ref']);v=self.body(a['view_ref']);dec=self.body(a['decision_ref'])
            assert not i['admitted'] and i['constraint_ref']==a['constraint_ref']
            assert a['interpretation_ref'] in v['conditional_refs'] and a['decision_ref'] in v['decision_refs']
            assert self.body(dec['proposal_ref'])['layer']=='assumption'
        self.check('all_source_units_conditional_assumptions_and_separate_admission',True)

    def time_selection(self,args):
        package=self.body(args['package_ref']);eligible=[];excluded=[];unknown=[]
        for rr in package['reading_refs']:
            r=self.body(rr);c=self.body(r['context_ref']);s=self.body(r['source_ref'])
            reason=None
            if c['period_start']!='2024-01-01' or c['period_end_exclusive']!='2024-07-01':reason='CONTEXT_MISMATCH'
            elif args['selection']=='original' and s['supersedes_refs']:reason='NOT_ORIGINAL_ROOT'
            elif args['admission_mode']=='investor_information':
                if not s['public_date'] or not s['public_bytes_verified']:
                    unknown.append({'reading_ref':rr,'reason':'PUBLICATION_UNVERIFIED'});continue
                start=datetime.fromisoformat(s['public_date']).replace(tzinfo=timezone.utc)
                cutoff=datetime.fromisoformat(args['information_cutoff'].replace('Z','+00:00'))
                if cutoff<start:reason='AFTER_INFORMATION_CUTOFF'
                elif cutoff<start+timedelta(days=1):
                    unknown.append({'reading_ref':rr,'reason':'PUBLICATION_PRECISION_UNRESOLVED'});continue
            elif args['admission_mode']=='system_as_of':
                cutoff=args['system_as_of']
                if not s['ingestion_verified'] or not s['ingested_at']:
                    unknown.append({'reading_ref':rr,'reason':'INGESTION_UNVERIFIED'});continue
                if s['ingested_at']>cutoff or (args['requested_layer']=='accepted' and self.body(r['admission_ref'])['accepted_at']>cutoff):reason='AFTER_SYSTEM_CUTOFF'
            if reason:excluded.append({'reading_ref':rr,'reason':reason})
            else:eligible.append(rr)
        if args['selection']=='latest_available':
            superseded={p['digest'] for rr in eligible for p in self.body(self.body(rr)['source_ref'])['supersedes_refs']}
            keep=[]
            for rr in eligible:
                if self.body(rr)['source_ref']['digest'] in superseded:excluded.append({'reading_ref':rr,'reason':'SUPERSEDED'})
                else:keep.append(rr)
            eligible=keep
        return eligible,excluded,unknown,None if unknown or len(eligible)!=1 else self.body(eligible[0])['value']

    def chronology(self):
        for case in self.cases.values():
            if not case['request_ref']:continue
            request=self.body(case['request_ref'])
            if request['operation']!='time.select@1':continue
            selected,excluded,unknown,value=self.time_selection(request['arguments']['value'])
            output=self.body(self.body(case['response_ref'])['payload']['result_refs'][0])
            self.check(case['id']+':independent_time_selection',output['selected_refs']==selected and sorted(excluded,key=canonical)==sorted(output['excluded'],key=canonical) and output['unresolved']==unknown and output['value']==value)
        assert number(self.body('h1.original')['value'])==120
        assert number(self.body('h1.corrected')['value'])==110
        assert self.body('NS.h1.original')['public_date']=='2024-08-01'
        assert self.body('NS.h1.correction')['public_date']=='2025-03-02'
        assert self.body('NS.h1.correction')['ingested_at'].startswith('2025-03-05')
        self.check('manuscript_chronology_and_original_correction_preserved',True)

    def history(self):
        inputs=json.loads((ROOT/'docs/design/fixtures/p05-economic-inputs-v1.json').read_text())
        old=json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text())
        reconstruction=self.body('historical.reconstruction')
        balance={a:Q(inputs['opening'].get(a,'0')) for a in ACCOUNTS}
        unit_cost=Q(inputs['inventory_unit_cost']);units=balance['inventory']/unit_cost
        assets=[{**a,'cost':Q(a['cost']),'life_years':Q(a['life_years'])} for a in inputs['assets']]
        reports={};step_index=0;sequence=0;previous=reconstruction['opening_ref']
        for period in inputs['periods']:
            p={k:Q(v) if k not in ['id','date','start'] else v for k,v in period.items()}
            ocash=balance['cash'];oequity=-balance['capital']-balance['retained']
            cost=p['delivery_units']*unit_cost;purchase=p['purchase_units']*unit_cost
            dep=sum(a['cost']/a['life_years']*p['years'] for a in assets if a['in_service']<=p['start'])
            interest=Q(inputs['contract']['principal'])*p['interest_rate']*p['years']
            pretax=p['sales_consideration']-cost-p['payroll']-dep-interest
            tax=max(Q(0),pretax)*p['tax_rate'];profit=pretax-tax
            steps=[('purchase',{'inventory':purchase,'payables':-purchase},p['purchase_units']),
                   ('delivery',{'receivables':p['sales_consideration'],'revenue':-p['sales_consideration'],'cost_of_sales':cost,'inventory':-cost},-p['delivery_units']),
                   ('collection',{'cash':p['collections'],'receivables':-p['collections']},0),
                   ('supplier_payment',{'payables':p['supplier_payment'],'cash':-p['supplier_payment']},0),
                   ('payroll',{'payroll':p['payroll'],'cash':-p['payroll']},0),
                   ('plant_addition',{'plant_cost':p['capex'],'cash':-p['capex']},0),
                   ('depreciation',{'depreciation':dep,'accum_depreciation':-dep},0),
                   ('interest',{'interest':interest,'cash':-interest},0),
                   ('tax',{'tax':tax,'tax_prepaid':p['tax_payment']-tax,'cash':-p['tax_payment']},0),
                   ('dividend',{'retained':p['dividend'],'cash':-p['dividend']},0),
                   ('close',{'revenue':p['sales_consideration'],'cost_of_sales':-cost,'payroll':-p['payroll'],'depreciation':-dep,'interest':-interest,'tax':-tax,'retained':-profit},0)]
            flows=defaultdict(Q)
            for kind,expected,units_change in steps:
                step=self.body(reconstruction['step_refs'][step_index]);step_index+=1;sequence+=1
                assert step['opening_ref']==previous and step['event_kind']==kind and step['period']==p['id']
                assert step['date']==p['date'] and self.body(step['template_ref'])['event_kind']==kind
                actual=delta(step['lines']);assert actual=={a:expected.get(a,Q(0)) for a in ACCOUNTS}
                assert sum(actual.values())==0
                for a,v in actual.items():balance[a]+=v
                units+=units_change
                assert balance['cash']>=0 and units>=0 and balance['inventory']==units*unit_cost
                assert balance['receivables']>=0 and balance['payables']<=0 and balance['tax_prepaid']>=0
                assert sum(balance.values())==0
                closing=self.body(step['closing_ref']);previous=step['closing_ref']
                assert {a:number(v) for a,v in closing['balances'].items()}==balance
                assert closing['sequence']==sequence and number(closing['inventory_units'])==units
                if step['cash_class']:flows[step['cash_class']]+=actual['cash']
                self.check(p['id']+':'+kind+':economic_journal_state',True)
            plant=balance['plant_cost']+balance['accum_depreciation']
            assets_total=balance['cash']+balance['receivables']+balance['inventory']+plant+balance['tax_prepaid']
            equity=-balance['capital']-balance['retained']
            report={k:balance[k] for k in ['cash','receivables','inventory','tax_prepaid']}
            report.update(plant_net=plant,assets=assets_total,payables=-balance['payables'],debt=-balance['debt'],capital=-balance['capital'],retained=-balance['retained'],equity=equity,revenue=p['sales_consideration'],cost_of_sales=cost,payroll=p['payroll'],depreciation=dep,interest=interest,profit_before_tax=pretax,tax=tax,profit=profit,oci=Q(0),comprehensive_income=profit,operating_cash=flows['operating'],investing_cash=flows['investing'],financing_cash=flows['financing'],cash_change=balance['cash']-ocash,opening_cash=ocash,opening_equity=oequity,dividends=p['dividend'],plant_additions=p['capex'])
            assert assets_total==equity-balance['payables']-balance['debt']
            assert equity==oequity+profit-p['dividend']
            assert report['cash_change']==sum(flows.values())
            reports[p['id']]=report
            assets.append({'cost':p['capex'],'life_years':p['capex_life'],'in_service':'2024-07-01' if p['id']=='2024H1' else '2025-01-01'})
        annual=deepcopy(reports['2024H2'])
        for k in 'revenue cost_of_sales payroll depreciation interest profit_before_tax tax profit oci comprehensive_income operating_cash investing_cash financing_cash cash_change dividends plant_additions'.split():annual[k]=reports['2024H1'][k]+reports['2024H2'][k]
        annual['opening_cash']=reports['2024H1']['opening_cash'];annual['opening_equity']=reports['2024H1']['opening_equity'];reports['2024FY']=annual
        assert len(reconstruction['step_refs'])==step_index and reconstruction['closing_ref']==previous
        for row in reconstruction['period_reports']:
            assert {k:number(v) for k,v in row['lines'].items()}==reports[row['period']]
            for k,v in old['expected'][row['period']].items():assert reports[row['period']][k]==Q(v)
        self.balance=balance;self.assets=assets;self.units=units;self.history_reports=reports
        self.derived['historical_reports']={p:{k:str(v) for k,v in row.items()} for p,row in reports.items()}
        self.check('historical_statements_independent_and_preserved_expectations',True)

    def projection(self,pr):
        p=self.body(pr);s=self.body(p['scenario_ref']);d=s['driver_values']
        q=lambda k:number(d[k]);missing=d['collection_fraction'].get('tag')=='unknown';tax_supported=s['tax_method_supported']
        native=json.loads((ROOT/'docs/design/fixtures/p05-economic-inputs-v1.json').read_text())['forecast']
        for k,v in d.items():
            if k!='floating_rate' and not (k=='collection_fraction' and missing):assert number(v)==Q(native[k])
        label=self.records[pr['digest']]['key']
        assert q('floating_rate')==Q('9/100' if label=='projection.stress9' else '7/100')
        opening=self.body(p['opening_ref']);assert opening['balances']==self.body(self.body('historical.reconstruction')['closing_ref'])['balances']
        b={a:lin(v) for a,v in self.balance.items()}
        unit_cost=number(self.body(p['assumptions_ref'])['inventory_unit_cost'])
        sales=q('demand_units')*q('price');cogs=q('demand_units')*unit_cost
        purchased=(q('demand_units')+q('target_inventory_units')-self.units)*unit_cost
        collections=None if missing else sales*q('collection_fraction')+q('legacy_collections')
        depreciation=sum(a['cost']/a['life_years']*q('years') for a in self.assets)
        debt=-self.balance['debt'];interest=(debt*q('fixed_rate')*q('years'),debt*(q('floating_rate')-q('fixed_rate'))*q('years'))
        pretax=plus(lin(sales-cogs-q('payroll')-depreciation),scale(interest,-1))
        assert min(pretax[0],sum(pretax))>0
        tax=scale(pretax,q('tax_rate'));profit=plus(pretax,scale(tax,-1))
        rows=[('purchase',{'inventory':lin(purchased),'payables':lin(-purchased)}),
              ('delivery',{'receivables':lin(sales),'revenue':lin(-sales),'cost_of_sales':lin(cogs),'inventory':lin(-cogs)})]
        if collections is not None:rows.append(('collection',{'cash':lin(collections),'receivables':lin(-collections)}))
        rows.extend([('supplier_payment',{'payables':lin(q('supplier_payment')),'cash':lin(-q('supplier_payment'))}),
                     ('payroll',{'payroll':lin(q('payroll')),'cash':lin(-q('payroll'))}),
                     ('plant_addition',{'plant_cost':lin(q('capex')),'cash':lin(-q('capex'))}),
                     ('depreciation',{'depreciation':lin(depreciation),'accum_depreciation':lin(-depreciation)}),
                     ('interest',{'interest':interest,'cash':scale(interest,-1)})])
        if tax_supported:rows.append(('tax',{'tax':tax,'cash':scale(tax,-1)}))
        rows.append(('dividend',{'retained':lin(q('dividend')),'cash':lin(-q('dividend'))}))
        if tax_supported:rows.append(('close',{'revenue':lin(sales),'cost_of_sales':lin(-cogs),'payroll':lin(-q('payroll')),'depreciation':lin(-depreciation),'interest':scale(interest,-1),'tax':scale(tax,-1),'retained':scale(profit,-1)}))
        assert len(rows)==len(p['proposed_journals'])
        for (kind,expected),journal in zip(rows,p['proposed_journals']):
            assert journal['event_kind']==kind and self.body(journal['template_ref'])['event_kind']==kind
            assert not journal['posting_permission']
            movement=delta(journal['lines'],True)
            assert movement=={a:expected.get(a,lin(0)) for a in ACCOUNTS}
            assert sum(v[0] for v in movement.values())==sum(v[1] for v in movement.values())==0
            for a in b:b[a]=plus(b[a],movement[a])
            if not missing and tax_supported:assert min(b['cash'][0],sum(b['cash']))>=0
        # Independently derived report from drivers; no expected field is an input.
        cfo=plus(lin((collections or 0)-q('supplier_payment')-q('payroll')),scale(plus(interest,tax),-1))
        change=plus(cfo,lin(-q('capex')-q('dividend')));cash=plus(lin(self.balance['cash']),change)
        ar=lin(self.balance['receivables']+sales-(collections or 0));inventory=lin(q('target_inventory_units')*unit_cost)
        plant=lin(self.balance['plant_cost']+self.balance['accum_depreciation']+q('capex')-depreciation)
        retained=plus(lin(-self.balance['retained']-q('dividend')),profit)
        equity=plus(lin(-self.balance['capital']),retained);assets=plus(plus(cash,ar),plus(inventory,plant))
        expected={'cash':cash,'receivables':ar,'inventory':inventory,'plant_net':plant,'tax_prepaid':lin(0),'assets':assets,'payables':lin(-self.balance['payables']+purchased-q('supplier_payment')),'debt':lin(debt),'capital':lin(-self.balance['capital']),'retained':retained,'equity':equity,'revenue':lin(sales),'cost_of_sales':lin(cogs),'payroll':lin(q('payroll')),'depreciation':lin(depreciation),'interest':interest,'profit_before_tax':pretax,'tax':tax,'profit':profit,'oci':lin(0),'comprehensive_income':profit,'operating_cash':cfo,'investing_cash':lin(-q('capex')),'financing_cash':lin(-q('dividend')),'cash_change':change,'opening_cash':lin(self.balance['cash']),'opening_equity':lin(-self.balance['capital']-self.balance['retained']),'dividends':lin(q('dividend')),'plant_additions':lin(q('capex'))}
        affected=set()
        if missing:affected.update('cash receivables assets operating_cash cash_change'.split())
        if not tax_supported:affected.update('tax profit comprehensive_income retained equity cash assets operating_cash cash_change tax_prepaid'.split())
        assert set(expected)==set(p['lines'])
        for k,value in expected.items():
            got=p['lines'][k]
            if k in affected:assert got.get('tag')=='unknown' and got['obligation_refs'] and set(r['digest'] for r in got['obligation_refs'])<=set(r['digest'] for r in p['obligation_refs'])
            else:assert read_aff(got)==value,(k,got,value)
        unknown_balances=set()
        if missing:unknown_balances.update(['cash','receivables'])
        if not tax_supported:unknown_balances.update(['cash','tax_prepaid','retained']+TEMP)
        for k,v in p['closing_balances'].items():
            if k in unknown_balances:assert v.get('tag')=='unknown'
            else:assert read_aff(v)==b[k],(k,v,b[k])
        if not affected:
            assert assets==plus(equity,plus(expected['payables'],expected['debt']))
            assert b['cash']==cash and scale(b['retained'],-1)==retained
            assert all(b[k]==lin(0) for k in TEMP)
            self.derived[self.records[pr['digest']]['key']]={k:[str(v) for v in a] for k,a in expected.items()}
        return expected,affected

    def finances(self):
        for key in ['projection.stress7','projection.stress9','projection.missing-collection','projection.unsupported-tax']:
            self.projection(self.alias[key]);self.check(key+':independent_affine_journal_statement_derivation',True)
        old=json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text())
        values,_=self.projection(self.alias['projection.stress7'])
        for x,name in [(0,'2025_fixed'),(1,'2025_floating')]:
            for k,v in old['expected'][name].items():assert values[k][0]+x*values[k][1]==Q(v)
        # Working-capital bridges use the reporting identities independently.
        fy=self.history_reports['2024FY'];op=json.loads((ROOT/'docs/design/fixtures/p05-economic-inputs-v1.json').read_text())['opening']
        derived=[fy['revenue']+Q(op['receivables'])-fy['receivables'],fy['cost_of_sales']+fy['inventory']-Q(op['inventory'])]
        derived.append(derived[1]-Q(op['payables'])-fy['payables'])
        actual=self.body('bridges.answer')['values'];assert [number(v['value']) for v in actual]==derived
        self.check('preserved_endpoint_expectations_and_working_capital_bridges',True)

    def compile_inputs(self):
        text=self.raw(self.body('compile-text.output')['authored_blob']).decode('ascii')
        w=r'[ \t\r\n]*';q=r'((?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?)'
        parts=['NorthstarDebt',r'\{','principal','=',q,';', 'x',':','Rational',r'in',r'\[',q,',',q,r'\]',';','fixed_rate','=',q,';','floating_rate','=',q,';','interest','=',q,r'\*',r'\(',r'\(','1','-','x',r'\)',r'\*','fixed_rate',r'\+','x',r'\*','floating_rate',r'\)',';',r'\}']
        match=re.fullmatch(w+w.join(parts)+w,text)
        assert match,'bounded text grammar'
        principal,lo,hi,fixed,floating,multiplier=map(Q,match.groups())
        mod=self.body('module.debt');formula=self.body(mod['derived_expression_refs'][0]);symbol=self.body(mod['symbol_refs'][0])
        assert principal==multiplier==number(formula['principal'])
        assert (lo,hi)==(number(symbol['lower']),number(symbol['upper']))
        assert fixed==number(formula['fixed_rate']) and floating==number(formula['floating_rate'])
        assert read_aff(formula['result'])==(principal*fixed,principal*(floating-fixed))
        assert formula['fraction_symbol_ref']==mod['symbol_refs'][0] and number(formula['year_fraction'])==1
        for key in ['compile-typed-debt','compile-corporate']:
            r=self.body(self.cases[key]['request_ref']);args=r['arguments']['value']
            assert self.raw(args['source_blob'])==canonical(self.records[args['module_ref']['digest']])
        assert self.body('compile-text.output')['module_ref']==self.body('compile-typed-debt.output')['module_ref']
        self.check('bounded_text_and_typed_debt_semantics_independently_decoded',True)

    def validate_input(self,case):
        def unique(pairs):
            d={}
            for k,v in pairs:
                if k in d:raise ValueError('duplicate key')
                d[k]=v
            return d
        raw=self.raw(self.body(case['submission_ref'])['blob_ref'])
        try:wire=json.loads(raw,object_pairs_hook=unique)
        except (ValueError,UnicodeDecodeError):return 'JSON_DECODE_FAILED',None
        try:
            assert set(wire)=={'kind','schema','key','revision','body','dependencies'}
            assert wire['kind']=='OperationRequest' and wire['schema']=='accdsl.operation.request.v1'
            Draft202012Validator(self.schemas['$defs']['OperationRequest'],format_checker=FormatChecker()).validate(wire['body'])
        except Exception:return 'UNKNOWN_FIELD',None
        try:
            exact_values(wire);deps={canonical(r):r for r in refs(wire['body'])}
            assert wire['dependencies']==[deps[k] for k in sorted(deps)]
            self.closure(wire['dependencies'])
        except (AssertionError,KeyError):return 'REQUIRED_REFERENCE_MISSING',None
        for changed in case.get('supplied_blob_overrides',[]):
            supplied=self.raw(changed['received_blob']);expected=changed['expected_blob']
            if len(supplied)!=expected['byte_length'] or hashlib.sha256(supplied).hexdigest()!=expected['digest']:
                return 'REQUIRED_BLOB_DIGEST_MISMATCH',None
        r=wire['body'];op=r['operation'];a=r['arguments']['value']
        if r['arguments']['tag']!=op or self.body(r['signature_ref'])['operation']!=op:return 'ARGUMENT_SIGNATURE_MISMATCH',None
        if op=='accounting.commit@1':
            basis=self.body(a['basis_ref']);auth=self.body(a['authorization_ref']);j=self.body(a['journal_ref']);d=self.body(a['delta_ref'])
            event=self.body(basis['event_ref']);opening=self.body(basis['opening_ref']);assumptions=self.body(basis['assumptions_ref'])
            try:
                assert auth['basis_ref']==a['basis_ref'] and auth['posting_permitted'] and auth['status']=='eligible'
                assert j['basis_ref']==d['basis_ref']==a['basis_ref'] and j['authorization_ref']==d['authorization_ref']==a['authorization_ref']
                assert auth['method_ref']==basis['method_ref'] and auth['posting_profile_ref']==r['profile_ref']
                assert auth['authority_refs']==basis['authority_refs'] and auth['view_ref']==basis['view_ref']==r['view_ref']
                assert event['context_ref']==basis['context_ref']==opening['context_ref']
                assert self.body(basis['branch_ref'])['book_mode']=='synthetic'
                assert self.body(basis['time_ref'])['economic_date']==event['date']
                assert basis['identity']['business_event_id']==event['business_event_id']
                assert r['expected_head']['state_ref']==basis['opening_ref']
                amount=number(event['parameters']['amount']);units=number(event['parameters']['units']);cost=number(assumptions['inventory_unit_cost'])
                assert amount==units*cost and units>=0 and event['event_kind']=='purchase'
                expected={k:Q(0) for k in ACCOUNTS};expected['inventory']=amount;expected['payables']=-amount
                assert delta(j['lines'])==expected=={k:number(v) for k,v in d['account_changes'].items()}
                assert number(d['inventory_units_before'])==number(opening['inventory_units'])
                assert number(d['inventory_units_after'])==number(opening['inventory_units'])+units
                assert event['sequence']==opening['sequence']+1
            except AssertionError:return 'ECONOMIC_DELTA_MISMATCH',None
        elif op=='review.commit@1':
            proposal=self.body(a['proposal_ref']);target=self.body(proposal['target_ref'])
            if target.get('proposed_meaning')=='invented_90_percent' and proposal['layer']!='assumption':return 'UNSUPPORTED_NUMERIC_INTERPRETATION',None
        elif op=='history.query@1' and a['query']=='period_difference':
            annual=self.body(a['annual_ref']);interim=self.body(a['interim_ref']);ca=self.body(annual['context_ref']);ci=self.body(interim['context_ref'])
            sa=self.body(annual['source_ref']);si=self.body(interim['source_ref'])
            if sa['revision_group']!=si['revision_group'] or any(ca[k]!=ci[k] for k in ['entity','book','perimeter','currency','unit','basis','period_start']):return 'REVISION_CONTEXT_MISMATCH',None
        elif op=='scenario.project@1':
            scenario=self.body(a['scenario_ref']);family=self.body(a['family_ref'])
            assert scenario['family_ref']==a['family_ref'] and family['view_ref']==a['view_ref']==r['view_ref']
            if scenario['information_mode']=='investor_information':
                sources=self.body(self.body(family['module_ref'])['view_ref'])['source_refs']
                if any(self.body(s)['public_date']+'T23:59:59Z'>scenario['information_cutoff'] for s in sources):return 'AFTER_INFORMATION_CUTOFF',None
            if scenario['driver_origin']=='future_realization' and scenario['realized_at']>scenario['decision_at'] and not scenario['future_realizations_permitted']:return 'FUTURE_REALIZATION_FORBIDDEN',None
        elif op=='report.build@1':
            projection=self.body(a['projection_ref']);mapping=self.body(a['statement_map_ref']);context=self.body(projection['context_ref'])
            if mapping['population_policy']!='partition':return 'OVERLAPPING_AGGREGATION',None
            if (a['interval_start'],a['interval_end_exclusive'])!=(context['period_start'],context['period_end_exclusive']):return 'REPORT_PERIOD_MISMATCH',None
            if mapping['context_ref']!=projection['context_ref']:return 'REPORT_CONTEXT_MISMATCH',None
            if a['require_current'] and (a['view_ref']!=projection['view_ref'] or r['view_ref']!=case['world_before']['review_head']['state_ref']):return 'DEPENDENCY_VIEW_SUPERSEDED',None
            family=self.body(projection['family_ref']);scenario=self.body(projection['scenario_ref'])
            assert scenario['family_ref']==projection['family_ref'] and family['view_ref']==projection['view_ref']
        elif op=='record.explain@1':
            output=self.body(a['output_ref'])
            if output.get('view_ref')!=a['frozen_view_ref']:return 'FROZEN_VIEW_MISMATCH',None
        elif op=='work.resume@1':
            checkpoint=self.body(a['checkpoint_ref'])
            if checkpoint['semantic_manifest_ref']!=a['semantic_manifest_ref']:return 'SEMANTIC_MANIFEST_CHANGED',None
            assert self.body(r['expected_head']['state_ref'])['checkpoint_ref']==a['checkpoint_ref']
        if case['request_ref']:
            assert raw==canonical(self.records[case['request_ref']['digest']])
        return None,r

    def world(self,world):
        published=set(world['published_records']);assert len(published)==len(world['published_records'])
        for d in published:
            assert d in self.records
            assert all(r['digest'] in published for r in self.records[d]['dependencies'])
        for name in ['head','review_head','import_head','work_head','model_head']:
            assert world[name]['state_ref']['digest'] in published
        size=len(world['receipts']);assert len(world['journals'])==len(world['deltas'])==len(world['events'])==size
        assert len({canonical(e['identity']) for e in world['events']})==size
        previous=self.alias['opening-2024']
        for i,(r,event) in enumerate(zip(world['receipts'],world['events'])):
            receipt=self.body(r);assert r['digest'] in published
            assert event=={'identity':receipt['identity'],'request_ref':receipt['request_ref'],'receipt_ref':r}
            assert receipt['opening_ref']==previous and receipt['generation']==i+1
            assert receipt['journal_ref']==world['journals'][i] and receipt['delta_ref']==world['deltas'][i]
            opening=self.body(previous);closing=self.body(receipt['closing_ref'])
            movement=delta(self.body(receipt['journal_ref'])['lines'])
            assert {k:number(v) for k,v in closing['balances'].items()}=={k:number(v)+movement[k] for k,v in opening['balances'].items()}
            assert sum(number(v) for v in closing['balances'].values())==0
            assert number(closing['inventory_units'])==number(self.body(receipt['delta_ref'])['inventory_units_after'])
            assert closing['sequence']==opening['sequence']+1
            previous=receipt['closing_ref']
        assert world['head']['state_ref']==previous and world['head']['generation']==size
        for r in world['review_receipts']+world['import_receipts']+world['work_receipts']:assert r['digest'] in published
        if world['work_receipts']:
            last=self.body(world['work_receipts'][-1]);assert last['closing_ref']==world['work_head']['state_ref'] and last['generation']==world['work_head']['generation']
        if world['import_receipts']:
            last=self.body(world['import_receipts'][-1]);assert last['closing_ref']==world['import_head']['state_ref']
        if world['review_receipts']:
            last=self.body(world['review_receipts'][-1]);assert last['new_view_ref']==world['review_head']['state_ref']

    def transactions(self):
        for case in self.cases.values():
            label=case['id'];before=case['world_before'];after=case['world_after']
            self.world(before);self.world(after)
            code,request=self.validate_input(case);response=self.body(case['response_ref'])
            assert response['submission_ref']==case['submission_ref']
            expected=deepcopy(before)
            if code:
                assert response['request_ref'] is None and response['payload'] is None and response['coverage'] is None
                assert response['operation'] is None and response['input_view_ref'] is None
                assert response['statuses']['structural_validity']=='invalid' and response['disposition']=='rejected'
                assert response['diagnostics'][0]['code']==code,(label,code,response['diagnostics'])
                assert response['commit_observation']=='not_committed'
            else:
                assert response['request_ref']==case['request_ref'] and response['statuses']['structural_validity']=='valid'
                assert response['operation']==request['operation'] and response['input_view_ref']==request['view_ref']
                assert response['payload']['tag']==request['operation']
                allowed=self.body(request['signature_ref'])['payload_kinds']
                assert all(r['kind'] in allowed for r in response['payload']['result_refs'])
                op=request['operation'];args=request['arguments']['value'];expected_code=None;expected_disposition=None
                if op=='accounting.commit@1':
                    identity=self.body(args['basis_ref'])['identity']
                    found=next((e for e in before['events'] if e['identity']==identity),None)
                    if found:
                        if found['request_ref']==case['request_ref']:
                            expected_disposition='replayed';assert response['receipt_ref']==found['receipt_ref']
                        else:expected_code='EVENT_ID_CONFLICT'
                    elif request['expected_head']!=before['head']:expected_code='STALE_OPENING_STATE'
                    else:
                        r=response['receipt_ref'];receipt=self.body(r)
                        assert receipt['request_ref']==case['request_ref'] and receipt['identity']==identity
                        assert all(receipt[k]==args[k] for k in args)
                        expected.update(head={**before['head'],'state_ref':receipt['closing_ref'],'generation':before['head']['generation']+1},events=before['events']+[{'identity':identity,'request_ref':case['request_ref'],'receipt_ref':r}],journals=before['journals']+[args['journal_ref']],deltas=before['deltas']+[args['delta_ref']],receipts=before['receipts']+[r])
                elif op=='review.commit@1':
                    assert request['expected_head']==before['review_head']
                    r=response['receipt_ref'];receipt=self.body(r);decision=self.body(receipt['decision_ref'])
                    assert decision['proposal_ref']==args['proposal_ref'] and receipt['request_ref']==case['request_ref']
                    assert decision['prior_view_ref']==receipt['old_view_ref']==before['review_head']['state_ref']
                    assert self.body(receipt['new_view_ref'])['parent_ref']==receipt['old_view_ref']
                    assert receipt['generation']==before['review_head']['generation']+1
                    expected.update(review_head={**before['review_head'],'state_ref':receipt['new_view_ref'],'generation':receipt['generation']},review_receipts=before['review_receipts']+[r])
                elif op=='store.import@1':
                    assert request['expected_head']==before['import_head']
                    manifest=self.body(args['manifest_ref']);r=response['receipt_ref'];receipt=self.body(r)
                    required=self.closure(manifest['root_refs'])
                    assert {x['digest'] for x in manifest['record_refs']}==required and manifest['complete']
                    required_blobs={canonical(b) for d in required for b in blobs(self.records[d])}
                    assert required_blobs=={canonical(b) for b in manifest['required_blobs']}
                    assert receipt['request_ref']==case['request_ref'] and receipt['manifest_ref']==args['manifest_ref']
                    assert receipt['original_to_local']==[{'original_ref':r,'local_ref':r} for r in manifest['record_refs']]
                    assert not receipt['financial_admission']
                    expected.update(import_head={**before['import_head'],'state_ref':receipt['closing_ref'],'generation':before['import_head']['generation']+1},import_receipts=before['import_receipts']+[r],import_records=manifest['record_refs'])
                elif op in ['work.resume@1','history.construct@1'] and request['expected_head']:
                    assert request['expected_head']==before['work_head']
                    r=response['receipt_ref'];receipt=self.body(r);checkpoint=self.body(receipt['checkpoint_ref'])
                    assert receipt['request_ref']==case['request_ref'] and receipt['opening_ref']==before['work_head']['state_ref']
                    assert receipt['generation']==before['work_head']['generation']+1
                    if op=='work.resume@1':
                        prev=self.body(args['checkpoint_ref']);assert checkpoint['partition_refs']==prev['partition_refs']
                        assert checkpoint['family_ref']==prev['family_ref'] and checkpoint['semantic_manifest_ref']==prev['semantic_manifest_ref']
                        assert checkpoint['next_index']==prev['next_index']+args['additional_cells']
                    else:assert checkpoint['next_index']==args['cell_budget']
                    expected.update(work_head={**before['work_head'],'state_ref':receipt['closing_ref'],'generation':receipt['generation']},work_receipts=before['work_receipts']+[r])
                elif op=='store.migrate@1':
                    parent=self.body(args['original_ref']);child=self.body(args['candidate_ref']);sym=self.body(parent['symbol_ref'])
                    assert child['parent_ref']==args['original_ref']
                    assert (number(child['lower']),number(child['upper']))!=(number(sym['lower']),number(sym['upper']))
                    assert not self.body(response['payload']['result_refs'][0])['accepted']
                    expected_code='MIGRATION_CHANGES_FINANCIAL_DOMAIN';expected_disposition='unsupported'
                if expected_code:
                    assert response['diagnostics'][0]['code']==expected_code,(label,expected_code)
                    assert response['disposition']==(expected_disposition or 'rejected') and response['receipt_ref'] is None
                elif expected_disposition:assert response['disposition']==expected_disposition
                mutates=expected!=before
                if mutates:
                    assert response['commit_observation']=='committed' and response['payload']['additional_commit']
                    roots=response['payload']['result_refs']
                    expected['published_records']=sorted(set(before['published_records'])|self.closure(roots))
                else:assert response['commit_observation']=='not_committed' and not response['payload']['additional_commit']
                self.coverage(response)
            assert after==expected,label+':world domains differ'
            if 'prior_transport_observation_ref' in case:
                observation=self.body(case['prior_transport_observation_ref'])
                assert observation['request_ref']==case['request_ref'] and observation['receipt_ref'] is None
                assert observation['commit_observation']=='unknown' and case['received_response_before_retry'] is None
            self.check(label+':input_decision_and_exact_world_effect',True)

    def coverage(self,response):
        c=response['coverage'];assert c and c['relation']=='disjoint_exhaustive'
        domain=self.body(c['domain_ref']);regions=[]
        for group in ['completed','unresolved','unsupported','infeasible','cancelled']:
            for r in c[group]:
                b=self.body(r);assert b['domain_ref']==c['domain_ref'];regions.append(b)
        if domain['meaning']=='singleton_request_decision':assert len(regions)==1 and regions[0]['predicate']=='this_request'
        else:
            assert domain['family_ref']==self.alias['family.corporate']
            ordered=sorted(regions,key=lambda r:number(r['lower']))
            assert number(ordered[0]['lower'])==0 and ordered[0]['lower_included']
            assert number(ordered[-1]['upper'])==1 and ordered[-1]['upper_included']
            for a,b in zip(ordered,ordered[1:]):
                assert number(a['upper'])==number(b['lower'])
                assert a['upper_included']!=b['lower_included']

    def payloads(self):
        for case in self.cases.values():
            response=self.body(case['response_ref'])
            if response['request_ref'] is None:continue
            request=self.body(response['request_ref']);a=request['arguments']['value'];op=request['operation']
            for r in response['payload']['result_refs']:
                b=self.body(r)
                if r['kind']=='Report':
                    projection=self.body(b['projection_ref'])
                    assert b['projection_ref']==a['projection_ref'] and b['map_ref']==a['statement_map_ref']
                    assert b['lines']==projection['lines'] and b['obligation_refs']==projection['obligation_refs']
                    assert response['disposition']==('partial' if b['obligation_refs'] else 'completed')
                elif r['kind']=='Projection':
                    assert response['disposition']==('partial' if b['obligation_refs'] else 'completed')
                    assert response['unresolved']==b['obligation_refs']
                elif r['kind']=='HistoryAnswer':
                    assert b['family_ref']==a['family_ref'] and b['query']==a['query'] and b['measure_ref'] is None
                    if b['query']=='interest_bounds':
                        f=self.body('economic-facts');principal=number(f['contract']['principal']);fixed=number(f['contract']['fixed_rate']);floating=number(a['scenario_rate'])
                        assert number(b['lower'])==min(principal*fixed,principal*floating) and number(b['upper'])==max(principal*fixed,principal*floating)
                        assert b['lower_attained'] and b['upper_attained']
                    if b['query'] in ['require_probability','nonlinear_bounds','approximate_bounds']:assert b['guarantee']=='unsupported' and response['disposition']=='unsupported'
                elif r['kind']=='PeriodDifference':assert number(b['amount'])==number(self.body(a['annual_ref'])['value'])-number(self.body(a['interim_ref'])['value'])
                elif r['kind']=='Preparation':
                    package=self.body(a['package_ref']);assert b['package_ref']==a['package_ref'] and b['obligation_refs']==package['obligation_refs'] and not b['semantic_admission']
                    assert response['disposition']==('partial' if b['obligation_refs'] else 'completed')
                elif r['kind']=='TimeSelection':assert response['disposition']==('partial' if b['unresolved'] else 'completed')
                elif r['kind']=='Checkpoint':
                    assert b['completed_refs']==b['partition_refs'][:b['next_index']] and b['unresolved_refs']==b['partition_refs'][b['next_index']:]
                    assert b['used_operation_count']==b['next_index']
                elif r['kind']=='Explanation':
                    assert b['output_ref']==a['output_ref'] and b['frozen_view_ref']==a['frozen_view_ref']
                    assert b['dependency_refs']==self.records[a['output_ref']['digest']]['dependencies']
        receipt=self.body('review.receipt')
        invalid=receipt['invalidated_refs'];assert self.alias['h1.original'] in invalid
        for key in ['original.selection','original.profit','original.equity']:
            assert self.alias[key] in invalid
            assert self.alias['h1.original']['digest'] in self.closure([self.alias[key]])
        assert self.alias['original.equity']['digest'] in self.closure([self.alias['late.original-equity']])
        assert self.body('view.membership-changed')['candidate_membership_revision']>self.body('view.corrected')['candidate_membership_revision']
        assert self.body('view.membership-changed')['reading_refs']!=self.body('view.corrected')['reading_refs']
        family=self.body('family.corporate');module=self.body(family['module_ref']);symbol=self.body(family['symbol_ref'])
        assert family['measure_ref'] is None and family['reconstruction_ref']==self.alias['historical.reconstruction']
        assert (number(symbol['lower']),number(symbol['upper']))==(0,1) and symbol['lower_included'] and symbol['upper_included']
        assert [self.body(r)['event_kind'] for r in module['template_refs']]==['purchase','delivery','collection','supplier_payment','payroll','plant_addition','depreciation','interest','tax','dividend','close']
        for r in family['constraint_refs']:
            c=self.body(r);a,b=read_aff(c['expression']);rhs=number(c['rhs'])
            if c['relation']=='eq':assert a==rhs and b==0
            elif c['relation']=='ge':assert min(a,a+b)>=rhs
            elif c['relation']=='le':assert max(a,a+b)<=rhs
        self.check('typed_payloads_reports_partition_and_transitive_invalidation',True)

    def mutations(self):
        # Adversarial mutations challenge the verifier, not the authoring functions.
        probes=[]
        d=self.alias['projection.stress9']['digest'];saved=deepcopy(self.records[d]['body'])
        self.records[d]['body']['lines']['cash']['coefficient_x']={'n':'-8','d':'5'}
        try:self.projection(self.alias['projection.stress9']);probes.append(False)
        except AssertionError:probes.append(True)
        finally:self.records[d]['body']=saved
        d=self.alias['delta.purchase']['digest'];saved=deepcopy(self.records[d]['body'])
        self.records[d]['body']['inventory_units_after']={'n':'21','d':'1'}
        try:probes.append(self.validate_input(self.cases['commit-purchase'])[0]=='ECONOMIC_DELTA_MISMATCH')
        finally:self.records[d]['body']=saved
        bad=deepcopy(self.cases['replay-after-head-advance']['world_before']);bad['receipts'].pop()
        try:self.world(bad);probes.append(False)
        except AssertionError:probes.append(True)
        d=self.alias['NS.h1.correction']['digest'];saved=deepcopy(self.records[d]['body'])
        self.records[d]['body']['public_date']='2025-03-04'
        try:
            args=self.body(self.cases['investor-corrected-archive']['request_ref'])['arguments']['value']
            probes.append(self.time_selection(args)[3]==self.body('h1.original')['value'])
        finally:self.records[d]['body']=saved
        d=self.alias['projection.unsupported-tax']['digest'];saved=deepcopy(self.records[d]['body'])
        self.records[d]['body']['closing_balances']['tax']={'constant':{'n':'0','d':'1'},'coefficient_x':{'n':'0','d':'1'}}
        try:self.projection(self.alias['projection.unsupported-tax']);probes.append(False)
        except AssertionError:probes.append(True)
        finally:self.records[d]['body']=saved
        self.check('adverse_mutations_wrong_rate_quantity_world_time_and_unknown',len(probes)==5 and all(probes),probes)

    def run(self):
        for name in ['structural','sources','chronology','history','finances','compile_inputs','transactions','payloads','mutations']:
            try:getattr(self,name)()
            except Exception:
                self.check('section:'+name,False,traceback.format_exc(limit=4))
        return all(c['passed'] for c in self.checks)

def main():
    started=datetime.now(timezone.utc).isoformat();timer=time.perf_counter()
    verifier=Verification();passed=verifier.run();elapsed=time.perf_counter()-timer
    result={'passed':passed,'check_count':len(verifier.checks),'checks':verifier.checks,'derived':verifier.derived,'evidence_mode':'specification_example','runtime_executed':False}
    (OUT/'independent-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'commands':['python3 -m py_compile data/accounting-master/corporate-portable-20261015/build_specification.py','python3 data/accounting-master/corporate-portable-20261015/build_specification.py','python3 data/accounting-master/corporate-portable-20261015/verify_specification.py'],'environment':'system Python; fractions/hashlib/jsonschema '+importlib.metadata.version('jsonschema'),'cpu_gpu':'CPU exact arithmetic; no ML framework or GPU initialization','data_version':'preserved Northstar/P05 sources pinned by SHA256','random_seeds':'N/A: deterministic rational examples','started_utc':started,'wall_seconds_verification':elapsed,'plan_file':'docs/plans/accounting-corporate-portable-20261015.md','result_file':'data/accounting-master/corporate-portable-20261015/result.md','artifacts':[{ 'path':str((OUT/n).relative_to(ROOT)),'sha256':hashlib.sha256((OUT/n).read_bytes()).hexdigest()} for n in ['build_specification.py','verify_specification.py','record-schemas.json','portable-exchanges.json','independent-checks.json']]}
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    failures=[c for c in verifier.checks if not c['passed']]
    print(json.dumps({'passed':passed,'checks':len(verifier.checks),'records':len(verifier.records),'exchanges':len(verifier.cases),'failures':failures[:8]},ensure_ascii=False))
    if not passed:raise SystemExit(1)

if __name__=='__main__':main()
