"""Read-only exact-rational reference for a finite documented matching history."""
from datetime import date
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
FINDINGS = {
    'external_eligible_instruments', 'eligible_individual_items',
    'managed_together_proportional_risk', 'documented_exact_origin_matching',
    'qualifying_history', 'remaining_qualifies', 'stopped_portion_no_longer_qualifies',
    'portion_of_entire_instrument', 'zero_value_zero_cost_origins',
    'linear_zero_discount_no_carry_credit_basis', 'no_historical_ineffectiveness',
    'complete_values_and_events', 'continuing_loss_recoverable',
    'complete_stopped_loss_facts', 'inventory_recognition_and_nrv',
    'pretax_no_other_activity',
}
QUOTE = {'id','operation','date','price','instrument_values','item_changes','facts_available_on'}


class Refusal(Exception):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason


def need(test, reason, status='rejected'):
    if not test:
        raise Refusal(status, reason)


def fields(value, keys):
    need(isinstance(value, dict) and set(value)==set(keys), 'fields')


def rational(value, nonnegative=False, positive=False):
    need(isinstance(value,str) and len(value)<=80 and
         re.fullmatch(r'(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?',value), 'rational')
    n=Q(value)
    need(str(n)==value, 'noncanonical_rational')
    need(not nonnegative or n>=0, 'numeric_domain')
    need(not positive or n>0, 'numeric_domain')
    return n


def day(value):
    need(isinstance(value,str), 'date')
    try:
        parsed=date.fromisoformat(value)
    except ValueError:
        raise Refusal('rejected','date')
    need(parsed.isoformat()==value, 'date')
    return value


def boolean(value):
    need(value is not None, 'unknown_fact', 'unresolved')
    need(type(value) is bool, 'boolean')
    return value


def identifier(value):
    need(isinstance(value,str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_.:-]{0,79}',value), 'identifier')
    return value


def source_check(root):
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        p=root/row['path']
        need(p.is_file(), 'source_missing', 'unresolved')
        need(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'], 'source_changed')


class Engine:
    def __init__(self, request):
        self.r=request
        fields(request, {'wire','operation','context','opening_cash','findings',
                         'origins','history','stop','after','closing'})
        need(request['wire']=='OriginMatchedCessation/1' and request['operation']=='report',
             'method', 'unsupported')
        ctx=request['context']
        fields(ctx, {'entity','book','currency','unit','underlying','rule','maturity','information_date'})
        need(all(isinstance(v,str) and 0<len(v)<=160 for v in ctx.values()), 'context')
        need(ctx['book']=='legal' and ctx['rule']=='EU2023/1803-original-IFRS9', 'context_profile','unsupported')
        self.maturity=day(ctx['maturity']); self.info=day(ctx['information_date'])
        need(self.maturity<=self.info, 'information_cutoff')
        f=request['findings']
        need(isinstance(f,dict), 'findings')
        need(not (set(f)-FINDINGS), 'unknown_finding')
        need(FINDINGS<=set(f), 'missing_finding','unresolved')
        for value in f.values():
            need(boolean(value), 'scope_finding','unsupported')
        self.capital=rational(request['opening_cash'],nonnegative=True)
        rows=request['origins']
        need(isinstance(rows,list) and 1<=len(rows)<=8, 'origins')
        self.origins={}; items=set(); instruments=set()
        for o in rows:
            fields(o, {'id','item_id','instrument_id','date','quantity','price',
                       'initial_value','initial_cash','facts_available_on'})
            key=identifier(o['id']); item=identifier(o['item_id']); inst=identifier(o['instrument_id'])
            need(key not in self.origins and item not in items and inst not in instruments, 'origin_collision')
            od=day(o['date']); self.facts(o,od)
            need(od<=self.maturity, 'origin_date')
            qty=rational(o['quantity'],positive=True); price=rational(o['price'],positive=True)
            need(rational(o['initial_value'])==0 and rational(o['initial_cash'])==0,
                 'nonzero_origin','unsupported')
            self.origins[key]=dict(id=key,item=item,instrument=inst,date=od,quantity=qty,price=price)
            items.add(item); instruments.add(inst)
        need(list(self.origins.values())==sorted(self.origins.values(),key=lambda o:o['date']), 'origin_order')
        self.remaining={k:o['quantity'] for k,o in self.origins.items()}
        self.active=set(); self.ids={'closing'}; self.date=None; self.price=None
        self.values={}; self.continuing=Q(0); self.frozen=Q(0); self.profit=Q(0)
        self.expected=None; self.stop_record=None; self.stop_price=None
        self.balances=dict(cash=self.capital,inventory=Q(0),capital=-self.capital,
            profit=Q(0),reserve_continuing=Q(0),reserve_stopped=Q(0))
        for o in self.origins.values():
            self.balances['derivative:'+o['instrument']]=Q(0)
        self.journals=[]; self.flows=[]; self.stages=[]
        self.snapshot('opening','opening')

    def facts(self, row, when):
        available=day(row['facts_available_on'])
        need(available<=when<=self.info, 'future_information')

    def unique(self, key):
        key=identifier(key)
        need(key not in self.ids, 'event_collision')
        self.ids.add(key)
        return key

    def post(self, key, entries):
        entries={k:v for k,v in entries.items() if v}
        assert sum(entries.values())==0, (key,entries)
        for k,v in entries.items():
            self.balances[k]+=v
        assert sum(self.balances.values())==0
        need(self.balances['cash']>=0, 'funding_shortfall','unsupported')
        self.journals.append(dict(id=key,entries={k:str(v) for k,v in entries.items()}))

    def snapshot(self, key, operation):
        d=sum(self.values.values())
        self.stages.append(dict(id=key,operation=operation,date=self.date,price=str(self.price) if self.price is not None else None,
            cash=str(self.balances['cash']),inventory=str(self.balances['inventory']),capital=str(self.capital),
            profit=str(self.profit),continuing_reserve=str(self.continuing),stopped_reserve=str(self.frozen),
            derivative_total=str(d),derivatives={k:str(v) for k,v in self.values.items()},
            gross_derivative_assets=str(sum(v for v in self.values.values() if v>0)),
            gross_derivative_liabilities=str(-sum(v for v in self.values.values() if v<0)),
            remaining_quantities={k:str(v) for k,v in self.remaining.items() if k in self.active},
            balances={k:str(v) for k,v in self.balances.items()}))

    def measure(self, row, allow_entry=False):
        fields(row,QUOTE); key=self.unique(row['id'])
        need(row['operation']=='measure', 'operation','unsupported')
        when=day(row['date']); self.facts(row,when)
        need((self.date is None or when>=self.date) and when<=self.maturity, 'measurement_date')
        price=rational(row['price'],nonnegative=True)
        if allow_entry:
            for k,o in self.origins.items():
                if k not in self.active and o['date']<=when:
                    need(o['date']==when, 'missing_origin_measurement')
                    need(o['price']==price, 'origin_price_mismatch')
                    self.active.add(k)
        need(self.active, 'no_active_origin')
        current={}; g=Q(0); changes=Q(0); signs=set()
        instruments={self.origins[k]['instrument'] for k in self.active}
        items={self.origins[k]['item'] for k in self.active}
        fields(row['instrument_values'],instruments); fields(row['item_changes'],items)
        for k,o in self.origins.items():
            if k not in self.active:
                continue
            v=rational(row['instrument_values'][o['instrument']])
            h=rational(row['item_changes'][o['item']])
            need(v==o['quantity']*(price-o['price']), 'actual_value_not_matched','unsupported')
            gain=self.remaining[k]*(price-o['price'])
            need(h==-gain, 'item_change_not_matched','unsupported')
            if gain:
                signs.add(1 if gain>0 else -1)
            current[o['instrument']]=v; g+=gain; changes+=h
        need(len(signs)<=1, 'opposed_origin_gains','unsupported')
        need(g*changes<=0, 'nonoffsetting_relationship','unsupported')
        reserve=(1 if g>0 else -1 if g<0 else 0)*min(abs(g),abs(changes))
        need(reserve==g, 'lower_of_trace_mismatch')
        delta_reserve=reserve-self.continuing
        entries={'derivative:'+k:v-self.values.get(k,Q(0)) for k,v in current.items()}
        delta_value=sum(entries.values()); delta_profit=delta_value-delta_reserve
        entries.update(reserve_continuing=-delta_reserve,profit=-delta_profit)
        self.post(key,entries)
        self.continuing=reserve; self.profit+=delta_profit; self.values=current
        self.date=when; self.price=price
        assert sum(self.values.values())==self.continuing+self.frozen+self.profit
        self.snapshot(key,'measure')

    def release(self, key, expected, loss):
        need(expected or loss==0, 'duplicate_cancellation_loss')
        if self.expected is False:
            need(not expected, 'cancellation_reinstatement','unsupported')
        if not expected:
            signed_release=self.frozen
        else:
            need(loss<=max(Q(0),-self.frozen), 'loss_exceeds_remaining_reserve')
            signed_release=-loss
        self.post(key,dict(reserve_stopped=signed_release,profit=-signed_release))
        self.frozen-=signed_release; self.profit+=signed_release; self.expected=expected
        if self.stop_record is not None:
            self.stop_record.update(remaining=str(self.frozen),
                released=str(Q(self.stop_record['gross'])-self.frozen),expected=expected)

    def stop(self, row):
        fields(row, {'id','date','origin_id','quantity','highly_probable','expected',
                     'unrecoverable_loss','facts_available_on'})
        key=self.unique(row['id']); when=day(row['date']); self.facts(row,when)
        need(when==self.date, 'stop_without_measurement')
        origin=row['origin_id']; need(isinstance(origin,str) and origin in self.origins, 'stop_origin')
        need(not boolean(row['highly_probable']), 'elective_cessation','unsupported')
        expected=boolean(row['expected']); loss=rational(row['unrecoverable_loss'],nonnegative=True)
        z=rational(row['quantity'],positive=True); o=self.origins[origin]
        need(z<o['quantity'], 'stop_quantity','unsupported')
        gross=z*(self.price-o['price'])
        self.post(key+'-split',dict(reserve_continuing=gross,reserve_stopped=-gross))
        self.continuing-=gross; self.frozen=gross; self.remaining[origin]-=z
        self.stop_price=self.price
        self.stop_record=dict(origin_id=origin,item_id=o['item'],instrument_id=o['instrument'],
            original_date=o['date'],original_price=str(o['price']),date=when,quantity=str(z),
            price=str(self.price),gross=str(gross),remaining=str(gross),released='0',expected=expected)
        self.release(key+'-release',expected,loss)
        assert sum(self.values.values())==self.continuing+self.frozen+self.profit
        self.snapshot(key,'stop')

    def assess(self,row):
        fields(row, {'id','operation','date','expected','unrecoverable_loss','facts_available_on'})
        key=self.unique(row['id']); when=day(row['date']); self.facts(row,when)
        need(when==self.date, 'assessment_without_measurement')
        expected=boolean(row['expected']); loss=rational(row['unrecoverable_loss'],nonnegative=True)
        self.release(key,expected,loss)
        assert sum(self.values.values())==self.continuing+self.frozen+self.profit
        self.snapshot(key,'assess_stopped')

    def close(self,row):
        fields(row, {'date','quantity','unit_price','supplier_cash','settlements','facts_available_on'})
        when=day(row['date']); self.facts(row,when)
        need(when==self.date==self.maturity, 'closing_without_maturity_measurement')
        qty=rational(row['quantity'],positive=True); price=rational(row['unit_price'],nonnegative=True)
        expected_qty=sum(self.remaining.values())+(Q(self.stop_record['quantity']) if self.expected else 0)
        need(qty==expected_qty, 'purchase_quantity')
        need(price==self.price, 'closing_price')
        supplier=rational(row['supplier_cash'],nonnegative=True)
        need(supplier==qty*price, 'supplier_cash')
        fields(row['settlements'],set(self.values))
        settlements={k:rational(v) for k,v in row['settlements'].items()}
        need(settlements==self.values, 'settlement_mismatch')
        attached=self.continuing+self.frozen
        need(supplier-attached>=0, 'negative_inventory_basis','unsupported')
        self.post('supplier',dict(cash=-supplier,inventory=supplier))
        self.flows.append(dict(id='supplier',amount=str(-supplier)))
        self.post('basis-transfer',dict(reserve_continuing=self.continuing,
            reserve_stopped=self.frozen,inventory=-attached))
        basis_trace=dict(continuing=str(self.continuing),stopped=str(self.frozen),
                         attached=str(attached),gross_cost=str(supplier),inventory=str(supplier-attached))
        self.stop_record.update(remaining_before_basis=str(self.frozen),
            basis_transfer=str(self.frozen),remaining='0')
        self.continuing=Q(0); self.frozen=Q(0)
        for o in self.origins.values():
            inst=o['instrument']; amount=settlements[inst]
            self.post('settle-'+inst,{'cash':amount,'derivative:'+inst:-amount})
            self.flows.append(dict(id=inst,amount=str(amount)))
            self.values[inst]=Q(0)
        self.snapshot('closing','purchase_and_settle')
        assert self.balances['cash']+self.balances['inventory']==self.capital+self.profit
        return basis_trace

    def run(self):
        history=self.r['history']; after=self.r['after']
        need(isinstance(history,list) and 1<=len(history)<=32, 'history')
        need(isinstance(after,list) and len(after)<=32, 'after')
        for row in history:
            self.measure(row,allow_entry=True)
        need(self.active==set(self.origins), 'incomplete_origin_history')
        self.stop(self.r['stop'])
        for row in after:
            need(isinstance(row,dict), 'fields')
            if row.get('operation')=='measure':
                self.measure(row)
            elif row.get('operation')=='assess_stopped':
                self.assess(row)
            else:
                raise Refusal('unsupported','operation')
        bridge=self.close(self.r['closing'])
        result={k:self.stages[-1][k] for k in ('cash','inventory','profit','capital',
                'continuing_reserve','stopped_reserve','derivative_total')}
        origins=[dict(id=o['id'],item_id=o['item'],instrument_id=o['instrument'],date=o['date'],
                      quantity=str(o['quantity']),price=str(o['price'])) for o in self.origins.values()]
        return dict(status='conditional_complete',reason=None,posts=False,mutations=[],
            context=self.r['context'].copy(),result=result,origins=origins,stopped=self.stop_record,
            closing_bridge=bridge,stages=self.stages,journals=self.journals,flows=self.flows)


def evaluate(request, source_root=ROOT):
    try:
        source_check(Path(source_root))
        return Engine(request).run()
    except Refusal as e:
        return dict(status=e.status,reason=e.reason,posts=False,mutations=[],context=None,
            result=None,origins=[],stopped=None,closing_bridge=None,stages=[],journals=[],flows=[])
