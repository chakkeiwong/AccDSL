"""Authored expected books and query outputs. Never imports financial_checks."""
from copy import deepcopy

ACCOUNTS=('cash','loans','goodwill','allowance','deposits','borrowing','stock','retained','interest_income','deposit_expense','loss_expense')
def balances(**v):return {k:str(v.get(k,0)) for k in ACCOUNTS}
OPEN=balances(cash=30,loans=100,goodwill=2,allowance='-4/5',deposits=-110,stock=-20,retained='-6/5')
FINAL=balances(cash=21,loans=120,goodwill=2,allowance='-12/5',deposits=-117,stock=-20,retained='-18/5')
# method, amount, economic date and independently authored signed journal
EVENTS=[
 ('loan.originate','20','2026-01-10',dict(loans='20',deposits='-20')),
 ('loan.external','15','2026-01-11',dict(deposits='15',cash='-15')),
 ('income.receive','6','2026-02-01',dict(cash='6',interest_income='-6')),
 ('deposits.interest','2','2026-03-01',dict(deposit_expense='2',deposits='-2')),
 ('allowance.measure','12/5','2026-03-15',dict(loss_expense='8/5',allowance='-8/5')),
 ('income.close','0','2026-03-31',dict(interest_income='6',deposit_expense='-2',loss_expense='-8/5',retained='-12/5'))]
BOOKS=[
 dict(id='opening',opening=OPEN,events=[],closing=OPEN,unpaid='0',facility='10'),
 dict(id='final',opening=OPEN,events=EVENTS,closing=FINAL,unpaid='0',facility='10'),
 dict(id='preclose',opening=OPEN,events=EVENTS[:-1],closing=balances(cash=21,loans=120,goodwill=2,allowance='-12/5',deposits=-117,stock=-20,retained='-6/5',interest_income=-6,deposit_expense=2,loss_expense='8/5'),unpaid='0',facility='10'),
 dict(id='runoff25',opening=OPEN,events=EVENTS+[
  ('funding.draw','4','2026-03-31',dict(cash='4',borrowing='-4')),
  ('deposits.runoff','25','2026-03-31',dict(deposits='25',cash='-25'))],
  closing=balances(loans=120,goodwill=2,allowance='-12/5',deposits=-92,borrowing=-4,stock=-20,retained='-18/5'),unpaid='0',facility='10'),
 dict(id='runoff40',opening=OPEN,events=EVENTS+[
  ('funding.draw','10','2026-03-31',dict(cash='10',borrowing='-10')),
  ('deposits.runoff','40','2026-03-31',dict(deposits='31',cash='-31'))],
  closing=balances(loans=120,goodwill=2,allowance='-12/5',deposits=-86,borrowing=-10,stock=-20,retained='-18/5'),unpaid='9',facility='10'),
 dict(id='zero',opening=balances(cash=20,stock=-20),events=[],closing=balances(cash=20,stock=-20),unpaid='0',facility='0'),
 dict(id='negative-denominator',opening=balances(cash=20,goodwill=2,deposits=-2,stock=-20),events=[],closing=balances(cash=20,goodwill=2,deposits=-2,stock=-20),unpaid='0',facility='0')]

def met(v=None,code=None):return dict(status='unresolved' if code else 'resolved',value=v,diagnostics=[code] if code else [])
def rat(n,d,v,undefined=False):return dict(status='undefined' if undefined else 'resolved',numerator=n,denominator=d,value=v,diagnostics=['nonpositive_denominator'] if undefined else [])
FINAL_AMOUNTS=dict(book_equity='118/5',gross_loans='120',allowance='12/5',goodwill='2',cap_base='120',cap='3/2',admitted_allowance='3/2',excess_allowance='9/10',rwa='1191/10',cet1='108/5',tier1='108/5',tier2='3/2',total_capital='231/10',leverage_denominator='143')
FINAL_RATIOS=dict(cet1_ratio=rat('108/5','1191/10','72/397'),tier1_ratio=rat('108/5','1191/10','72/397'),total_ratio=rat('231/10','1191/10','77/397'),leverage_ratio=rat('108/5','143','108/715'))
LINKS=dict(cet1_ratio=('cet1','rwa'),tier1_ratio=('tier1','rwa'),total_ratio=('total_capital','rwa'),leverage_ratio=('tier1','leverage_denominator'))
def expected(amounts=FINAL_AMOUNTS,ratios=FINAL_RATIOS):return dict(amounts={k:met(v) for k,v in amounts.items()},ratios=deepcopy(ratios))
def unresolved(out,keys,code):
 for k in keys:out['amounts'][k]=met(code=code)
 for k,(n,d) in LINKS.items():
  if n in keys or d in keys:
   out['ratios'][k]=dict(status='unresolved',numerator=out['amounts'][n]['value'],denominator=out['amounts'][d]['value'],value=None,diagnostics=[code])
 return out
CAPITAL_CASES=[dict(id=k,book=k,average='145',changes={},expected=expected()) for k in ('final','preclose','runoff25','runoff40')]
CAPITAL_CASES.append(dict(id='opening',book='opening',average='140',changes={},expected=expected(
 dict(book_equity='106/5',gross_loans='100',allowance='4/5',goodwill='2',cap_base='100',cap='5/4',admitted_allowance='4/5',excess_allowance='0',rwa='100',cet1='96/5',tier1='96/5',tier2='4/5',total_capital='20',leverage_denominator='138'),
 dict(cet1_ratio=rat('96/5','100','24/125'),tier1_ratio=rat('96/5','100','24/125'),total_ratio=rat('20','100','1/5'),leverage_ratio=rat('96/5','138','16/115')))))
CAPITAL_CASES.append(dict(id='missing-average',book='final',average=None,changes={},expected=unresolved(expected(),['leverage_denominator'],'average_assets_missing')))
for i in range(1,14):
 CAPITAL_CASES.append(dict(id='unknown-stock-'+str(i),book='final',average='145',changes={'eligibility':{'condition_'+str(i):'unknown'}},expected=unresolved(expected(),['cet1','tier1','total_capital'],'stock_eligibility_unknown')))
CAPITAL_CASES.append(dict(id='unknown-exposure',book='final',average='145',changes={'exposure':{'loan_class':'unknown'}},expected=unresolved(expected(),['cap_base','cap','admitted_allowance','excess_allowance','rwa','tier2','total_capital'],'exposure_classification_unknown')))
CAPITAL_CASES.append(dict(id='unknown-allowance',book='final',average='145',changes={'allowance':'unknown'},expected=unresolved(expected(),['admitted_allowance','excess_allowance','rwa','tier2','total_capital'],'allowance_admission_unknown')))
CAPITAL_CASES.append(dict(id='unknown-deduction',book='final',average='145',changes={'deduction':'unknown'},expected=unresolved(expected(),['cap_base','cap','admitted_allowance','excess_allowance','rwa','tier2','cet1','tier1','total_capital','leverage_denominator'],'deduction_unknown')))
CAPITAL_CASES.append(dict(id='unknown-applicability',book='final',average='145',changes={'applicability':{'aoci':'unknown'}},expected=unresolved(expected(),['cap_base','cap','admitted_allowance','excess_allowance','rwa','tier2','cet1','tier1','total_capital','leverage_denominator'],'applicability_unknown')))
for name,w,e,m,den in [('zero','0','20','0','0'),('negative-denominator','2','20','1','-1')]:
 amounts=dict(book_equity=e,gross_loans='0',allowance='0',goodwill=w,cap_base='0',cap='0',admitted_allowance='0',excess_allowance='0',rwa='0',cet1='20' if name=='zero' else '18',tier1='20' if name=='zero' else '18',tier2='0',total_capital='20' if name=='zero' else '18',leverage_denominator=den)
 n=amounts['cet1'];rs={k:rat(n,'0',None,True) for k in ('cet1_ratio','tier1_ratio','total_ratio')};rs['leverage_ratio']=rat(n,den,None,True)
 CAPITAL_CASES.append(dict(id=name,book=name,average=m,changes={},expected=expected(amounts,rs)))

CELLS=[dict(cell_id='early',default_date='2026-06-30',ead='100',lgd='1/2',cash_shortfall='50',discount_factor='1'),dict(cell_id='late',default_date='2027-03-31',ead='200',lgd='1/4',cash_shortfall='50',discount_factor='1'),dict(cell_id='none',default_date=None,ead='0',lgd='0',cash_shortfall='0',discount_factor='1')]
def law_result(name,mass,weights,loss,code=None):return dict(law_id=name,status='unresolved' if code else 'resolved',conditioning_mass=mass,conditional_weights=weights,expected_loss=loss,diagnostic=code)
def loss_expected(rows,values,possible=('0','50'),status='resolved',code=None,bounds=None,target='expectation_over_candidate_laws'):
 return dict(law_results=rows,possible_losses=list(possible),expectation_status=status,expectation_values=values,lower=bounds[0] if bounds else values[0] if values else None,upper=bounds[1] if bounds else values[-1] if values else None,bounds_target=target,diagnostics=[code] if code else [],accounting_allowance_claim=False)
P=('law-original',['1/10','1/10','4/5']);Q=('law-alternative',['1/5','3/10','1/2'])
LOSS_CASES=[
 dict(id='original',mode='point_law',candidates=[P],origin='2026-04-01',end='2028-04-01',condition=None,vintage='original',expected=loss_expected([law_result(P[0],'1',P[1],'10')],['10'])),
 dict(id='first-window',mode='point_law',candidates=[P],origin='2026-04-01',end='2027-03-31',condition=None,vintage='original',expected=loss_expected([law_result(P[0],'1',P[1],'5')],['5'])),
 dict(id='survival',mode='point_law',candidates=[P],origin='2026-10-01',end='2028-04-01',condition='2026-09-30',vintage='original',expected=loss_expected([law_result(P[0],'9/10',['0','1/9','8/9'],'50/9')],['50/9'])),
 dict(id='law-family',mode='law_family',candidates=[P,Q],origin='2026-04-01',end='2028-04-01',condition=None,vintage='original',expected=loss_expected([law_result(P[0],'1',P[1],'10'),law_result(Q[0],'1',Q[1],'25')],['10','25'],status='set_valued')),
 dict(id='unweighted',mode='unweighted_histories',candidates=[],origin='2026-04-01',end='2028-04-01',condition=None,vintage='original',expected=loss_expected([],[],status='unresolved',code='probability_measure_missing',bounds=('0','50'),target='possible_history_losses')),
 dict(id='zero-mass',mode='point_law',candidates=[('law-zero',['1','0','0'])],origin='2026-10-01',end='2028-04-01',condition='2026-09-30',vintage='original',expected=loss_expected([law_result('law-zero','0',[],None,'zero_conditioning_mass')],[],status='unresolved',code='zero_conditioning_mass',target='undefined')),
 dict(id='new-forecast',mode='point_law',candidates=[('law-new',['0','1/5','4/5'])],origin='2026-10-01',end='2028-04-01',condition=None,vintage='new',expected=loss_expected([law_result('law-new','1',['0','1/5','4/5'],'10')],['10']))]
