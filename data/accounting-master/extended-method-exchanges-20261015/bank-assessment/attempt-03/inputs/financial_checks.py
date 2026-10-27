"""Independent rational derivations. Never imports builder or authored cases."""
from fractions import Fraction as F

class Refusal(Exception):pass
def need(ok,code):
 if not ok:raise Refusal(code)
def num(v):
 if isinstance(v,dict):
  need(set(v)=={'n','d'},'invalid_rational')
  x=F(int(v['n']),int(v['d']))
  need(str(x.numerator)==v['n'] and str(x.denominator)==v['d'],'noncanonical_rational')
  return x
 return F(v)
def q(v):
 x=F(v);return dict(n=str(x.numerator),d=str(x.denominator))
def metric(v=None,diagnostic=None):return dict(status='unresolved' if diagnostic else 'resolved',value=None if diagnostic else q(v),diagnostics=[diagnostic] if diagnostic else [])
def ratio(n,d):
 diagnostics=list(dict.fromkeys(n['diagnostics']+d['diagnostics']))
 if diagnostics:return dict(status='unresolved',numerator=n['value'],denominator=d['value'],value=None,diagnostics=diagnostics)
 a,b=num(n['value']),num(d['value'])
 return dict(status='resolved' if b>0 else 'undefined',numerator=q(a),denominator=q(b),value=q(a/b) if b>0 else None,diagnostics=[] if b>0 else ['nonpositive_denominator'])

def ledger(opening,events,facility_limit):
 b={k:num(v) for k,v in opening.items()};journals=[];unpaid=F(0)
 limit=num(facility_limit)
 need(limit>=0 and -b['borrowing']<=limit,'facility_limit_exceeded')
 need(sum(b.values())==0,'opening_unbalanced')
 need(all(b[k]>=0 for k in ('cash','loans','goodwill')) and all(b[k]<=0 for k in ('allowance','deposits','borrowing','stock')),'invalid_book_sign')
 for e in events:
  m,a=e['method_id'],num(e['amount']);need(a>=0,'negative_event_amount')
  j={}
  if m=='loan.originate':j={'loans':a,'deposits':-a}
  elif m=='loan.external':
   need(a<=b['cash'] and a<=-b['deposits'],'unfunded_external_settlement');j={'deposits':a,'cash':-a}
  elif m=='income.receive':j={'cash':a,'interest_income':-a}
  elif m=='deposits.interest':j={'deposit_expense':a,'deposits':-a}
  elif m=='allowance.measure':
   need(a<=b['loans'],'allowance_exceeds_loans');change=a+b['allowance'];j={'loss_expense':change,'allowance':-change}
  elif m=='income.close':
   need(a==0,'nonzero_closing_parameter')
   pnl=sum(b[k] for k in ('interest_income','deposit_expense','loss_expense'))
   j={k:-b[k] for k in ('interest_income','deposit_expense','loss_expense')};j['retained']=pnl
  elif m=='funding.draw':
   need(-b['borrowing']+a<=limit,'facility_limit_exceeded');j={'cash':a,'borrowing':-a}
  elif m=='deposits.runoff':
   need(a<=-b['deposits'],'runoff_exceeds_deposits');paid=min(a,b['cash']);unpaid+=a-paid;j={'deposits':paid,'cash':-paid}
  else:raise Refusal('unsupported_accounting_event')
  j={k:v for k,v in j.items() if v};need(sum(j.values())==0,'journal_unbalanced')
  for k,v in j.items():b[k]+=v
  journals.append({k:q(v) for k,v in j.items()})
 need(sum(b.values())==0,'closing_unbalanced')
 return {k:q(v) for k,v in b.items()},journals,q(unpaid)

def capital(b,app,elig,exposure,allowance,deduction,average):
 b={k:num(v) for k,v in b.items()}
 need(sum(b.values())==0,'book_unbalanced')
 need(all(v!='present' for v in app.values()),'unsupported_regime')
 need(all(v!='failed' for v in elig.values()),'stock_eligibility_failed')
 need(exposure['reserve_venue']!='commercial_bank' and exposure['loan_class'] not in ('PCD','nonaccrual'),'unsupported_exposure')
 need(allowance!='no','unsupported_allowance');need(deduction!='no','unsupported_deduction')
 g,a,w=b['loans'],-b['allowance'],b['goodwill']
 need(g>=0 and 0<=a<=g and w>=0,'invalid_exposure_amount')
 equity=-sum(b[k] for k in ('stock','retained','interest_income','deposit_expense','loss_expense'))
 out={k:metric(v) for k,v in dict(book_equity=equity,gross_loans=g,allowance=a,goodwill=w).items()}
 regime='applicability_unknown' if 'unknown' in app.values() else None
 deduction_unknown='deduction_unknown' if deduction=='unknown' else None
 exposure_unknown='exposure_classification_unknown' if 'unknown' in exposure.values() else None
 risk_problem=regime or deduction_unknown or exposure_unknown
 out['cap_base']=metric(g,risk_problem);out['cap']=metric(g/80,risk_problem)
 allowance_problem=risk_problem or ('allowance_admission_unknown' if allowance=='unknown' else None)
 t=min(a,g/80);x=a-t
 for k,v in dict(admitted_allowance=t,excess_allowance=x,rwa=g-x,tier2=t).items():out[k]=metric(v,allowance_problem)
 equity_problem=regime or deduction_unknown or ('stock_eligibility_unknown' if 'unknown' in elig.values() else None)
 out['cet1']=metric(equity-w,equity_problem);out['tier1']=metric(equity-w,equity_problem)
 out['total_capital']=metric(equity-w+t,equity_problem or allowance_problem)
 if average is None:out['leverage_denominator']=metric(diagnostic='average_assets_missing')
 else:
  m=num(average);need(m>=0,'negative_average_assets');out['leverage_denominator']=metric(m-w,regime or deduction_unknown)
 ratios={k:ratio(out[n],out[d]) for k,n,d in [('cet1_ratio','cet1','rwa'),('tier1_ratio','tier1','rwa'),('total_ratio','total_capital','rwa'),('leverage_ratio','tier1','leverage_denominator')]}
 return out,ratios

def loss(cells,candidates,mode,condition,window_start,window_end):
 need(len({c['cell_id'] for c in cells})==len(cells),'duplicate_joint_cell')
 values=[];retained=[]
 for c in cells:
  e,l,s,d=(num(c[k]) for k in ('ead','lgd','cash_shortfall','discount_factor'))
  need(e>=0 and 0<=l<=1 and s>=0 and d>0,'invalid_joint_cell')
  need(e*l==s,'joint_shortfall_mismatch')
  if c['default_date'] is None:need(s==0 and e==0 and l==0,'no_default_loss')
  values.append(s*d if c['default_date'] is not None and window_start<=c['default_date']<window_end else F(0))
  retained.append(condition is None or c['default_date'] is None or c['default_date']>condition)
 possible=sorted({v for v,ok in zip(values,retained) if ok})
 need(mode in ('point_law','law_family','unweighted_histories'),'measure_mode')
 need((mode=='point_law' and len(candidates)==1) or (mode=='law_family' and len(candidates)>=1) or (mode=='unweighted_histories' and not candidates),'measure_mode_weights')
 need(len({c['law_id'] for c in candidates})==len(candidates),'duplicate_candidate_law')
 results=[];expectations=[];unresolved=False
 for c in candidates:
  weights=[num(w) for w in c['weights']]
  need(len(weights)==len(cells) and all(w>=0 for w in weights) and sum(weights)==1,'invalid_probability_measure')
  mass=sum(w for w,ok in zip(weights,retained) if ok)
  if mass==0:
   unresolved=True;results.append(dict(law_id=c['law_id'],status='unresolved',conditioning_mass=q(0),conditional_weights=[],expected_loss=None,diagnostic='zero_conditioning_mass'));continue
  conditioned=[w/mass if ok else F(0) for w,ok in zip(weights,retained)]
  value=sum(w*v for w,v in zip(conditioned,values));expectations.append(value)
  results.append(dict(law_id=c['law_id'],status='resolved',conditioning_mass=q(mass),conditional_weights=[q(w) for w in conditioned],expected_loss=q(value),diagnostic=None))
 expectations=sorted(set(expectations))
 if mode=='unweighted_histories':
  return dict(law_results=[],possible_losses=[q(v) for v in possible],expectation_status='unresolved',expectation_values=[],lower=q(min(possible)) if possible else None,upper=q(max(possible)) if possible else None,bounds_target='possible_history_losses',diagnostics=['probability_measure_missing'],accounting_allowance_claim=False)
 return dict(law_results=results,possible_losses=[q(v) for v in possible],expectation_status='unresolved' if unresolved else 'set_valued' if mode=='law_family' else 'resolved',expectation_values=[q(v) for v in expectations],lower=q(min(expectations)) if expectations and not unresolved else None,upper=q(max(expectations)) if expectations and not unresolved else None,bounds_target='undefined' if unresolved else 'expectation_over_candidate_laws',diagnostics=['zero_conditioning_mass'] if unresolved else [],accounting_allowance_claim=False)
