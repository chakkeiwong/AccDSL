"""Independent explicit signed journals and full reports for the supplied case."""
from copy import deepcopy
from fractions import Fraction as F
from bridge import rt,fmt,CLASSES,DATES
# Shared format/schema constants only. No candidate condition/posting method.
def financial_oracle(body,mapping,case):
 mode,right,r1,r2,R,a1,a2=case
 def I(r):
  if mode=='fixed':return F(5)
  return F(3) if F(r)<=F(3,100) else F(6) if F(r)>=F(3,50) else 100*F(r)
 amounts={'accrue1':I(r1),'accrue2':I(r2),'receipt2':F(R)}
 cur=deepcopy(body['opening']);traces=[];stop=None
 for command in body['commands']:
  key=command['method_key'];t=int(key[-1]);mem=cur['memory'];cash=F(cur['balances'][mapping['cash']])
  delta={k:F(0) for k in CLASSES};flows=[];changes={}
  if key.startswith('accrue'):
   value=amounts[key];delta.update(interest_expense=value,interest_payable=-value);changes={'phase':'due'+str(t),'due'+str(t):fmt(value)}
  elif key=='receipt2':
   value=F(R);delta.update(cash=value,income=-value);changes={'phase':'receipt2'}
   flows=[('operating_receipt','operating',value)]
  elif key=='repay2':
   value=F(cur['balances'][mapping['facility_debt']])
   delta.update(cash=value,facility_debt=-value);changes={'phase':'repaid2'}
   flows=[('facility_repayment','financing',value)]
  else:
   value=I(r1 if t==1 else r2);draw=key.startswith('draw')
   permitted=(right and not mem['used'] and value>F(11,2) and cash+F(3,4)>=value) if draw else cash>=value
   if not permitted:stop={'key':key,'phase':mem['phase'],'unpaid':value};break
   delta.update(cash=(F(3,4) if draw else F(0))-value,interest_payable=value)
   changes={'phase':'settled'+str(t),'paid'+str(t):fmt(value),'action'+str(t):'draw' if draw else 'pay'}
   if draw:
    delta.update(facility_debt=F(-1),fee_expense=F(1,4));changes['used']=True
    flows=[('facility_draw','financing',F(1)),('facility_fee','operating',F(-1,4))]
   flows.append(('interest_payment','operating',-value))
  before=deepcopy(cur)
  for role,value in delta.items():cur['balances'][mapping[role]]=fmt(F(cur['balances'][mapping[role]])+value)
  cur['memory'].update(changes);cur['date']=DATES[t];cur['seen'].append(key)
  flowrows=[{'id':rt.digest([key,name]),'entity':cur['context']['entity'],'book':cur['context']['book'],'currency':'USD','event_id':key,'date':DATES[t],'activity':activity,'origin':name,'amount':fmt(value)} for name,activity,value in flows]
  cur['flows'].extend(flowrows)
  traces.append({'key':key,'before':before,'after':deepcopy(cur),'journal':{mapping[k]:fmt(v) for k,v in delta.items()},'flows':flowrows})
 return cur,traces,stop

def report_oracle(body,current):
 opening=body['opening'];groups={k:[] for k in ('asset','liability','equity','income','expense')}
 begin={k:F(0) for k in groups};end={k:F(0) for k in groups}
 for row in body['mapping']['lines']:
  k=row['classification'];sgn=-1 if k in ('liability','equity','income') else 1
  a=sgn*sum(F(opening['balances'][x]) for x in row['accounts']);b=sgn*sum(F(current['balances'][x]) for x in row['accounts'])
  begin[k]+=a;end[k]+=b;groups[k].append({**deepcopy(row),'opening':fmt(a),'closing':fmt(b)})
 profit=end['income']-end['expense'];cash0=F(opening['balances'][opening['cash_account']]);cash1=F(current['balances'][current['cash_account']])
 activities={}
 for activity in ('operating','investing','financing'):
  xs=[F(f['amount']) for f in current['flows'] if f['activity']==activity];pos=sum(x for x in xs if x>=0);neg=-sum(x for x in xs if x<0)
  activities[activity]={'receipts':fmt(pos),'payments':fmt(neg),'net':fmt(pos-neg)}
 # Metadata binds the entire report request. It is not the financial oracle.
 req={'profile':rt.reports.PROFILE,'opening':deepcopy(opening),'closing':deepcopy(current),'schemas':deepcopy(body['schemas']),'mapping':deepcopy(body['mapping']),'equity_movements':[],'notes':[],'expected_opening_sha256':rt.digest(opening),'expected_closing_sha256':rt.digest(current),'expected_mapping_sha256':rt.digest(body['mapping'])}
 result={'profile':rt.reports.PROFILE,**rt.reports.FLAGS,'status':'reported','scope':'recorded_period_only','context':deepcopy(current['context']),'period':deepcopy(current['period']),'as_of':current['date'],'statement_lines':groups,
 'opening_totals':{k:fmt(v) for k,v in begin.items()},'closing_totals':{k:fmt(v) for k,v in end.items()},
 'balance_sheet':{'total_assets':fmt(end['asset']),'total_liabilities':fmt(end['liability']),'equity_including_profit':fmt(end['equity']+profit)},
 'income':{'income':fmt(end['income']),'expenses':fmt(end['expense']),'profit':fmt(profit)},
 'cash_flows':{'activities':activities,'opening_cash':fmt(cash0),'closing_cash':fmt(cash1),'net_movement':fmt(cash1-cash0),'gross_origins':deepcopy(current['flows'])},
 'equity':{'opening':fmt(begin['equity']),'direct_movements':'0/1','profit':fmt(profit),'closing':fmt(end['equity']+profit),'by_account':{k:'0/1' for k,v in current['accounts'].items() if v['classification']=='equity'},'movements':[]},
 'reconciliations':{'balance_sheet':fmt(end['asset']-end['liability']-end['equity']-profit),'cash':fmt(cash1-cash0-sum(F(x['amount']) for x in current['flows'])),'equity':fmt(end['equity']-begin['equity'])},'notes':[],
 'unresolved':['Event-population completeness','Source and accounting admission','Complete note package','Indirect operating cash-flow bridge'],
 'request_sha256':rt.digest(req),'opening_sha256':rt.digest(opening),'closing_sha256':rt.digest(current),'mapping_sha256':rt.digest(body['mapping']),'implementation_sha256':rt.sha256(rt.Path(rt.reports.__file__).read_bytes()).hexdigest() if hasattr(rt,'sha256') else None,'book_sha256':rt.reports.BOOK_SHA256}
 return result
