"""Smallest diagnostic of authored expectations against independent formulas."""
from pathlib import Path
import json
import re
import time
from authored_cases import BOOKS,CAPITAL_CASES,LOSS_CASES,CELLS
from schema_design import EXCLUSIONS,ELIGIBILITY
from financial_checks import ledger,capital,loss,q

def wire(v):
 if isinstance(v,str) and re.fullmatch(r'-?[0-9]+(?:/[0-9]+)?',v):return q(v)
 if isinstance(v,dict):return {k:wire(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [wire(x) for x in v]
 return v

def main():
 start=time.monotonic();checks=[]
 def check(name,observed,expected):checks.append(dict(check=name,passed=observed==expected,observed=observed if observed!=expected else None,expected=expected if observed!=expected else None))
 books={x['id']:x for x in BOOKS}
 for b in BOOKS:
  events=[dict(method_id=m,amount=q(a),event_date=d) for m,a,d,j in b['events']]
  state,journals,unpaid=ledger(wire(b['opening']),events,q(b['facility']))
  check(b['id']+'.balances',state,wire(b['closing']))
  check(b['id']+'.journals',journals,wire([x[3] for x in b['events']]))
  check(b['id']+'.unpaid',unpaid,q(b['unpaid']))
 for c in CAPITAL_CASES:
  app={k:'absent' for k in EXCLUSIONS};elig={k:'satisfied' for k in ELIGIBILITY}
  exp=dict(reserve_venue='federal_reserve',loan_class='ordinary_performing_nonPCD_corporate')
  changes=c['changes'];app.update(changes.get('applicability',{}));elig.update(changes.get('eligibility',{}));exp.update(changes.get('exposure',{}))
  a,r=capital(wire(books[c['book']]['closing']),app,elig,exp,changes.get('allowance','yes'),changes.get('deduction','yes'),q(c['average']) if c['average'] is not None else None)
  check(c['id']+'.capital',dict(amounts=a,ratios=r),wire(c['expected']))
 for c in LOSS_CASES:
  observed=loss(wire(CELLS),[dict(law_id=k,weights=wire(w)) for k,w in c['candidates']],c['mode'],c['condition'],c['origin'],c['end'])
  check(c['id']+'.loss',observed,wire(c['expected']))
 out=Path(__file__).resolve().parent;n=1
 while (out/f'draft-checks-{n:02}.json').exists():n+=1
 report=dict(checks=checks,total=len(checks),failures=sum(not x['passed'] for x in checks),wall_seconds=time.monotonic()-start)
 (out/f'draft-checks-{n:02}.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
 if report['failures']:print(json.dumps([x['check'] for x in checks if not x['passed']]))
 raise SystemExit(bool(report['failures']))

if __name__=='__main__':main()
