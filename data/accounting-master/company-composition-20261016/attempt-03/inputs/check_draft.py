"""Debugging-only check; the numbered verifier supplies acceptance evidence."""
from copy import deepcopy
from fractions import Fraction as F
import json
from authored_cases import OPENING,EVENTS,EXPECTED_REPORTS
from financial_checks import derive,report
from schema_design import ACCOUNTS
def need(ok,code,status='rejected'):
 if not ok:raise AssertionError((code,status))
def main():
 s=deepcopy(OPENING);s['books']={e:{k:str(F(b.get(k,0))) for k in ACCOUNTS} for e,b in s['books'].items()};s.update(sequence=0,flows=[])
 states=[s];failures=[]
 for x in EVENTS:
  z,j,c=derive(s,x['event'],need)
  expected={e:{k:str(F(x['journals'].get(e,{}).get(k,0))) for k in ACCOUNTS} for e in ['P','S']}
  if j!=expected:failures.append({'case':x['id'],'kind':'journal','actual':j,'expected':expected})
  if c!=x['cash']:failures.append({'case':x['id'],'kind':'cash'})
  for k,v in x['changes'].items():
   if z[k]!=v:failures.append({'case':x['id'],'field':k,'actual':z[k],'expected':v})
  s=z;states.append(s)
 for key,x in EXPECTED_REPORTS.items():
  g,l=report(states[8 if key=='h2' else 0],states[x['through']],x['start'],x['end'],need)
  for scope,actual in [('group',g),('legal',l)]:
   if actual!=x[scope]:failures.append({'report':key,'scope':scope,'actual':actual,'expected':x[scope]})
 print(json.dumps({'debug_only':True,'events':len(EVENTS),'failures':failures}))
 raise SystemExit(bool(failures))
if __name__=='__main__':main()
