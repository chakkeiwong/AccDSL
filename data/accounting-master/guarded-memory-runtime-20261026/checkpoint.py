"""Replay-validated finite concrete checkpoints, not continuous certification."""
from copy import deepcopy as cp
from itertools import product
import bridge as b
rt=b.rt
PROFILE='SelectedGuardedCheckpoint/1'

def need(ok,label):
 if not ok:raise ValueError(label)
def scope():
 return {'source_revision':'synthetic-source-v1','clause':'once-only-v1','actor':'manager','observation':'refined-first-and-second-cash-coverage','actions':['pay','draw'],'query':'full-book-refusal-prefix','horizon':'two-dates','precision':'exact-rational','method':'common-engine-selected-bridge-1'}
def seed(body,expected_scope):
 rt.validate(body)
 return {'profile':PROFILE,'scope':cp(expected_scope),'program':rt.digest(body),'registry':rt.digest(body['registry']),'cursor':0,'current':cp(body['opening']),'accepted':[],'stop':None,'remaining':[rt.identity(x) for x in body['commands']],'status':'pending_concrete'}
def step(body,record):
 need(record['stop'] is None,'already_refused');i=record['cursor'];need(i<len(body['commands']),'already_complete')
 command=body['commands'][i];before=cp(record['current']);req=rt.call(before,body['registry'],command);proposal=rt.methods.propose(before,req)
 entry={'index':i,'command':cp(command),'request':req,'result':proposal,'before_sha256':rt.digest(before)}
 if proposal['status']=='proposed':
  record['current']=cp(proposal['transition']['after']);record['accepted'].append(entry);record['cursor']+=1
 else:record['stop']=entry
 record['remaining']=[rt.identity(c) for c in body['commands'][record['cursor']:]]
 record['status']='refused_concrete' if record['stop'] else 'complete_concrete' if record['cursor']==len(body['commands']) else 'pending_concrete'
 return record

def validate(body,expected_scope,record):
 need(isinstance(record,dict),'record');need(record.get('profile')==PROFILE,'profile')
 need(record.get('scope')==expected_scope,'scope_changed');need(record.get('program')==rt.digest(body),'program_changed');need(record.get('registry')==rt.digest(body['registry']),'registry_changed')
 cursor=record.get('cursor');need(type(cursor)==int and 0<=cursor<=len(body['commands']),'cursor')
 fresh=seed(body,expected_scope)
 for _ in range(cursor):
  need(fresh['stop'] is None,'cursor_after_refusal');step(body,fresh)
  need(fresh['stop'] is None,'cursor_includes_refusal')
 if record.get('stop') is not None:
  need(cursor<len(body['commands']),'stop_after_complete');step(body,fresh);need(fresh['stop'] is not None,'invented_stop')
 need(fresh==record,'checkpoint_replay_mismatch')
 return True

def advance(body,expected_scope,record,budget):
 need(type(budget)==int and budget>=0,'budget')
 validate(body,expected_scope,record);out=cp(record)
 attempted=0
 while attempted<budget and out['stop'] is None and out['cursor']<len(body['commands']):
  step(body,out);attempted+=1
 return out,attempted

def roster():
 # IDs are complete region obligations for the exact two-date fixture. No
 # witness checkpoint can populate completed_regions in this layer.
 return ['|'.join(map(str,x)) for x in product(('fixed','floating'),(False,True),range(11),range(11),('pay','draw'),('pay','draw'),(6,7))]

def queue(jobs):
 need(isinstance(jobs,dict) and all(isinstance(k,str) and isinstance(v,str) for k,v in jobs.items()),'job_program_map')
 return {'profile':'SelectedGuardedQueue/1','jobs':list(jobs),'job_programs':cp(jobs),'pending':list(jobs),'completed':[],'refused':[],'records':{},'region_roster':roster(),'completed_regions':[],'continuous_status':'unresolved'}
def validate_queue(expected_jobs,q):
 need(q.get('profile')=='SelectedGuardedQueue/1','queue_profile');need(q.get('jobs')==list(expected_jobs) and q.get('job_programs')==expected_jobs,'changed_job_roster')
 parts=q['pending']+q['completed']+q['refused'];need(len(parts)==len(set(parts)) and set(parts)==set(expected_jobs),'job_partition')
 need(set(q['records'])==set(q['completed']+q['refused']),'record_partition')
 for k in q['records']:need(q['records'][k]['program']==expected_jobs[k],'record_program_binding')
 for k in q['completed']:need(q['records'][k]['status']=='complete_concrete','completed_status')
 for k in q['refused']:need(q['records'][k]['status']=='refused_concrete','refused_status')
 need(q['region_roster']==roster() and not q['completed_regions'] and q['continuous_status']=='unresolved','unjustified_region_completion')
 return True

def finish(q,key,record):
 out=cp(q);need(key in out['pending'],'job_not_pending');need(record['status'] in ('complete_concrete','refused_concrete'),'unfinished_job')
 out['pending'].remove(key);out['completed' if record['status']=='complete_concrete' else 'refused'].append(key);out['records'][key]=cp(record)
 validate_queue(out['job_programs'],out);return out
