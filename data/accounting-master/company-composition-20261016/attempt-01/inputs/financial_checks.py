"""Independent exact reconstruction. Does not import authored expectations."""
from fractions import Fraction as F
from copy import deepcopy
ACCOUNTS=['cash','inventory','ppe','recovery_asset','investment','dta','dtl','refund_liability','debt','receivable','payable',
 'capital','retained','original_equity','revenue','cogs','selling_expense','wages','depreciation','finance_expense','current_tax','deferred_tax']
INCOME=['revenue','cogs','selling_expense','wages','depreciation','finance_expense','current_tax','deferred_tax']
ASSETS=['cash','inventory','ppe','recovery_asset','investment','dta','receivable']
LIABS=['dtl','refund_liability','debt','payable']
def number(x):return F(x)
def fmt(x):return str(F(x))
def balances(s,e):return {k:F(v) for k,v in s['books'][e].items()}
def profit(b):return -sum(b[k] for k in INCOME)
def pretax(b):return -sum(b[k] for k in INCOME if k not in ['current_tax','deferred_tax'])
def equity(b):return -sum(b[k] for k in ['capital','retained','original_equity',*INCOME])
def invariant(s,need):
 need(s['currency']=='USD' and s['basis']=='historical_EU_IFRS_conditional','context_unsupported')
 need(s['same_policies'] and s['same_calendar'] and s['noninvestment_entity'],'group_admission_missing','partial')
 need(s['entities']==['P','S'] and s['parent']=='P' and s['subsidiary']=='S','owner_mismatch')
 need(F(s['parent_fraction']) in (F(4,5),F(9,10)),'ownership_outside_subset','unsupported')
 for e in ['P','S']:
  b=balances(s,e);need(sum(b.values())==0,'unbalanced_legal_book');need(b['cash']>=0,'cash_shortfall')
 p=balances(s,'P');u=balances(s,'S');r=s['returns'];d=s['compound'];lot=s['lot']
 need(p['refund_liability']==-F(r['refund']) and p['recovery_asset']==F(r['recovery']),'return_allocation_mismatch')
 need(p['debt']==-F(d['debt']) and p['original_equity']==-F(d['original_equity']),'compound_allocation_mismatch')
 left=1-F(lot['sold_fraction']);need(0<=left<=1,'lot_fraction_invalid')
 need(p['inventory']==F(s['return_inventory'])+(0 if lot['transferred'] else F(lot['original_cost'])),'parent_inventory_allocation')
 need(u['inventory']==(F(lot['internal_price'])*left if lot['transferred'] else 0),'subsidiary_inventory_allocation')
 outstanding=F(lot['internal_price']) if lot['transferred'] and not lot['settled'] else F(0)
 need(p['receivable']==outstanding and u['payable']==-outstanding,'reciprocal_book_mismatch')

def derive(s,event,need):
 invariant(s,need);z=deepcopy(s);p=event['parameters'];m=event['method'];date=event['date']
 need(event['currency']==s['currency'],'currency_mismatch')
 need('2025-01-01'<=date<'2026-01-01' and date>=s['date'],'event_period_mismatch')
 need(s['control_start']<=date<s['control_end_exclusive'],'outside_control_interval')
 j={e:{k:F(0) for k in ACCOUNTS} for e in ['P','S']};flows=[]
 def post(e,k,x):j[e][k]+=F(x)
 def cash(e,a,x,origin):
  post(e,'cash',x);flows.append(dict(entity=e,activity=a,amount=fmt(x),origin=origin))
 def yes(x,code):need(x is not None,code,'partial');need(x,code)
 if m=='compound.redeem':
  d=z['compound'];yes(p['original_rights_unchanged'],'original_rights_missing')
  need(d['phase']=='matured' and date>=d['due_date'],'redemption_order')
  amount=F(p['amount']);basis=F(d['debt_cash_basis']);need(amount==F(d['debt']) and 0<basis<=amount,'redemption_amount')
  post('P','debt',amount);cash('P','operating',-(amount-basis),'interest');cash('P','financing',-basis,'principal')
  d.update(phase='ended',debt='0')
 elif m=='returns.settle':
  r=z['returns'];need(not r['settled'],'return_duplicate');need(p['all_rights_closed'],'return_window_open','partial')
  yes(p['handling_is_selling_cost'],'handling_classification_missing')
  n,h,d=map(F,[p['actual_units'],p['unit_handling'],p['unit_deterioration']]);cost=F(r['unit_cost'])
  need(0<=n<=F(r['sold_units']) and h>=0 and 0<=d<=cost and F(p['inventory_nrv'])>=0,'return_inputs_invalid')
  refund=n*F(r['unit_refund']);handling=n*h;recovered=min(n*(cost-d),F(p['inventory_nrv']))
  need(F(p['refund_cash'])==refund and F(p['handling_cash'])==handling,'return_cash_mismatch')
  post('P','refund_liability',r['refund']);post('P','recovery_asset',-F(r['recovery']));post('P','inventory',recovered)
  post('P','revenue',refund-F(r['refund']));post('P','cogs',F(r['recovery'])-recovered);post('P','selling_expense',handling)
  cash('P','operating',-refund,'refund');cash('P','operating',-handling,'handling')
  r.update(refund='0',recovery='0',inventory=fmt(recovered),settled=True);z['return_inventory']=fmt(recovered)
 elif m=='payroll.pay':
  yes(p['service_received'],'service_finding_missing');yes(p['tax_deductible'],'payroll_tax_finding_missing')
  need(F(p['amount'])>=0,'negative_wages');post('P','wages',p['amount']);cash('P','operating',-F(p['amount']),'wages')
 elif m=='ppe.depreciate':
  yes(p['systematic_basis'],'depreciation_basis_missing');yes(p['tax_matches_book'],'depreciation_tax_basis_missing')
  v=F(p['amount']);need(0<=v<=F(s['books']['P']['ppe']),'depreciation_amount')
  post('P','ppe',-v);post('P','depreciation',v)
 elif m=='inventory.transfer':
  lot=z['lot'];need(not lot['transferred'],'internal_sale_duplicate');yes(p['counterparty_confirmed'],'counterparty_missing')
  need((p['seller'],p['buyer'])==('P','S'),'transfer_direction_unsupported','unsupported')
  need((p['lot_id'],p['invoice_id'])==(lot['lot_id'],lot['invoice_id']),'internal_identity_mismatch')
  v,c=F(p['seller_amount']),F(p['cost']);need(v==F(p['buyer_amount']) and v>=c==F(lot['original_cost']),'reciprocal_amount_mismatch')
  for e,k,x in [('P','receivable',v),('P','revenue',-v),('P','cogs',c),('P','inventory',-c),('S','inventory',v),('S','payable',-v)]:post(e,k,x)
  lot.update(internal_price=fmt(v),transferred=True)
 elif m=='inventory.sell':
  yes(p['performance_complete'],'performance_missing');e=p['entity'];fraction=F(p['fraction']);v=F(p['proceeds'])
  need(v>=0 and 0<fraction<=1,'sale_amount_invalid')
  if e=='S' and p['lot_id']==z['lot']['lot_id']:
   lot=z['lot'];need(lot['transferred'],'sale_before_transfer');need(F(lot['sold_fraction'])+fraction<=1,'oversold_lot')
   c=F(lot['internal_price'])*fraction;lot['sold_fraction']=fmt(F(lot['sold_fraction'])+fraction)
  elif e=='P' and p['lot_id']=='recovered':
   need(fraction==1 and F(z['return_inventory'])>0,'return_inventory_sale_scope','unsupported')
   c=F(z['return_inventory']);z['return_inventory']='0'
  else:need(False,'sale_owner_or_lot_mismatch')
  cash(e,'operating',v,'external_sale');post(e,'revenue',-v);post(e,'inventory',-c);post(e,'cogs',c)
 elif m=='intercompany.pay':
  lot=z['lot'];need(lot['transferred'] and not lot['settled'],'internal_settlement_order')
  need((p['payer'],p['payee'],p['invoice_id'])==('S','P',lot['invoice_id']),'internal_identity_mismatch')
  v=F(p['payer_amount']);need(v==F(p['payee_amount'])==F(lot['internal_price']),'reciprocal_cash_mismatch')
  cash('P','operating',v,'internal');post('P','receivable',-v);post('S','payable',v);cash('S','operating',-v,'internal');lot['settled']=True
 elif m=='tax.close':
  for k in ['rate_enacted','recovery_supported','temporary_difference_inventory_complete','outside_basis_timing_control','outside_basis_no_foreseeable_reversal']:yes(p[k],'tax_'+k+'_missing')
  need(p['rate'] is not None,'tax_rate_missing','partial');rate=F(p['rate']);need(rate==F(s['tax_rate'])==F(1,4),'tax_rate_outside_subset','unsupported')
  need(p['return_tax_timing']=='refund_and_recovered_stock_on_settlement','return_tax_law_missing','partial')
  need(s['returns']['settled'],'tax_return_settlement_required','partial')
  expected_start=s['tax_closes'][-1] if s['tax_closes'] else '2025-01-01'
  need(p['period_start']==expected_start and p['period_end_exclusive'] in ['2025-07-01','2026-01-01'],'tax_period_mismatch')
  need(date=={'2025-07-01':'2025-06-30','2026-01-01':'2025-12-31'}[p['period_end_exclusive']],'tax_cutoff_mismatch')
  for e in ['P','S']:
   b=balances(s,e);difference=F(0)
   if e=='P':
    r=s['returns'];difference=-F(r['expected_units'])*F(r['unit_refund'])+F(r['expected_units'])*(F(r['unit_cost'])-F(r['estimated_handling'])-F(r['estimated_deterioration']))
   current=(pretax(b)+difference)*rate-b['current_tax'];need(current>=0,'tax_refund_route_unspecified','unsupported')
   post(e,'current_tax',current);cash(e,'operating',-current,'income_tax')
   post(e,'dta',-b['dta']);post(e,'dtl',-b['dtl']);post(e,'deferred_tax',b['dta']+b['dtl'])
  z['tax_closes'].append(p['period_end_exclusive'])
 elif m=='ownership.purchase':
  yes(p['control_retained'],'control_loss_requires_other_method');yes(p['same_rights_per_share'],'ownership_rights_missing')
  need(z['ownership_purchase'] is None and s['tax_closes']==['2025-07-01'] and date=='2025-07-01','ownership_timing_scope','unsupported')
  old,new,v=F(s['parent_fraction']),F(p['new_parent_fraction']),F(p['consideration'])
  need(old==F(4,5) and new==F(9,10) and v>=0,'ownership_subset_unsupported','unsupported')
  sub=balances(s,'S');base=equity(sub);change=(new-old)*base
  z['ownership_purchase']=dict(date=date,old_fraction=fmt(old),new_fraction=fmt(new),consideration=fmt(v),
   nci_before=fmt((1-old)*base),carrying_reduction=fmt(change),parent_equity_debit=fmt(v-change),subsidiary_profit_before=fmt(profit(sub)))
  z['parent_fraction']=fmt(new);post('P','investment',v);cash('P','investing',-v,'nci_purchase')
 else:need(False,'method_unsupported','unsupported')
 for e in ['P','S']:
  need(sum(j[e].values())==0,'derived_journal_unbalanced')
  z['books'][e]={k:fmt(F(s['books'][e][k])+j[e][k]) for k in ACCOUNTS}
  need(j[e]['cash']==sum(F(f['amount']) for f in flows if f['entity']==e),'derived_cash_mismatch')
 z['date']=date;z['sequence']+=1;z['flows'] += [dict(f,date=date) for f in flows]
 invariant(z,need)
 return z,{e:{k:fmt(v) for k,v in b.items()} for e,b in j.items()},flows

def cumulative(s,need):
 invariant(s,need);b={e:balances(s,e) for e in ['P','S']};lot=s['lot'];rate=F(s['tax_rate'])
 internal=F(lot['internal_price']) if lot['transferred'] else F(0)
 unreal=(internal-F(lot['original_cost']))*(1-F(lot['sold_fraction'])) if lot['transferred'] else F(0)
 need(s['tax_recovery_supported'],'group_dta_recovery_missing','partial')
 income={k:sum(x[k] for x in b.values()) for k in INCOME}
 income['revenue']+=internal;income['cogs']-=internal-unreal;income['deferred_tax']-=unreal*rate
 g={k:sum(x[k] for x in b.values()) for k in ['cash','inventory','ppe','dta','dtl']}
 g['inventory']-=unreal;g['dta']+=unreal*rate;g['dtl']=-g['dtl']
 g['assets']=sum(sum(x[k] for k in ASSETS) for x in b.values())-b['P']['investment']-b['P']['receivable']-unreal+unreal*rate
 g['liabilities']=-sum(sum(x[k] for k in LIABS) for x in b.values())+b['S']['payable']
 g['equity']=g['assets']-g['liabilities'];g.update(income);g['revenue']=-g['revenue']
 g['pretax']=-sum(v for k,v in income.items() if k not in ['current_tax','deferred_tax']);g['profit']=-sum(income.values())
 purchase=s['ownership_purchase'];sp=profit(b['S'])
 if purchase:
  old,new,prior=map(F,[purchase['old_fraction'],purchase['new_fraction'],purchase['subsidiary_profit_before']])
  nci=(1-old)*prior+(1-new)*(sp-prior);reduction=F(purchase['carrying_reduction'])
 else:nci=F(1,5)*sp;reduction=0
 g['nci_profit']=nci;g['parent_profit']=g['profit']-nci;g['nci_equity']=20+nci-reduction;g['parent_equity']=g['equity']-g['nci_equity']
 need(g['equity']==642+g['profit']-(F(purchase['consideration']) if purchase else 0),'group_equity_bridge')
 return g

def report(opening,closing,start,end,need):
 need(start<end and opening['date']<=start and closing['date']<end,'report_period_invalid')
 need(end in closing['tax_closes'],'report_tax_close_missing','partial')
 g0=cumulative(opening,need);g=cumulative(closing,need)
 for k in ['revenue','cogs','selling_expense','wages','depreciation','finance_expense','current_tax','deferred_tax','pretax','profit','nci_profit','parent_profit']:g[k]-=g0[k]
 for a in ['operating','investing','financing']:
  g[a+'_receipts']=F(0);g[a+'_payments']=F(0)
 g['interest_paid']=F(0);g['tax_paid']=F(0)
 internal=[]
 for f in closing['flows']:
  if not start<=f['date']<end:continue
  v=F(f['amount']);a=f['activity']
  if f['origin']=='internal':internal.append(v);continue
  if f['origin']=='nci_purchase':a='financing'
  g[a+('_receipts' if v>=0 else '_payments')]+=abs(v)
  if f['origin']=='interest':g['interest_paid']-=v
  if f['origin']=='income_tax':g['tax_paid']-=v
 need(not internal or len(internal)==2 and sum(internal)==0,'internal_cash_join_failed')
 g['net_cash']=sum(g[a+'_receipts']-g[a+'_payments'] for a in ['operating','investing','financing'])
 need(g['cash']-g0['cash']==g['net_cash'],'group_cash_bridge')
 legal={}
 for e in ['P','S']:
  b0,b1=balances(opening,e),balances(closing,e)
  legal[e]={'cash':fmt(b1['cash']),'profit':fmt(profit(b1)-profit(b0)),'equity':fmt(equity(b1)),
   'taxable_income':fmt((b1['current_tax']-b0['current_tax'])/F(closing['tax_rate']))}
 return {k:fmt(v) for k,v in g.items()},legal
