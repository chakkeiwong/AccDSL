"""Independent row reconstruction from original observations and supplied finite tables."""
import json

def rows(bundle,d,e):
 answer=[]
 for outcome in sorted(bundle['outcomes'],key=lambda x:x['outcome_sha256']):
  o=outcome['outcome']
  if o['status']!='selected_conditional':continue
  oid=outcome['outcome_sha256'];spec=next(x for x in d['maps'] if x['outcome_sha256']==oid);s=o['scenario']
  tag=spec['tag'];when=tag['reveal'];tok=None if when=='never' else d['tag_observations'][tag['observation_sha256']]['token']
  for r in e.rows:
   if r['receipt']!=s['receipt'] or s['family']=='committed' and not r['right']:continue
   obs=r['obs1'] if s['view']=='refined' else [r['obs1'][0]]
   msg=next(x['token'] for x in spec['first'] if x['key']==obs)
   later=None
   if r['obs2'] is not None:later=[next(x['token'] for x in spec['second'] if x['key']==r['obs2'][-2:]),tok if when in ('first','second') else '']
   answer.append({'id':oid+'/'+r['row_id'],'support':r['row_id'],'mechanism':oid,'a1':r['a1'],'a2':r['a2'],'message1':json.dumps([msg,tok if when=='first' else None],ensure_ascii=False,separators=(',',':')),'message2':later,'status':r['status']})
 return answer
