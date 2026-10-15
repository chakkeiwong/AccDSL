"""Exact two-method projection; no renaming and no whole-profile migration."""
from copy import deepcopy
from fractions import Fraction as F
import json,hashlib
from pathlib import Path
SPECS={
 'return':{'packet':'data/accounting-master/extended-method-exchanges-20261015/corporate-residuals/attempt-01/portable-exchanges.json',
  'profile':'CorporateResiduals/1','case':'return-expected','index':0,'method':'rcost.settle',
  'accounts':{'cash':'cash','inventory':'inventory','recovery_asset':'recovery_asset','refund_liability':'refund_liability',
   'original_equity':'original_equity','revenue':'revenue','cost_of_sales':'cogs','cost_expense':'selling_expense'}},
 'compound':{'packet':'data/accounting-master/extended-method-exchanges-20261015/financing-v2/attempt-02/portable-exchanges.json',
  'profile':'FinancingComponents/2','case':'original-redeem','index':2,'method':'compound.end',
  'accounts':{'cash':'cash','debt':'debt','original_equity':'original_equity','finance_expense':'finance_expense','capital':'capital'}}}
def value(v):return F(int(v['n']),int(v['d']))
def rational(v):
 q=F(v);return {'n':str(q.numerator),'d':str(q.denominator)}
def projection(packet,state_ref,key,need):
 spec=SPECS[key];need(packet['profile']==spec['profile'],'migration_profile_unsupported','unsupported')
 reg=packet['record_registry'];state=reg[state_ref['digest']]['body'];component=reg[state['component_ref']['digest']]['body']
 expected='rcost' if key=='return' else 'compound';need(component['tag']==expected,'migration_component_unsupported','unsupported')
 need(set(state)=={'context_ref','view_ref','sequence','instant','as_of_date','component_ref','balances','cash_movements','cash_receipts','cash_payments','oci_movements','equity_movements','tax_status'},'migration_unknown_field','unsupported')
 mapped=spec['accounts'];need(all(k in mapped or value(v)==0 for k,v in state['balances'].items()),'migration_unmapped_balance','unsupported')
 ctx=reg[state['context_ref']['digest']]['body']
 need(ctx['currency']=='USD' and ctx['basis']=='historical_EU_IFRS_conditional','migration_context_unsupported','unsupported')
 if key=='return':need(not component['value']['settled'],'migration_settled_return','unsupported')
 else:need(component['value']['phase']=='matured','migration_debt_phase','unsupported')
 return {'subset':key,'owner':{k:ctx[k] for k in ['entity_id','book_id','branch_key']},
  'source_context_ref':state['context_ref'],'source_view_ref':state['view_ref'],
  'sequence':state['sequence'],'instant':state['instant'],'as_of_date':state['as_of_date'],
  'component':deepcopy(component),
  'balances':{target:str(value(state['balances'][source])) for source,target in mapped.items()},
  'accumulators':{k:deepcopy(state[k]) for k in ['cash_movements','cash_receipts','cash_payments','oci_movements','equity_movements']},
  'tax_status':state['tax_status']}

def target_step(projected,event,need):
 z=deepcopy(projected);v=z['component']['value'];p=event['parameters'];j={};cash={'operating':F(0),'investing':F(0),'financing':F(0),'unclassified':F(0)}
 def post(k,x):j[k]=j.get(k,F(0))+x
 if z['subset']=='return':
  need(event['method_id']=='rcost.settle','migration_method_unsupported','unsupported')
  need(not v['settled'] and p['all_rights_closed'] and p['handling_is_selling_cost'] is True,'migration_return_facts')
  n,h,d=value(p['actual_units']),value(p['unit_handling']),value(p['unit_deterioration']);cost=value(v['unit_cost'])
  need(0<=n<=value(v['sold_units']) and h>=0 and 0<=d<=cost,'migration_return_amount')
  refund=n*value(v['unit_refund']);handling=n*h;stock=min(n*(cost-d),value(p['inventory_nrv']))
  need(refund==value(p['refund_cash']) and handling==value(p['handling_cash']),'migration_cash_mismatch')
  for k,x in [('cash',-refund-handling),('inventory',stock),('refund_liability',value(v['refund'])),('recovery_asset',-value(v['recovery'])),
   ('revenue',refund-value(v['refund'])),('cogs',value(v['recovery'])-stock),('selling_expense',handling)]:post(k,x)
  cash['operating']=-refund-handling;v.update(refund=rational(0),recovery=rational(0),inventory=rational(value(v['inventory'])+stock),settled=True)
 else:
  need(event['method_id']=='compound.end' and p['route']=='redeem','migration_method_unsupported','unsupported')
  need(v['phase']=='matured' and p['original_rights_unchanged'] and event['event_date']>=v['due_date'],'migration_redemption_facts')
  amount=value(v['debt']);basis=value(v['debt_cash_basis']);need(amount==value(p['amount_or_shares'])==value(v['redemption']) and 0<basis<=amount,'migration_redemption_amount')
  post('cash',-amount);post('debt',amount);cash['operating']=-(amount-basis);cash['financing']=-basis;v.update(debt=rational(0),phase='ended')
 need(sum(j.values())==0,'migration_journal_balance')
 z['balances']={k:str(F(x)+j.get(k,0)) for k,x in z['balances'].items()};z['sequence']+=1;z['instant']=event['instant'];z['as_of_date']=event['event_date']
 for k,x in cash.items():
  for name,delta in [('cash_movements',x),('cash_receipts',max(F(0),x)),('cash_payments',max(F(0),-x))]:
   z['accumulators'][name][k]=rational(value(z['accumulators'][name][k])+delta)
 return z

def map_closed_result(packet,state_ref,key):
 # After-state mapper has the same field map, without the opening eligibility restriction.
 reg=packet['record_registry'];s=reg[state_ref['digest']]['body'];c=reg[s['component_ref']['digest']]['body'];ctx=reg[s['context_ref']['digest']]['body']
 return {'subset':key,'owner':{k:ctx[k] for k in ['entity_id','book_id','branch_key']},'source_context_ref':s['context_ref'],'source_view_ref':s['view_ref'],
 'sequence':s['sequence'],'instant':s['instant'],'as_of_date':s['as_of_date'],'component':deepcopy(c),
 'balances':{t:str(value(s['balances'][a])) for a,t in SPECS[key]['accounts'].items()},
 'accumulators':{k:deepcopy(s[k]) for k in ['cash_movements','cash_receipts','cash_payments','oci_movements','equity_movements']},'tax_status':s['tax_status']}

def projection_schema(source_schema,key):
 from schema_design import obj,enum,Q,TXT,I,DATE
 defs=source_schema['$defs'];state=defs['CompanyState']['properties'];tag='rcost' if key=='return' else 'compound'
 component=next(x for x in defs['ComponentState']['oneOf'] if x['properties']['tag']['const']==tag)
 return obj({'subset':{'const':key},'owner':obj({k:TXT for k in ['entity_id','book_id','branch_key']}),
  'source_context_ref':deepcopy(state['context_ref']),'source_view_ref':deepcopy(state['view_ref']),
  'sequence':I,'instant':I,'as_of_date':DATE,'component':deepcopy(component),
  'balances':obj({v:Q for v in SPECS[key]['accounts'].values()}),
  'accumulators':obj({k:deepcopy(state[k]) for k in ['cash_movements','cash_receipts','cash_payments','oci_movements','equity_movements']}),
  'tax_status':deepcopy(state['tax_status'])})
