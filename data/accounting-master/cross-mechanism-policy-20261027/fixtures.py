"""Explicit synthetic message encodings over protected financial worlds."""
from pathlib import Path
import sys,json
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'temporal-family-binding-20261027'))
import family as f
MAPPING={'A':{('low',False):'L',('high',False):'H',('high',True):'X'},'B':{('low',False):'L',('high',False):'X',('high',True):'H'}}

def financial(e,mechanisms=('A','B')):
 selected=[r for r in e.rows if r['receipt']==7 and r['right']];rows=[]
 for mechanism in mechanisms:
  for row in selected:rows.append({'id':mechanism+'/'+row['row_id'],'support':row['row_id'],'mechanism':mechanism,'a1':row['a1'],'a2':row['a2'],'message1':MAPPING[mechanism][tuple(row['obs1'])],'message2':None if row['obs2'] is None else row['obs2'][-2:],'status':row['status']})
 return rows

def cash_late(transparent=False):
 rows=[]
 for mechanism in ('A','B'):
  for cash,right,raw in [(1,False,'cash'),(0,True,'facility')]:
   message=raw if mechanism=='A' or transparent else ('facility' if raw=='cash' else 'cash')
   for a2 in ('pay','draw'):
    ok=(a2=='pay' and cash>=1) or (a2=='draw' and right and cash+1>=1)
    rows.append({'id':f'{mechanism}/{raw}/wait/{a2}','support':f'{cash}/{right}/wait/{a2}','mechanism':mechanism,'a1':'wait','a2':a2,'message1':'same','message2':[message],'status':'accepted' if ok else 'refused2'})
 return rows,('wait',),('pay','draw')

def family_rows(bundle,expected,e):
 f.verify(bundle,expected,bundle['input_sha256'],e)
 if not bundle['temporal_complete']:return {'status':'unresolved_timing_budget','rows':[],'supports':bundle['supports']}
 if bundle['temporal']['status']=='inconsistent_clocks':return {'status':'inconsistent_clocks','rows':[],'supports':bundle['supports']}
 if any(z['outcome']['status']=='unresolved' for z in bundle['outcomes']):return {'status':'unresolved_observation_map','rows':[],'supports':bundle['supports']}
 rows=[]
 for item in bundle['outcomes']:
  o=item['outcome'];s=o['scenario'];mechanism=item['outcome_sha256']
  for row in e.rows:
   if row['receipt']!=s['receipt'] or (s['family']=='committed' and not row['right']):continue
   message=row['obs1'][0] if s['view']=='coarse' else row['obs1'][0]+':'+str(int(row['obs1'][1]))
   rows.append({'id':mechanism+'/'+row['row_id'],'support':row['row_id'],'mechanism':mechanism,'a1':row['a1'],'a2':row['a2'],'message1':message,'message2':None if row['obs2'] is None else row['obs2'][-2:],'status':row['status']})
 return {'status':'conditional_rows','rows':rows,'supports':bundle['supports']}
